"""
Alert Model
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class Alert(db.Model):
    """Alert model for storing system-generated alerts for students."""
    
    __tablename__ = 'alerts'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    
    # Alert details
    alert_type = db.Column(db.Enum('Attendance', 'Academic', 'Fee', 'Behavior', 'General', name='alert_types'),
                          nullable=False, index=True)
    severity = db.Column(db.Enum('Info', 'Warning', 'Critical', name='alert_severities'),
                        nullable=False, default='Info', index=True)
    message = db.Column(db.Text, nullable=False)
    suggestion = db.Column(db.Text)
    is_read = db.Column(db.Boolean, nullable=False, default=False, index=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, student_id, alert_type, message, severity='Info', 
                 suggestion=None, is_read=False):
        """Initialize alert."""
        self.student_id = student_id
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.suggestion = suggestion
        self.is_read = is_read
    
    @property
    def is_critical(self):
        """Check if alert is critical."""
        return self.severity == 'Critical'
    
    @property
    def is_warning(self):
        """Check if alert is warning."""
        return self.severity == 'Warning'
    
    @property
    def is_info(self):
        """Check if alert is info."""
        return self.severity == 'Info'
    
    def mark_as_read(self):
        """Mark alert as read."""
        self.is_read = True
    
    @staticmethod
    def get_alerts_by_student(student_id, is_read=None, alert_type=None):
        """
        Get alerts for a student.
        
        Args:
            student_id: Student ID
            is_read: Filter by read status (optional)
            alert_type: Filter by alert type (optional)
            
        Returns:
            List of alerts
        """
        query = Alert.query.filter_by(student_id=student_id)
        
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_unread_alerts(student_id=None):
        """
        Get unread alerts.
        
        Args:
            student_id: Filter by student (optional)
            
        Returns:
            List of unread alerts
        """
        query = Alert.query.filter_by(is_read=False)
        if student_id:
            query = query.filter_by(student_id=student_id)
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_critical_alerts(student_id=None):
        """
        Get critical alerts.
        
        Args:
            student_id: Filter by student (optional)
            
        Returns:
            List of critical alerts
        """
        query = Alert.query.filter_by(severity='Critical')
        if student_id:
            query = query.filter_by(student_id=student_id)
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_alerts_by_type(alert_type, student_id=None):
        """
        Get alerts by type.
        
        Args:
            alert_type: Alert type
            student_id: Filter by student (optional)
            
        Returns:
            List of alerts
        """
        query = Alert.query.filter_by(alert_type=alert_type)
        if student_id:
            query = query.filter_by(student_id=student_id)
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def get_alerts_by_severity(severity, student_id=None):
        """
        Get alerts by severity.
        
        Args:
            severity: Alert severity
            student_id: Filter by student (optional)
            
        Returns:
            List of alerts
        """
        query = Alert.query.filter_by(severity=severity)
        if student_id:
            query = query.filter_by(student_id=student_id)
        return query.order_by(Alert.created_at.desc()).all()
    
    @staticmethod
    def mark_all_as_read(student_id):
        """
        Mark all alerts as read for a student.
        
        Args:
            student_id: Student ID
        """
        Alert.query.filter_by(student_id=student_id, is_read=False).update({'is_read': True})
    
    @staticmethod
    def get_alert_count(student_id=None, is_read=None):
        """
        Get alert count.
        
        Args:
            student_id: Filter by student (optional)
            is_read: Filter by read status (optional)
            
        Returns:
            Alert count
        """
        query = Alert.query
        if student_id:
            query = query.filter_by(student_id=student_id)
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        return query.count()
    
    def to_dict(self):
        """Convert alert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'message': self.message,
            'suggestion': self.suggestion,
            'is_read': self.is_read,
            'is_critical': self.is_critical,
            'is_warning': self.is_warning,
            'is_info': self.is_info,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of Alert."""
        return f'<Alert {self.id}: {self.alert_type} ({self.severity})>'
