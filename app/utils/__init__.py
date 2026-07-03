"""
Utility Functions for Intelligent Student Risk Monitoring & Decision Support System
"""

from app.utils.helpers import (
    calculate_attendance_percentage,
    calculate_average_marks,
    calculate_fee_status,
    get_risk_level,
    format_currency,
    format_date,
    generate_student_id,
    generate_receipt_number,
    send_email_alert,
    export_to_csv,
    export_to_pdf
)

from app.utils.decorators import (
    role_required,
    admin_required,
    teacher_required,
    student_required,
    log_activity
)

from app.utils.validators import (
    validate_student_id,
    validate_phone,
    validate_email_unique,
    validate_file_extension,
    validate_file_size
)

__all__ = [
    # Helper functions
    'calculate_attendance_percentage',
    'calculate_average_marks',
    'calculate_fee_status',
    'get_risk_level',
    'format_currency',
    'format_date',
    'generate_student_id',
    'generate_receipt_number',
    'send_email_alert',
    'export_to_csv',
    'export_to_pdf',
    
    # Decorators
    'role_required',
    'admin_required',
    'teacher_required',
    'student_required',
    'log_activity',
    
    # Validators
    'validate_student_id',
    'validate_phone',
    'validate_email_unique',
    'validate_file_extension',
    'validate_file_size',
]
