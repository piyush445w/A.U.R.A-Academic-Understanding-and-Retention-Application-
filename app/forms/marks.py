"""
Academic Marks Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, DecimalField, 
    TextAreaField, SubmitField, HiddenField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)
from datetime import date
from app.models.marks import Marks
from app.models.student import Student
from app.models.subject import Subject


class MarksForm(FlaskForm):
    """Form for adding/editing student marks."""
    
    student_id = SelectField(
        'Student',
        coerce=int,
        validators=[DataRequired(message='Please select a student')],
        render_kw={'placeholder': 'Select student'}
    )
    
    subject_id = SelectField(
        'Subject',
        coerce=int,
        validators=[DataRequired(message='Please select a subject')],
        render_kw={'placeholder': 'Select subject'}
    )
    
    exam_type = SelectField(
        'Exam Type',
        choices=[
            ('Midterm', 'Midterm'),
            ('Final', 'Final'),
            ('Assignment', 'Assignment'),
            ('Quiz', 'Quiz'),
            ('Project', 'Project')
        ],
        validators=[DataRequired(message='Please select exam type')]
    )
    
    marks_obtained = DecimalField(
        'Marks Obtained',
        validators=[
            DataRequired(message='Marks obtained is required'),
            NumberRange(min=0, message='Marks cannot be negative')
        ],
        places=2,
        render_kw={'placeholder': 'Enter marks obtained'}
    )
    
    max_marks = DecimalField(
        'Maximum Marks',
        validators=[
            DataRequired(message='Maximum marks is required'),
            NumberRange(min=1, message='Maximum marks must be at least 1')
        ],
        places=2,
        render_kw={'placeholder': 'Enter maximum marks'}
    )
    
    exam_date = DateField(
        'Exam Date',
        validators=[DataRequired(message='Exam date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    remarks = TextAreaField(
        'Remarks',
        validators=[
            Optional(),
            Length(max=500, message='Remarks must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter any remarks', 'rows': 3}
    )
    
    submit = SubmitField('Save Marks')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with student and subject choices."""
        super(MarksForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [
            (s.id, f"{s.student_id} - {s.full_name}") 
            for s in Student.query.order_by(Student.first_name).all()
        ]
        self.subject_id.choices = [
            (s.id, f"{s.subject_code} - {s.subject_name}") 
            for s in Subject.query.order_by(Subject.subject_name).all()
        ]
    
    def validate_marks_obtained(self, field):
        """Validate marks obtained doesn't exceed max marks."""
        if self.max_marks.data and field.data > self.max_marks.data:
            raise ValidationError('Marks obtained cannot exceed maximum marks')
    
    def validate_exam_date(self, field):
        """Validate exam date is not in the future."""
        if field.data > date.today():
            raise ValidationError('Exam date cannot be in the future')


class BulkMarksForm(FlaskForm):
    """Form for adding bulk marks for a subject."""
    
    subject_id = SelectField(
        'Subject',
        coerce=int,
        validators=[DataRequired(message='Please select a subject')],
        render_kw={'placeholder': 'Select subject'}
    )
    
    exam_type = SelectField(
        'Exam Type',
        choices=[
            ('Midterm', 'Midterm'),
            ('Final', 'Final'),
            ('Assignment', 'Assignment'),
            ('Quiz', 'Quiz'),
            ('Project', 'Project')
        ],
        validators=[DataRequired(message='Please select exam type')]
    )
    
    max_marks = DecimalField(
        'Maximum Marks',
        validators=[
            DataRequired(message='Maximum marks is required'),
            NumberRange(min=1, message='Maximum marks must be at least 1')
        ],
        places=2,
        render_kw={'placeholder': 'Enter maximum marks'}
    )
    
    exam_date = DateField(
        'Exam Date',
        validators=[DataRequired(message='Exam date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    marks_data = HiddenField(
        'Marks Data',
        validators=[DataRequired(message='Marks data is required')]
    )
    
    submit = SubmitField('Save Bulk Marks')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with subject choices."""
        super(BulkMarksForm, self).__init__(*args, **kwargs)
        self.subject_id.choices = [
            (s.id, f"{s.subject_code} - {s.subject_name}") 
            for s in Subject.query.order_by(Subject.subject_name).all()
        ]
    
    def validate_exam_date(self, field):
        """Validate exam date is not in the future."""
        if field.data > date.today():
            raise ValidationError('Exam date cannot be in the future')
