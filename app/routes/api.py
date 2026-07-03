"""
API Routes - V1
Intelligent Student Risk Monitoring & Decision Support System
All JSON APIs moved here for clean separation.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, limiter
from flask_limiter.util import get_remote_address
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.marks import Marks
from app.models.fee import Fee
from app.models.library import LibraryBook, LibraryTransaction
from app.models.complaint import Complaint
from app.models.alert import Alert
from app.models.prediction import Prediction, MLModel
from app.models.activity_log import ActivityLog
from datetime import datetime
from app.utils.decorators import admin_required, teacher_required

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# User Management APIs
@api_bp.route('/admin/users', methods=['GET'])
@login_required
@limiter.limit("10 per minute")
def get_users():
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)
    
    query = User.query
    if role:
        query = query.filter_by(role=role)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    
    users = query.order_by(User.created_at.desc()).all()
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    })

@api_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get_or_404(user_id)
    return jsonify({'user': user.to_dict()})

# Student APIs
@api_bp.route('/students', methods=['GET'])
@login_required
def get_students():
    if not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Teacher or admin access required'}), 403
    
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    
    query = Student.query
    if course:
        query = query.filter_by(course=course)
    if semester:
        query = query.filter_by(semester=semester)
    
    students = query.order_by(Student.created_at.desc()).all()
    
    return jsonify({'students': [student.to_dict() for student in students]})

# Dashboard Stats
@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    if not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Teacher or admin access required'}), 403
    
    total_students = Student.query.count()
    total_users = User.query.count()
    active_alerts = Alert.query.filter_by(is_read=False).count()
    open_complaints = Complaint.query.filter_by(status='Open').count()
    high_risk_students = Prediction.query.filter_by(risk_level='High').count()
    
    return jsonify({
        'total_students': total_students,
        'total_users': total_users,
        'active_alerts': active_alerts,
        'open_complaints': open_complaints,
        'high_risk_students': high_risk_students
    })

# Activity Logs
@api_bp.route('/admin/activity-logs', methods=['GET'])
@login_required
def get_activity_logs():
    if not current_user.is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')
    limit = request.args.get('limit', 100, type=int)
    
    query = ActivityLog.query
    if user_id:
        query = query.filter_by(user_id=user_id)
    if action:
        query = query.filter_by(action=action)
    if entity_type:
        query = query.filter_by(entity_type=entity_type)
    
    logs = query.order_by(ActivityLog.created_at.desc()).limit(limit).all()
    
    return jsonify({'logs': [log.to_dict() for log in logs]})

