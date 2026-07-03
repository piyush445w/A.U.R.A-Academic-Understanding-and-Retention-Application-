"""
Study Group Routes
A.U.R.A - Academic Understanding and Retention Application
Manages student groups, roles, and class representatives
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.subject import Subject
from app.models.study_group import StudyGroup, GroupMember, SessionGroup
from app.models.activity_log import ActivityLog
from app.utils.decorators import teacher_required, admin_required
from datetime import datetime, date
import secrets
import string

study_groups_bp = Blueprint('study_groups', __name__, url_prefix='/study-groups')


def generate_group_code(length=6):
    """Generate a unique group code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


# ==================== HTML Pages ====================

@study_groups_bp.route('/')
@login_required
def index():
    """Study groups overview page."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    groups = StudyGroup.query.order_by(StudyGroup.created_at.desc()).all()
    return render_template('study_groups/index.html', groups=groups)


@study_groups_bp.route('/create')
@login_required
def create_page():
    """Create new study group page."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    subjects = Subject.query.all()
    students = Student.query.filter_by().all()
    
    return render_template('study_groups/create.html', 
                           courses=courses, 
                           subjects=subjects,
                           students=students)


@study_groups_bp.route('/<int:group_id>')
@login_required
def detail_page(group_id):
    """Study group detail page."""
    group = StudyGroup.query.get_or_404(group_id)
    return render_template('study_groups/detail.html', group=group)


@study_groups_bp.route('/<int:group_id>/edit')
@login_required
def edit_page(group_id):
    """Edit study group page."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    group = StudyGroup.query.get_or_404(group_id)
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    subjects = Subject.query.all()
    students = Student.query.filter_by().all()
    
    return render_template('study_groups/edit.html', 
                           group=group,
                           courses=courses, 
                           subjects=subjects,
                           students=students)


@study_groups_bp.route('/sessions')
@login_required
def sessions_page():
    """Session groups page."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    sessions = SessionGroup.query.order_by(SessionGroup.session_date.desc()).all()
    return render_template('study_groups/sessions.html', sessions=sessions)


@study_groups_bp.route('/sessions/create')
@login_required
def create_session_page():
    """Create session group page."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        flash('Access denied', 'danger')
        return redirect(url_for('main.dashboard'))
    
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    subjects = Subject.query.all()
    students = Student.query.filter_by().all()
    
    return render_template('study_groups/create_session.html',
                           courses=courses,
                           subjects=subjects,
                           students=students)


# ==================== API Endpoints ====================

@study_groups_bp.route('/api/groups', methods=['GET'])
@login_required
def get_groups():
    """Get all study groups."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Access denied'}), 403
    
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    
    query = StudyGroup.query
    if course:
        query = query.filter_by(course=course)
    if semester:
        query = query.filter_by(semester=semester)
    
    groups = query.order_by(StudyGroup.created_at.desc()).all()
    return jsonify({'groups': [g.to_dict() for g in groups]})


