"""
Attendance Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class Attendance(db.Model):
    """Attendance model for tracking daily student attendance."""
    
    __tablename__ = 'attendance'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT', onupdate='CASCADE'),
                         nullable=False, index=True)
    
    # Attendance details
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.Enum('Present', 'Absent', 'Late', 'Excused', name='attendance_status'),
                      nullable=False, index=True)
    remarks = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Unique constraint to prevent duplicate attendance entries
    __table_args__ = (
        db.UniqueConstraint('student_id', 'date', name='uk_attendance_student_date'),
    )
    
    def __init__(self, student_id, date, status, marked_by, remarks=None):
        """Initialize attendance record."""
        self.student_id = student_id
        self.date = date
        self.status = status
        self.marked_by = marked_by
        self.remarks = remarks
    
    @property
    def is_present(self):
        """Check if student was present."""
        return self.status in ['Present', 'Late']
    
    @property
    def is_absent(self):
        """Check if student was absent."""
        return self.status == 'Absent'
    
    @property
    def is_excused(self):
        """Check if absence was excused."""
        return self.status == 'Excused'
    
    @staticmethod
    def get_attendance_by_date_range(student_id, start_date, end_date):
        """
        Get attendance records for a student within a date range.
        
        Args:
            student_id: Student ID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of attendance records
        """
        return Attendance.query.filter(
            Attendance.student_id == student_id,
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).order_by(Attendance.date).all()
    
    @staticmethod
    def get_attendance_summary(student_id, start_date=None, end_date=None):
        """
        Get attendance summary for a student.
        
        Args:
            student_id: Student ID
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Dictionary with attendance statistics
        """
        query = Attendance.query.filter_by(student_id=student_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        total = query.count()
        present = query.filter(Attendance.status.in_(['Present', 'Late'])).count()
        absent = query.filter_by(status='Absent').count()
        late = query.filter_by(status='Late').count()
        excused = query.filter_by(status='Excused').count()
        
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            'total_days': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'percentage': round(percentage, 2)
        }
    
    def to_dict(self):
        """Convert attendance to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'marked_by': self.marked_by,
            'date': self.date.isoformat() if self.date else None,
            'status': self.status,
            'remarks': self.remarks,
            'is_present': self.is_present,
            'is_absent': self.is_absent,
            'is_excused': self.is_excused,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of Attendance."""
        return f'<Attendance {self.student_id} on {self.date}: {self.status}>'
