"""
Custom Decorators for Intelligent Student Risk Monitoring & Decision Support System
"""

from functools import wraps
from flask import flash, redirect, url_for, abort, request
from flask_login import current_user
from app import db
from app.models.activity_log import ActivityLog


def role_required(*roles):
    """
    Decorator to restrict access to specific user roles.
    
    Args:
        *roles: Allowed roles (e.g., 'admin', 'teacher', 'student')
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            if current_user.role not in roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """
    Decorator to restrict access to teacher users only.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_teacher() and not current_user.is_admin():
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """
    Decorator to restrict access to student users only.
    
    Args:
        f: Function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_student():
            flash('You do not have permission to access this page.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def log_activity(action, entity_type):
    """
    Decorator to log user activity.
    
    Args:
        action: Action being performed (e.g., 'create', 'update', 'delete')
        entity_type: Type of entity being acted upon (e.g., 'student', 'attendance')
        
    Returns:
        Decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Execute the function first
            result = f(*args, **kwargs)
            
            # Log the activity
            try:
                if current_user.is_authenticated:
                    # Get entity ID from kwargs if available
                    entity_id = kwargs.get('id') or kwargs.get('student_id') or kwargs.get('fee_id')
                    
                    activity_log = ActivityLog(
                        user_id=current_user.id,
                        action=action,
                        entity_type=entity_type,
                        entity_id=entity_id,
                        ip_address=request.remote_addr,
                        user_agent=request.user_agent.string[:500] if request.user_agent else None
                    )
                    db.session.add(activity_log)
                    db.session.commit()
            except Exception as e:
                # Log error but don't fail the request
                db.session.rollback()
                print(f"Failed to log activity: {str(e)}")
            
            return result
        return decorated_function
    return decorator
