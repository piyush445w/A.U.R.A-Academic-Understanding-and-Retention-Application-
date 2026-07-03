"""
Helper Functions for Intelligent Student Risk Monitoring & Decision Support System
"""

import csv
import io
import os
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from flask import current_app, render_template
from flask_mail import Message
from app import db, mail
from app.models.student import Student
from app.models.attendance import Attendance
from app.models.marks import Marks
from app.models.fee import Fee


def calculate_attendance_percentage(student_id: int, start_date: Optional[date] = None, 
                                   end_date: Optional[date] = None) -> float:
    """
    Calculate attendance percentage for a student.
    
    Args:
        student_id: Student ID
        start_date: Start date for calculation (optional)
        end_date: End date for calculation (optional)
        
    Returns:
        Attendance percentage (0-100)
    """
    query = Attendance.query.filter_by(student_id=student_id)
    
    if start_date:
        query = query.filter(Attendance.date >= start_date)
    if end_date:
        query = query.filter(Attendance.date <= end_date)
    
    total_days = query.count()
    if total_days == 0:
        return 0.0
    
    present_days = query.filter(Attendance.status.in_(['Present', 'Late'])).count()
    return round((present_days / total_days) * 100, 2)


def calculate_average_marks(student_id: int, subject_id: Optional[int] = None,
                           exam_type: Optional[str] = None) -> float:
    """
    Calculate average marks percentage for a student.
    
    Args:
        student_id: Student ID
        subject_id: Filter by subject (optional)
        exam_type: Filter by exam type (optional)
        
    Returns:
        Average marks percentage (0-100)
    """
    query = Marks.query.filter_by(student_id=student_id)
    
    if subject_id:
        query = query.filter_by(subject_id=subject_id)
    if exam_type:
        query = query.filter_by(exam_type=exam_type)
    
    marks_records = query.all()
    if not marks_records:
        return 0.0
    
    total_percentage = sum(
        (float(record.marks_obtained) / float(record.max_marks)) * 100 
        for record in marks_records
    )
    return round(total_percentage / len(marks_records), 2)


def calculate_fee_status(student_id: int) -> Dict[str, Any]:
    """
    Calculate fee status for a student.
    
    Args:
        student_id: Student ID
        
    Returns:
        Dictionary with fee statistics
    """
    fees = Fee.query.filter_by(student_id=student_id).all()
    
    total_fees = sum(float(fee.amount) for fee in fees)
    paid_fees = sum(float(fee.amount) for fee in fees if fee.status == 'Paid')
    pending_fees = sum(float(fee.amount) for fee in fees if fee.status in ['Pending', 'Overdue'])
    overdue_fees = sum(float(fee.amount) for fee in fees if fee.status == 'Overdue')
    
    return {
        'total_fees': round(total_fees, 2),
        'paid_fees': round(paid_fees, 2),
        'pending_fees': round(pending_fees, 2),
        'overdue_fees': round(overdue_fees, 2),
        'payment_percentage': round((paid_fees / total_fees * 100) if total_fees > 0 else 0, 2)
    }


def get_risk_level(score: float) -> str:
    """
    Get risk level based on risk score.
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Risk level string
    """
    if score >= 80:
        return 'Critical'
    elif score >= 60:
        return 'High'
    elif score >= 40:
        return 'Medium'
    elif score >= 20:
        return 'Low'
    else:
        return 'Minimal'


def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code (default: USD)
        
    Returns:
        Formatted currency string
    """
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹'
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_date(date_obj: Optional[date], format_str: str = '%Y-%m-%d') -> str:
    """
    Format date object to string.
    
    Args:
        date_obj: Date object to format
        format_str: Format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ''
    return date_obj.strftime(format_str)


def generate_student_id() -> str:
    """
    Generate a unique student ID.
    
    Returns:
        Unique student ID string
    """
    year = datetime.now().year
    # Get count of students this year
    count = Student.query.filter(
        Student.student_id.like(f'STU{year}%')
    ).count()
    return f'STU{year}{count + 1:04d}'


def generate_receipt_number() -> str:
    """
    Generate a unique receipt number.
    
    Returns:
        Unique receipt number string
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # Get count of fees today
    today = date.today()
    count = Fee.query.filter(
        db.func.date(Fee.created_at) == today
    ).count()
    return f'RCP{timestamp}{count + 1:03d}'


def send_email_alert(student: Student, alert_type: str, message: str) -> bool:
    """
    Send email alert to student.
    
    Args:
        student: Student object
        alert_type: Type of alert
        message: Alert message
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        if not student.user or not student.user.email:
            current_app.logger.warning(f"No email found for student {student.student_id}")
            return False
        
        msg = Message(
            subject=f"Student Risk Monitoring Alert: {alert_type}",
            recipients=[student.user.email],
            html=render_template(
                'email/alert.html',
                student=student,
                alert_type=alert_type,
                message=message
            )
        )
        mail.send(msg)
        current_app.logger.info(f"Alert email sent to {student.user.email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email alert: {str(e)}")
        return False


def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
    """
    Export data to CSV file.
    
    Args:
        data: List of dictionaries containing data
        filename: Output filename
        
    Returns:
        Path to the generated CSV file
    """
    if not data:
        return ''
    
    # Create exports directory if it doesn't exist
    exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    
    filepath = os.path.join(exports_dir, filename)
    
    # Get fieldnames from first row
    fieldnames = data[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return filepath


def export_to_pdf(data: List[Dict[str, Any]], filename: str, title: str = 'Report') -> str:
    """
    Export data to PDF file.
    
    Args:
        data: List of dictionaries containing data
        filename: Output filename
        title: Report title
        
    Returns:
        Path to the generated PDF file
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        
        # Create exports directory if it doesn't exist
        exports_dir = os.path.join(current_app.root_path, 'static', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        filepath = os.path.join(exports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=landscape(letter))
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles['Title']))
        
        # Create table data
        if data:
            # Header
            table_data = [list(data[0].keys())]
            # Rows
            for row in data:
                table_data.append([str(val) for val in row.values()])
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        return filepath
        
    except ImportError:
        current_app.logger.warning("reportlab not installed, PDF export unavailable")
        return ''
    except Exception as e:
        current_app.logger.error(f"Failed to export PDF: {str(e)}")
        return ''
