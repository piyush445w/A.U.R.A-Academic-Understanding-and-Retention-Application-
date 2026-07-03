"""
Counseling Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Student, User
from app.models.counseling import CounselingSession, SupportPlan, Intervention
from app.models.prediction import Prediction
from app.utils.decorators import role_required, teacher_required, admin_required, log_activity

counseling_bp = Blueprint('counseling', __name__, url_prefix='/counseling')


@counseling_bp.route('/')
@login_required
@role_required('admin', 'teacher')
def dashboard():
    """Counseling and support dashboard."""
    
    active_cases = CounselingSession.get_active_cases()
    upcoming_sessions = CounselingSession.get_upcoming()
    overdue_followups = CounselingSession.get_overdue()
    active_interventions = Intervention.get_active()
    overdue_interventions = Intervention.get_overdue()
    
    total_students_in_counseling = len(set([s.student_id for s in active_cases]))
    now = datetime.utcnow()
    sessions_this_month = CounselingSession.query.filter(
        CounselingSession.session_date >= now.replace(day=1)
    ).count()
    
    risk_students_without_support = []
    high_risk_preds = Prediction.query.filter(
        Prediction.risk_level.in_(['High', 'Critical'])
    ).all()
    for pred in high_risk_preds:
        student = Student.query.get(pred.student_id)
        if student:
            has_active_session = any(s.student_id == student.id for s in active_cases)
            if not has_active_session:
                risk_students_without_support.append({
                    'student_id': student.student_id,
                    'full_name': student.full_name,
                    'course': student.course,
                    'risk_level': pred.risk_level,
                    'risk_score': int(float(pred.risk_score) * 100)
                })
    
    return render_template('counseling/dashboard.html',
                          active_cases=active_cases,
                          upcoming_sessions=upcoming_sessions,
                          overdue_followups=overdue_followups,
                          active_interventions=active_interventions,
                          overdue_interventions=overdue_interventions,
                          total_students_in_counseling=total_students_in_counseling,
                          sessions_this_month=sessions_this_month,
                          risk_students_without_support=risk_students_without_support[:10],
                          now=now)


@counseling_bp.route('/sessions')
@login_required
@role_required('admin', 'teacher')
def sessions():
    """List all counseling sessions."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = CounselingSession.query.order_by(CounselingSession.session_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('counseling/sessions.html',
                          sessions=pagination.items,
                          pagination=pagination,
                          now=datetime.utcnow())


@counseling_bp.route('/sessions/<int:session_id>')
@login_required
@role_required('admin', 'teacher', 'counselor')
def session_detail(session_id):
    """View counseling session details."""
    session = CounselingSession.query.get_or_404(session_id)
    student = Student.query.get(session.student_id)
    interventions = Intervention.get_by_student(session.student_id)
    
    return render_template('counseling/session_detail.html',
                          session=session,
                          student=student,
                          interventions=interventions)


