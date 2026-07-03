"""
Admin Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response
from flask_login import login_required, current_user, logout_user
from app import db
from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.subject import Subject
from app.models.marks import Marks
from app.models.fee import Fee
from app.models.library import LibraryBook, LibraryTransaction
from app.models.complaint import Complaint
from app.models.alert import Alert
from app.models.prediction import Prediction, MLModel
from app.models.activity_log import ActivityLog
from datetime import datetime, date
import csv
import functools
import io
from app.utils.decorators import teacher_required

admin_bp = Blueprint('admin', __name__)


# HTML Pages
@admin_bp.route('/')
@login_required
def index():
    """Admin home page."""
    return render_template('admin/users.html')


@admin_bp.route('/users')
@login_required
def users_page():
    """Users management page."""
    return render_template('admin/users.html')


@admin_bp.route('/students')
@login_required
def students_page():
    """Students management page."""
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    search = request.args.get('search')
    risk_level = request.args.get('risk_level')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    all_courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in all_courses if c[0]]
    
    query = Student.query
    if course:
        query = query.filter_by(course=course)
    if semester:
        query = query.filter_by(semester=semester)
    if search:
        query = query.filter(
            (Student.first_name.ilike(f'%{search}%')) | 
            (Student.last_name.ilike(f'%{search}%')) |
            (Student.student_id.ilike(f'%{search}%'))
        )
    
    if risk_level:
        subquery = db.session.query(
            Prediction.student_id,
            db.func.max(Prediction.prediction_date).label('max_date')
        ).group_by(Prediction.student_id).subquery()
        
        latest_pred = db.session.query(Prediction).join(
            subquery,
            (Prediction.student_id == subquery.c.student_id) & 
            (Prediction.prediction_date == subquery.c.max_date)
        ).filter(Prediction.risk_level == risk_level).subquery()
        
        query = query.join(latest_pred, Student.id == latest_pred.c.student_id)
    
    query = query.order_by(Student.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    
    return render_template('students/list.html', 
                       students=students, 
                       courses=courses, 
                       selected_course=course, 
                       selected_semester=semester,
                       pagination=pagination,
                       selected_risk_level=risk_level)


@admin_bp.route('/students/add')
@login_required
def add_student_page():
    """Add student page."""
    courses = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical Engineering', 
                'Civil Engineering', 'Electrical Engineering', 'Business Administration', 'Commerce',
                'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Arts', 'Law']
    return render_template('students/add.html', courses=courses)


@admin_bp.route('/students/<int:student_id>')
@teacher_required
def student_detail(student_id):
    """View student detail page."""
    from app.models.attendance import Attendance
    from app.models.marks import Marks
    from app.models.fee import Fee
    from app.models.library import LibraryTransaction
    from app.models.complaint import Complaint
    from app.models.prediction import Prediction
    
    student = Student.query.get_or_404(student_id)
    
    # Fetch related records
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(Attendance.date.desc()).limit(50).all()
    marks_records = Marks.query.filter_by(student_id=student.id).order_by(Marks.exam_date.desc()).limit(50).all()
    fee_records = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).all()
    library_transactions = LibraryTransaction.query.filter_by(student_id=student.id).order_by(LibraryTransaction.issue_date.desc()).limit(20).all()
    complaints = Complaint.query.filter_by(student_id=student.id).order_by(Complaint.created_at.desc()).limit(20).all()
    predictions = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).limit(10).all()
    
    # Calculate attendance percentage
    total_attendance = len(attendance_records)
    present_count = sum(1 for att in attendance_records if att.status == 'Present')
    attendance_percentage = round((present_count / total_attendance) * 100, 1) if total_attendance > 0 else 0
    
    # Get latest risk prediction
    latest_prediction = predictions[0] if predictions else None
    risk_score = int(float(latest_prediction.risk_score) * 100) if latest_prediction and latest_prediction.risk_score else 0
    risk_level = latest_prediction.risk_level if latest_prediction else 'Low'
    
    # Add calculated values to student object for template access
    student.attendance_percentage = attendance_percentage
    student.risk_score = risk_score
    student.risk_level = risk_level
    
    return render_template('students/view.html', 
        student=student,
        attendance_records=attendance_records,
        marks_records=marks_records,
        fee_records=fee_records,
        library_transactions=library_transactions,
        complaints=complaints,
        predictions=predictions)


@admin_bp.route('/alerts')
@login_required
def alerts_page():
    """Alerts management page."""
    # Get all students for the create alert dropdown
    students = Student.query.order_by(Student.full_name).all()
    return render_template('admin/alerts.html', students=students)


@admin_bp.route('/models')
@login_required
def models_page():
    """ML Models management page."""
    return render_template('admin/models.html')


# Marks Pages
@admin_bp.route('/marks')
@login_required
def marks_page():
    """Marks management page."""
    from app.models.subject import Subject
    from app.models.user import User
    subjects = Subject.query.all()
    # Join with User to filter active students
    students = db.session.query(Student).join(User, Student.user_id == User.id).filter(User.is_active == True).all()
    return render_template('marks/add.html', subjects=subjects, students=students)


@admin_bp.route('/marks/add', methods=['POST'])
@teacher_required
def submit_marks():
    """Add marks for a student via form."""
    data = request.form.to_dict()
    
    if not data:
        flash('No data provided', 'danger')
        return redirect(url_for('admin.marks_page'))
    
    try:
        exam_date = datetime.strptime(data.get('exam_date'), '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD', 'danger')
        return redirect(url_for('admin.marks_page'))
    
    try:
        marks = Marks(
            student_id=int(data.get('student_id')),
            subject_id=int(data.get('subject_id')),
            exam_type=data.get('exam_type'),
            marks_obtained=float(data.get('marks_obtained')),
            max_marks=float(data.get('max_marks', 100)),
            exam_date=exam_date,
            graded_by=current_user.id,
            remarks=data.get('remarks')
        )
        
        db.session.add(marks)
        db.session.commit()
        
        flash('Marks added successfully', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding marks: {str(e)}', 'danger')
    
    return redirect(url_for('admin.marks_page'))


@admin_bp.route('/marks/bulk')
@login_required
def marks_bulk_page():
    """Bulk marks page."""
    from app.models.subject import Subject
    subjects = Subject.query.all()
    return render_template('marks/bulk.html', subjects=subjects)


@admin_bp.route('/marks/report')
@login_required
def marks_report_page():
    """Marks report page."""
    return render_template('marks/report.html')


# Fee Pages
@admin_bp.route('/fees')
@login_required
def fees_page():
    """Fee management page."""
    return render_template('fees/list.html')


@admin_bp.route('/fees/add')
@login_required
def add_fee_page():
    """Add fee page."""
    students = Student.query.filter_by(is_active=True).all()
    return render_template('fees/add.html', students=students)


@admin_bp.route('/fees/payment')
@login_required
def fees_payment_page():
    """Payment page."""
    return render_template('fees/payment.html')


# Library Pages
@admin_bp.route('/library')
@login_required
def library_page():
    """Library management page."""
    from app.models.library import LibraryBook
    books = LibraryBook.query.all()
    return render_template('library/books.html', books=books)


@admin_bp.route('/library/books')
@login_required
def library_books_page():
    """Library books page."""
    return render_template('library/books.html')


@admin_bp.route('/library/add')
@login_required
def library_add_book_page():
    """Add book page."""
    return render_template('library/add_book.html')


@admin_bp.route('/library/issue')
@login_required
def library_issue_page():
    """Issue book page."""
    from app.models.library import LibraryBook
    students = Student.query.filter_by(is_active=True).all()
    available_books = LibraryBook.query.filter(LibraryBook.available_copies > 0).all()
    return render_template('library/issue.html', students=students, books=available_books)


@admin_bp.route('/library/transactions')
@login_required
def library_transactions_page():
    """Library transactions page."""
    return render_template('library/transactions.html')


# Complaint Pages
@admin_bp.route('/complaints')
@login_required
def complaints_page():
    """Complaints management page."""
    return render_template('complaints/list.html')


@admin_bp.route('/complaints/add')
@login_required
def add_complaint_page():
    """Add complaint page."""
    return render_template('complaints/add.html')


@admin_bp.route('/complaints/<int:complaint_id>')
@login_required
def complaints_view_page(complaint_id):
    """View complaint page."""
    return render_template('complaints/view.html')


@admin_bp.route('/reports')
@login_required
def reports_page():
    """Reports dashboard page."""
    return render_template('reports/academic.html')


# Report Pages
@admin_bp.route('/reports/attendance')
@login_required
def report_attendance_page():
    """Attendance report page."""
    return render_template('reports/attendance.html')


@admin_bp.route('/reports/academic')
@login_required
def report_academic_page():
    """Academic report page."""
    from app.models.subject import Subject
    from app.models.marks import Marks
    from app.models.student import Student
    
    # Get filter parameters from request args
    course = request.args.get('course', '') or ''
    semester = request.args.get('semester', type=int) or 0
    subject_id = request.args.get('subject_id', type=int) or 0
    exam_type = request.args.get('exam_type', '') or ''
    
    # Get all subjects for the dropdown (always show all, filter after course selection)
    subjects = Subject.query.order_by(Subject.course, Subject.semester, Subject.subject_name).all()
    
    # Get all distinct courses for the dropdown (from both Student and Subject tables)
    student_courses = db.session.query(Student.course).distinct().all()
    subject_courses = db.session.query(Subject.course).distinct().all()
    all_courses = set()
    for c in student_courses:
        if c[0]:
            all_courses.add(c[0])
    for c in subject_courses:
        if c[0]:
            all_courses.add(c[0])
    courses = sorted(list(all_courses))
    
    # Build query for academic data
    query = Marks.query.join(Student, Marks.student_id == Student.id).join(Subject, Marks.subject_id == Subject.id)
    
    if course:
        query = query.filter(Student.course == course)
    if semester and semester > 0:
        query = query.filter(Student.semester == semester)
    if subject_id and subject_id > 0:
        query = query.filter(Marks.subject_id == subject_id)
    if exam_type:
        query = query.filter(Marks.exam_type == exam_type)
    
    # Get marks records
    academic_data = query.all()
    
    # Calculate statistics
    total_records = len(academic_data)
    if total_records > 0:
        scores = [float(m.percentage) for m in academic_data if m.percentage is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        pass_count = len([s for s in scores if s >= 50])
        pass_rate = (pass_count / len(scores) * 100) if scores else 0
        at_risk = len([s for s in scores if s < 50])
        failing = len([s for s in scores if s < 35])  # Assuming <35 is failing
    else:
        avg_score = 0
        pass_rate = 0
        at_risk = 0
        failing = 0
    
    stats = {
        'avg_score': round(avg_score, 1),
        'pass_rate': round(pass_rate, 1),
        'at_risk': at_risk,
        'failing': failing
    }
    
    return render_template('reports/academic.html', 
                         subjects=subjects,
                         courses=courses,
                         academic_data=academic_data,
                         stats=stats,
                         selected_course=course,
                         selected_semester=semester,
                         selected_subject_id=subject_id,
                         exam_type=exam_type)


@admin_bp.route('/reports/financial')
@login_required
def report_financial_page():
    """Financial report page."""
    return render_template('reports/financial.html')


# Prediction Pages
@admin_bp.route('/predictions')
@login_required
def predictions_page():
    """Predictions dashboard page."""
    from app.models import Prediction, Student, MLModel
    
    # Get prediction stats for the dashboard
    total_predictions = Prediction.query.count()
    low_risk = Prediction.query.filter_by(risk_level='Low').count()
    medium_risk = Prediction.query.filter_by(risk_level='Medium').count()
    high_risk = Prediction.query.filter_by(risk_level='High').count()
    critical_risk = Prediction.query.filter_by(risk_level='Critical').count()
    
    # Get active ML model metrics
    active_model = MLModel.query.filter_by(is_active=True).first()
    if active_model:
        model_metrics = {
            'accuracy': round(active_model.accuracy * 100, 1) if active_model.accuracy else 0,
            'precision': round(active_model.precision_score * 100, 1) if active_model.precision_score else 0,
            'recall': round(active_model.recall_score * 100, 1) if active_model.recall_score else 0,
            'f1_score': round(active_model.f1_score * 100, 1) if active_model.f1_score else 0,
            'last_trained': active_model.training_date.strftime('%Y-%m-%d') if active_model.training_date else None,
            'model_name': active_model.model_name,
            'model_version': active_model.model_version
        }
    else:
        model_metrics = {
            'accuracy': 85,
            'precision': 83,
            'recall': 87,
            'f1_score': 85,
            'last_trained': None,
            'model_name': 'Student Risk Predictor',
            'model_version': '1.0.0'
        }
    
    stats = {
        'total': total_predictions,
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk,
        'critical_risk': critical_risk,
        'accuracy': model_metrics['accuracy']
    }
    
    # Get high-risk and critical students with details
    high_risk_students = []
    high_risk_predictions = Prediction.query.filter(
        Prediction.risk_level.in_(['High', 'Critical'])
    ).order_by(Prediction.risk_score.desc()).limit(20).all()
    for pred in high_risk_predictions:
        student = Student.query.get(pred.student_id)
        if student:
            high_risk_students.append({
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.full_name,
                'course': student.course or 'N/A',
                'semester': student.semester,
                'risk_score': round(pred.risk_score * 100, 1) if pred.risk_score else 0,
                'attendance': pred.attendance_percentage,
                'marks': pred.average_marks,
                'risk_level': pred.risk_level,
                'is_manual': pred.is_manual,
                'flag_for_review': pred.flag_for_review,
                'factors': 'Attendance, Grades, Fees'
            })
    
    # Get flagged students
    flagged_students = []
    flagged_predictions = Prediction.query.filter_by(flag_for_review=True).order_by(Prediction.risk_score.desc()).limit(10).all()
    for pred in flagged_predictions:
        student = Student.query.get(pred.student_id)
        if student:
            flagged_students.append({
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.full_name,
                'course': student.course or 'N/A',
                'risk_score': round(pred.risk_score * 100, 1) if pred.risk_score else 0,
                'review_note': pred.review_note
            })
    
    return render_template('predictions/dashboard.html', 
                         stats=stats, 
                         model=model_metrics,
                         high_risk_students=high_risk_students,
                         flagged_students=flagged_students)


@admin_bp.route('/predictions/student')
@login_required
def predictions_student_page():
    """Student prediction page."""
    selected_student = None
    prediction = None
    
    student_id = request.args.get('student_id', type=int)
    
    students = Student.query.order_by(Student.full_name).all()
    
    if student_id:
        selected_student = Student.query.get(student_id)
        if selected_student:
            pred = Prediction.get_latest_prediction(student_id)
            if pred:
                attendance = float(pred.attendance_percentage) if pred.attendance_percentage else 0
                marks = float(pred.average_marks) if pred.average_marks else 0
                fee = pred.fee_status or 'Paid'
                
                prediction = {
                    'risk_score': int(float(pred.risk_score) * 100),
                    'risk_level': pred.risk_level,
                    'prediction_date': pred.prediction_date,
                    'attendance_risk': 'High' if attendance < 60 else 'Medium' if attendance < 75 else 'Low',
                    'academic_risk': 'High' if marks < 50 else 'Medium' if marks < 65 else 'Low',
                    'fee_risk': 'High' if fee in ['Overdue', 'Unpaid'] else 'Medium' if fee == 'Partial' else 'Low',
                    'library_risk': 'Low'
                }
    
    return render_template('predictions/student.html', 
                          students=students,
                          selected_student=selected_student,
                          prediction=prediction)


# Logout
@admin_bp.route('/logout', methods=['GET'])
@login_required
def logout_page():
    """Logout page."""
    logout_user()
    return redirect(url_for('main.index'))


def admin_required(f):
    """Decorator to require admin role."""
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if request.is_json or 'api' in request.path:
            if not current_user.is_admin():
                return jsonify({'error': 'Admin access required'}), 403
        else:
            if not current_user.is_admin():
                flash('Admin access required', 'danger')
                return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_function


def teacher_required(f):
    """Decorator to require teacher or admin role."""
    @functools.wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if request.is_json or 'api' in request.path:
            if not current_user.is_admin() and not current_user.is_teacher():
                return jsonify({'error': 'Teacher or admin access required'}), 403
        else:
            if not current_user.is_admin() and not current_user.is_teacher():
                flash('Teacher or admin access required', 'danger')
                return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_function


# User Management
@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users."""
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


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get user by ID."""
    user = User.query.get_or_404(user_id)
    return jsonify({
        'user': user.to_dict()
    })


@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status."""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='toggle_user_active',
        entity_type='user',
        entity_id=user.id,
        details=f'User {user.username} {"activated" if user.is_active else "deactivated"}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
        'user': user.to_dict()
    })


