"""
Routes Package
Intelligent Student Risk Monitoring & Decision Support System
"""

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.student import student_bp
from app.routes.admin import admin_bp
from app.routes.api import api_bp
from app.routes.predictions import predictions_bp
from app.routes.study_groups import study_groups_bp
from app.routes.counseling import counseling_bp

__all__ = ['main_bp', 'auth_bp', 'student_bp', 'admin_bp', 'api_bp', 'predictions_bp', 'study_groups_bp', 'counseling_bp']
