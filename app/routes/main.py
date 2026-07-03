"""
Main Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page endpoint."""
    from app.models import Student, Alert, Prediction, MLModel
    from app import db
    
    stats = {
        'students_monitored': Student.query.count(),
        'prediction_accuracy': MLModel.query.filter_by(is_active=True).first().accuracy * 100 if MLModel.query.filter_by(is_active=True).first() else 0,
        'early_interventions': Alert.query.filter_by(is_read=False).count(),
        'dropout_reduction': Student.query.count() * 0.3  # Proxy metric
    }
    
    return render_template('index.html', stats=stats)


@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'A.U.R.A - Academic Understanding and Retention Application'
    })


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard endpoint."""
    from app.models import Student, Attendance, Marks, Fee, Alert, Complaint, Prediction
    from app import db
    
    role = current_user.role
    
    if role == 'admin':
        from sqlalchemy import func
        
        total_students = Student.query.count()
        active_alerts = Alert.query.filter_by(is_read=False).count()
        open_complaints = Complaint.query.filter_by(status='Open').count()
        high_risk = Prediction.query.filter_by(risk_level='High').count()
        total_pending_fees = Fee.query.filter_by(status='Pending').count()
        
        # Calculate risk distribution
        low_risk = Prediction.query.filter_by(risk_level='Low').count()
        medium_risk = Prediction.query.filter_by(risk_level='Medium').count()
        risk_distribution = {
            'low': low_risk,
            'medium': medium_risk,
            'high': high_risk
        }
        
        # Calculate average attendance
        from app.models.attendance import Attendance
        total_attendance = Attendance.query.count()
        present_attendance = Attendance.query.filter_by(status='Present').count()
        avg_attendance = 0
        if total_attendance > 0:
            avg_attendance = round((present_attendance / total_attendance) * 100, 1)
        
        # Get attendance data for charts (use available data or defaults)
        from app.models.attendance import Attendance
        all_attendance = Attendance.query.all()
        if all_attendance:
            present = sum(1 for a in all_attendance if a.status == 'Present')
            total = len(all_attendance)
            avg_attendance = round((present / total) * 100, 1) if total > 0 else 0
            
            # Get unique dates for chart
            dates = sorted(set([a.date for a in all_attendance]))
            attendance_labels = [d.strftime('%b %d') for d in dates[-6:]]
            
            # Calculate attendance per date
            attendance_data = []
            for d in dates[-6:]:
                day_att = Attendance.query.filter_by(date=d).all()
                if day_att:
                    p = sum(1 for a in day_att if a.status == 'Present')
                    attendance_data.append(round((p / len(day_att)) * 100, 1))
                else:
                    attendance_data.append(0)
        else:
            avg_attendance = 0
            attendance_labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6']
            attendance_data = [85, 82, 88, 85, 90, 87]
        
        # Calculate average marks
        from app.models.marks import Marks
        marks_stats = db.session.query(
            func.avg(Marks.marks_obtained * 100.0 / Marks.max_marks).label('avg')
        ).first()
        avg_marks = round(marks_stats.avg, 1) if marks_stats and marks_stats.avg else 0
        
        # Fee status distribution
        fee_paid = Fee.query.filter_by(status='Paid').count()
        fee_pending = Fee.query.filter_by(status='Pending').count()
        fee_overdue = Fee.query.filter_by(status='Overdue').count()
        fee_status = {
            'paid': fee_paid,
            'pending': fee_pending,
            'overdue': fee_overdue
        }
        
        # Get high risk students with details
        high_risk_students_data = []
        high_risk_preds = Prediction.query.filter_by(risk_level='High').limit(10).all()
        for pred in high_risk_preds:
            student = Student.query.get(pred.student_id)
            if student:
                attendance_pct = float(pred.attendance_percentage) if pred.attendance_percentage else 0
                high_risk_students_data.append({
                    'id': student.id,
                    'student_id': student.student_id,
                    'full_name': student.full_name,
                    'course': student.course,
                    'semester': student.semester,
                    'risk_score': int(float(pred.risk_score) * 100) if pred.risk_score else 0,
                    'attendance_percentage': int(attendance_pct)
                })
        
        # Recent activities
        recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
        recent_alerts_query = Alert.query.order_by(Alert.created_at.desc()).limit(5).all()
        
        # Build alert list with student name as dictionary
        recent_alerts = []
        for alert in recent_alerts_query:
            student = Student.query.get(alert.student_id)
            recent_alerts.append({
                'id': alert.id,
                'student_id': alert.student_id,
                'student_name': student.full_name if student else f'Student #{alert.student_id}',
                'alert_type': alert.alert_type,
                'severity': alert.severity,
                'message': alert.message,
                'created_at': alert.created_at
            })
        
        stats = {
            'total_students': total_students,
            'high_risk_students': high_risk,
            'avg_attendance': avg_attendance,
            'avg_marks': avg_marks,
            'total_pending_fees': total_pending_fees,
            'pending_fees': total_pending_fees,
            'active_alerts': active_alerts,
            'open_complaints': open_complaints
        }
        
        return render_template('dashboard/admin_dashboard.html',
            stats=stats,
            alerts=recent_alerts,
            recent_students=recent_students,
            recent_alerts=recent_alerts,
            total_students=total_students,
            active_alerts=active_alerts,
            open_complaints=open_complaints,
            high_risk=high_risk,
            total_fees=total_pending_fees,
            risk_distribution=risk_distribution,
            attendance_labels=attendance_labels,
            attendance_data=attendance_data,
            fee_status=fee_status,
            high_risk_students=high_risk_students_data)
    
    elif role == 'teacher':
        from sqlalchemy import func
        
        # Get all students
        total_students = Student.query.count()
        
        # Get high risk students
        high_risk = Prediction.query.filter_by(risk_level='High').count()
        
        # Get active alerts
        active_alerts = Alert.query.filter_by(is_read=False).count()
        
        # Get open complaints
        open_complaints = Complaint.query.filter_by(status='Open').count()
        
        # Get pending fees
        pending_fees = Fee.query.filter_by(status='Pending').count()
        
        # Get recent students
        recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()
        
        # Get high risk student list
        high_risk_students = []
        high_risk_preds = Prediction.query.filter_by(risk_level='High').limit(10).all()
        for pred in high_risk_preds:
            student = Student.query.get(pred.student_id)
            if student:
                high_risk_students.append({
                    'name': student.full_name,
                    'student_id': student.student_id,
                    'course': student.course,
                    'risk_score': int(float(pred.risk_score) * 100) if pred.risk_score else 0
                })
        
        stats = {
            'total_students': total_students,
            'high_risk': high_risk,
            'active_alerts': active_alerts,
            'open_complaints': open_complaints,
            'pending_fees': pending_fees
        }
        
        return render_template('dashboard/teacher_dashboard.html',
            stats=stats,
            recent_students=recent_students,
            high_risk_students=high_risk_students)
    
    elif role == 'student':
        student = Student.query.filter_by(user_id=current_user.id).first()
        fees_list = []
        attendance_list = []
        marks_list = []
        alerts_list = []
        risk_level = 'Low'
        risk_score = 0
        
        if student:
            fees_list = Fee.query.filter_by(student_id=student.id).all()
            attendance_list = Attendance.query.filter_by(student_id=student.id).all()
            marks_list = Marks.query.filter_by(student_id=student.id).all()
            alerts_list = Alert.query.filter_by(student_id=student.id, is_read=False).all()
            pred = Prediction.query.filter_by(student_id=student.id).order_by(Prediction.prediction_date.desc()).first()
            if pred:
                risk_level = pred.risk_level
                risk_score = int(float(pred.risk_score) * 100) if pred.risk_score else 0
            
            # Calculate attendance stats
            total_classes = len(attendance_list)
            present_count = sum(1 for att in attendance_list if att.status == 'Present')
            absent_count = sum(1 for att in attendance_list if att.status == 'Absent')
            attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
            
            # Calculate marks stats (average)
            if marks_list:
                total_marks = sum((mark.marks_obtained / mark.max_marks * 100) for mark in marks_list)
                average_marks_percentage = total_marks / len(marks_list)
            else:
                average_marks_percentage = 0
            
            # Calculate fee totals
            total_paid = sum(fee.amount for fee in fees_list if fee.status == 'Paid')
            total_pending = sum(fee.amount for fee in fees_list if fee.status == 'Pending')
        else:
            total_classes = 0
            present_count = 0
            absent_count = 0
            attendance_percentage = 0
            average_marks_percentage = 0
            total_paid = 0
            total_pending = 0
        
        return render_template('dashboard/student_dashboard.html',
            student=student,
            fees=fees_list,
            attendance={
                'percentage': attendance_percentage,
                'present': present_count,
                'absent': absent_count
            },
            recent_marks=marks_list[:10] if marks_list else [],
            alerts=alerts_list,
            risk_level=risk_level,
            risk_score=risk_score,
            total_paid=total_paid,
            total_pending=total_pending,
            total_classes=total_classes,
            present_count=present_count,
            absent_count=absent_count,
            attendance_percentage=attendance_percentage,
            average_marks_percentage=average_marks_percentage)
    
    else:
        return render_template('dashboard/admin_dashboard.html')
