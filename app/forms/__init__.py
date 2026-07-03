"""
Flask-WTF Forms for Intelligent Student Risk Monitoring & Decision Support System
"""

from app.forms.auth import (
    LoginForm,
    RegistrationForm,
    ChangePasswordForm,
    ProfileForm
)

from app.forms.student import (
    StudentForm,
    StudentSearchForm
)

from app.forms.attendance import (
    AttendanceForm,
    BulkAttendanceForm,
    AttendanceReportForm
)

from app.forms.marks import (
    MarksForm,
    BulkMarksForm
)

from app.forms.fee import (
    FeeForm,
    PaymentForm
)

from app.forms.library import (
    BookForm,
    IssueBookForm,
    ReturnBookForm
)

from app.forms.complaint import (
    ComplaintForm,
    ComplaintResponseForm
)

from app.forms.prediction import (
    DatasetUploadForm,
    ModelTrainForm
)

__all__ = [
    # Auth forms
    'LoginForm',
    'RegistrationForm',
    'ChangePasswordForm',
    'ProfileForm',
    
    # Student forms
    'StudentForm',
    'StudentSearchForm',
    
    # Attendance forms
    'AttendanceForm',
    'BulkAttendanceForm',
    'AttendanceReportForm',
    
    # Marks forms
    'MarksForm',
    'BulkMarksForm',
    
    # Fee forms
    'FeeForm',
    'PaymentForm',
    
    # Library forms
    'BookForm',
    'IssueBookForm',
    'ReturnBookForm',
    
    # Complaint forms
    'ComplaintForm',
    'ComplaintResponseForm',
    
    # Prediction forms
    'DatasetUploadForm',
    'ModelTrainForm',
]
