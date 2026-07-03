"""
Student Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.marks import Marks
from app.models.fee import Fee
from app.models.library import LibraryTransaction
from app.models.complaint import Complaint
from app.models.alert import Alert
from app.models.prediction import Prediction
from app.models.activity_log import ActivityLog

student_bp = Blueprint('student', __name__)


# HTML Pages
@student_bp.route('/')
def index():
    """Student home page."""
    return render_template('students/list.html')


@student_bp.route('/list')
@login_required
def list_page():
    """Students list page."""
    return render_template('students/list.html')


@student_bp.route('/add')
@login_required
def add_page():
    """Add student page."""
    return render_template('students/add.html')


@student_bp.route('/<int:student_id>')
@login_required
def view_page(student_id):
    """View student page."""
    return render_template('students/view.html')


@student_bp.route('/<int:student_id>/edit')
@login_required
def edit_page(student_id):
    """Edit student page."""
    return render_template('students/edit.html')


@student_bp.route('/my/profile')
@login_required
def profile_page():
    """Student's own profile page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    return render_template('students/view.html', student=student)


@student_bp.route('/my/attendance')
@login_required
def attendance_page():
    """Student's own attendance page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(
        Attendance.date.desc()
    ).all()
    summary = Attendance.get_attendance_summary(student.id)
    return render_template('attendance/report.html', student=student, attendance=attendance_records, summary=summary)


@student_bp.route('/marks')
@login_required
def marks_page():
    """Student's own marks page - View All."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    
    marks_records = Marks.get_marks_by_student(student.id)
    
    # Calculate stats for template
    if marks_records:
        percentages = [mark.percentage for mark in marks_records]
        average_marks = sum(percentages) / len(percentages)
        passing_rate = (sum(1 for p in percentages if p >= 40) / len(percentages)) * 100
        failing_count = sum(1 for p in percentages if p < 40)
        best_score = max(percentages)
    else:
        average_marks = 0
        passing_rate = 0
        failing_count = 0
        best_score = 0
    
    return render_template('marks/my_marks.html', 
                         student=student, 
                         marks=marks_records, 
                         average_marks=average_marks,
                         passing_rate=passing_rate,
                         failing_count=failing_count,
                         best_score=best_score)


@student_bp.route('/my/fees')
@login_required
def fees_page():
    """Student's own fees page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    fee_records = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).all()
    pending_amount = student.get_pending_fees()
    return render_template('fees/list.html', student=student, fees=fee_records, pending_amount=pending_amount)


@student_bp.route('/my/library')
@login_required
def library_page():
    """Student's own library transactions page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    transactions = LibraryTransaction.get_transaction_history(student.id)
    overdue_books = student.get_overdue_books()
    return render_template('library/transactions.html', student=student, transactions=transactions, overdue_books=overdue_books)


@student_bp.route('/my/complaints')
@login_required
def complaints_page():
    """Student's own complaints page."""
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return render_template('students/no_profile.html')
    complaints = Complaint.get_complaints_by_student(student.id)
    return render_template('complaints/list.html', student=student, complaints=complaints)


# API Endpoints
@student_bp.route('/profile', methods=['GET'])
@login_required
def get_student_profile():
    """Get student profile."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    return jsonify({
        'student': student.to_dict()
    })


@student_bp.route('/attendance', methods=['GET'])
@login_required
def get_attendance():
    """Get student attendance records."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date and end_date:
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date()
        attendance_records = Attendance.get_attendance_by_date_range(student.id, start, end)
    else:
        attendance_records = Attendance.query.filter_by(student_id=student.id).order_by(
            Attendance.date.desc()
        ).all()
    
    return jsonify({
        'attendance': [record.to_dict() for record in attendance_records],
        'summary': Attendance.get_attendance_summary(student.id)
    })


