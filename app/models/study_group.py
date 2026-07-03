"""
Study Group Models
A.U.R.A - Academic Understanding and Retention Application
Manages student groups, group roles, and class representatives
"""

from datetime import datetime
from app import db


class StudyGroup(db.Model):
    """Study group model for managing student groups."""
    
    __tablename__ = 'study_groups'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Group identification
    group_name = db.Column(db.String(100), nullable=False)
    group_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Academic context
    course = db.Column(db.String(100), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=False, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), index=True)
    
    # Class Representative (Anchor)
    class_rep_id = db.Column(db.Integer, db.ForeignKey('students.id'), index=True)
    is_class_rep_active = db.Column(db.Boolean, default=True)
    
    # Session Link
    session_id = db.Column(db.Integer, db.ForeignKey('session_groups.id'), index=True)
    
    # Group settings
    max_members = db.Column(db.Integer, default=5)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    members = db.relationship('GroupMember', backref='group', lazy='dynamic', cascade='all, delete-orphan')
    class_rep = db.relationship('Student', foreign_keys=[class_rep_id], backref='class_rep_of')
    
    def __init__(self, group_name, group_code, course, semester, description=None, 
                 subject_id=None, max_members=5):
        """Initialize study group."""
        self.group_name = group_name
        self.group_code = group_code
        self.course = course
        self.semester = semester
        self.description = description
        self.subject_id = subject_id
        self.max_members = max_members
    
    @property
    def member_count(self):
        """Return number of active members."""
        return self.members.filter_by(is_active=True).count()
    
    @property
    def leader(self):
        """Return the group leader."""
        return self.members.filter_by(role='leader', is_active=True).first()
    
    @property
    def is_full(self):
        """Check if group is at max capacity."""
        return self.member_count >= self.max_members
    
    def to_dict(self):
        """Convert group to dictionary."""
        return {
            'id': self.id,
            'group_name': self.group_name,
            'group_code': self.group_code,
            'description': self.description,
            'course': self.course,
            'semester': self.semester,
            'subject_id': self.subject_id,
            'class_rep_id': self.class_rep_id,
            'class_rep_name': self.class_rep.full_name if self.class_rep else None,
            'max_members': self.max_members,
            'member_count': self.member_count,
            'is_full': self.is_full,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<StudyGroup {self.group_name}: {self.group_code}>'


class GroupMember(db.Model):
    """Group member model for managing student roles in groups."""
    
    __tablename__ = 'group_members'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), 
                          nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('study_groups.id', ondelete='CASCADE'), 
                        nullable=False, index=True)
    
    # Role in group
    role = db.Column(db.Enum('leader', 'participant', 'observer', name='group_roles'),
                    nullable=False, default='participant')
    
    # Member status
    is_active = db.Column(db.Boolean, default=True, index=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Additional info
    notes = db.Column(db.Text)
    
    # Relationships
    student = db.relationship('Student', backref='group_memberships')
    
    def __init__(self, student_id, group_id, role='participant'):
        """Initialize group member."""
        self.student_id = student_id
        self.group_id = group_id
        self.role = role
    
    @property
    def is_leader(self):
        """Check if member is leader."""
        return self.role == 'leader'
    
    @property
    def is_participant(self):
        """Check if member is participant."""
        return self.role == 'participant'
    
    @property
    def is_observer(self):
        """Check if member is observer."""
        return self.role == 'observer'
    
    def to_dict(self):
        """Convert member to dictionary."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student.full_name if self.student else None,
            'student_id_number': self.student.student_id if self.student else None,
            'group_id': self.group_id,
            'role': self.role,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<GroupMember {self.student_id} in Group {self.group_id}: {self.role}>'


class SessionGroup(db.Model):
    """Session group model for managing class session groups."""
    
    __tablename__ = 'session_groups'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Session identification
    session_name = db.Column(db.String(100), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), index=True)
    course = db.Column(db.String(100), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    
    # Group settings
    group_count = db.Column(db.Integer, default=5)
    students_per_group = db.Column(db.Integer, default=4)
    
    # Session Anchor (similar to class rep but for sessions)
    session_anchor_id = db.Column(db.Integer, db.ForeignKey('students.id'), index=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    groups = db.relationship('StudyGroup', backref='session', lazy='dynamic')
    session_anchor = db.relationship('Student', foreign_keys=[session_anchor_id], backref='anchored_sessions')
    
    def __init__(self, session_name, session_date, course, semester, 
                 group_count=5, students_per_group=4, subject_id=None):
        """Initialize session group."""
        self.session_name = session_name
        self.session_date = session_date
        self.course = course
        self.semester = semester
        self.group_count = group_count
        self.students_per_group = students_per_group
        self.subject_id = subject_id
    
    @property
    def total_students(self):
        """Get total number of students in session."""
        return sum(g.member_count for g in self.groups)
    
    @property
    def completion_percentage(self):
        """Get session completion percentage."""
        if self.is_completed:
            return 100
        active_groups = self.groups.filter_by(is_active=True).count()
        if self.group_count == 0:
            return 0
        return int((active_groups / self.group_count) * 100)
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'session_name': self.session_name,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'subject_id': self.subject_id,
            'course': self.course,
            'semester': self.semester,
            'group_count': self.group_count,
            'students_per_group': self.students_per_group,
            'total_students': self.total_students,
            'session_anchor_id': self.session_anchor_id,
            'session_anchor_name': self.session_anchor.full_name if self.session_anchor else None,
            'is_active': self.is_active,
            'is_completed': self.is_completed,
            'completion_percentage': self.completion_percentage,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<SessionGroup {self.session_name} on {self.session_date}>'