# Student Management
@admin_bp.route('/students', methods=['GET'])
@teacher_required
def get_students():
    """Get all students."""
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    
    query = Student.query
    if course:
        query = query.filter_by(course=course)
    if semester:
        query = query.filter_by(semester=semester)
    
    students = query.order_by(Student.created_at.desc()).all()
    
    return jsonify({
        'students': [student.to_dict() for student in students]
    })


@admin_bp.route('/students/export')
@login_required
def export_students():
    """Export students data as CSV."""
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    
    query = Student.query
    if course:
        query = query.filter_by(course=course)
    if semester:
        query = query.filter_by(semester=semester)
    
    students = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Student ID', 'First Name', 'Last Name', 'Email', 'Course', 'Semester', 'Phone', 'Admission Date'])
    
    for s in students:
        writer.writerow([
            s.student_id,
            s.first_name,
            s.last_name,
            s.user.email if s.user else '',
            s.course,
            s.semester,
            s.phone or '',
            s.admission_date.isoformat() if s.admission_date else ''
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=students_export.csv'
    
    return response


@admin_bp.route('/students/<int:student_id>', methods=['GET'])
@teacher_required
def get_student(student_id):
    """Get student by ID."""
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'student': student.to_dict()
    })


@admin_bp.route('/students', methods=['POST'])
@admin_required
def create_student():
    """Create a new student."""
    if request.is_json:
        data = request.get_json()
        is_json = True
    else:
        data = request.form.to_dict()
        is_json = False
    
    if not data:
        if is_json:
            return jsonify({'error': 'No data provided'}), 400
        flash('No data provided', 'danger')
        return redirect(url_for('admin.add_student_page'))
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'student_id', 'first_name', 'last_name', 'course', 'semester']
    missing = [f for f in required_fields if not data.get(f)]
    if missing:
        if is_json:
            return jsonify({'error': f'Missing required fields: {", ".join(missing)}'}), 400
        flash(f'Missing required fields: {", ".join(missing)}', 'danger')
        return redirect(url_for('admin.add_student_page'))
    
    # Check if username or email already exists
    if User.query.filter_by(username=data.get('username')).first():
        if is_json:
            return jsonify({'error': 'Username already exists'}), 400
        flash('Username already exists', 'danger')
        return redirect(url_for('admin.add_student_page'))
    
    if User.query.filter_by(email=data.get('email')).first():
        if is_json:
            return jsonify({'error': 'Email already exists'}), 400
        flash('Email already exists', 'danger')
        return redirect(url_for('admin.add_student_page'))
    
    # Create user account
    try:
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            role='student'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create student profile
        try:
            date_of_birth = datetime.strptime(data.get('date_of_birth', ''), '%Y-%m-%d').date() if data.get('date_of_birth') else None
            admission_date = datetime.strptime(data.get('admission_date', ''), '%Y-%m-%d').date() if data.get('admission_date') else date.today()
        except ValueError:
            if is_json:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            flash('Invalid date format. Use YYYY-MM-DD', 'danger')
            return redirect(url_for('admin.add_student_page'))
        
        student = Student(
            user_id=user.id,
            student_id=data.get('student_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            date_of_birth=date_of_birth,
            gender=data.get('gender'),
            course=data.get('course'),
            semester=int(data.get('semester', 1)) if data.get('semester') else 1,
            admission_date=admission_date,
            phone=data.get('phone'),
            address=data.get('address'),
            guardian_name=data.get('guardian_name'),
            guardian_phone=data.get('guardian_phone')
        )
        db.session.add(student)
        db.session.commit()
        
        # Log activity
        ActivityLog.log_activity(
            user_id=current_user.id,
            action='create_student',
            entity_type='student',
            entity_id=student.id,
            details=f'Created student: {student.full_name}',
            ip_address=request.remote_addr
        )
        
        if is_json:
            return jsonify({
                'message': 'Student created successfully',
                'student': student.to_dict()
            }), 201
        else:
            flash('Student created successfully', 'success')
            return redirect(url_for('admin.students_page'))
            
    except Exception as e:
        db.session.rollback()
        if is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Error creating student: {str(e)}', 'danger')
        return redirect(url_for('admin.add_student_page'))


# Attendance Pages
@admin_bp.route('/attendance')
@login_required
def attendance_page():
    """Attendance management page."""
    students = Student.query.all()
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    return render_template('attendance/mark.html', courses=courses, students=students)


@admin_bp.route('/attendance/bulk')
@login_required
def attendance_bulk_page():
    """Bulk attendance page."""
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    return render_template('attendance/bulk.html', courses=courses)


@admin_bp.route('/attendance/report')
@login_required
def attendance_report_page():
    """Attendance report page."""
    return render_template('attendance/report.html')


@admin_bp.route('/attendance/by-class')
@login_required
def attendance_by_class_page():
    """Mark attendance by class (course/semester)."""
    courses = db.session.query(Student.course).distinct().all()
    courses = [c[0] for c in courses if c[0]]
    return render_template('attendance/mark_class.html', courses=courses)


@admin_bp.route('/attendance', methods=['POST'])
@login_required
def mark_attendance():
    """Mark attendance for a student."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    student_id = data.get('student_id')
    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400
    
    try:
        student_id = int(student_id)
    except ValueError:
        return jsonify({'error': 'Invalid student ID'}), 400
    
    try:
        attendance_date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    status = data.get('status')
    remarks = data.get('remarks') or ''
    
    try:
        existing = Attendance.query.filter_by(
            student_id=student_id,
            date=attendance_date
        ).first()
        
        if existing:
            existing.status = status
            existing.remarks = remarks
            existing.marked_by = current_user.id
        else:
            attendance = Attendance(
                student_id=student_id,
                date=attendance_date,
                status=status,
                marked_by=current_user.id,
                remarks=remarks
            )
            db.session.add(attendance)
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='mark_attendance',
        entity_type='attendance',
        entity_id=student_id,
        details=f'Marked attendance for student {student_id}: {status}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Attendance marked successfully'
    })


@admin_bp.route('/attendance/bulk', methods=['POST'])
@teacher_required
def bulk_mark_attendance():
    """Mark attendance for multiple students (by class)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    course = data.get('course')
    semester = data.get('semester')
    date_str = data.get('date')
    attendance_data = data.get('attendance', [])
    
    if not all([course, semester, date_str]):
        return jsonify({'error': 'Course, semester, and date are required'}), 400
    
    try:
        attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Get all students in the class
    students = Student.query.filter_by(course=course, semester=semester).all()
    
    marked_count = 0
    for student in students:
        status = attendance_data.get(str(student.id), 'Absent')
        remarks = attendance_data.get(f'remarks_{student.id}', '')
        
        # Check if attendance already exists
        existing = Attendance.query.filter_by(
            student_id=student.id,
            date=attendance_date
        ).first()
        
        if existing:
            existing.status = status
            existing.remarks = remarks
            existing.marked_by = current_user.id
        else:
            attendance = Attendance(
                student_id=student.id,
                date=attendance_date,
                status=status,
                marked_by=current_user.id,
                remarks=remarks
            )
            db.session.add(attendance)
        
        marked_count += 1
    
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='bulk_mark_attendance',
        entity_type='attendance',
        entity_id=0,
        details=f'Bulk marked attendance for {marked_count} students in {course} Sem {semester}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': f'Attendance marked for {marked_count} students',
        'marked': marked_count
    })