@student_bp.route('/marks', methods=['GET'])
@login_required
def get_marks():
    """Get student marks."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    # Get query parameters
    subject_id = request.args.get('subject_id', type=int)
    exam_type = request.args.get('exam_type')
    
    marks_records = Marks.get_marks_by_student(student.id, subject_id, exam_type)
    
    return jsonify({
        'marks': [record.to_dict() for record in marks_records],
        'average_marks': student.calculate_average_marks()
    })


@student_bp.route('/fees', methods=['GET'])
@login_required
def get_fees():
    """Get student fee records."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    fee_records = Fee.query.filter_by(student_id=student.id).order_by(Fee.due_date.desc()).all()
    
    return jsonify({
        'fees': [record.to_dict() for record in fee_records],
        'pending_amount': student.get_pending_fees()
    })


@student_bp.route('/library', methods=['GET'])
@login_required
def get_library_transactions():
    """Get student library transactions."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    transactions = LibraryTransaction.get_transaction_history(student.id)
    
    return jsonify({
        'transactions': [record.to_dict() for record in transactions],
        'overdue_books': student.get_overdue_books()
    })


@student_bp.route('/complaints', methods=['GET'])
@login_required
def get_complaints():
    """Get student complaints."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    status = request.args.get('status')
    complaints = Complaint.get_complaints_by_student(student.id, status)
    
    return jsonify({
        'complaints': [record.to_dict() for record in complaints]
    })


@student_bp.route('/complaints', methods=['POST'])
@login_required
def create_complaint():
    """Create a new complaint."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    subject = data.get('subject')
    description = data.get('description')
    category = data.get('category')
    priority = data.get('priority', 'Medium')
    
    if not subject or not description or not category:
        return jsonify({'error': 'Subject, description, and category are required'}), 400
    
    complaint = Complaint(
        student_id=student.id,
        subject=subject,
        description=description,
        category=category,
        priority=priority
    )
    
    db.session.add(complaint)
    db.session.commit()
    
    # Log activity
    ActivityLog.log_activity(
        user_id=current_user.id,
        action='create_complaint',
        entity_type='complaint',
        entity_id=complaint.id,
        details=f'Created complaint: {subject}',
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'message': 'Complaint created successfully',
        'complaint': complaint.to_dict()
    }), 201


@student_bp.route('/alerts', methods=['GET'])
@login_required
def get_alerts():
    """Get student alerts."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    is_read = request.args.get('is_read', type=bool)
    alerts = Alert.get_alerts_by_student(student.id, is_read)
    
    return jsonify({
        'alerts': [record.to_dict() for record in alerts],
        'unread_count': Alert.get_alert_count(student.id, is_read=False)
    })


@student_bp.route('/alerts/<int:alert_id>/read', methods=['POST'])
@login_required
def mark_alert_as_read(alert_id):
    """Mark alert as read."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    alert = Alert.query.filter_by(id=alert_id, student_id=student.id).first()
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.mark_as_read()
    db.session.commit()
    
    return jsonify({'message': 'Alert marked as read'})


@student_bp.route('/predictions', methods=['GET'])
@login_required
def get_predictions():
    """Get student predictions."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    limit = request.args.get('limit', type=int)
    predictions = Prediction.get_predictions_by_student(student.id, limit)
    
    return jsonify({
        'predictions': [record.to_dict() for record in predictions],
        'latest_prediction': Prediction.get_latest_prediction(student.id).to_dict() if Prediction.get_latest_prediction(student.id) else None
    })


@student_bp.route('/risk-assessment', methods=['GET'])
@login_required
def get_risk_assessment():
    """Get student risk assessment."""
    if not current_user.is_student():
        return jsonify({'error': 'Access denied'}), 403
    
    student = Student.query.filter_by(user_id=current_user.id).first()
    if not student:
        return jsonify({'error': 'Student profile not found'}), 404
    
    return jsonify({
        'risk_score': student.calculate_risk_score(),
        'risk_level': student.get_risk_level(),
        'attendance_percentage': student.calculate_attendance_percentage(),
        'average_marks': student.calculate_average_marks(),
        'pending_fees': student.get_pending_fees(),
        'overdue_books': student.get_overdue_books()
    })

