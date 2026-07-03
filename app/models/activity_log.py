"""
ActivityLog Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class ActivityLog(db.Model):
    """ActivityLog model for storing system activity and audit trail."""
    
    __tablename__ = 'activity_log'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'),
                       nullable=False, index=True)
    
    # Activity details
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False, index=True)
    entity_id = db.Column(db.Integer, index=True)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, user_id, action, entity_type, entity_id=None, details=None, ip_address=None):
        """Initialize activity log."""
        self.user_id = user_id
        self.action = action
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.details = details
        self.ip_address = ip_address
    
    @staticmethod
    def log_activity(user_id, action, entity_type, entity_id=None, details=None, ip_address=None):
        """
        Log an activity.
        
        Args:
            user_id: User ID
            action: Action performed
            entity_type: Type of entity
            entity_id: Entity ID (optional)
            details: Additional details (optional)
            ip_address: IP address (optional)
            
        Returns:
            ActivityLog instance
        """
        log = ActivityLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        return log
    
    @staticmethod
    def get_logs_by_user(user_id, limit=None):
        """
        Get activity logs for a user.
        
        Args:
            user_id: User ID
            limit: Limit number of results (optional)
            
        Returns:
            List of activity logs
        """
        query = ActivityLog.query.filter_by(user_id=user_id).order_by(
            ActivityLog.created_at.desc()
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_logs_by_entity(entity_type, entity_id=None, limit=None):
        """
        Get activity logs for an entity.
        
        Args:
            entity_type: Entity type
            entity_id: Entity ID (optional)
            limit: Limit number of results (optional)
            
        Returns:
            List of activity logs
        """
        query = ActivityLog.query.filter_by(entity_type=entity_type)
        if entity_id:
            query = query.filter_by(entity_id=entity_id)
        query = query.order_by(ActivityLog.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_logs_by_action(action, limit=None):
        """
        Get activity logs by action.
        
        Args:
            action: Action type
            limit: Limit number of results (optional)
            
        Returns:
            List of activity logs
        """
        query = ActivityLog.query.filter_by(action=action).order_by(
            ActivityLog.created_at.desc()
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_logs_by_date_range(start_date, end_date, limit=None):
        """
        Get activity logs within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            limit: Limit number of results (optional)
            
        Returns:
            List of activity logs
        """
        query = ActivityLog.query.filter(
            ActivityLog.created_at >= start_date,
            ActivityLog.created_at <= end_date
        ).order_by(ActivityLog.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_recent_logs(limit=100):
        """
        Get recent activity logs.
        
        Args:
            limit: Number of logs to retrieve
            
        Returns:
            List of activity logs
        """
        return ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_logs_by_ip(ip_address, limit=None):
        """
        Get activity logs by IP address.
        
        Args:
            ip_address: IP address
            limit: Limit number of results (optional)
            
        Returns:
            List of activity logs
        """
        query = ActivityLog.query.filter_by(ip_address=ip_address).order_by(
            ActivityLog.created_at.desc()
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def to_dict(self):
        """Convert activity log to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of ActivityLog."""
        return f'<ActivityLog {self.id}: {self.user_id} - {self.action} on {self.entity_type}>'
