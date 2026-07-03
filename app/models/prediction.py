"""
Prediction and MLModel Models
Intelligent Student Risk Monitoring & Decision Support System
"""

from datetime import datetime
from app import db


class MLModel(db.Model):
    """MLModel model for storing machine learning model metadata."""
    
    __tablename__ = 'ml_models'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Model details
    model_name = db.Column(db.String(100), nullable=False, index=True)
    model_version = db.Column(db.String(20), nullable=False, index=True)
    algorithm = db.Column(db.String(100), nullable=False)
    
    # Performance metrics
    accuracy = db.Column(db.Numeric(5, 4))
    precision_score = db.Column(db.Numeric(5, 4))
    recall_score = db.Column(db.Numeric(5, 4))
    f1_score = db.Column(db.Numeric(5, 4))
    
    # Model metadata
    training_date = db.Column(db.DateTime, nullable=False, index=True)
    model_path = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, nullable=False, default=False, index=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='model', lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, model_name, model_version, algorithm, training_date,
                 accuracy=None, precision_score=None, recall_score=None, f1_score=None,
                 model_path=None, is_active=False):
        """Initialize ML model."""
        self.model_name = model_name
        self.model_version = model_version
        self.algorithm = algorithm
        self.training_date = training_date
        self.accuracy = accuracy
        self.precision_score = precision_score
        self.recall_score = recall_score
        self.f1_score = f1_score
        self.model_path = model_path
        self.is_active = is_active
    
    def activate(self):
        """Activate this model and deactivate others."""
        # Deactivate all other models
        MLModel.query.filter(MLModel.id != self.id).update({'is_active': False})
        # Activate this model
        self.is_active = True
    
    def deactivate(self):
        """Deactivate this model."""
        self.is_active = False
    
    @staticmethod
    def get_active_model():
        """
        Get the currently active model.
        
        Returns:
            Active MLModel instance or None
        """
        return MLModel.query.filter_by(is_active=True).first()
    
    @staticmethod
    def get_models_by_name(model_name):
        """
        Get all versions of a model by name.
        
        Args:
            model_name: Model name
            
        Returns:
            List of models
        """
        return MLModel.query.filter_by(model_name=model_name).order_by(
            MLModel.training_date.desc()
        ).all()
    
    def to_dict(self):
        """Convert ML model to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'algorithm': self.algorithm,
            'accuracy': float(self.accuracy) if self.accuracy else None,
            'precision_score': float(self.precision_score) if self.precision_score else None,
            'recall_score': float(self.recall_score) if self.recall_score else None,
            'f1_score': float(self.f1_score) if self.f1_score else None,
            'training_date': self.training_date.isoformat() if self.training_date else None,
            'model_path': self.model_path,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        """String representation of MLModel."""
        return f'<MLModel {self.model_name} v{self.model_version} ({self.algorithm})>'


class Prediction(db.Model):
    """Prediction model for storing ML model predictions for student risk assessment."""
    
    __tablename__ = 'predictions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE', onupdate='CASCADE'),
                          nullable=False, index=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id', ondelete='RESTRICT', onupdate='CASCADE'),
                        nullable=False, index=True)
    override_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL', onupdate='CASCADE'),
                           nullable=True, index=True)
    
    # Prediction details
    risk_level = db.Column(db.Enum('Low', 'Medium', 'High', 'Critical', name='risk_levels'),
                          nullable=False, index=True)
    risk_score = db.Column(db.Numeric(5, 4), nullable=False)
    probability = db.Column(db.Numeric(5, 4), nullable=False)
    
    # Input features
    attendance_percentage = db.Column(db.Numeric(5, 2))
    average_marks = db.Column(db.Numeric(5, 2))
    fee_status = db.Column(db.String(50))
    
    # Prediction metadata
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    recommendations = db.Column(db.Text)
    
    # Manual override fields
    is_manual = db.Column(db.Boolean, nullable=False, default=False, index=True)
    override_reason = db.Column(db.String(500), nullable=True)
    
    # Teacher review fields
    flag_for_review = db.Column(db.Boolean, nullable=False, default=False, index=True)
    review_note = db.Column(db.String(500), nullable=True)
    
    # Check constraints
    __table_args__ = (
        db.CheckConstraint('risk_score >= 0 AND risk_score <= 1', name='chk_predictions_risk_score'),
        db.CheckConstraint('probability >= 0 AND probability <= 1', name='chk_predictions_probability'),
    )
    
    # Relationships
    override_user = db.relationship('User', foreign_keys=[override_by], backref='manual_overrides')
    
    def __init__(self, student_id, model_id, risk_level, risk_score, probability,
                 attendance_percentage=None, average_marks=None, fee_status=None,
                 recommendations=None, is_manual=False, override_reason=None, override_by=None,
                 flag_for_review=False, review_note=None):
        """Initialize prediction."""
        self.student_id = student_id
        self.model_id = model_id
        self.risk_level = risk_level
        self.risk_score = risk_score
        self.probability = probability
        self.attendance_percentage = attendance_percentage
        self.average_marks = average_marks
        self.fee_status = fee_status
        self.recommendations = recommendations
        self.is_manual = is_manual
        self.override_reason = override_reason
        self.override_by = override_by
        self.flag_for_review = flag_for_review
        self.review_note = review_note
    
    @property
    def is_high_risk(self):
        """Check if prediction indicates high risk."""
        return self.risk_level == 'High'
    
    @property
    def is_medium_risk(self):
        """Check if prediction indicates medium risk."""
        return self.risk_level == 'Medium'
    
    @property
    def is_low_risk(self):
        """Check if prediction indicates low risk."""
        return self.risk_level == 'Low'
    
    @property
    def is_critical_risk(self):
        """Check if prediction indicates critical risk."""
        return self.risk_level == 'Critical'
    
    def mark_as_manual(self, override_by, override_reason):
        """
        Mark prediction as a manual override.
        
        Args:
            override_by: User ID who made the override
            override_reason: Reason for the manual override
        """
        self.is_manual = True
        self.override_by = override_by
        self.override_reason = override_reason
    
    def flag_for_teacher_review(self, review_note):
        """
        Flag prediction for teacher review.
        
        Args:
            review_note: Note from teacher explaining why flagged
        """
        self.flag_for_review = True
        self.review_note = review_note
    
    def clear_review_flag(self):
        """Clear the review flag and review note."""
        self.flag_for_review = False
        self.review_note = None
    
    @staticmethod
    def get_predictions_by_student(student_id, limit=None):
        """
        Get predictions for a student.
        
        Args:
            student_id: Student ID
            limit: Limit number of results (optional)
            
        Returns:
            List of predictions
        """
        query = Prediction.query.filter_by(student_id=student_id).order_by(
            Prediction.prediction_date.desc()
        )
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_latest_prediction(student_id):
        """
        Get the latest prediction for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            Latest prediction or None
        """
        return Prediction.query.filter_by(student_id=student_id).order_by(
            Prediction.prediction_date.desc()
        ).first()
    
    @staticmethod
    def get_high_risk_students():
        """
        Get all students with high risk predictions.
        
        Returns:
            List of predictions for high-risk students
        """
        return Prediction.query.filter(Prediction.risk_level.in_(['High', 'Critical'])).order_by(
            Prediction.risk_score.desc()
        ).all()
    
    @staticmethod
    def get_predictions_by_risk_level(risk_level):
        """
        Get predictions by risk level.
        
        Args:
            risk_level: Risk level ('Low', 'Medium', 'High', 'Critical')
            
        Returns:
            List of predictions
        """
        return Prediction.query.filter_by(risk_level=risk_level).order_by(
            Prediction.risk_score.desc()
        ).all()
    
    @staticmethod
    def get_predictions_by_date_range(start_date, end_date):
        """
        Get predictions within a date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of predictions
        """
        return Prediction.query.filter(
            Prediction.prediction_date >= start_date,
            Prediction.prediction_date <= end_date
        ).order_by(Prediction.prediction_date.desc()).all()
    
    @staticmethod
    def get_flagged_for_review():
        """
        Get all predictions flagged for teacher review.
        
        Returns:
            List of predictions flagged for review
        """
        return Prediction.query.filter_by(flag_for_review=True).order_by(
            Prediction.prediction_date.desc()
        ).all()
    
    @staticmethod
    def get_manual_overrides():
        """
        Get all manual override predictions.
        
        Returns:
            List of manual override predictions
        """
        return Prediction.query.filter_by(is_manual=True).order_by(
            Prediction.prediction_date.desc()
        ).all()
    
    def to_dict(self):
        """Convert prediction to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'model_id': self.model_id,
            'risk_level': self.risk_level,
            'risk_score': float(self.risk_score),
            'probability': float(self.probability),
            'attendance_percentage': float(self.attendance_percentage) if self.attendance_percentage else None,
            'average_marks': float(self.average_marks) if self.average_marks else None,
            'fee_status': self.fee_status,
            'recommendations': self.recommendations,
            'is_high_risk': self.is_high_risk,
            'is_medium_risk': self.is_medium_risk,
            'is_low_risk': self.is_low_risk,
            'is_critical_risk': self.is_critical_risk,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'is_manual': self.is_manual,
            'override_reason': self.override_reason,
            'override_by': self.override_by,
            'flag_for_review': self.flag_for_review,
            'review_note': self.review_note
        }
    
    def __repr__(self):
        """String representation of Prediction."""
        return f'<Prediction {self.student_id}: {self.risk_level} ({self.risk_score})>'