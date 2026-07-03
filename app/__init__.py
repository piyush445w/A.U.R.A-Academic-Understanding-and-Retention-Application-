"""
Flask Application Initialization
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)


def create_app(config_name='default'):
    """
    Application factory pattern for creating Flask app.
    
    Args:
        config_name: Configuration to use (development, testing, production)
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import main_bp, auth_bp, student_bp, admin_bp, api_bp, predictions_bp, study_groups_bp, counseling_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp)
    app.register_blueprint(predictions_bp, url_prefix='/predictions')
    app.register_blueprint(study_groups_bp, url_prefix='/study-groups')
    app.register_blueprint(counseling_bp, url_prefix='/counseling')
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables safely
    with app.app_context():
        try:
            from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog
            from app.models.counseling import CounselingSession, SupportPlan, Intervention
            db.create_all()
        except Exception as e:
            print(f"DB init warning (non-fatal): {e}")
    
    return app


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request_error(error):
        return {'error': 'Bad Request', 'message': str(error)}, 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return {'error': 'Forbidden', 'message': 'You do not have permission to access this resource'}, 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found', 'message': 'The requested resource was not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}, 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return {'error': 'Request Entity Too Large', 'message': 'File size exceeds the maximum allowed limit'}, 413


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    from app.models.user import User
    return User.query.get(int(user_id))
