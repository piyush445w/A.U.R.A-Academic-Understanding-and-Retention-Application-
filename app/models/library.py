"""
Library Models
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime, date
from app import db


class LibraryBook(db.Model):
    """Library book model for storing book inventory information."""
    
    __tablename__ = 'library_books'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Book details
    book_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    author = db.Column(db.String(200), nullable=False, index=True)
    isbn = db.Column(db.String(20), unique=True, index=True)
    category = db.Column(db.String(100), index=True)
    total_copies = db.Column(db.Integer, nullable=False, default=1)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    transactions = db.relationship('LibraryTransaction', backref='book', lazy='dynamic', cascade='all, delete-orphan')
    
    # Check constraint to ensure available copies don't exceed total
    __table_args__ = (
        db.CheckConstraint('available_copies >= 0 AND available_copies <= total_copies', 
                          name='chk_library_books_copies'),
    )
    
    def __init__(self, book_id, title, author, isbn=None, category=None, 
                 total_copies=1, available_copies=None):
        """Initialize library book."""
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.total_copies = total_copies
        self.available_copies = available_copies if available_copies is not None else total_copies
    
    @property
    def is_available(self):
        """Check if book is available for issue."""
        return self.available_copies > 0
    
    @property
    def issued_copies(self):
        """Get number of issued copies."""
        return self.total_copies - self.available_copies
    
    def issue_book(self):
        """Issue a copy of the book."""
        if not self.is_available:
            raise ValueError("No copies available for issue")
        self.available_copies -= 1
    
    def return_book(self):
        """Return a copy of the book."""
        if self.available_copies >= self.total_copies:
            raise ValueError("All copies are already available")
        self.available_copies += 1
    
    @staticmethod
    def search_books(query):
        """
        Search books by title, author, or ISBN.
        
        Args:
            query: Search query
            
        Returns:
            List of matching books
        """
        search_pattern = f'%{query}%'
        return LibraryBook.query.filter(
            db.or_(
                LibraryBook.title.ilike(search_pattern),
                LibraryBook.author.ilike(search_pattern),
                LibraryBook.isbn.ilike(search_pattern)
            )
        ).all()
    
    @staticmethod
    def get_books_by_category(category):
        """
        Get books by category.
        
        Args:
            category: Book category
            
        Returns:
            List of books
        """
        return LibraryBook.query.filter_by(category=category).all()
    
    def to_dict(self):
        """Convert book to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'category': self.category,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'issued_copies': self.issued_copies,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of LibraryBook."""
        return f'<LibraryBook {self.book_id}: {self.title}>'


class LibraryTransaction(db.Model):
    """Library transaction model for book issue and return records."""
    
    __tablename__ = 'library_transactions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('library_books.id', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False, index=True)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT', onupdate='CASCADE'),
                         nullable=False, index=True)
    returned_to = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'))
    
    # Transaction details
    issue_date = db.Column(db.Date, nullable=False, index=True)
    due_date = db.Column(db.Date, nullable=False, index=True)
    return_date = db.Column(db.Date)
    status = db.Column(db.Enum('Issued', 'Returned', 'Overdue', name='transaction_status'),
                      nullable=False, default='Issued', index=True)
    fine_amount = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Check constraint to ensure fine is non-negative
    __table_args__ = (
        db.CheckConstraint('fine_amount >= 0', name='chk_library_transactions_fine'),
    )
    
    def __init__(self, student_id, book_id, issue_date, due_date, issued_by,
                 status='Issued', fine_amount=0.00):
        """Initialize library transaction."""
        self.student_id = student_id
        self.book_id = book_id
        self.issue_date = issue_date
        self.due_date = due_date
        self.issued_by = issued_by
        self.status = status
        self.fine_amount = fine_amount
    
    @property
    def is_overdue(self):
        """Check if book is overdue."""
        if self.status == 'Returned':
            return False
        return date.today() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    @property
    def calculate_fine(self):
        """Calculate fine based on days overdue."""
        if not self.is_overdue:
            return 0.00
        # Fine rate: $0.50 per day
        return round(self.days_overdue * 0.50, 2)
    
    def return_book(self, returned_to):
        """Return the book."""
        self.status = 'Returned'
        self.return_date = date.today()
        self.returned_to = returned_to
        self.fine_amount = self.calculate_fine
        
        # Update book availability
        self.book.return_book()
    
    def mark_as_overdue(self):
        """Mark transaction as overdue."""
        if self.status == 'Issued' and self.is_overdue:
            self.status = 'Overdue'
            self.fine_amount = self.calculate_fine
    
    @staticmethod
    def get_active_transactions(student_id):
        """
        Get active (issued/overdue) transactions for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of active transactions
        """
        return LibraryTransaction.query.filter(
            LibraryTransaction.student_id == student_id,
            LibraryTransaction.status.in_(['Issued', 'Overdue'])
        ).order_by(LibraryTransaction.due_date).all()
    
    @staticmethod
    def get_overdue_transactions(student_id=None):
        """
        Get overdue transactions.
        
        Args:
            student_id: Filter by student (optional)
            
        Returns:
            List of overdue transactions
        """
        query = LibraryTransaction.query.filter_by(status='Overdue')
        if student_id:
            query = query.filter_by(student_id=student_id)
        return query.order_by(LibraryTransaction.due_date).all()
    
    @staticmethod
    def get_transaction_history(student_id):
        """
        Get transaction history for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of transactions
        """
        return LibraryTransaction.query.filter_by(student_id=student_id).order_by(
            LibraryTransaction.issue_date.desc()
        ).all()
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'book_id': self.book_id,
            'issued_by': self.issued_by,
            'returned_to': self.returned_to,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'status': self.status,
            'fine_amount': float(self.fine_amount),
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'calculated_fine': self.calculate_fine,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of LibraryTransaction."""
        return f'<LibraryTransaction {self.student_id} - {self.book_id}: {self.status}>'
