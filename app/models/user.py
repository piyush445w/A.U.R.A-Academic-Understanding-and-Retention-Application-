"""
User Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """User model for authentication and role management."""
    
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Authentication fields
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role and status
    role = db.Column(db.Enum('admin', 'teacher', 'student', name='user_roles'), 
                     nullable=False, default='student', index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    students = db.relationship('Student', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    marked_attendance = db.relationship('Attendance', backref='marked_by_user', lazy='dynamic', 
                                       foreign_keys='Attendance.marked_by')
    graded_marks = db.relationship('Marks', backref='graded_by_user', lazy='dynamic',
                                   foreign_keys='Marks.graded_by')
    issued_books = db.relationship('LibraryTransaction', backref='issued_by_user', lazy='dynamic',
                                   foreign_keys='LibraryTransaction.issued_by')
    returned_books = db.relationship('LibraryTransaction', backref='returned_to_user', lazy='dynamic',
                                     foreign_keys='LibraryTransaction.returned_to')
    assigned_complaints = db.relationship('Complaint', backref='assigned_to_user', lazy='dynamic',
                                          foreign_keys='Complaint.assigned_to')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, username, email, password, role='student', is_active=True):
        """Initialize user with hashed password."""
        self.username = username
        self.email = email
        self.set_password(password)
        self.role = role
        self.is_active = is_active
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        if not self.password_hash or not self.password_hash.strip():
            return False
        try:
            return check_password_hash(self.password_hash, password)
        except Exception:
            return False
    
    def get_id(self):
        """Return user ID as string for Flask-Login."""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Return True if user is authenticated."""
        return True
    
    @property
    def is_anonymous(self):
        """Return False as this is not an anonymous user."""
        return False
    
    def has_role(self, role):
        """Check if user has specific role."""
        return self.role == role
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def is_teacher(self):
        """Check if user is teacher."""
        return self.role == 'teacher'
    
    def is_student(self):
        """Check if user is student."""
        return self.role == 'student'
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """String representation of User."""
        return f'<User {self.username} ({self.role})>'
