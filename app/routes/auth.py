"""
Auth Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app import csrf, db
from app.models.user import User
from app.models.activity_log import ActivityLog

auth_bp = Blueprint('auth', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day", "100 per hour"]
)

@auth_bp.route('/login', methods=['GET'])
def login_page():
    """Login page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')


@auth_bp.route('/login', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
def login():
    """User login endpoint."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        if not request.is_json:
            flash('Username and password are required', 'danger')
            return redirect(url_for('auth.login_page'))
        return jsonify({'error': 'Username and password are required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        if not request.is_json:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login_page'))
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        if not request.is_json:
            flash('Account is deactivated', 'danger')
            return redirect(url_for('auth.login_page'))
        return jsonify({'error': 'Account is deactivated'}), 403
    
    login_user(user)
    
    # Log activity
    ActivityLog.log_activity(
        user_id=user.id,
        action='login',
        entity_type='user',
        entity_id=user.id,
        details=f'User {username} logged in',
        ip_address=request.remote_addr
    )
    
    if not request.is_json:
        flash('Login successful', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict()
    })


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout endpoint."""
    user_id = current_user.id
    username = current_user.username
    
    # Log activity
    ActivityLog.log_activity(
        user_id=user_id,
        action='logout',
        entity_type='user',
        entity_id=user_id,
        details=f'User {username} logged out',
        ip_address=request.remote_addr
    )
    
    logout_user()
    
    return redirect(url_for('main.index'))


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout_api():
    """User logout API endpoint."""
    user_id = current_user.id
    username = current_user.username
    
    # Log activity
    ActivityLog.log_activity(
        user_id=user_id,
        action='logout',
        entity_type='user',
        entity_id=user_id,
        details=f'User {username} logged out',
        ip_address=request.remote_addr
    )
    
    logout_user()
    
    return jsonify({'message': 'Logout successful'})


@auth_bp.route('/register', methods=['GET'])
def register_page():
    """Registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/register.html')


@auth_bp.route('/register', methods=['POST'])
@csrf.exempt
@limiter.limit("3 per minute")
def register():
    """User registration endpoint."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    role = data.get('role', 'student')
    
    if not username or not email or not password:
        if not request.is_json:
            flash('Username, email, and password are required', 'danger')
            return redirect(url_for('auth.register_page'))
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    if password != confirm_password:
        if not request.is_json:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register_page'))
        return jsonify({'error': 'Passwords do not match'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        if not request.is_json:
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register_page'))
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        if not request.is_json:
            flash('Email already exists', 'danger')
            return redirect(url_for('auth.register_page'))
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=username,
        email=email,
        password=password,
        role=role
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=user.id,
        action='register',
        entity_type='user',
        entity_id=user.id,
        details=f'User {username} registered with role {role}',
        ip_address=request.remote_addr
    )
    
    if not request.is_json:
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login_page'))
    
    return jsonify({
        'message': 'Registration successful',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile."""
    return jsonify({
        'user': current_user.to_dict()
    })


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user profile."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update allowed fields
    if 'email' in data:
        # Check if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user.id:
            return jsonify({'error': 'Email already exists'}), 400
        current_user.email = data['email']
    
    if 'password' in data:
        current_user.set_password(data['password'])
    
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='update_profile',
        entity_type='user',
        entity_id=current_user.id,
        details='User profile updated',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': current_user.to_dict()
    })


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current password and new password are required'}), 400
    
    if not current_user.check_password(current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    current_user.set_password(new_password)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='change_password',
        entity_type='user',
        entity_id=current_user.id,
        details='Password changed',
        ip_address=request.remote_addr
    )
    
    return jsonify({'message': 'Password changed successfully'})