@admin_bp.route('/attendance/students')
@login_required
def get_class_students():
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    
    if not course or not semester:
        return jsonify({'error': 'Course and semester required'}), 400
    
    students = Student.query.filter_by(course=course, semester=semester).all()
    
    return jsonify({
        'students': [{
            'id': s.id,
            'student_id': s.student_id,
            'name': s.full_name
        } for s in students]
    })


# Marks Management
@admin_bp.route('/marks', methods=['POST'])
@teacher_required
def add_marks():
    """Add marks for a student."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        exam_date = datetime.strptime(data.get('exam_date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    marks = Marks(
        student_id=data.get('student_id'),
        subject_id=data.get('subject_id'),
        exam_type=data.get('exam_type'),
        marks_obtained=data.get('marks_obtained'),
        max_marks=data.get('max_marks'),
        exam_date=exam_date,
        graded_by=current_user.id,
        remarks=data.get('remarks')
    )
    
    db.session.add(marks)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='add_marks',
        entity_type='marks',
        entity_id=marks.id,
        details=f'Added marks for student {marks.student_id}: {marks.marks_obtained}/{marks.max_marks}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Marks added successfully',
        'marks': marks.to_dict()
    }), 201


# Fee Management
@admin_bp.route('/fees', methods=['POST'])
@admin_required
def add_fee():
    """Add fee for a student."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    fee = Fee(
        student_id=data.get('student_id'),
        fee_type=data.get('fee_type'),
        amount=data.get('amount'),
        due_date=due_date,
        status=data.get('status', 'Pending')
    )
    
    db.session.add(fee)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='add_fee',
        entity_type='fee',
        entity_id=fee.id,
        details=f'Added fee for student {fee.student_id}: {fee.amount}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Fee added successfully',
        'fee': fee.to_dict()
    }), 201


