"""
Unit Tests for Database Models
Intelligent Student Risk Monitoring & Decision Support System
"""

import pytest
from datetime import datetime, date, timedelta
from app import db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog


class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, test_app):
        """Test user creation with valid data."""
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student',
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.role == 'student'
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_password_hashing(self, test_app):
        """Test password hashing and verification."""
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
        
        # Password should be hashed
        assert user.password_hash != 'testpass123'
        assert user.check_password('testpass123') is True
        assert user.check_password('wrongpassword') is False
    
    def test_user_role_methods(self, test_app):
        """Test user role checking methods."""
        admin = User(username='admin', email='admin@example.com', password='pass', role='admin')
        teacher = User(username='teacher', email='teacher@example.com', password='pass', role='teacher')
        student = User(username='student', email='student@example.com', password='pass', role='student')
        
        assert admin.is_admin() is True
        assert admin.is_teacher() is False
        assert admin.is_student() is False
        
        assert teacher.is_admin() is False
        assert teacher.is_teacher() is True
        assert teacher.is_student() is False
        
        assert student.is_admin() is False
        assert student.is_teacher() is False
        assert student.is_student() is True
    
    def test_user_to_dict(self, test_app):
        """Test user to dictionary conversion."""
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        
        user_dict = user.to_dict()
        assert 'id' in user_dict
        assert 'username' in user_dict
        assert 'email' in user_dict
        assert 'role' in user_dict
        assert 'is_active' in user_dict
        assert 'created_at' in user_dict
        assert 'password_hash' not in user_dict  # Should not expose password hash
    
    def test_user_repr(self, test_app):
        """Test user string representation."""
        user = User(username='testuser', email='test@example.com', password='pass', role='student')
        assert 'testuser' in repr(user)
        assert 'student' in repr(user)


class TestStudentModel:
    """Test cases for Student model."""
    
    def test_student_creation(self, test_app, student_user):
        """Test student creation with valid data."""
        student = Student(
            user_id=student_user.id,
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 15),
            gender='Male',
            course='Computer Science',
            semester=3,
            admission_date=date(2023, 8, 1)
        )
        db.session.add(student)
        db.session.commit()
        
        assert student.id is not None
        assert student.student_id == 'STU001'
        assert student.first_name == 'John'
        assert student.last_name == 'Doe'
        assert student.full_name == 'John Doe'
        assert student.course == 'Computer Science'
        assert student.semester == 3
    
    def test_student_age_calculation(self, test_app, student_user):
        """Test student age calculation."""
        student = Student(
            user_id=student_user.id,
            student_id='STU001',
            first_name='John',
            last_name='Doe',
            date_of_birth=date(2000, 1, 15),
            gender='Male',
            course='Computer Science',
            semester=3,
            admission_date=date(2023, 8, 1)
        )
        
        # Age should be calculated correctly
        expected_age = date.today().year - 2000
        if (date.today().month, date.today().day) < (1, 15):
            expected_age -= 1
        
        assert student.age == expected_age
    
    def test_student_attendance_percentage(self, test_app, sample_student, sample_attendance):
        """Test attendance percentage calculation."""
        percentage = sample_student.calculate_attendance_percentage()
        assert 0 <= percentage <= 100
    
    def test_student_average_marks(self, test_app, sample_student, sample_marks):
        """Test average marks calculation."""
        average = sample_student.calculate_average_marks()
        assert 0 <= average <= 100
    
    def test_student_risk_score(self, test_app, sample_student, sample_attendance, sample_marks, sample_fees):
        """Test risk score calculation."""
        risk_score = sample_student.calculate_risk_score()
        assert 0 <= risk_score <= 1
    
    def test_student_risk_level(self, test_app, sample_student, sample_attendance, sample_marks, sample_fees):
        """Test risk level determination."""
        risk_level = sample_student.get_risk_level()
        assert risk_level in ['Low', 'Medium', 'High']
    
    def test_student_pending_fees(self, test_app, sample_student, sample_fees):
        """Test pending fees calculation."""
        pending = sample_student.get_pending_fees()
        assert pending >= 0
    
    def test_student_overdue_books(self, test_app, sample_student, sample_library_transaction):
        """Test overdue books count."""
        overdue = sample_student.get_overdue_books()
        assert overdue >= 0
    
    def test_student_to_dict(self, test_app, sample_student):
        """Test student to dictionary conversion."""
        student_dict = sample_student.to_dict()
        assert 'id' in student_dict
        assert 'student_id' in student_dict
        assert 'full_name' in student_dict
        assert 'age' in student_dict
        assert 'attendance_percentage' in student_dict
        assert 'average_marks' in student_dict
        assert 'risk_score' in student_dict
        assert 'risk_level' in student_dict


