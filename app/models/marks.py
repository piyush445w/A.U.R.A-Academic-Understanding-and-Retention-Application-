"""
Marks Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class Marks(db.Model):
    """Marks model for storing academic marks/grades."""
    
    __tablename__ = 'marks'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    graded_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT', onupdate='CASCADE'),
                         nullable=False, index=True)
    
    # Marks details
    exam_type = db.Column(db.Enum('Midterm', 'Final', 'Assignment', 'Quiz', 'Project', name='exam_types'),
                         nullable=False, index=True)
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=False)
    max_marks = db.Column(db.Numeric(5, 2), nullable=False)
    exam_date = db.Column(db.Date, nullable=False, index=True)
    remarks = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Check constraint to ensure marks are valid
    __table_args__ = (
        db.CheckConstraint('marks_obtained >= 0 AND marks_obtained <= max_marks', name='chk_marks_valid'),
    )
    
    def __init__(self, student_id, subject_id, exam_type, marks_obtained, max_marks, 
                 exam_date, graded_by, remarks=None):
        """Initialize marks record."""
        self.student_id = student_id
        self.subject_id = subject_id
        self.exam_type = exam_type
        self.marks_obtained = marks_obtained
        self.max_marks = max_marks
        self.exam_date = exam_date
        self.graded_by = graded_by
        self.remarks = remarks
    
    @property
    def percentage(self):
        """Calculate marks percentage."""
        if self.max_marks == 0:
            return 0.0
        return round((float(self.marks_obtained) / float(self.max_marks)) * 100, 2)
    
    @property
    def grade(self):
        """Calculate grade based on percentage."""
        pct = self.percentage
        if pct >= 90:
            return 'A+'
        elif pct >= 80:
            return 'A'
        elif pct >= 70:
            return 'B+'
        elif pct >= 60:
            return 'B'
        elif pct >= 50:
            return 'C'
        elif pct >= 40:
            return 'D'
        else:
            return 'F'
    
    @property
    def is_passing(self):
        """Check if marks are passing (>= 40%)."""
        return self.percentage >= 40
    
    @staticmethod
    def get_marks_by_student(student_id, subject_id=None, exam_type=None):
        """
        Get marks for a student.
        
        Args:
            student_id: Student ID
            subject_id: Filter by subject (optional)
            exam_type: Filter by exam type (optional)
            
        Returns:
            List of marks records
        """
        query = Marks.query.filter_by(student_id=student_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        
        return query.order_by(Marks.exam_date.desc()).all()
    
    @staticmethod
    def get_marks_by_subject(subject_id, exam_type=None):
        """
        Get marks for a subject.
        
        Args:
            subject_id: Subject ID
            exam_type: Filter by exam type (optional)
            
        Returns:
            List of marks records
        """
        query = Marks.query.filter_by(subject_id=subject_id)
        
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        
        return query.order_by(Marks.exam_date.desc()).all()
    
    @staticmethod
    def get_average_by_student(student_id, subject_id=None):
        """
        Get average marks for a student.
        
        Args:
            student_id: Student ID
            subject_id: Filter by subject (optional)
            
        Returns:
            Average percentage
        """
        query = Marks.query.filter_by(student_id=student_id)
        
        if subject_id:
            query = query.filter_by(subject_id=subject_id)
        
        marks_records = query.all()
        if not marks_records:
            return 0.0
        
        total_percentage = sum(record.percentage for record in marks_records)
        return round(total_percentage / len(marks_records), 2)
    
    def to_dict(self):
        """Convert marks to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'subject_id': self.subject_id,
            'graded_by': self.graded_by,
            'exam_type': self.exam_type,
            'marks_obtained': float(self.marks_obtained),
            'max_marks': float(self.max_marks),
            'percentage': self.percentage,
            'grade': self.grade,
            'is_passing': self.is_passing,
            'exam_date': self.exam_date.isoformat() if self.exam_date else None,
            'remarks': self.remarks,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of Marks."""
        return f'<Marks {self.student_id} - {self.subject_id}: {self.marks_obtained}/{self.max_marks}>'
