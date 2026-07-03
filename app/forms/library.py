"""
Library Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, IntegerField, 
    DecimalField, TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)
from datetime import date, timedelta
from app.models.library import LibraryBook, LibraryTransaction
from app.models.student import Student


class BookForm(FlaskForm):
    """Form for adding/editing library books."""
    
    book_id = StringField(
        'Book ID',
        validators=[
            DataRequired(message='Book ID is required'),
            Length(min=3, max=20, message='Book ID must be between 3 and 20 characters')
        ],
        render_kw={'placeholder': 'Enter book ID'}
    )
    
    title = StringField(
        'Title',
        validators=[
            DataRequired(message='Title is required'),
            Length(max=255, message='Title must not exceed 255 characters')
        ],
        render_kw={'placeholder': 'Enter book title'}
    )
    
    author = StringField(
        'Author',
        validators=[
            DataRequired(message='Author is required'),
            Length(max=200, message='Author must not exceed 200 characters')
        ],
        render_kw={'placeholder': 'Enter author name'}
    )
    
    isbn = StringField(
        'ISBN',
        validators=[
            Optional(),
            Length(max=20, message='ISBN must not exceed 20 characters')
        ],
        render_kw={'placeholder': 'Enter ISBN'}
    )
    
    category = StringField(
        'Category',
        validators=[
            Optional(),
            Length(max=100, message='Category must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter book category'}
    )
    
    total_copies = IntegerField(
        'Total Copies',
        validators=[
            DataRequired(message='Total copies is required'),
            NumberRange(min=1, message='Total copies must be at least 1')
        ],
        render_kw={'placeholder': 'Enter total copies'}
    )
    
    submit = SubmitField('Save Book')
    
    def __init__(self, book=None, *args, **kwargs):
        """Initialize form with book for editing."""
        super(BookForm, self).__init__(*args, **kwargs)
        self.book = book
    
    def validate_book_id(self, field):
        """Validate that book ID is unique."""
        if self.book:
            # Editing existing book
            if field.data != self.book.book_id:
                if LibraryBook.query.filter_by(book_id=field.data).first():
                    raise ValidationError('Book ID already exists')
        else:
            # New book
            if LibraryBook.query.filter_by(book_id=field.data).first():
                raise ValidationError('Book ID already exists')
    
    def validate_isbn(self, field):
        """Validate that ISBN is unique."""
        if field.data:
            if self.book:
                # Editing existing book
                if field.data != self.book.isbn:
                    if LibraryBook.query.filter_by(isbn=field.data).first():
                        raise ValidationError('ISBN already exists')
            else:
                # New book
                if LibraryBook.query.filter_by(isbn=field.data).first():
                    raise ValidationError('ISBN already exists')


class IssueBookForm(FlaskForm):
    """Form for issuing books to students."""
    
    student_id = SelectField(
        'Student',
        coerce=int,
        validators=[DataRequired(message='Please select a student')],
        render_kw={'placeholder': 'Select student'}
    )
    
    book_id = SelectField(
        'Book',
        coerce=int,
        validators=[DataRequired(message='Please select a book')],
        render_kw={'placeholder': 'Select book'}
    )
    
    due_date = DateField(
        'Due Date',
        validators=[DataRequired(message='Due date is required')],
        format='%Y-%m-%d',
        default=lambda: date.today() + timedelta(days=14),
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    submit = SubmitField('Issue Book')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with student and book choices."""
        super(IssueBookForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [
            (s.id, f"{s.student_id} - {s.full_name}") 
            for s in Student.query.order_by(Student.first_name).all()
        ]
        # Only show available books
        self.book_id.choices = [
            (b.id, f"{b.book_id} - {b.title} ({b.available_copies} available)") 
            for b in LibraryBook.query.filter(LibraryBook.available_copies > 0).order_by(LibraryBook.title).all()
        ]
    
    def validate_due_date(self, field):
        """Validate due date is in the future."""
        if field.data <= date.today():
            raise ValidationError('Due date must be in the future')


class ReturnBookForm(FlaskForm):
    """Form for returning books."""
    
    transaction_id = SelectField(
        'Transaction',
        coerce=int,
        validators=[DataRequired(message='Please select a transaction')],
        render_kw={'placeholder': 'Select transaction'}
    )
    
    fine_amount = DecimalField(
        'Fine Amount',
        validators=[
            Optional(),
            NumberRange(min=0, message='Fine amount cannot be negative')
        ],
        places=2,
        default=0,
        render_kw={'placeholder': 'Enter fine amount (if any)'}
    )
    
    remarks = TextAreaField(
        'Remarks',
        validators=[
            Optional(),
            Length(max=500, message='Remarks must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter any remarks', 'rows': 3}
    )
    
    submit = SubmitField('Return Book')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with active transaction choices."""
        super(ReturnBookForm, self).__init__(*args, **kwargs)
        # Only show issued transactions
        self.transaction_id.choices = [
            (t.id, f"{t.transaction_id} - {t.book.title} (Issued to: {t.student.full_name})") 
            for t in LibraryTransaction.query.filter_by(status='Issued').order_by(LibraryTransaction.issue_date).all()
        ]