class TestAttendanceModel:
    """Test cases for Attendance model."""
    
    def test_attendance_creation(self, test_app, sample_student, teacher_user):
        """Test attendance creation with valid data."""
        attendance = Attendance(
            student_id=sample_student.id,
            date=date.today(),
            status='Present',
            marked_by=teacher_user.id,
            remarks='Test attendance'
        )
        db.session.add(attendance)
        db.session.commit()
        
        assert attendance.id is not None
        assert attendance.status == 'Present'
        assert attendance.is_present is True
        assert attendance.is_absent is False
    
    def test_attendance_status_properties(self, test_app, sample_student, teacher_user):
        """Test attendance status properties."""
        present = Attendance(
            student_id=sample_student.id,
            date=date.today(),
            status='Present',
            marked_by=teacher_user.id
        )
        absent = Attendance(
            student_id=sample_student.id,
            date=date.today() - timedelta(days=1),
            status='Absent',
            marked_by=teacher_user.id
        )
        late = Attendance(
            student_id=sample_student.id,
            date=date.today() - timedelta(days=2),
            status='Late',
            marked_by=teacher_user.id
        )
        excused = Attendance(
            student_id=sample_student.id,
            date=date.today() - timedelta(days=3),
            status='Excused',
            marked_by=teacher_user.id
        )
        
        assert present.is_present is True
        assert present.is_absent is False
        assert present.is_excused is False
        
        assert absent.is_present is False
        assert absent.is_absent is True
        assert absent.is_excused is False
        
        assert late.is_present is True
        assert late.is_absent is False
        assert late.is_excused is False
        
        assert excused.is_present is False
        assert excused.is_absent is False
        assert excused.is_excused is True
    
    def test_attendance_summary(self, test_app, sample_attendance):
        """Test attendance summary calculation."""
        summary = Attendance.get_attendance_summary(sample_attendance[0].student_id)
        assert 'total_days' in summary
        assert 'present' in summary
        assert 'absent' in summary
        assert 'percentage' in summary
        assert summary['total_days'] > 0
    
    def test_attendance_to_dict(self, test_app, sample_attendance):
        """Test attendance to dictionary conversion."""
        attendance_dict = sample_attendance[0].to_dict()
        assert 'id' in attendance_dict
        assert 'student_id' in attendance_dict
        assert 'date' in attendance_dict
        assert 'status' in attendance_dict
        assert 'is_present' in attendance_dict


class TestMarksModel:
    """Test cases for Marks model."""
    
    def test_marks_creation(self, test_app, sample_student, sample_subject, teacher_user):
        """Test marks creation with valid data."""
        marks = Marks(
            student_id=sample_student.id,
            subject_id=sample_subject.id,
            exam_type='Midterm',
            marks_obtained=85,
            max_marks=100,
            exam_date=date.today(),
            graded_by=teacher_user.id,
            remarks='Good performance'
        )
        db.session.add(marks)
        db.session.commit()
        
        assert marks.id is not None
        assert marks.marks_obtained == 85
        assert marks.max_marks == 100
        assert marks.percentage == 85.0
        assert marks.grade == 'A'
        assert marks.is_passing is True
    
    def test_marks_grade_calculation(self, test_app, sample_student, sample_subject, teacher_user):
        """Test grade calculation based on percentage."""
        test_cases = [
            (95, 'A+'),
            (85, 'A'),
            (75, 'B+'),
            (65, 'B'),
            (55, 'C'),
            (45, 'D'),
            (35, 'F')
        ]
        
        for marks_obtained, expected_grade in test_cases:
            marks = Marks(
                student_id=sample_student.id,
                subject_id=sample_subject.id,
                exam_type='Midterm',
                marks_obtained=marks_obtained,
                max_marks=100,
                exam_date=date.today(),
                graded_by=teacher_user.id
            )
            assert marks.grade == expected_grade
    
    def test_marks_passing_status(self, test_app, sample_student, sample_subject, teacher_user):
        """Test passing status determination."""
        passing_marks = Marks(
            student_id=sample_student.id,
            subject_id=sample_subject.id,
            exam_type='Midterm',
            marks_obtained=45,
            max_marks=100,
            exam_date=date.today(),
            graded_by=teacher_user.id
        )
        failing_marks = Marks(
            student_id=sample_student.id,
            subject_id=sample_subject.id,
            exam_type='Final',
            marks_obtained=35,
            max_marks=100,
            exam_date=date.today(),
            graded_by=teacher_user.id
        )
        
        assert passing_marks.is_passing is True
        assert failing_marks.is_passing is False
    
    def test_marks_to_dict(self, test_app, sample_marks):
        """Test marks to dictionary conversion."""
        marks_dict = sample_marks[0].to_dict()
        assert 'id' in marks_dict
        assert 'student_id' in marks_dict
        assert 'subject_id' in marks_dict
        assert 'marks_obtained' in marks_dict
        assert 'max_marks' in marks_dict
        assert 'percentage' in marks_dict
        assert 'grade' in marks_dict
        assert 'is_passing' in marks_dict


