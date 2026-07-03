"""
Fee Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime, date
from app import db


class Fee(db.Model):
    """Fee model for storing fee payment information."""
    
    __tablename__ = 'fees'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    
    # Fee details
    fee_type = db.Column(db.Enum('Tuition', 'Library', 'Laboratory', 'Hostel', 'Other', name='fee_types'),
                        nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    due_date = db.Column(db.Date, nullable=False, index=True)
    paid_date = db.Column(db.Date, index=True)
    status = db.Column(db.Enum('Pending', 'Paid', 'Overdue', 'Partial', name='fee_status'),
                      nullable=False, default='Pending', index=True)
    
    # Payment details
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    receipt_number = db.Column(db.String(50))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Check constraint to ensure amount is positive
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='chk_fees_amount'),
    )
    
    def __init__(self, student_id, fee_type, amount, due_date, status='Pending',
                 paid_date=None, payment_method=None, transaction_id=None, receipt_number=None):
        """Initialize fee record."""
        self.student_id = student_id
        self.fee_type = fee_type
        self.amount = amount
        self.due_date = due_date
        self.status = status
        self.paid_date = paid_date
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.receipt_number = receipt_number
    
    @property
    def is_overdue(self):
        """Check if fee is overdue."""
        if self.status == 'Paid':
            return False
        return date.today() > self.due_date
    
    @property
    def days_overdue(self):
        """Calculate days overdue."""
        if not self.is_overdue:
            return 0
        return (date.today() - self.due_date).days
    
    def mark_as_paid(self, payment_method, transaction_id=None, receipt_number=None):
        """Mark fee as paid."""
        self.status = 'Paid'
        self.paid_date = date.today()
        self.payment_method = payment_method
        self.transaction_id = transaction_id
        self.receipt_number = receipt_number
    
    def mark_as_overdue(self):
        """Mark fee as overdue."""
        if self.status == 'Pending' and self.is_overdue:
            self.status = 'Overdue'
    
    @staticmethod
    def get_pending_fees(student_id):
        """
        Get all pending fees for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of pending fees
        """
        return Fee.query.filter(
            Fee.student_id == student_id,
            Fee.status.in_(['Pending', 'Overdue'])
        ).order_by(Fee.due_date).all()
    
    @staticmethod
    def get_total_pending_amount(student_id):
        """
        Get total pending amount for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Total pending amount
        """
        from sqlalchemy import func
        
        result = db.session.query(func.sum(Fee.amount)).filter(
            Fee.student_id == student_id,
            Fee.status.in_(['Pending', 'Overdue'])
        ).scalar()
        
        return float(result) if result else 0.0
    
    @staticmethod
    def get_overdue_fees(student_id):
        """
        Get all overdue fees for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of overdue fees
        """
        return Fee.query.filter(
            Fee.student_id == student_id,
            Fee.status == 'Overdue'
        ).order_by(Fee.due_date).all()
    
    @staticmethod
    def get_fees_by_type(student_id, fee_type):
        """
        Get fees by type for a student.
        
        Args:
            student_id: Student ID
            fee_type: Fee type
            
        Returns:
            List of fees
        """
        return Fee.query.filter_by(
            student_id=student_id,
            fee_type=fee_type
        ).order_by(Fee.due_date.desc()).all()
    
    def to_dict(self):
        """Convert fee to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'fee_type': self.fee_type,
            'amount': float(self.amount),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'paid_date': self.paid_date.isoformat() if self.paid_date else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'receipt_number': self.receipt_number,
            'is_overdue': self.is_overdue,
            'days_overdue': self.days_overdue,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of Fee."""
        return f'<Fee {self.student_id} - {self.fee_type}: {self.amount} ({self.status})>'