@study_groups_bp.route('/api/groups', methods=['POST'])
@teacher_required
def create_group():
    """Create a new study group."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Generate unique group code
    group_code = generate_group_code()
    while StudyGroup.query.filter_by(group_code=group_code).first():
        group_code = generate_group_code()
    
    group = StudyGroup(
        group_name=data.get('group_name'),
        group_code=group_code,
        description=data.get('description'),
        course=data.get('course'),
        semester=data.get('semester'),
        subject_id=data.get('subject_id'),
        max_members=data.get('max_members', 5)
    )
    
    # Set class representative if provided
    if data.get('class_rep_id'):
        group.class_rep_id = data.get('class_rep_id')
    
    db.session.add(group)
    db.session.commit()
    
    # Add members if provided
    member_ids = data.get('member_ids', [])
    for member_data in member_ids:
        member = GroupMember(
            student_id=member_data.get('student_id'),
            group_id=group.id,
            role=member_data.get('role', 'participant')
        )
        db.session.add(member)
    
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='create_study_group',
        entity_type='study_group',
        entity_id=group.id,
        details=f'Created study group: {group.group_name}',
        ip_address=request.remote_addr
    )
    
    return jsonify({'group': group.to_dict()}), 201


@study_groups_bp.route('/api/groups/<int:group_id>', methods=['GET'])
@login_required
def get_group(group_id):
    """Get a specific study group."""
    group = StudyGroup.query.get_or_404(group_id)
    return jsonify({'group': group.to_dict()})


@study_groups_bp.route('/api/groups/<int:group_id>', methods=['PUT'])
@teacher_required
def update_group(group_id):
    """Update a study group."""
    group = StudyGroup.query.get_or_404(group_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if data.get('group_name'):
        group.group_name = data.get('group_name')
    if data.get('description') is not None:
        group.description = data.get('description')
    if data.get('course'):
        group.course = data.get('course')
    if data.get('semester'):
        group.semester = data.get('semester')
    if data.get('subject_id'):
        group.subject_id = data.get('subject_id')
    if data.get('max_members'):
        group.max_members = data.get('max_members')
    if 'class_rep_id' in data:
        group.class_rep_id = data.get('class_rep_id')
    if 'is_active' in data:
        group.is_active = data.get('is_active')
    
    db.session.commit()
    
    return jsonify({'group': group.to_dict()})


@study_groups_bp.route('/api/groups/<int:group_id>', methods=['DELETE'])
@admin_required
def delete_group(group_id):
    """Delete a study group."""
    group = StudyGroup.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({'message': 'Group deleted successfully'})


@study_groups_bp.route('/api/groups/<int:group_id>/members', methods=['POST'])
@teacher_required
def add_member(group_id):
    """Add a member to a group."""
    group = StudyGroup.query.get_or_404(group_id)
    data = request.get_json()
    
    if not data or not data.get('student_id'):
        return jsonify({'error': 'Student ID required'}), 400
    
    # Check if already a member
    existing = GroupMember.query.filter_by(
        student_id=data.get('student_id'),
        group_id=group_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Student already in group'}), 400
    
    # Check if group is full
    if group.is_full:
        return jsonify({'error': 'Group is at max capacity'}), 400
    
    member = GroupMember(
        student_id=data.get('student_id'),
        group_id=group_id,
        role=data.get('role', 'participant')
    )
    
    db.session.add(member)
    db.session.commit()
    
    return jsonify({'member': member.to_dict()}), 201


@study_groups_bp.route('/api/groups/<int:group_id>/members/<int:member_id>', methods=['PUT'])
@teacher_required
def update_member(group_id, member_id):
    """Update member role or status."""
    member = GroupMember.query.get_or_404(member_id)
    data = request.get_json()
    
    if data.get('role'):
        member.role = data.get('role')
    if 'is_active' in data:
        member.is_active = data.get('is_active')
    if data.get('notes') is not None:
        member.notes = data.get('notes')
    
    db.session.commit()
    
    return jsonify({'member': member.to_dict()})


@study_groups_bp.route('/api/groups/<int:group_id>/members/<int:member_id>', methods=['DELETE'])
@teacher_required
def remove_member(group_id, member_id):
    """Remove a member from a group."""
    member = GroupMember.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    
    return jsonify({'message': 'Member removed successfully'})


@study_groups_bp.route('/api/groups/<int:group_id>/class-rep', methods=['POST'])
@teacher_required
def set_class_rep(group_id):
    """Set or update class representative."""
    group = StudyGroup.query.get_or_404(group_id)
    data = request.get_json()
    
    if not data or not data.get('student_id'):
        return jsonify({'error': 'Student ID required'}), 400
    
    student = Student.query.get_or_404(data.get('student_id'))
    group.class_rep_id = student.id
    group.is_class_rep_active = True
    db.session.commit()
    
    return jsonify({
        'message': f'{student.full_name} set as Class Representative',
        'group': group.to_dict()
    })


@study_groups_bp.route('/api/groups/<int:group_id>/class-rep', methods=['DELETE'])
@teacher_required
def remove_class_rep(group_id):
    """Remove class representative."""
    group = StudyGroup.query.get_or_404(group_id)
    group.class_rep_id = None
    group.is_class_rep_active = False
    db.session.commit()
    
    return jsonify({'message': 'Class Representative removed', 'group': group.to_dict()})


# ==================== Session Group APIs ====================

@study_groups_bp.route('/api/sessions', methods=['GET'])
@login_required
def get_sessions():
    """Get all session groups."""
    if not (current_user.is_admin() or current_user.is_teacher()):
        return jsonify({'error': 'Access denied'}), 403
    
    sessions = SessionGroup.query.order_by(SessionGroup.session_date.desc()).all()
    return jsonify({'sessions': [s.to_dict() for s in sessions]})


@study_groups_bp.route('/api/sessions', methods=['POST'])
@teacher_required
def create_session():
    """Create a new session group."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    session = SessionGroup(
        session_name=data.get('session_name'),
        session_date=datetime.strptime(data.get('session_date'), '%Y-%m-%d').date(),
        course=data.get('course'),
        semester=data.get('semester'),
        subject_id=data.get('subject_id'),
        group_count=data.get('group_count', 5),
        students_per_group=data.get('students_per_group', 4)
    )
    
    if data.get('session_anchor_id'):
        session.session_anchor_id = data.get('session_anchor_id')
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({'session': session.to_dict()}), 201