@admin_bp.route('/fees/<int:fee_id>/pay', methods=['POST'])
@admin_required
def pay_fee(fee_id):
    """Mark fee as paid."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    fee = Fee.query.get_or_404(fee_id)
    fee.mark_as_paid(
        payment_method=data.get('payment_method'),
        transaction_id=data.get('transaction_id'),
        receipt_number=data.get('receipt_number')
    )
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='pay_fee',
        entity_type='fee',
        entity_id=fee.id,
        details=f'Marked fee {fee.id} as paid',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Fee marked as paid',
        'fee': fee.to_dict()
    })


# Library Management
@admin_bp.route('/library/books', methods=['GET'])
@login_required
def get_books():
    """Get all library books."""
    category = request.args.get('category')
    search = request.args.get('search')
    
    if search:
        books = LibraryBook.search_books(search)
    elif category:
        books = LibraryBook.get_books_by_category(category)
    else:
        books = LibraryBook.query.all()
    
    return jsonify({
        'books': [book.to_dict() for book in books]
    })


@admin_bp.route('/library/books', methods=['POST'])
@admin_required
def add_book():
    """Add a new library book."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    book = LibraryBook(
        book_id=data.get('book_id'),
        title=data.get('title'),
        author=data.get('author'),
        isbn=data.get('isbn'),
        category=data.get('category'),
        total_copies=data.get('total_copies', 1),
        available_copies=data.get('available_copies')
    )
    
    db.session.add(book)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='add_book',
        entity_type='library_book',
        entity_id=book.id,
        details=f'Added book: {book.title}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Book added successfully',
        'book': book.to_dict()
    }), 201