class TestFeeModel:
    """Test cases for Fee model."""
    
    def test_fee_creation(self, test_app, sample_student):
        """Test fee creation with valid data."""
        fee = Fee(
            student_id=sample_student.id,
            fee_type='Tuition',
            amount=1000.00,
            due_date=date.today() + timedelta(days=30),
            status='Pending'
        )
        db.session.add(fee)
        db.session.commit()
        
        assert fee.id is not None
        assert fee.fee_type == 'Tuition'
        assert fee.amount == 1000.00
        assert fee.status == 'Pending'
        assert fee.is_overdue is False
    
    def test_fee_overdue_status(self, test_app, sample_student):
        """Test fee overdue status."""
        overdue_fee = Fee(
            student_id=sample_student.id,
            fee_type='Tuition',
            amount=1000.00,
            due_date=date.today() - timedelta(days=10),
            status='Pending'
        )
        assert overdue_fee.is_overdue is True
        assert overdue_fee.days_overdue > 0
    
    def test_fee_mark_as_paid(self, test_app, sample_student):
        """Test marking fee as paid."""
        fee = Fee(
            student_id=sample_student.id,
            fee_type='Tuition',
            amount=1000.00,
            due_date=date.today() + timedelta(days=30),
            status='Pending'
        )
        fee.mark_as_paid('Cash', 'TXN001', 'RCP001')
        
        assert fee.status == 'Paid'
        assert fee.paid_date == date.today()
        assert fee.payment_method == 'Cash'
        assert fee.transaction_id == 'TXN001'
        assert fee.receipt_number == 'RCP001'
    
    def test_fee_to_dict(self, test_app, sample_fees):
        """Test fee to dictionary conversion."""
        fee_dict = sample_fees[0].to_dict()
        assert 'id' in fee_dict
        assert 'student_id' in fee_dict
        assert 'fee_type' in fee_dict
        assert 'amount' in fee_dict
        assert 'due_date' in fee_dict
        assert 'status' in fee_dict
        assert 'is_overdue' in fee_dict


class TestLibraryModels:
    """Test cases for Library models."""
    
    def test_library_book_creation(self, test_app):
        """Test library book creation with valid data."""
        book = LibraryBook(
            book_id='BK001',
            title='Python Programming',
            author='John Smith',
            isbn='978-0-123456-78-9',
            category='Programming',
            total_copies=5,
            available_copies=3
        )
        db.session.add(book)
        db.session.commit()
        
        assert book.id is not None
        assert book.title == 'Python Programming'
        assert book.is_available is True
        assert book.issued_copies == 2
    
    def test_library_book_issue_return(self, test_app, sample_library_book):
        """Test book issue and return."""
        initial_available = sample_library_book.available_copies
        
        sample_library_book.issue_book()
        assert sample_library_book.available_copies == initial_available - 1
        
        sample_library_book.return_book()
        assert sample_library_book.available_copies == initial_available
    
    def test_library_transaction_creation(self, test_app, sample_student, sample_library_book, teacher_user):
        """Test library transaction creation with valid data."""
        transaction = LibraryTransaction(
            student_id=sample_student.id,
            book_id=sample_library_book.id,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=14),
            issued_by=teacher_user.id,
            status='Issued'
        )
        db.session.add(transaction)
        db.session.commit()
        
        assert transaction.id is not None
        assert transaction.status == 'Issued'
        assert transaction.is_overdue is False
    
    def test_library_transaction_overdue(self, test_app, sample_student, sample_library_book, teacher_user):
        """Test library transaction overdue status."""
        transaction = LibraryTransaction(
            student_id=sample_student.id,
            book_id=sample_library_book.id,
            issue_date=date.today() - timedelta(days=20),
            due_date=date.today() - timedelta(days=6),
            issued_by=teacher_user.id,
            status='Issued'
        )
        
        assert transaction.is_overdue is True
        assert transaction.days_overdue > 0
        assert transaction.calculate_fine > 0
    
    def test_library_transaction_return(self, test_app, sample_library_transaction, teacher_user):
        """Test library transaction return."""
        sample_library_transaction.return_book(teacher_user.id)
        
        assert sample_library_transaction.status == 'Returned'
        assert sample_library_transaction.return_date == date.today()
        assert sample_library_transaction.returned_to == teacher_user.id
    
    def test_library_book_to_dict(self, test_app, sample_library_book):
        """Test library book to dictionary conversion."""
        book_dict = sample_library_book.to_dict()
        assert 'id' in book_dict
        assert 'book_id' in book_dict
        assert 'title' in book_dict
        assert 'author' in book_dict
        assert 'is_available' in book_dict
    
    def test_library_transaction_to_dict(self, test_app, sample_library_transaction):
        """Test library transaction to dictionary conversion."""
        transaction_dict = sample_library_transaction.to_dict()
        assert 'id' in transaction_dict
        assert 'student_id' in transaction_dict
        assert 'book_id' in transaction_dict
        assert 'status' in transaction_dict
        assert 'is_overdue' in transaction_dict