@study_groups_bp.route('/api/sessions/<int:session_id>/generate-groups', methods=['POST'])
@teacher_required
def generate_session_groups(session_id):
    """Auto-generate groups for a session."""
    session = SessionGroup.query.get_or_404(session_id)
    data = request.get_json() or {}
    
    # Get students for this course and semester
    students = Student.query.filter_by(
        course=session.course,
        semester=session.semester
    ).all()
    
    if not students:
        return jsonify({'error': 'No students found for this course and semester'}), 400
    
    # Shuffle students for random assignment
    import random
    shuffled = list(students)
    random.shuffle(shuffled)
    
    # Create groups
    total_groups = session.group_count
    students_per_group = session.students_per_group
    
    for i in range(total_groups):
        group_name = f"Group {i+1}"
        group_code = generate_group_code()
        
        group = StudyGroup(
            group_name=group_name,
            group_code=group_code,
            course=session.course,
            semester=session.semester,
            subject_id=session.subject_id,
            max_members=students_per_group
        )
        db.session.add(group)
        db.session.flush()
        
        # Assign students to group
        start_idx = i * students_per_group
        end_idx = min(start_idx + students_per_group, len(shuffled))
        
        for j, student in enumerate(shuffled[start_idx:end_idx]):
            role = 'leader' if j == 0 else 'participant'  # First student is leader
            member = GroupMember(
                student_id=student.id,
                group_id=group.id,
                role=role
            )
            db.session.add(member)
        
        # Link to session
        group.session_id = session.id
    
    db.session.commit()
    
    return jsonify({
        'message': f'Generated {total_groups} groups',
        'session': session.to_dict()
    })


@study_groups_bp.route('/api/sessions/<int:session_id>', methods=['PUT'])
@teacher_required
def update_session(session_id):
    """Update a session group."""
    session = SessionGroup.query.get_or_404(session_id)
    data = request.get_json()
    
    if data.get('session_name'):
        session.session_name = data.get('session_name')
    if data.get('session_anchor_id'):
        session.session_anchor_id = data.get('session_anchor_id')
    if 'is_active' in data:
        session.is_active = data.get('is_active')
    if 'is_completed' in data:
        session.is_completed = data.get('is_completed')
        if data.get('is_completed'):
            session.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'session': session.to_dict()})


@study_groups_bp.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@admin_required
def delete_session(session_id):
    """Delete a session group."""
    session = SessionGroup.query.get_or_404(session_id)
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({'message': 'Session deleted successfully'})