@admin_bp.route('/library/issue', methods=['POST'])
@teacher_required
def issue_book():
    """Issue a book to a student."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    student_id = data.get('student_id')
    book_id = data.get('book_id')
    try:
        due_date = datetime.strptime(data.get('due_date'), '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    book = LibraryBook.query.get_or_404(book_id)
    
    if not book.is_available:
        return jsonify({'error': 'Book not available for issue'}), 400
    
    transaction = LibraryTransaction(
        student_id=student_id,
        book_id=book_id,
        issue_date=date.today(),
        due_date=due_date,
        issued_by=current_user.id
    )
    
    book.issue_book()
    db.session.add(transaction)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='issue_book',
        entity_type='library_transaction',
        entity_id=transaction.id,
        details=f'Issued book {book.title} to student {student_id}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Book issued successfully',
        'transaction': transaction.to_dict()
    }), 201


@admin_bp.route('/library/return/<int:transaction_id>', methods=['POST'])
@teacher_required
def return_book(transaction_id):
    """Return a book."""
    transaction = LibraryTransaction.query.get_or_404(transaction_id)
    transaction.return_book(current_user.id)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='return_book',
        entity_type='library_transaction',
        entity_id=transaction.id,
        details=f'Returned book {transaction.book.title} from student {transaction.student_id}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Book returned successfully',
        'transaction': transaction.to_dict()
    })


# Complaint Management
@admin_bp.route('/complaints', methods=['GET'])
@teacher_required
def get_complaints():
    """Get all complaints."""
    status = request.args.get('status')
    category = request.args.get('category')
    priority = request.args.get('priority')
    
    query = Complaint.query
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    if priority:
        query = query.filter_by(priority=priority)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    
    return jsonify({
        'complaints': [complaint.to_dict() for complaint in complaints]
    })


@admin_bp.route('/complaints/<int:complaint_id>/assign', methods=['POST'])
@admin_required
def assign_complaint(complaint_id):
    """Assign complaint to a user."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.assign(data.get('assigned_to'))
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='assign_complaint',
        entity_type='complaint',
        entity_id=complaint.id,
        details=f'Assigned complaint {complaint.id} to user {complaint.assigned_to}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Complaint assigned successfully',
        'complaint': complaint.to_dict()
    })


