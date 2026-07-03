"""
Counseling Models
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class CounselingSession(db.Model):
    """Counseling session model for tracking student support and counseling."""
    
    __tablename__ = 'counseling_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    counselor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'),
                            nullable=True, index=True)
    
    session_date = db.Column(db.DateTime, nullable=False, index=True)
    session_type = db.Column(db.Enum('Initial', 'Follow-up', 'Crisis', 'Routine', 'Exit', name='session_types'),
                             nullable=False, default='Routine', index=True)
    session_mode = db.Column(db.Enum('In-Person', 'Virtual', 'Phone', name='session_modes'),
                            nullable=False, default='In-Person')
    
    duration_minutes = db.Column(db.Integer, nullable=True)
    
    concern_areas = db.Column(db.Text)
    discussion_summary = db.Column(db.Text)
    
    action_items = db.Column(db.Text)
    resources_provided = db.Column(db.Text)
    referrals = db.Column(db.Text)
    
    outcome = db.Column(db.Enum('Ongoing', 'Resolved', 'Escalated', 'No Show', name='counseling_outcomes'),
                       nullable=False, default='Ongoing', index=True)
    
    follow_up_required = db.Column(db.Boolean, nullable=False, default=True, index=True)
    follow_up_date = db.Column(db.DateTime, nullable=True, index=True)
    
    student_agreed = db.Column(db.Boolean, nullable=False, default=False)
    student_satisfaction = db.Column(db.Integer, nullable=True)
    
    is_confidential = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='counseling_sessions')
    counselor = db.relationship('User', backref='counseling_sessions_conducted')
    
    def __init__(self, student_id, session_date, session_type='Routine', session_mode='In-Person',
                 counselor_id=None, duration_minutes=None, concern_areas=None, discussion_summary=None,
                 action_items=None, resources_provided=None, referrals=None, outcome='Ongoing',
                 follow_up_required=True, follow_up_date=None, student_agreed=False, 
                 student_satisfaction=None, is_confidential=True):
        self.student_id = student_id
        self.session_date = session_date
        self.session_type = session_type
        self.session_mode = session_mode
        self.counselor_id = counselor_id
        self.duration_minutes = duration_minutes
        self.concern_areas = concern_areas
        self.discussion_summary = discussion_summary
        self.action_items = action_items
        self.resources_provided = resources_provided
        self.referrals = referrals
        self.outcome = outcome
        self.follow_up_required = follow_up_required
        self.follow_up_date = follow_up_date
        self.student_agreed = student_agreed
        self.student_satisfaction = student_satisfaction
        self.is_confidential = is_confidential
    
    @property
    def is_completed(self):
        return self.outcome in ['Resolved', 'Escalated', 'No Show']
    
    @property
    def needs_follow_up(self):
        return self.follow_up_required and not self.is_completed
    
    @staticmethod
    def get_by_student(student_id):
        return CounselingSession.query.filter_by(student_id=student_id).order_by(
            CounselingSession.session_date.desc()
        ).all()
    
    @staticmethod
    def get_upcoming():
        return CounselingSession.query.filter(
            CounselingSession.session_date >= datetime.utcnow(),
            CounselingSession.outcome == 'Ongoing'
        ).order_by(CounselingSession.session_date.asc()).all()
    
    @staticmethod
    def get_overdue():
        return CounselingSession.query.filter(
            CounselingSession.follow_up_required == True,
            CounselingSession.follow_up_date < datetime.utcnow(),
            CounselingSession.outcome == 'Ongoing'
        ).order_by(CounselingSession.follow_up_date.asc()).all()
    
    @staticmethod
    def get_active_cases():
        return CounselingSession.query.filter(
            CounselingSession.outcome == 'Ongoing'
        ).order_by(CounselingSession.session_date.desc()).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'counselor_id': self.counselor_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'session_type': self.session_type,
            'session_mode': self.session_mode,
            'duration_minutes': self.duration_minutes,
            'concern_areas': self.concern_areas,
            'discussion_summary': self.discussion_summary,
            'action_items': self.action_items,
            'resources_provided': self.resources_provided,
            'referrals': self.referrals,
            'outcome': self.outcome,
            'follow_up_required': self.follow_up_required,
            'follow_up_date': self.follow_up_date.isoformat() if self.follow_up_date else None,
            'student_agreed': self.student_agreed,
            'student_satisfaction': self.student_satisfaction,
            'is_confidential': self.is_confidential,
            'is_completed': self.is_completed,
            'needs_follow_up': self.needs_follow_up
        }


class SupportPlan(db.Model):
    """Support plan model for individual student support strategies."""
    
    __tablename__ = 'support_plans'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'),
                          nullable=True)
    
    plan_type = db.Column(db.Enum('Academic', 'Behavioral', 'Financial', 'Personal', 'General', name='plan_types'),
                         nullable=False, default='General', index=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    goals = db.Column(db.Text)
    strategies = db.Column(db.Text)
    resources_needed = db.Column(db.Text)
    
    start_date = db.Column(db.DateTime, nullable=False)
    target_end_date = db.Column(db.DateTime, nullable=True)
    actual_end_date = db.Column(db.DateTime, nullable=True)
    
    status = db.Column(db.Enum('Draft', 'Active', 'Completed', 'Cancelled', name='plan_status'),
                     nullable=False, default='Draft', index=True)
    
    review_frequency = db.Column(db.String(50), nullable=True)
    last_review_date = db.Column(db.DateTime, nullable=True)
    
    is_active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='support_plans')
    creator = db.relationship('User', backref='support_plans_created')
    
    def __init__(self, student_id, title, start_date, plan_type='General', description=None,
                 goals=None, strategies=None, resources_needed=None, target_end_date=None,
                 status='Draft', review_frequency=None, created_by=None):
        self.student_id = student_id
        self.title = title
        self.start_date = start_date
        self.plan_type = plan_type
        self.description = description
        self.goals = goals
        self.strategies = strategies
        self.resources_needed = resources_needed
        self.target_end_date = target_end_date
        self.status = status
        self.review_frequency = review_frequency
        self.created_by = created_by
    
    @property
    def is_expired(self):
        if self.target_end_date and self.status == 'Active':
            return datetime.utcnow() > self.target_end_date
        return False
    
    @property
    def is_active(self):
        return self.status == 'Active'
    
    @staticmethod
    def get_by_student(student_id):
        return SupportPlan.query.filter_by(student_id=student_id).order_by(
            SupportPlan.created_at.desc()
        ).all()
    
    @staticmethod
    def get_active_plans():
        return SupportPlan.query.filter_by(status='Active', is_active=True).all()
    
    @staticmethod
    def get_overdue_reviews():
        return SupportPlan.query.filter(
            SupportPlan.status == 'Active',
            SupportPlan.is_active == True,
            SupportPlan.last_review_date != None,
            SupportPlan.review_frequency != None
        ).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'plan_type': self.plan_type,
            'title': self.title,
            'description': self.description,
            'goals': self.goals,
            'strategies': self.strategies,
            'resources_needed': self.resources_needed,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_end_date': self.target_end_date.isoformat() if self.target_end_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'status': self.status,
            'review_frequency': self.review_frequency,
            'last_review_date': self.last_review_date.isoformat() if self.last_review_date else None,
            'is_active': self.is_active,
            'is_expired': self.is_expired
        }


class Intervention(db.Model):
    """Intervention model for tracking specific interventions for at-risk students."""
    
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    counseling_session_id = db.Column(db.Integer, db.ForeignKey('counseling_sessions.id', ondelete='SET NULL', onupdate='CASCADE'),
                                     nullable=True, index=True)
    support_plan_id = db.Column(db.Integer, db.ForeignKey('support_plans.id', ondelete='SET NULL', onupdate='CASCADE'),
                               nullable=True, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'),
                          nullable=True)
    
    intervention_type = db.Column(db.Enum('Academic Support', 'Mentoring', 'Financial Aid', 'Counseling', 
                                          'Behavioral Plan', 'Referral', 'Other', name='intervention_types'),
                                 nullable=False, index=True)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    
    start_date = db.Column(db.DateTime, nullable=False)
    target_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    status = db.Column(db.Enum('Planned', 'In Progress', 'Completed', 'Cancelled', name='intervention_status'),
                      nullable=False, default='Planned', index=True)
    
    outcome = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    priority = db.Column(db.Enum('Low', 'Medium', 'High', 'Urgent', name='intervention_priorities'),
                        nullable=False, default='Medium', index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    student = db.relationship('Student', backref='interventions')
    session = db.relationship('CounselingSession', backref='interventions')
    plan = db.relationship('SupportPlan', backref='interventions')
    creator = db.relationship('User', backref='interventions_created')
    
    def __init__(self, student_id, title, start_date, intervention_type='Other', description=None,
                 target_date=None, status='Planned', priority='Medium', created_by=None,
                 counseling_session_id=None, support_plan_id=None):
        self.student_id = student_id
        self.title = title
        self.start_date = start_date
        self.intervention_type = intervention_type
        self.description = description
        self.target_date = target_date
        self.status = status
        self.priority = priority
        self.created_by = created_by
        self.counseling_session_id = counseling_session_id
        self.support_plan_id = support_plan_id
    
    @property
    def is_overdue(self):
        if self.target_date and self.status in ['Planned', 'In Progress']:
            return datetime.utcnow() > self.target_date
        return False
    
    @property
    def is_completed(self):
        return self.status == 'Completed'
    
    @staticmethod
    def get_by_student(student_id):
        return Intervention.query.filter_by(student_id=student_id).order_by(
            Intervention.start_date.desc()
        ).all()
    
    @staticmethod
    def get_active():
        return Intervention.query.filter(
            Intervention.status.in_(['Planned', 'In Progress'])
        ).order_by(Intervention.priority.desc(), Intervention.start_date.asc()).all()
    
    @staticmethod
    def get_overdue():
        return Intervention.query.filter(
            Intervention.status.in_(['Planned', 'In Progress']),
            Intervention.target_date < datetime.utcnow()
        ).order_by(Intervention.target_date.asc()).all()
    
    @staticmethod
    def get_by_priority(priority):
        return Intervention.query.filter_by(priority=priority, status='In Progress').all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'counseling_session_id': self.counseling_session_id,
            'support_plan_id': self.support_plan_id,
            'intervention_type': self.intervention_type,
            'title': self.title,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'target_date': self.target_date.isoformat() if self.target_date else None,
            'completed_date': self.completed_date.isoformat() if self.completed_date else None,
            'status': self.status,
            'outcome': self.outcome,
            'notes': self.notes,
            'priority': self.priority,
            'is_overdue': self.is_overdue,
            'is_completed': self.is_completed
        }