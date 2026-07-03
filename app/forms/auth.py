"""
Authentication Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SelectField, 
    SubmitField, TextAreaField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError, Optional
)
from app.models.user import User


class LoginForm(FlaskForm):
    """Login form for user authentication."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=50, message='Username must be between 3 and 50 characters')
        ],
        render_kw={'placeholder': 'Enter your username', 'autofocus': True}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, message='Password must be at least 6 characters')
        ],
        render_kw={'placeholder': 'Enter your password'}
    )
    
    remember_me = BooleanField('Remember Me')
    
    submit = SubmitField('Login')
    
    def validate_username(self, field):
        """Validate that username exists."""
        user = User.query.filter_by(username=field.data).first()
        if not user:
            raise ValidationError('Invalid username or password')
        if not user.is_active:
            raise ValidationError('This account has been deactivated')
    
    def validate_password(self, field):
        """Validate password against stored hash."""
        user = User.query.filter_by(username=self.username.data).first()
        if user and not user.check_password(field.data):
            raise ValidationError('Invalid username or password')


class RegistrationForm(FlaskForm):
    """Registration form for new users."""
    
    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required'),
            Length(min=3, max=50, message='Username must be between 3 and 50 characters')
        ],
        render_kw={'placeholder': 'Choose a username'}
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=100, message='Email must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter your email address'}
    )
    
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required'),
            Length(min=6, max=128, message='Password must be between 6 and 128 characters')
        ],
        render_kw={'placeholder': 'Create a password'}
    )
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(message='Please confirm your password'),
            EqualTo('password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm your password'}
    )
    
    role = SelectField(
        'Role',
        choices=[
            ('student', 'Student'),
            ('teacher', 'Teacher'),
            ('admin', 'Admin')
        ],
        validators=[DataRequired(message='Please select a role')],
        default='student'
    )
    
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Validate that username is unique."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists')
    
    def validate_email(self, field):
        """Validate that email is unique."""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email address already registered')


class ChangePasswordForm(FlaskForm):
    """Form for changing user password."""
    
    current_password = PasswordField(
        'Current Password',
        validators=[
            DataRequired(message='Current password is required')
        ],
        render_kw={'placeholder': 'Enter your current password'}
    )
    
    new_password = PasswordField(
        'New Password',
        validators=[
            DataRequired(message='New password is required'),
            Length(min=6, max=128, message='Password must be between 6 and 128 characters')
        ],
        render_kw={'placeholder': 'Enter new password'}
    )
    
    confirm_password = PasswordField(
        'Confirm New Password',
        validators=[
            DataRequired(message='Please confirm your new password'),
            EqualTo('new_password', message='Passwords must match')
        ],
        render_kw={'placeholder': 'Confirm new password'}
    )
    
    submit = SubmitField('Change Password')
    
    def __init__(self, user, *args, **kwargs):
        """Initialize form with user for validation."""
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_current_password(self, field):
        """Validate current password."""
        if not self.user.check_password(field.data):
            raise ValidationError('Current password is incorrect')
    
    def validate_new_password(self, field):
        """Validate new password is different from current."""
        if self.user.check_password(field.data):
            raise ValidationError('New password must be different from current password')


class ProfileForm(FlaskForm):
    """Form for updating user profile."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='Email is required'),
            Email(message='Please enter a valid email address'),
            Length(max=100, message='Email must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter your email address'}
    )
    
    phone = StringField(
        'Phone Number',
        validators=[
            Optional(),
            Length(max=20, message='Phone number must not exceed 20 characters')
        ],
        render_kw={'placeholder': 'Enter your phone number'}
    )
    
    address = TextAreaField(
        'Address',
        validators=[
            Optional(),
            Length(max=500, message='Address must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter your address', 'rows': 3}
    )
    
    submit = SubmitField('Update Profile')
    
    def __init__(self, user, *args, **kwargs):
        """Initialize form with user for validation."""
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def validate_email(self, field):
        """Validate that email is unique (excluding current user)."""
        if field.data != self.user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError('Email address already registered')