@admin_bp.route('/complaints/<int:complaint_id>/resolve', methods=['POST'])
@teacher_required
def resolve_complaint(complaint_id):
    """Resolve a complaint."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    complaint = Complaint.query.get_or_404(complaint_id)
    complaint.resolve(data.get('resolution'))
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='resolve_complaint',
        entity_type='complaint',
        entity_id=complaint.id,
        details=f'Resolved complaint {complaint.id}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Complaint resolved successfully',
        'complaint': complaint.to_dict()
    })


# Alert Management
@admin_bp.route('/alerts', methods=['GET'])
@teacher_required
def get_alerts():
    """Get all alerts."""
    student_id = request.args.get('student_id', type=int)
    alert_type = request.args.get('alert_type')
    severity = request.args.get('severity')
    is_read = request.args.get('is_read', type=bool)
    
    query = Alert.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)
    if severity:
        query = query.filter_by(severity=severity)
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts]
    })


@admin_bp.route('/alerts', methods=['POST'])
@teacher_required
def create_alert():
    """Create a new alert."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    alert = Alert(
        student_id=data.get('student_id'),
        alert_type=data.get('alert_type'),
        severity=data.get('severity', 'Info'),
        message=data.get('message'),
        suggestion=data.get('suggestion')
    )
    
    db.session.add(alert)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='create_alert',
        entity_type='alert',
        entity_id=alert.id,
        details=f'Created alert for student {alert.student_id}: {alert.alert_type}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Alert created successfully',
        'alert': alert.to_dict()
    }), 201


