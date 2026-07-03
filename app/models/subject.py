"""
Subject Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class Subject(db.Model):
    """Subject model for storing course/subject information."""
    
    __tablename__ = 'subjects'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Subject details
    subject_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    subject_name = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, index=True)
    credits = db.Column(db.Integer, nullable=False, default=3)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    marks_records = db.relationship('Marks', backref='subject', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, subject_code, subject_name, course, semester, credits=3):
        """Initialize subject."""
        self.subject_code = subject_code
        self.subject_name = subject_name
        self.course = course
        self.semester = semester
        self.credits = credits
    
    @staticmethod
    def get_subjects_by_course(course):
        """
        Get all subjects for a specific course.
        
        Args:
            course: Course name
            
        Returns:
            List of subjects
        """
        return Subject.query.filter_by(course=course).order_by(Subject.semester, Subject.subject_code).all()
    
    @staticmethod
    def get_subjects_by_semester(course, semester):
        """
        Get all subjects for a specific course and semester.
        
        Args:
            course: Course name
            semester: Semester number
            
        Returns:
            List of subjects
        """
        return Subject.query.filter_by(course=course, semester=semester).order_by(Subject.subject_code).all()
    
    def get_average_marks(self, student_id=None):
        """
        Get average marks for this subject.
        
        Args:
            student_id: Filter by specific student (optional)
            
        Returns:
            Average marks percentage
        """
        from app.models.marks import Marks
        
        query = Marks.query.filter_by(subject_id=self.id)
        if student_id:
            query = query.filter_by(student_id=student_id)
        
        marks_records = query.all()
        if not marks_records:
            return 0.0
        
        total_percentage = sum(
            (record.marks_obtained / record.max_marks) * 100 
            for record in marks_records
        )
        return round(total_percentage / len(marks_records), 2)
    
    def to_dict(self):
        """Convert subject to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'course': self.course,
            'semester': self.semester,
            'credits': self.credits,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of Subject."""
        return f'<Subject {self.subject_code}: {self.subject_name}>'
