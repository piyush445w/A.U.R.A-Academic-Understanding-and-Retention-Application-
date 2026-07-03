"""
Complaint Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class Complaint(db.Model):
    """Complaint model for storing student complaints and their resolution status."""
    
    __tablename__ = 'complaints'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'),
                           index=True)
    
    # Complaint details
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum('Academic', 'Administrative', 'Infrastructure', 'Other', name='complaint_categories'),
                        nullable=False, index=True)
    priority = db.Column(db.Enum('Low', 'Medium', 'High', 'Urgent', name='complaint_priorities'),
                        nullable=False, default='Medium', index=True)
    status = db.Column(db.Enum('Open', 'In Progress', 'Resolved', 'Closed', name='complaint_status'),
                      nullable=False, default='Open', index=True)
    resolution = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, student_id, subject, description, category, priority='Medium',
                 status='Open', assigned_to=None, resolution=None):
        """Initialize complaint."""
        self.student_id = student_id
        self.subject = subject
        self.description = description
        self.category = category
        self.priority = priority
        self.status = status
        self.assigned_to = assigned_to
        self.resolution = resolution
    
    @property
    def is_open(self):
        """Check if complaint is open."""
        return self.status == 'Open'
    
    @property
    def is_in_progress(self):
        """Check if complaint is in progress."""
        return self.status == 'In Progress'
    
    @property
    def is_resolved(self):
        """Check if complaint is resolved."""
        return self.status in ['Resolved', 'Closed']
    
    @property
    def is_urgent(self):
        """Check if complaint is urgent."""
        return self.priority == 'Urgent'
    
    def assign(self, user_id):
        """Assign complaint to a user."""
        self.assigned_to = user_id
        self.status = 'In Progress'
    
    def resolve(self, resolution):
        """Resolve complaint with resolution."""
        self.resolution = resolution
        self.status = 'Resolved'
    
    def close(self):
        """Close complaint."""
        if self.status == 'Resolved':
            self.status = 'Closed'
    
    @staticmethod
    def get_complaints_by_student(student_id, status=None):
        """
        Get complaints for a student.
        
        Args:
            student_id: Student ID
            status: Filter by status (optional)
            
        Returns:
            List of complaints
        """
        query = Complaint.query.filter_by(student_id=student_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.created_at.desc()).all()
    
    @staticmethod
    def get_complaints_by_category(category, status=None):
        """
        Get complaints by category.
        
        Args:
            category: Complaint category
            status: Filter by status (optional)
            
        Returns:
            List of complaints
        """
        query = Complaint.query.filter_by(category=category)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.created_at.desc()).all()
    
    @staticmethod
    def get_complaints_by_priority(priority, status=None):
        """
        Get complaints by priority.
        
        Args:
            priority: Complaint priority
            status: Filter by status (optional)
            
        Returns:
            List of complaints
        """
        query = Complaint.query.filter_by(priority=priority)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(Complaint.created_at.desc()).all()
    
    @staticmethod
    def get_open_complaints():
        """
        Get all open complaints.
        
        Returns:
            List of open complaints
        """
        return Complaint.query.filter_by(status='Open').order_by(
            Complaint.priority.desc(),
            Complaint.created_at.desc()
        ).all()
    
    @staticmethod
    def get_complaints_assigned_to(user_id):
        """
        Get complaints assigned to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of complaints
        """
        return Complaint.query.filter_by(assigned_to=user_id).order_by(
            Complaint.status,
            Complaint.priority.desc()
        ).all()
    
    def to_dict(self):
        """Convert complaint to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'assigned_to': self.assigned_to,
            'subject': self.subject,
            'description': self.description,
            'category': self.category,
            'priority': self.priority,
            'status': self.status,
            'resolution': self.resolution,
            'is_open': self.is_open,
            'is_in_progress': self.is_in_progress,
            'is_resolved': self.is_resolved,
            'is_urgent': self.is_urgent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of Complaint."""
        return f'<Complaint {self.id}: {self.subject} ({self.status})>'