# Prediction Management
@admin_bp.route('/predictions', methods=['GET'])
@teacher_required
def get_predictions():
    """Get all predictions."""
    student_id = request.args.get('student_id', type=int)
    risk_level = request.args.get('risk_level')
    
    query = Prediction.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if risk_level:
        query = query.filter_by(risk_level=risk_level)
    
    predictions = query.order_by(Prediction.prediction_date.desc()).all()
    
    return jsonify({
        'predictions': [prediction.to_dict() for prediction in predictions]
    })


@admin_bp.route('/predictions/high-risk', methods=['GET'])
@teacher_required
def get_high_risk_students():
    """Get all high-risk students."""
    predictions = Prediction.get_high_risk_students()
    
    return jsonify({
        'high_risk_students': [prediction.to_dict() for prediction in predictions]
    })


# ML Model Management
@admin_bp.route('/ml-models', methods=['GET'])
@admin_required
def get_ml_models():
    """Get all ML models."""
    models = MLModel.query.order_by(MLModel.training_date.desc()).all()
    
    return jsonify({
        'models': [model.to_dict() for model in models]
    })


@admin_bp.route('/ml-models/active', methods=['GET'])
@admin_required
def get_active_model():
    """Get active ML model."""
    model = MLModel.get_active_model()
    
    return jsonify({
        'model': model.to_dict() if model else None
    })


