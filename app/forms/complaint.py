"""
Complaint Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, ValidationError
)
from app.models.complaint import Complaint
from app.models.user import User


class ComplaintForm(FlaskForm):
    """Form for submitting complaints."""
    
    subject = StringField(
        'Subject',
        validators=[
            DataRequired(message='Subject is required'),
            Length(min=5, max=200, message='Subject must be between 5 and 200 characters')
        ],
        render_kw={'placeholder': 'Enter complaint subject'}
    )
    
    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message='Description is required'),
            Length(min=10, max=2000, message='Description must be between 10 and 2000 characters')
        ],
        render_kw={'placeholder': 'Describe your complaint in detail', 'rows': 5}
    )
    
    category = SelectField(
        'Category',
        choices=[
            ('Academic', 'Academic'),
            ('Administrative', 'Administrative'),
            ('Infrastructure', 'Infrastructure'),
            ('Other', 'Other')
        ],
        validators=[DataRequired(message='Please select a category')]
    )
    
    priority = SelectField(
        'Priority',
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
            ('Urgent', 'Urgent')
        ],
        validators=[DataRequired(message='Please select priority')],
        default='Medium'
    )
    
    submit = SubmitField('Submit Complaint')


class ComplaintResponseForm(FlaskForm):
    """Form for responding to complaints."""
    
    status = SelectField(
        'Status',
        choices=[
            ('Open', 'Open'),
            ('In Progress', 'In Progress'),
            ('Resolved', 'Resolved'),
            ('Closed', 'Closed')
        ],
        validators=[DataRequired(message='Please select status')]
    )
    
    assigned_to = SelectField(
        'Assign To',
        coerce=int,
        validators=[Optional()],
        render_kw={'placeholder': 'Select assignee'}
    )
    
    resolution = TextAreaField(
        'Resolution',
        validators=[
            Optional(),
            Length(max=2000, message='Resolution must not exceed 2000 characters')
        ],
        render_kw={'placeholder': 'Enter resolution details', 'rows': 5}
    )
    
    submit = SubmitField('Update Complaint')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with user choices for assignment."""
        super(ComplaintResponseForm, self).__init__(*args, **kwargs)
        # Only show admin and teacher users for assignment
        self.assigned_to.choices = [
            (0, 'Unassigned')
        ] + [
            (u.id, f"{u.username} ({u.role})") 
            for u in User.query.filter(User.role.in_(['admin', 'teacher'])).order_by(User.username).all()
        ]
    
    def validate_resolution(self, field):
        """Validate resolution is provided when status is Resolved or Closed."""
        if self.status.data in ['Resolved', 'Closed'] and not field.data:
            raise ValidationError('Resolution is required when status is Resolved or Closed')