class TestComplaintModel:
    """Test cases for Complaint model."""
    
    def test_complaint_creation(self, test_app, sample_student):
        """Test complaint creation with valid data."""
        complaint = Complaint(
            student_id=sample_student.id,
            subject='Library Issue',
            description='Cannot access online library resources',
            category='Infrastructure',
            priority='Medium',
            status='Open'
        )
        db.session.add(complaint)
        db.session.commit()
        
        assert complaint.id is not None
        assert complaint.subject == 'Library Issue'
        assert complaint.status == 'Open'
        assert complaint.is_open is True
        assert complaint.is_resolved is False
    
    def test_complaint_status_properties(self, test_app, sample_student):
        """Test complaint status properties."""
        open_complaint = Complaint(
            student_id=sample_student.id,
            subject='Test',
            description='Test',
            category='Other',
            status='Open'
        )
        in_progress = Complaint(
            student_id=sample_student.id,
            subject='Test',
            description='Test',
            category='Other',
            status='In Progress'
        )
        resolved = Complaint(
            student_id=sample_student.id,
            subject='Test',
            description='Test',
            category='Other',
            status='Resolved'
        )
        
        assert open_complaint.is_open is True
        assert open_complaint.is_in_progress is False
        assert open_complaint.is_resolved is False
        
        assert in_progress.is_open is False
        assert in_progress.is_in_progress is True
        assert in_progress.is_resolved is False
        
        assert resolved.is_open is False
        assert resolved.is_in_progress is False
        assert resolved.is_resolved is True
    
    def test_complaint_assign(self, test_app, sample_complaint, teacher_user):
        """Test complaint assignment."""
        sample_complaint.assign(teacher_user.id)
        
        assert sample_complaint.assigned_to == teacher_user.id
        assert sample_complaint.status == 'In Progress'
    
    def test_complaint_resolve(self, test_app, sample_complaint):
        """Test complaint resolution."""
        sample_complaint.resolve('Issue resolved')
        
        assert sample_complaint.resolution == 'Issue resolved'
        assert sample_complaint.status == 'Resolved'
    
    def test_complaint_to_dict(self, test_app, sample_complaint):
        """Test complaint to dictionary conversion."""
        complaint_dict = sample_complaint.to_dict()
        assert 'id' in complaint_dict
        assert 'student_id' in complaint_dict
        assert 'subject' in complaint_dict
        assert 'status' in complaint_dict
        assert 'is_open' in complaint_dict


