"""
Attendance Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, TextAreaField, 
    SubmitField, HiddenField
)
from wtforms.validators import (
    DataRequired, Length, Optional, ValidationError
)
from datetime import date
from app.models.attendance import Attendance
from app.models.student import Student


class AttendanceForm(FlaskForm):
    """Form for marking individual student attendance."""
    
    student_id = SelectField(
        'Student',
        coerce=int,
        validators=[DataRequired(message='Please select a student')],
        render_kw={'placeholder': 'Select student'}
    )
    
    date = DateField(
        'Date',
        validators=[DataRequired(message='Date is required')],
        format='%Y-%m-%d',
        default=date.today,
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent'),
            ('Late', 'Late'),
            ('Excused', 'Excused')
        ],
        validators=[DataRequired(message='Please select attendance status')]
    )
    
    remarks = TextAreaField(
        'Remarks',
        validators=[
            Optional(),
            Length(max=500, message='Remarks must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter any remarks', 'rows': 3}
    )
    
    submit = SubmitField('Mark Attendance')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with student choices."""
        super(AttendanceForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [
            (s.id, f"{s.student_id} - {s.full_name}") 
            for s in Student.query.order_by(Student.first_name).all()
        ]
    
    def validate_date(self, field):
        """Validate date is not in the future."""
        if field.data > date.today():
            raise ValidationError('Attendance date cannot be in the future')


class BulkAttendanceForm(FlaskForm):
    """Form for marking bulk attendance for a class."""
    
    date = DateField(
        'Date',
        validators=[DataRequired(message='Date is required')],
        format='%Y-%m-%d',
        default=date.today,
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    course = StringField(
        'Course',
        validators=[
            DataRequired(message='Course is required'),
            Length(max=100, message='Course must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter course name'}
    )
    
    semester = StringField(
        'Semester',
        validators=[
            DataRequired(message='Semester is required'),
            Length(max=10, message='Semester must not exceed 10 characters')
        ],
        render_kw={'placeholder': 'Enter semester'}
    )
    
    attendance_data = HiddenField(
        'Attendance Data',
        validators=[DataRequired(message='Attendance data is required')]
    )
    
    submit = SubmitField('Save Bulk Attendance')
    
    def validate_date(self, field):
        """Validate date is not in the future."""
        if field.data > date.today():
            raise ValidationError('Attendance date cannot be in the future')


class AttendanceReportForm(FlaskForm):
    """Form for generating attendance reports."""
    
    start_date = DateField(
        'Start Date',
        validators=[DataRequired(message='Start date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    end_date = DateField(
        'End Date',
        validators=[DataRequired(message='End date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    course = StringField(
        'Course',
        validators=[
            Optional(),
            Length(max=100, message='Course must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Filter by course (optional)'}
    )
    
    semester = StringField(
        'Semester',
        validators=[
            Optional(),
            Length(max=10, message='Semester must not exceed 10 characters')
        ],
        render_kw={'placeholder': 'Filter by semester (optional)'}
    )
    
    submit = SubmitField('Generate Report')
    
    def validate_start_date(self, field):
        """Validate start date is not in the future."""
        if field.data > date.today():
            raise ValidationError('Start date cannot be in the future')
    
    def validate_end_date(self, field):
        """Validate end date is after start date."""
        if self.start_date.data and field.data < self.start_date.data:
            raise ValidationError('End date must be after start date')
