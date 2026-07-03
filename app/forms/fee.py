"""
Fee Management Forms
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, DateField, SelectField, DecimalField, 
    TextAreaField, SubmitField
)
from wtforms.validators import (
    DataRequired, Length, Optional, NumberRange, ValidationError
)
from datetime import date
from app.models.fee import Fee
from app.models.student import Student


class FeeForm(FlaskForm):
    """Form for adding/editing fee records."""
    
    student_id = SelectField(
        'Student',
        coerce=int,
        validators=[DataRequired(message='Please select a student')],
        render_kw={'placeholder': 'Select student'}
    )
    
    fee_type = SelectField(
        'Fee Type',
        choices=[
            ('Tuition', 'Tuition'),
            ('Library', 'Library'),
            ('Laboratory', 'Laboratory'),
            ('Hostel', 'Hostel'),
            ('Other', 'Other')
        ],
        validators=[DataRequired(message='Please select fee type')]
    )
    
    amount = DecimalField(
        'Amount',
        validators=[
            DataRequired(message='Amount is required'),
            NumberRange(min=0.01, message='Amount must be greater than 0')
        ],
        places=2,
        render_kw={'placeholder': 'Enter amount'}
    )
    
    due_date = DateField(
        'Due Date',
        validators=[DataRequired(message='Due date is required')],
        format='%Y-%m-%d',
        render_kw={'placeholder': 'YYYY-MM-DD'}
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Overdue', 'Overdue'),
            ('Partial', 'Partial')
        ],
        validators=[DataRequired(message='Please select status')],
        default='Pending'
    )
    
    payment_method = StringField(
        'Payment Method',
        validators=[
            Optional(),
            Length(max=50, message='Payment method must not exceed 50 characters')
        ],
        render_kw={'placeholder': 'Enter payment method'}
    )
    
    transaction_id = StringField(
        'Transaction ID',
        validators=[
            Optional(),
            Length(max=100, message='Transaction ID must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter transaction ID'}
    )
    
    receipt_number = StringField(
        'Receipt Number',
        validators=[
            Optional(),
            Length(max=50, message='Receipt number must not exceed 50 characters')
        ],
        render_kw={'placeholder': 'Enter receipt number'}
    )
    
    submit = SubmitField('Save Fee')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with student choices."""
        super(FeeForm, self).__init__(*args, **kwargs)
        self.student_id.choices = [
            (s.id, f"{s.student_id} - {s.full_name}") 
            for s in Student.query.order_by(Student.first_name).all()
        ]


class PaymentForm(FlaskForm):
    """Form for recording fee payments."""
    
    fee_id = SelectField(
        'Fee Record',
        coerce=int,
        validators=[DataRequired(message='Please select a fee record')],
        render_kw={'placeholder': 'Select fee record'}
    )
    
    payment_method = SelectField(
        'Payment Method',
        choices=[
            ('Cash', 'Cash'),
            ('Card', 'Card'),
            ('Bank Transfer', 'Bank Transfer'),
            ('Online Payment', 'Online Payment'),
            ('Cheque', 'Cheque'),
            ('Other', 'Other')
        ],
        validators=[DataRequired(message='Please select payment method')]
    )
    
    transaction_id = StringField(
        'Transaction ID',
        validators=[
            Optional(),
            Length(max=100, message='Transaction ID must not exceed 100 characters')
        ],
        render_kw={'placeholder': 'Enter transaction ID'}
    )
    
    paid_amount = DecimalField(
        'Amount Paid',
        validators=[
            DataRequired(message='Amount paid is required'),
            NumberRange(min=0.01, message='Amount must be greater than 0')
        ],
        places=2,
        render_kw={'placeholder': 'Enter amount paid'}
    )
    
    remarks = TextAreaField(
        'Remarks',
        validators=[
            Optional(),
            Length(max=500, message='Remarks must not exceed 500 characters')
        ],
        render_kw={'placeholder': 'Enter any remarks', 'rows': 3}
    )
    
    submit = SubmitField('Record Payment')
    
    def __init__(self, *args, **kwargs):
        """Initialize form with pending fee choices."""
        super(PaymentForm, self).__init__(*args, **kwargs)
        # Only show pending or overdue fees
        self.fee_id.choices = [
            (f.id, f"{f.student.full_name} - {f.fee_type} - ${f.amount} (Due: {f.due_date})") 
            for f in Fee.query.filter(Fee.status.in_(['Pending', 'Overdue'])).order_by(Fee.due_date).all()
        ]
