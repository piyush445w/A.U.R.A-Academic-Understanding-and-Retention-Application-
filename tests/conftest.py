"""
Pytest Fixtures for Testing
Intelligent Student Risk Monitoring & Decision Support System
"""

import pytest
from datetime import datetime, date, timedelta
from app import create_app, db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog


@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    # Establish application context
    with app.app_context():
        yield app


@pytest.fixture(scope='function')
def test_app(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.create_all()
        yield app
        db.session.rollback()
        db.drop_all()


@pytest.fixture(scope='function')
def client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture(scope='function')
def runner(test_app):
    """Create a test CLI runner."""
    return test_app.test_cli_runner()


@pytest.fixture(scope='function')
def admin_user(test_app):
    """Create an admin user for testing."""
    user = User(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='admin',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def teacher_user(test_app):
    """Create a teacher user for testing."""
    user = User(
        username='teacher',
        email='teacher@example.com',
        password='teacher123',
        role='teacher',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def student_user(test_app):
    """Create a student user for testing."""
    user = User(
        username='student',
        email='student@example.com',
        password='student123',
        role='student',
        is_active=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture(scope='function')
def sample_student(test_app, student_user):
    """Create a sample student for testing."""
    student = Student(
        user_id=student_user.id,
        student_id='STU001',
        first_name='John',
        last_name='Doe',
        date_of_birth=date(2000, 1, 15),
        gender='Male',
        course='Computer Science',
        semester=3,
        admission_date=date(2023, 8, 1),
        phone='1234567890',
        address='123 Main St',
        guardian_name='Jane Doe',
        guardian_phone='0987654321'
    )
    db.session.add(student)
    db.session.commit()
    return student


@pytest.fixture(scope='function')
def sample_subject(test_app):
    """Create a sample subject for testing."""
    subject = Subject(
        subject_id='CS101',
        name='Introduction to Programming',
        description='Basic programming concepts',
        credits=3,
        department='Computer Science'
    )
    db.session.add(subject)
    db.session.commit()
    return subject


@pytest.fixture(scope='function')
def sample_attendance(test_app, sample_student, teacher_user):
    """Create sample attendance records for testing."""
    attendances = []
    for i in range(10):
        attendance = Attendance(
            student_id=sample_student.id,
            date=date.today() - timedelta(days=i),
            status='Present' if i % 3 != 0 else 'Absent',
            marked_by=teacher_user.id,
            remarks='Test attendance'
        )
        db.session.add(attendance)
        attendances.append(attendance)
    db.session.commit()
    return attendances


@pytest.fixture(scope='function')
def sample_marks(test_app, sample_student, sample_subject, teacher_user):
    """Create sample marks records for testing."""
    marks_records = []
    exam_types = ['Midterm', 'Final', 'Assignment', 'Quiz']
    for i, exam_type in enumerate(exam_types):
        marks = Marks(
            student_id=sample_student.id,
            subject_id=sample_subject.id,
            exam_type=exam_type,
            marks_obtained=70 + i * 5,
            max_marks=100,
            exam_date=date.today() - timedelta(days=30 - i * 7),
            graded_by=teacher_user.id,
            remarks='Test marks'
        )
        db.session.add(marks)
        marks_records.append(marks)
    db.session.commit()
    return marks_records


@pytest.fixture(scope='function')
def sample_fees(test_app, sample_student):
    """Create sample fee records for testing."""
    fees = []
    fee_types = ['Tuition', 'Library', 'Laboratory']
    for i, fee_type in enumerate(fee_types):
        fee = Fee(
            student_id=sample_student.id,
            fee_type=fee_type,
            amount=1000 + i * 500,
            due_date=date.today() + timedelta(days=30 - i * 10),
            status='Pending' if i != 2 else 'Paid',
            paid_date=date.today() if i == 2 else None,
            payment_method='Cash' if i == 2 else None,
            transaction_id='TXN001' if i == 2 else None,
            receipt_number='RCP001' if i == 2 else None
        )
        db.session.add(fee)
        fees.append(fee)
    db.session.commit()
    return fees


@pytest.fixture(scope='function')
def sample_library_book(test_app):
    """Create a sample library book for testing."""
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
    return book


@pytest.fixture(scope='function')
def sample_library_transaction(test_app, sample_student, sample_library_book, teacher_user):
    """Create a sample library transaction for testing."""
    transaction = LibraryTransaction(
        student_id=sample_student.id,
        book_id=sample_library_book.id,
        issue_date=date.today() - timedelta(days=10),
        due_date=date.today() + timedelta(days=4),
        issued_by=teacher_user.id,
        status='Issued',
        fine_amount=0.00
    )
    db.session.add(transaction)
    db.session.commit()
    return transaction


@pytest.fixture(scope='function')
def sample_complaint(test_app, sample_student):
    """Create a sample complaint for testing."""
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
    return complaint


@pytest.fixture(scope='function')
def sample_ml_model(test_app):
    """Create a sample ML model for testing."""
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
    return model


@pytest.fixture(scope='function')
def sample_prediction(test_app, sample_student, sample_ml_model):
    """Create a sample prediction for testing."""
    prediction = Prediction(
        student_id=sample_student.id,
        model_id=sample_ml_model.id,
        risk_level='Medium',
        risk_score=0.55,
        probability=0.65,
        attendance_percentage=75.0,
        average_marks=65.0,
        fee_status='Pending',
        recommendations='Improve attendance and academic performance'
    )
    db.session.add(prediction)
    db.session.commit()
    return prediction


@pytest.fixture(scope='function')
def sample_alert(test_app, sample_student):
    """Create a sample alert for testing."""
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
    return alert


@pytest.fixture(scope='function')
def authenticated_client(client, student_user):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = student_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture(scope='function')
def admin_authenticated_client(client, admin_user):
    """Create an admin authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['_fresh'] = True
    return client


@pytest.fixture(scope='function')
def teacher_authenticated_client(client, teacher_user):
    """Create a teacher authenticated test client."""
    with client.session_transaction() as sess:
        sess['user_id'] = teacher_user.id
        sess['_fresh'] = True
    return client
