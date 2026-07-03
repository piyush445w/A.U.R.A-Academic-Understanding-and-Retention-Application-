"""
Machine Learning Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import (
    StringField, SelectField, DecimalField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)


class DatasetUploadForm(FlaskForm):
    """Form for uploading training datasets."""
    
    file = FileField(
        'Dataset File',
        validators=[
            FileRequired(message='Please select a file to upload'),
            FileAllowed(['csv', 'xlsx', 'xls'], message='Only CSV and Excel files are allowed')
        ],
        render_kw={'accept': '.csv,.xlsx,.xls'}
    )
    
    merge_option = SelectField(
        'Merge Option',
        choices=[
            ('replace', 'Replace existing data'),
            ('append', 'Append to existing data'),
            ('update', 'Update existing records')
        ],
        validators=[DataRequired(message='Please select merge option')],
        default='replace'
    )
    
    description = StringField(
        'Description',
        validators=[
            Optional(),
            Length(max=500, message='Description must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter dataset description'}
    )
    
    submit = SubmitField('Upload Dataset')
    
    def validate_file(self, field):
        """Validate file size (max 10MB)."""
        if field.data:
            # Check file size (10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB in bytes
            field.data.seek(0, 2)  # Seek to end
            file_size = field.data.tell()
            field.data.seek(0)  # Reset to beginning
            
            if file_size > max_size:
                raise ValidationError('File size must not exceed 10MB')


class ModelTrainForm(FlaskForm):
    """Form for training ML models."""
    
    algorithm = SelectField(
        'Algorithm',
        choices=[
            ('random_forest', 'Random Forest'),
            ('gradient_boosting', 'Gradient Boosting'),
            ('logistic_regression', 'Logistic Regression'),
            ('svm', 'Support Vector Machine'),
            ('neural_network', 'Neural Network')
        ],
        validators=[DataRequired(message='Please select an algorithm')],
        default='random_forest'
    )
    
    test_size = DecimalField(
        'Test Size (%)',
        validators=[
            DataRequired(message='Test size is required'),
            NumberRange(min=10, max=50, message='Test size must be between 10% and 50%')
        ],
        places=0,
        default=20,
        render_kw={'placeholder': 'Enter test size percentage'}
    )
    
    model_name = StringField(
        'Model Name',
        validators=[
            DataRequired(message='Model name is required'),
            Length(min=3, max=100, message='Model name must be between 3 and 100 characters')
        ],
        render_kw={'placeholder': 'Enter model name'}
    )
    
    model_version = StringField(
        'Model Version',
        validators=[
            DataRequired(message='Model version is required'),
            Length(min=1, max=20, message='Model version must not exceed 20 characters')
        ],
        render_kw={'placeholder': 'e.g., 1.0, 2.1'}
    )
    
    submit = SubmitField('Train Model')