class TestPredictionModel:
    """Test cases for Prediction model."""
    
    def test_prediction_creation(self, test_app, sample_student, sample_ml_model):
        """Test prediction creation with valid data."""
        prediction = Prediction(
            student_id=sample_student.id,
            model_id=sample_ml_model.id,
            risk_level='Medium',
            risk_score=0.55,
            probability=0.65,
            attendance_percentage=75.0,
            average_marks=65.0,
            fee_status='Pending',
            recommendations='Improve attendance'
        )
        db.session.add(prediction)
        db.session.commit()
        
        assert prediction.id is not None
        assert prediction.risk_level == 'Medium'
        assert prediction.risk_score == 0.55
        assert prediction.is_medium_risk is True
        assert prediction.is_high_risk is False
        assert prediction.is_low_risk is False
    
    def test_prediction_risk_properties(self, test_app, sample_student, sample_ml_model):
        """Test prediction risk level properties."""
        high_risk = Prediction(
            student_id=sample_student.id,
            model_id=sample_ml_model.id,
            risk_level='High',
            risk_score=0.85,
            probability=0.90
        )
        medium_risk = Prediction(
            student_id=sample_student.id,
            model_id=sample_ml_model.id,
            risk_level='Medium',
            risk_score=0.55,
            probability=0.65
        )
        low_risk = Prediction(
            student_id=sample_student.id,
            model_id=sample_ml_model.id,
            risk_level='Low',
            risk_score=0.25,
            probability=0.30
        )
        
        assert high_risk.is_high_risk is True
        assert high_risk.is_medium_risk is False
        assert high_risk.is_low_risk is False
        
        assert medium_risk.is_high_risk is False
        assert medium_risk.is_medium_risk is True
        assert medium_risk.is_low_risk is False
        
        assert low_risk.is_high_risk is False
        assert low_risk.is_medium_risk is False
        assert low_risk.is_low_risk is True
    
    def test_prediction_to_dict(self, test_app, sample_prediction):
        """Test prediction to dictionary conversion."""
        prediction_dict = sample_prediction.to_dict()
        assert 'id' in prediction_dict
        assert 'student_id' in prediction_dict
        assert 'risk_level' in prediction_dict
        assert 'risk_score' in prediction_dict
        assert 'is_high_risk' in prediction_dict


class TestAlertModel:
    """Test cases for Alert model."""
    
    def test_alert_creation(self, test_app, sample_student):
        """Test alert creation with valid data."""
        alert = Alert(
            student_id=sample_student.id,
            alert_type='Attendance',
            severity='Warning',
            message='Attendance below 75%',
            suggestion='Attend classes regularly',
            is_read=False
        )
        db.session.add(alert)
        db.session.commit()
        
        assert alert.id is not None
        assert alert.alert_type == 'Attendance'
        assert alert.severity == 'Warning'
        assert alert.is_warning is True
        assert alert.is_critical is False
        assert alert.is_info is False
        assert alert.is_read is False
    
    def test_alert_severity_properties(self, test_app, sample_student):
        """Test alert severity properties."""
        critical = Alert(
            student_id=sample_student.id,
            alert_type='Academic',
            severity='Critical',
            message='Critical alert'
        )
        warning = Alert(
            student_id=sample_student.id,
            alert_type='Attendance',
            severity='Warning',
            message='Warning alert'
        )
        info = Alert(
            student_id=sample_student.id,
            alert_type='General',
            severity='Info',
            message='Info alert'
        )
        
        assert critical.is_critical is True
        assert critical.is_warning is False
        assert critical.is_info is False
        
        assert warning.is_critical is False
        assert warning.is_warning is True
        assert warning.is_info is False
        
        assert info.is_critical is False
        assert info.is_warning is False
        assert info.is_info is True
    
    def test_alert_mark_as_read(self, test_app, sample_alert):
        """Test marking alert as read."""
        sample_alert.mark_as_read()
        assert sample_alert.is_read is True
    
    def test_alert_to_dict(self, test_app, sample_alert):
        """Test alert to dictionary conversion."""
        alert_dict = sample_alert.to_dict()
        assert 'id' in alert_dict
        assert 'student_id' in alert_dict
        assert 'alert_type' in alert_dict
        assert 'severity' in alert_dict
        assert 'message' in alert_dict
        assert 'is_read' in alert_dict


class TestMLModelModel:
    """Test cases for MLModel model."""
    
    def test_ml_model_creation(self, test_app):
        """Test ML model creation with valid data."""
        model = MLModel(
            model_name='risk_model_v1',
            model_version='1.0.0',
            algorithm='Random Forest',
            training_date=datetime.utcnow(),
            accuracy=0.85,
            precision_score=0.82,
            recall_score=0.88,
            f1_score=0.85,
            model_path='models/risk_model_v1.pkl',
            is_active=True
        )
        db.session.add(model)
        db.session.commit()
        
        assert model.id is not None
        assert model.model_name == 'risk_model_v1'
        assert model.accuracy == 0.85
        assert model.is_active is True
    
    def test_ml_model_activate_deactivate(self, test_app, sample_ml_model):
        """Test ML model activation and deactivation."""
        sample_ml_model.deactivate()
        assert sample_ml_model.is_active is False
        
        sample_ml_model.activate()
        assert sample_ml_model.is_active is True
    
    def test_ml_model_to_dict(self, test_app, sample_ml_model):
        """Test ML model to dictionary conversion."""
        model_dict = sample_ml_model.to_dict()
        assert 'id' in model_dict
        assert 'model_name' in model_dict
        assert 'algorithm' in model_dict
        assert 'accuracy' in model_dict
        assert 'is_active' in model_dict