@admin_bp.route('/ml-models/<int:model_id>/activate', methods=['POST'])
@admin_required
def activate_model(model_id):
    """Activate an ML model."""
    model = MLModel.query.get_or_404(model_id)
    model.activate()
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='activate_model',
        entity_type='ml_model',
        entity_id=model.id,
        details=f'Activated model: {model.model_name} v{model.model_version}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Model activated successfully',
        'model': model.to_dict()
    })


# Dashboard Statistics
@admin_bp.route('/dashboard/stats', methods=['GET'])
@teacher_required
def get_dashboard_stats():
    """Get dashboard statistics."""
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
@admin_bp.route('/activity-logs', methods=['GET'])
@admin_required
def get_activity_logs():
    """Get activity logs."""
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
    
    return jsonify({
        'logs': [log.to_dict() for log in logs]
    })


@admin_bp.route('/reports/academic/export/pdf')
@login_required
def export_academic_pdf():
    """Export academic report as PDF (CSV format)."""
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    subject_id = request.args.get('subject_id', type=int)
    exam_type = request.args.get('exam_type')
    
    query = Marks.query.join(Student).join(Subject)
    
    if course:
        query = query.filter(Student.course == course)
    if semester:
        query = query.filter(Student.semester == semester)
    if subject_id:
        query = query.filter(Marks.subject_id == subject_id)
    if exam_type:
        query = query.filter(Marks.exam_type == exam_type)
    
    marks_records = query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Student ID', 'Name', 'Course', 'Subject', 'Marks', 'Percentage', 'Status'])
    
    for m in marks_records:
        student = Student.query.get(m.student_id)
        subject = Subject.query.get(m.subject_id)
        percentage = m.percentage
        if percentage >= 75:
            status = 'Excellent'
        elif percentage >= 50:
            status = 'Average'
        else:
            status = 'Needs Improvement'
        
        writer.writerow([
            student.student_id if student else '',
            f"{student.first_name} {student.last_name}" if student else '',
            student.course if student else '',
            subject.subject_name if subject else '',
            f"{m.marks_obtained}/{m.max_marks}",
            f"{percentage}%",
            status
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=academic_report.csv'
    
    return response


@admin_bp.route('/reports/academic/export/excel')
@login_required
def export_academic_excel():
    """Export academic report as Excel (CSV format)."""
    return export_academic_pdf()


@admin_bp.route('/reports/attendance/export/pdf')
@login_required
def export_attendance_pdf():
    """Export attendance report as PDF (CSV format)."""
    course = request.args.get('course')
    semester = request.args.get('semester', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Student.query
    
    if course:
        query = query.filter(Student.course == course)
    if semester:
        query = query.filter(Student.semester == semester)
    
    students = query.all()
    
    start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
    end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['Student ID', 'Name', 'Course', 'Total Days', 'Present', 'Absent', 'Attendance %', 'Status'])
    
    for student in students:
        if start or end:
            summary = Attendance.get_attendance_summary(student.id, start, end)
        else:
            summary = Attendance.get_attendance_summary(student.id)
        
        total_days = summary['total_days']
        present = summary['present']
        absent = summary['absent']
        percentage = summary['percentage']
        
        if percentage >= 75:
            status = 'Good'
        elif percentage >= 50:
            status = 'Warning'
        else:
            status = 'Critical'
        
        writer.writerow([
            student.student_id,
            f"{student.first_name} {student.last_name}",
            student.course,
            total_days,
            present,
            absent,
            f"{percentage}%",
            status
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=attendance_report.csv'
    
    return response


@admin_bp.route('/reports/attendance/export/excel')
@login_required
def export_attendance_excel():
    """Export attendance report as Excel (CSV format)."""
    return export_attendance_pdf()