@counseling_bp.route('/sessions/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='create_session', entity_type='counseling_session')
def new_session():
    """Create a new counseling session."""
    if request.method == 'POST':
        data = request.form
        
        session = CounselingSession(
            student_id=data.get('student_id', type=int),
            counselor_id=current_user.id if current_user.role in ['admin', 'teacher', 'counselor'] else None,
            session_date=datetime.fromisoformat(data.get('session_date')),
            session_type=data.get('session_type', 'Routine'),
            session_mode=data.get('session_mode', 'In-Person'),
            duration_minutes=data.get('duration_minutes', type=int) if data.get('duration_minutes') else None,
            concern_areas=data.get('concern_areas'),
            discussion_summary=data.get('discussion_summary'),
            action_items=data.get('action_items'),
            resources_provided=data.get('resources_provided'),
            referrals=data.get('referrals'),
            outcome=data.get('outcome', 'Ongoing'),
            follow_up_required='follow_up_required' in data,
            follow_up_date=datetime.fromisoformat(data.get('follow_up_date')) if data.get('follow_up_date') else None,
            student_agreed='student_agreed' in data,
            is_confidential='is_confidential' not in data
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({'message': 'Counseling session created successfully', 'session_id': session.id}), 201
    
    students = Student.query.order_by(Student.first_name, Student.last_name).all()
    return render_template('counseling/new_session.html', students=students)


@counseling_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='update_session', entity_type='counseling_session')
def update_session(session_id):
    """Update a counseling session."""
    session = CounselingSession.query.get_or_404(session_id)
    data = request.get_json()
    
    if data.get('session_type'):
        session.session_type = data['session_type']
    if data.get('session_mode'):
        session.session_mode = data['session_mode']
    if data.get('duration_minutes'):
        session.duration_minutes = data['duration_minutes']
    if data.get('concern_areas'):
        session.concern_areas = data['concern_areas']
    if data.get('discussion_summary'):
        session.discussion_summary = data['discussion_summary']
    if data.get('action_items'):
        session.action_items = data['action_items']
    if data.get('resources_provided'):
        session.resources_provided = data['resources_provided']
    if data.get('referrals'):
        session.referrals = data['referrals']
    if data.get('outcome'):
        session.outcome = data['outcome']
    if 'follow_up_required' in data:
        session.follow_up_required = data['follow_up_required']
    if data.get('follow_up_date'):
        session.follow_up_date = datetime.fromisoformat(data['follow_up_date'])
    if 'student_agreed' in data:
        session.student_agreed = data['student_agreed']
    if data.get('student_satisfaction'):
        session.student_satisfaction = data['student_satisfaction']
    
    db.session.commit()
    
    return jsonify({'message': 'Session updated successfully', 'session': session.to_dict()})


@counseling_bp.route('/sessions/<int:session_id>', methods=['DELETE'])
@login_required
@admin_required
@log_activity(action='delete_session', entity_type='counseling_session')
def delete_session(session_id):
    """Delete a counseling session."""
    session = CounselingSession.query.get_or_404(session_id)
    
    db.session.delete(session)
    db.session.commit()
    
    return jsonify({'message': 'Session deleted successfully'})


@counseling_bp.route('/plans')
@login_required
@role_required('admin', 'teacher', 'counselor')
def support_plans():
    """List all support plans."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    
    query = SupportPlan.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    query = query.order_by(SupportPlan.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('counseling/plans.html',
                          plans=pagination.items,
                          pagination=pagination,
                          status_filter=status_filter)


@counseling_bp.route('/plans/<int:plan_id>')
@login_required
@role_required('admin', 'teacher', 'counselor')
def plan_detail(plan_id):
    """View support plan details."""
    plan = SupportPlan.query.get_or_404(plan_id)
    student = Student.query.get(plan.student_id)
    interventions = Intervention.query.filter_by(support_plan_id=plan_id).order_by(
        Intervention.start_date.desc()
    ).all()
    sessions = CounselingSession.query.filter_by(student_id=plan.student_id).order_by(
        CounselingSession.session_date.desc()
    ).all()
    
    return render_template('counseling/plan_detail.html',
                          plan=plan,
                          student=student,
                          interventions=interventions,
                          sessions=sessions)


@counseling_bp.route('/plans/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='create_plan', entity_type='support_plan')
def new_plan():
    """Create a new support plan."""
    if request.method == 'POST':
        data = request.form
        
        plan = SupportPlan(
            student_id=data.get('student_id', type=int),
            created_by=current_user.id,
            plan_type=data.get('plan_type', 'General'),
            title=data.get('title'),
            description=data.get('description'),
            goals=data.get('goals'),
            strategies=data.get('strategies'),
            resources_needed=data.get('resources_needed'),
            start_date=datetime.fromisoformat(data.get('start_date')),
            target_end_date=datetime.fromisoformat(data.get('target_end_date')) if data.get('target_end_date') else None,
            status=data.get('status', 'Draft'),
            review_frequency=data.get('review_frequency')
        )
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({'message': 'Support plan created successfully', 'plan_id': plan.id}), 201
    
    students = Student.query.order_by(Student.first_name, Student.last_name).all()
    return render_template('counseling/new_plan.html', students=students)


@counseling_bp.route('/plans/<int:plan_id>', methods=['PUT'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='update_plan', entity_type='support_plan')
def update_plan(plan_id):
    """Update a support plan."""
    plan = SupportPlan.query.get_or_404(plan_id)
    data = request.get_json()
    
    if data.get('plan_type'):
        plan.plan_type = data['plan_type']
    if data.get('title'):
        plan.title = data['title']
    if data.get('description'):
        plan.description = data['description']
    if data.get('goals'):
        plan.goals = data['goals']
    if data.get('strategies'):
        plan.strategies = data['strategies']
    if data.get('resources_needed'):
        plan.resources_needed = data['resources_needed']
    if data.get('status'):
        plan.status = data['status']
        if data['status'] == 'Completed':
            plan.actual_end_date = datetime.utcnow()
    if data.get('target_end_date'):
        plan.target_end_date = datetime.fromisoformat(data['target_end_date'])
    if data.get('review_frequency'):
        plan.review_frequency = data['review_frequency']
    
    plan.last_review_date = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Support plan updated successfully', 'plan': plan.to_dict()})


@counseling_bp.route('/interventions')
@login_required
@role_required('admin', 'teacher', 'counselor')
def interventions():
    """List all interventions."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    
    query = Intervention.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    query = query.order_by(Intervention.priority.desc(), Intervention.start_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('counseling/interventions.html',
                          interventions=pagination.items,
                          pagination=pagination,
                          status_filter=status_filter,
                          priority_filter=priority_filter)


@counseling_bp.route('/interventions/<int:intervention_id>')
@login_required
@role_required('admin', 'teacher', 'counselor')
def intervention_detail(intervention_id):
    """View intervention details."""
    intervention = Intervention.query.get_or_404(intervention_id)
    student = Student.query.get(intervention.student_id)
    
    return render_template('counseling/intervention_detail.html',
                          intervention=intervention,
                          student=student)


@counseling_bp.route('/interventions/new', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='create_intervention', entity_type='intervention')
def new_intervention():
    """Create a new intervention."""
    if request.method == 'POST':
        data = request.form
        
        intervention = Intervention(
            student_id=data.get('student_id', type=int),
            created_by=current_user.id,
            intervention_type=data.get('intervention_type', 'Other'),
            title=data.get('title'),
            description=data.get('description'),
            start_date=datetime.fromisoformat(data.get('start_date')),
            target_date=datetime.fromisoformat(data.get('target_date')) if data.get('target_date') else None,
            status=data.get('status', 'Planned'),
            priority=data.get('priority', 'Medium'),
            support_plan_id=data.get('support_plan_id', type=int) if data.get('support_plan_id') else None,
            counseling_session_id=data.get('counseling_session_id', type=int) if data.get('counseling_session_id') else None
        )
        
        db.session.add(intervention)
        db.session.commit()
        
        return jsonify({'message': 'Intervention created successfully', 'intervention_id': intervention.id}), 201
    
    students = Student.query.order_by(Student.first_name, Student.last_name).all()
    plans = SupportPlan.query.filter_by(status='Active').all()
    sessions = CounselingSession.query.filter_by(outcome='Ongoing').all()
    return render_template('counseling/new_intervention.html', 
                          students=students, plans=plans, sessions=sessions)


@counseling_bp.route('/interventions/<int:intervention_id>', methods=['PUT'])
@login_required
@role_required('admin', 'teacher', 'counselor')
@log_activity(action='update_intervention', entity_type='intervention')
def update_intervention(intervention_id):
    """Update an intervention."""
    intervention = Intervention.query.get_or_404(intervention_id)
    data = request.get_json()
    
    if data.get('intervention_type'):
        intervention.intervention_type = data['intervention_type']
    if data.get('title'):
        intervention.title = data['title']
    if data.get('description'):
        intervention.description = data['description']
    if data.get('status'):
        intervention.status = data['status']
        if data['status'] == 'Completed':
            intervention.completed_date = datetime.utcnow()
    if data.get('priority'):
        intervention.priority = data['priority']
    if data.get('target_date'):
        intervention.target_date = datetime.fromisoformat(data['target_date'])
    if data.get('outcome'):
        intervention.outcome = data['outcome']
    if data.get('notes'):
        intervention.notes = data['notes']
    
    db.session.commit()
    
    return jsonify({'message': 'Intervention updated successfully', 'intervention': intervention.to_dict()})


@counseling_bp.route('/student/<int:student_id>')
@login_required
@role_required('admin', 'teacher', 'counselor')
def student_support_history(student_id):
    """View all support activities for a student."""
    student = Student.query.get_or_404(student_id)
    
    sessions = CounselingSession.get_by_student(student_id)
    plans = SupportPlan.get_by_student(student_id)
    interventions = Intervention.get_by_student(student_id)
    
    latest_prediction = Prediction.get_latest_prediction(student_id)
    
    return render_template('counseling/student_support.html',
                          student=student,
                          sessions=sessions,
                          plans=plans,
                          interventions=interventions,
                          prediction=latest_prediction)


@counseling_bp.route('/api/stats')
@login_required
@role_required('admin', 'teacher', 'counselor')
def api_stats():
    """Get counseling statistics."""
    stats = {
        'active_cases': len(CounselingSession.get_active_cases()),
        'upcoming_sessions': len(CounselingSession.get_upcoming()),
        'overdue_followups': len(CounselingSession.get_overdue()),
        'active_interventions': len(Intervention.get_active()),
        'overdue_interventions': len(Intervention.get_overdue()),
        'sessions_this_month': CounselingSession.query.filter(
            CounselingSession.session_date >= datetime.utcnow().replace(day=1)
        ).count()
    }
    
    return jsonify(stats)