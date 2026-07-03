"""
Custom Validators for Intelligent Student Risk Monitoring & Decision Support System
"""

import re
from wtforms import ValidationError
from app.models.student import Student
from app.models.user import User


def validate_student_id(form, field):
    """
    Validate student ID format.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If student ID format is invalid
    """
    if not field.data:
        return
    
    # Student ID should be alphanumeric and 3-20 characters
    pattern = r'^[A-Za-z0-9]{3,20}$'
    if not re.match(pattern, field.data):
        raise ValidationError('Student ID must be alphanumeric and between 3-20 characters')


def validate_phone(form, field):
    """
    Validate phone number format.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If phone number format is invalid
    """
    if not field.data:
        return
    
    # Remove common separators for validation
    cleaned = re.sub(r'[\s\-\(\)\+]', '', field.data)
    
    # Check if it's a valid phone number (7-15 digits)
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 15:
        raise ValidationError('Please enter a valid phone number')


def validate_email_unique(form, field):
    """
    Validate that email is unique in the system.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If email already exists
    """
    if not field.data:
        return
    
    # Check if user exists with this email
    user = User.query.filter_by(email=field.data).first()
    
    # If editing, exclude current user from check
    if hasattr(form, 'user') and form.user:
        if user and user.id != form.user.id:
            raise ValidationError('Email address already registered')
    else:
        if user:
            raise ValidationError('Email address already registered')


def validate_file_extension(allowed_extensions):
    """
    Create a validator for file extensions.
    
    Args:
        allowed_extensions: List of allowed file extensions (e.g., ['csv', 'xlsx'])
        
    Returns:
        Validator function
    """
    def validator(form, field):
        """
        Validate file extension.
        
        Args:
            form: Form object
            field: Field to validate
            
        Raises:
            ValidationError: If file extension is not allowed
        """
        if not field.data:
            return
        
        filename = field.data.filename.lower()
        if not any(filename.endswith(f'.{ext}') for ext in allowed_extensions):
            raise ValidationError(f'Only {", ".join(allowed_extensions)} files are allowed')
    
    return validator


def validate_file_size(max_size_mb=10):
    """
    Create a validator for file size.
    
    Args:
        max_size_mb: Maximum file size in megabytes (default: 10)
        
    Returns:
        Validator function
    """
    def validator(form, field):
        """
        Validate file size.
        
        Args:
            form: Form object
            field: Field to validate
            
        Raises:
            ValidationError: If file size exceeds limit
        """
        if not field.data:
            return
        
        # Get file size
        field.data.seek(0, 2)  # Seek to end
        file_size = field.data.tell()
        field.data.seek(0)  # Reset to beginning
        
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValidationError(f'File size must not exceed {max_size_mb}MB')
    
    return validator


def validate_marks_range(form, field):
    """
    Validate that marks are within valid range.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If marks are invalid
    """
    if field.data is None:
        return
    
    if field.data < 0:
        raise ValidationError('Marks cannot be negative')
    
    # Check if max_marks is provided and marks don't exceed it
    if hasattr(form, 'max_marks') and form.max_marks.data:
        if field.data > form.max_marks.data:
            raise ValidationError('Marks obtained cannot exceed maximum marks')


def validate_date_not_future(form, field):
    """
    Validate that date is not in the future.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If date is in the future
    """
    from datetime import date
    
    if not field.data:
        return
    
    if field.data > date.today():
        raise ValidationError('Date cannot be in the future')


def validate_date_after_start(form, field):
    """
    Validate that end date is after start date.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If end date is before start date
    """
    if not field.data:
        return
    
    if hasattr(form, 'start_date') and form.start_date.data:
        if field.data < form.start_date.data:
            raise ValidationError('End date must be after start date')


def validate_password_strength(form, field):
    """
    Validate password strength.
    
    Args:
        form: Form object
        field: Field to validate
        
    Raises:
        ValidationError: If password is too weak
    """
    if not field.data:
        return
    
    password = field.data
    
    # Check minimum length
    if len(password) < 6:
        raise ValidationError('Password must be at least 6 characters long')
    
    # Check for at least one letter
    if not re.search(r'[A-Za-z]', password):
        raise ValidationError('Password must contain at least one letter')
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValidationError('Password must contain at least one digit')


def validate_unique_constraint(model, field_name, exclude_id=None):
    """
    Create a validator for unique constraint.
    
    Args:
        model: SQLAlchemy model class
        field_name: Name of the field to check
        exclude_id: ID to exclude from check (for updates)
        
    Returns:
        Validator function
    """
    def validator(form, field):
        """
        Validate unique constraint.
        
        Args:
            form: Form object
            field: Field to validate
            
        Raises:
            ValidationError: If value already exists
        """
        if not field.data:
            return
        
        query = model.query.filter_by(**{field_name: field.data})
        
        if exclude_id:
            query = query.filter(model.id != exclude_id)
        
        if query.first():
            raise ValidationError(f'{field_name.replace("_", " ").title()} already exists')
    
    return validator
