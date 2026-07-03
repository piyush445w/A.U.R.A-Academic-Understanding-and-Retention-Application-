"""
Student Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime, date
from app import db


class Student(db.Model):
    """Student model for storing student personal and academic information."""
    
    __tablename__ = 'students'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to users
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
                        nullable=False, index=True)
    
    # Student identification
    student_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Personal information
    first_name = db.Column(db.String(50), nullable=False, index=True)
    last_name = db.Column(db.String(50), nullable=False, index=True)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender_types'), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Academic information
    course = db.Column(db.String(100), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, index=True)
    admission_date = db.Column(db.Date, nullable=False, index=True)
    
    # Guardian information
    guardian_name = db.Column(db.String(100))
    guardian_phone = db.Column(db.String(20))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    marks_records = db.relationship('Marks', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    fee_records = db.relationship('Fee', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    library_transactions = db.relationship('LibraryTransaction', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    complaints = db.relationship('Complaint', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, user_id, student_id, first_name, last_name, date_of_birth, gender,
                 course, semester, admission_date, phone=None, address=None,
                 guardian_name=None, guardian_phone=None):
        """Initialize student."""
        self.user_id = user_id
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.course = course
        self.semester = semester
        self.admission_date = admission_date
        self.phone = phone
        self.address = address
        self.guardian_name = guardian_name
        self.guardian_phone = guardian_phone
    
    @property
    def full_name(self):
        """Return full name of student."""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def attendance_percentage(self):
        """Return attendance percentage."""
        return self.calculate_attendance_percentage()
    
    @property
    def risk_level(self):
        """Return risk level based on predictions."""
        from app.models.prediction import Prediction
        latest = Prediction.query.filter_by(student_id=self.id).order_by(Prediction.prediction_date.desc()).first()
        return latest.risk_level if latest else 'Low'
    
    @property
    def is_active(self):
        """Return if student user account is active."""
        return self.user.is_active if self.user else False
    
    @property
    def age(self):
        """Calculate age from date of birth."""
        today = date.today()
        return today.year - self.date_of_birth.year - \
               ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    def calculate_attendance_percentage(self, start_date=None, end_date=None):
        """
        Calculate attendance percentage for a date range.
        
        Args:
            start_date: Start date for calculation (optional)
            end_date: End date for calculation (optional)
            
        Returns:
            Attendance percentage (0-100)
        """
        from app.models.attendance import Attendance
        
        query = Attendance.query.filter_by(student_id=self.id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        total_records = query.count()
        if total_records == 0:
            return 0.0
        
        present_records = query.filter(Attendance.status.in_(['Present', 'Late'])).count()
        return round((present_records / total_records) * 100, 2)
    
    def calculate_average_marks(self, subject_id=None, exam_type=None):
        """
        Calculate average marks for the student.
        
        Args:
            subject_id: Filter by specific subject (optional)
            exam_type: Filter by exam type (optional)
            
        Returns:
            Average marks percentage (0-100)
        """
        from app.models.marks import Marks
        
        query = Marks.query.filter_by(student_id=self.id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        
        marks_records = query.all()
        if not marks_records:
            return 0.0
        
        total_percentage = sum(
            (record.marks_obtained / record.max_marks) * 100 
            for record in marks_records
        )
        return round(total_percentage / len(marks_records), 2)
    
    def calculate_risk_score(self):
        """
        Calculate overall risk score based on multiple factors.
        
        Returns:
            Risk score (0-1, where 1 is highest risk)
        """
        # Attendance weight: 40%
        attendance_pct = self.calculate_attendance_percentage()
        attendance_risk = max(0, (75 - attendance_pct) / 75) if attendance_pct < 75 else 0
        
        # Academic performance weight: 40%
        avg_marks = self.calculate_average_marks()
        academic_risk = max(0, (50 - avg_marks) / 50) if avg_marks < 50 else 0
        
        # Fee status weight: 20%
        from app.models.fee import Fee
        overdue_fees = Fee.query.filter_by(
            student_id=self.id, 
            status='Overdue'
        ).count()
        fee_risk = min(1.0, overdue_fees * 0.3)
        
        # Calculate weighted risk score
        risk_score = (attendance_risk * 0.4) + (academic_risk * 0.4) + (fee_risk * 0.2)
        return round(min(1.0, risk_score), 4)
    
    def get_risk_level(self):
        """
        Get risk level based on risk score.
        
        Returns:
            Risk level string: 'Low', 'Medium', or 'High'
        """
        risk_score = self.calculate_risk_score()
        if risk_score >= 0.7:
            return 'High'
        elif risk_score >= 0.4:
            return 'Medium'
        else:
            return 'Low'
    
    def get_pending_fees(self):
        """Get total pending fees amount."""
        from app.models.fee import Fee
        from sqlalchemy import func
        
        result = db.session.query(func.sum(Fee.amount)).filter(
            Fee.student_id == self.id,
            Fee.status.in_(['Pending', 'Overdue'])
        ).scalar()
        
        return float(result) if result else 0.0
    
    def get_overdue_books(self):
        """Get count of overdue library books."""
        from app.models.library import LibraryTransaction
        from datetime import date
        
        return LibraryTransaction.query.filter(
            LibraryTransaction.student_id == self.id,
            LibraryTransaction.status == 'Issued',
            LibraryTransaction.due_date < date.today()
        ).count()
    
    def to_dict(self):
        """Convert student to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'age': self.age,
            'gender': self.gender,
            'phone': self.phone,
            'address': self.address,
            'course': self.course,
            'semester': self.semester,
            'admission_date': self.admission_date.isoformat() if self.admission_date else None,
            'guardian_name': self.guardian_name,
            'guardian_phone': self.guardian_phone,
            'attendance_percentage': self.calculate_attendance_percentage(),
            'average_marks': self.calculate_average_marks(),
            'risk_score': self.calculate_risk_score(),
            'risk_level': self.get_risk_level(),
            'pending_fees': self.get_pending_fees(),
            'overdue_books': self.get_overdue_books(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of Student."""
        return f'<Student {self.student_id}: {self.full_name}>'
