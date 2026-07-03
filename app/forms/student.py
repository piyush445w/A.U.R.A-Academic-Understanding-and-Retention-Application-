"""
Student Management Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, IntegerField, 
    TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)
from datetime import date
from app.models.student import Student


class StudentForm(FlaskForm):
    """Form for adding/editing student information."""
    
    student_id = StringField(
        'Student ID',
        validators=[
            DataRequired(message='Student ID is required'),
            Length(min=3, max=20, message='Student ID must be between 3 and 20 characters')
        ],
        render_kw={'placeholder': 'Enter student ID'}
    )
    
    first_name = StringField(
        'First Name',
        validators=[
            DataRequired(message='First name is required'),
            Length(min=2, max=50, message='First name must be between 2 and 50 characters')
        ],
        render_kw={'placeholder': 'Enter first name'}
    )
    
    last_name = StringField(
        'Last Name',
        validators=[
            DataRequired(message='Last name is required'),
            Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
        ],
        render_kw={'placeholder': 'Enter last name'}
    )
    
    date_of_birth = DateField(
        'Date of Birth',
        validators=[DataRequired(message='Date of birth is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    gender = SelectField(
        'Gender',
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ],
        validators=[DataRequired(message='Please select gender')]
    )
    
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(max=20, message='Phone number must not exceed 20 characters')
        ],
        render_kw={'placeholder': 'Enter phone number'}
    )
    
    address = TextAreaField(
        'Address',
        validators=[
            Optional(),
            Length(max=500, message='Address must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter address', 'rows': 3}
    )
    
    course = StringField(
        'Course',
        validators=[
            DataRequired(message='Course is required'),
            Length(max=100, message='Course must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter course name'}
    )
    
    semester = IntegerField(
        'Semester',
        validators=[
            DataRequired(message='Semester is required'),
            NumberRange(min=1, max=10, message='Semester must be between 1 and 10')
        ],
        render_kw={'placeholder': 'Enter semester number'}
    )
    
    admission_date = DateField(
        'Admission Date',
        validators=[DataRequired(message='Admission date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    guardian_name = StringField(
        'Guardian Name',
        validators=[
            Optional(),
            Length(max=100, message='Guardian name must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter guardian name'}
    )
    
    guardian_phone = StringField(
        'Guardian Phone',
        validators=[
            Optional(),
            Length(max=20, message='Guardian phone must not exceed 20 characters')
        ],
        render_kw={'placeholder': 'Enter guardian phone number'}
    )
    
    submit = SubmitField('Save Student')
    
    def __init__(self, student=None, *args, **kwargs):
        """Initialize form with student for editing."""
        super(StudentForm, self).__init__(*args, **kwargs)
        self.student = student
    
    def validate_student_id(self, field):
        """Validate that student ID is unique."""
        if self.student:
            # Editing existing student
            if field.data != self.student.student_id:
                if Student.query.filter_by(student_id=field.data).first():
                    raise ValidationError('Student ID already exists')
        else:
            # New student
            if Student.query.filter_by(student_id=field.data).first():
                raise ValidationError('Student ID already exists')
    
    def validate_date_of_birth(self, field):
        """Validate date of birth is not in the future."""
        if field.data > date.today():
            raise ValidationError('Date of birth cannot be in the future')
    
    def validate_admission_date(self, field):
        """Validate admission date is not before date of birth."""
        if self.date_of_birth.data and field.data < self.date_of_birth.data:
            raise ValidationError('Admission date cannot be before date of birth')


class StudentSearchForm(FlaskForm):
    """Form for searching students."""
    
    search_query = StringField(
        'Search',
        validators=[
            Optional(),
            Length(max=100, message='Search query must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Search by name or student ID'}
    )
    
    course = StringField(
        'Course',
        validators=[
            Optional(),
            Length(max=100, message='Course must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Filter by course'}
    )
    
    semester = IntegerField(
        'Semester',
        validators=[
            Optional(),
            NumberRange(min=1, max=10, message='Semester must be between 1 and 10')
        ],
        render_kw={'placeholder': 'Filter by semester'}
    )
    
    submit = SubmitField('Search')
