#!/usr/bin/env python3
"""
Data Seeding Script
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import sys
import csv
import logging
from datetime import datetime, date, timedelta
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('seed_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_sample_students(app):
    """
    Load sample students from CSV file.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Loading sample students...")
        
        import random
        
        csv_file = Path('datasets/students_sample.csv')
        
        if not csv_file.exists():
            logger.warning("Students CSV file not found, creating sample data")
            return create_sample_students(app)
        
        with app.app_context():
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                missing_columns = {'student_id', 'first_name', 'last_name', 'date_of_birth', 'gender', 'course', 'semester', 'admission_date'}
                if reader.fieldnames:
                    missing_columns = missing_columns - set(reader.fieldnames)
                
                for row in reader:
                    try:
                        if 'student_id' not in row or not row.get('student_id'):
                            logger.warning("Skipping row with missing student_id")
                            continue
                        
                        existing_student = Student.query.filter_by(student_id=row['student_id']).first()
                        
                        if existing_student:
                            logger.info(f"Student {row['student_id']} already exists, skipping")
                            continue
                        
                        dob = None
                        if 'date_of_birth' in row and row.get('date_of_birth'):
                            try:
                                dob = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                            except ValueError:
                                dob = date(random.randint(1999, 2003), random.randint(1, 12), random.randint(1, 28))
                        else:
                            dob = date(random.randint(1999, 2003), random.randint(1, 12), random.randint(1, 28))
                        
                        admission_date = None
                        if 'admission_date' in row and row.get('admission_date'):
                            try:
                                admission_date = datetime.strptime(row['admission_date'], '%Y-%m-%d').date()
                            except ValueError:
                                admission_date = date(2023, 8, 1)
                        else:
                            admission_date = date(2023, 8, 1)
                        
                        user = User(
                            username=row['student_id'],
                            email=f"{row['student_id']}@student.edu",
                            password='student123',
                            role='student',
                            is_active=True
                        )
                        db.session.add(user)
                        db.session.flush()
                        
                        student = Student(
                            user_id=user.id,
                            student_id=row['student_id'],
                            first_name=row.get('first_name', 'Unknown'),
                            last_name=row.get('last_name', 'Unknown'),
                            date_of_birth=dob,
                            gender=row.get('gender', random.choice(['Male', 'Female'])),
                            course=row.get('course', 'Computer Science'),
                            semester=int(row.get('semester', 1)),
                            admission_date=admission_date,
                            phone=row.get('phone'),
                            address=row.get('address'),
                            guardian_name=row.get('guardian_name'),
                            guardian_phone=row.get('guardian_phone')
                        )
                        db.session.add(student)
                        logger.info(f"Created student: {row['student_id']}")
                        
                    except Exception as row_error:
                        logger.warning(f"Error processing row {row.get('student_id', 'unknown')}: {str(row_error)}")
                        continue
                
                db.session.commit()
                logger.info("Sample students loaded successfully")
                
        return True
    except Exception as e:
        logger.error(f"Error loading sample students: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return create_sample_students(app)


def create_sample_students(app):
    """
    Create sample students for all streams (Computer Science, Electronics, Mechanical, Civil, Mathematics).
    Creates 5 courses × 6 semesters × 20 students = 600 students total.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample students...")
        
        import random
        
        first_names = ['John', 'Alice', 'Bob', 'Emma', 'Michael', 'Sarah', 'David', 'Lisa', 'James', 'Emily', 
                       'Robert', 'Jennifer', 'William', 'Linda', 'Richard', 'Patricia', 'Thomas', 'Barbara',
                       'Daniel', 'Jessica', 'Matthew', 'Karen', 'Christopher', 'Nancy', 'Anthony', 'Betty']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Martinez', 'Wilson',
                      'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris']
        
        courses = [
            ('Computer Science', [1, 2, 3, 4, 5, 6]),
            ('Electronics', [1, 2, 3, 4, 5, 6]),
            ('Mechanical', [1, 2, 3, 4, 5, 6]),
            ('Civil', [1, 2, 3, 4, 5, 6]),
            ('Mathematics', [1, 2, 3, 4, 5, 6])
        ]
        
        target_total = 5 * 6 * 20
        
        with app.app_context():
            existing_count = Student.query.count()
            students_to_create = max(0, target_total - existing_count)
            
            if students_to_create == 0:
                logger.info(f"All {existing_count} students already exist")
                return True
            
            logger.info(f"Creating {students_to_create} new students (target: {target_total})...")
            
            student_counter = existing_count
            created_count = 0
            
            for course_name, semesters in courses:
                for sem in semesters:
                    for i in range(20):
                        student_counter += 1
                        student_id = f"STU{student_counter:03d}"
                        
                        existing = Student.query.filter_by(student_id=student_id).first()
                        if existing:
                            continue
                        
                        first_name = random.choice(first_names)
                        last_name = random.choice(last_names)
                        
                        user = User(
                            username=student_id,
                            email=f"{student_id}@student.edu",
                            password='student123',
                            role='student',
                            is_active=True
                        )
                        db.session.add(user)
                        db.session.flush()
                        
                        year = 2024 - (sem // 2) - random.randint(0, 1)
                        student = Student(
                            user_id=user.id,
                            student_id=student_id,
                            first_name=first_name,
                            last_name=last_name,
                            date_of_birth=date(random.randint(1999, 2003), random.randint(1, 12), random.randint(1, 28)),
                            gender=random.choice(['Male', 'Female']),
                            course=course_name,
                            semester=sem,
                            admission_date=date(year, 8, 1),
                            phone=f"{random.randint(1000000000, 9999999999)}",
                            address=f"{random.randint(1, 999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Maple'])} {random.choice(['St', 'Rd', 'Ave', 'Dr'])}",
                            guardian_name=f"{random.choice(['Mr.', 'Mrs.'])} {random.choice(last_names)}",
                            guardian_phone=f"{random.randint(1000000000, 9999999999)}"
                        )
                        db.session.add(student)
                        created_count += 1
                        
                        if created_count % 50 == 0:
                            logger.info(f"Created {created_count} students...")
            
            db.session.commit()
            logger.info(f"Sample students created successfully: {created_count} new students")
        
        return True
    except Exception as e:
        logger.error(f"Error creating sample students: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def load_sample_attendance(app):
    """
    Load sample attendance records from CSV or generate for existing students.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Loading sample attendance...")
        
        import random
        
        with app.app_context():
            teacher = User.query.filter_by(role='teacher').first()
            
            if not teacher:
                logger.error("Teacher user not found")
                return False
            
            csv_file = Path('datasets/attendance_sample.csv')
            
            if csv_file.exists():
                with open(csv_file, 'r') as f:
                    reader = csv.DictReader(f)
                    
                    for row in reader:
                        student = Student.query.filter_by(student_id=row['student_id']).first()
                        
                        if not student:
                            continue
                        
                        attendance_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                        existing = Attendance.query.filter_by(
                            student_id=student.id,
                            date=attendance_date
                        ).first()
                        
                        if existing:
                            continue
                        
                        attendance = Attendance(
                            student_id=student.id,
                            date=attendance_date,
                            status=row['status'],
                            marked_by=teacher.id,
                            remarks=row.get('remarks')
                        )
                        db.session.add(attendance)
                
                db.session.commit()
            
            students = Student.query.all()
            logger.info(f"Creating attendance for {len(students)} students...")
            
            for student in students:
                for i in range(30):
                    attendance_date = date.today() - timedelta(days=i)
                    
                    existing = Attendance.query.filter_by(
                        student_id=student.id,
                        date=attendance_date
                    ).first()
                    
                    if existing:
                        continue
                    
                    status = random.choice(['Present', 'Present', 'Present', 'Absent', 'Late'])
                    
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        marked_by=teacher.id,
                        remarks='Sample attendance'
                    )
                    db.session.add(attendance)
            
            db.session.commit()
            logger.info("Sample attendance created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error loading sample attendance: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def create_sample_attendance(app):
    """
    Create sample attendance records.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample attendance...")
        
        with app.app_context():
            # Get teacher user
            teacher = User.query.filter_by(role='teacher').first()
            
            if not teacher:
                logger.error("Teacher user not found")
                return False
            
            # Get all students
            students = Student.query.all()
            
            if not students:
                logger.error("No students found")
                return False
            
            # Create attendance for last 30 days
            for student in students:
                for i in range(30):
                    attendance_date = date.today() - timedelta(days=i)
                    
                    # Check if attendance already exists
                    existing = Attendance.query.filter_by(
                        student_id=student.id,
                        date=attendance_date
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Randomly assign status
                    import random
                    status = random.choice(['Present', 'Present', 'Present', 'Absent', 'Late'])
                    
                    attendance = Attendance(
                        student_id=student.id,
                        date=attendance_date,
                        status=status,
                        marked_by=teacher.id,
                        remarks='Sample attendance'
                    )
                    db.session.add(attendance)
            
            db.session.commit()
            logger.info("Sample attendance created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample attendance: {str(e)}")
        db.session.rollback()
        return False


def create_sample_users(app):
    """
    Create sample users (admin and teachers).
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample users...")
        
        with app.app_context():
            users_data = [
                {
                    'username': 'admin',
                    'email': 'admin@school.edu',
                    'password': 'admin123',
                    'role': 'admin'
                },
                {
                    'username': 'teacher1',
                    'email': 'teacher1@school.edu',
                    'password': 'teacher123',
                    'role': 'teacher'
                },
                {
                    'username': 'teacher2',
                    'email': 'teacher2@school.edu',
                    'password': 'teacher123',
                    'role': 'teacher'
                }
            ]
            
            for user_data in users_data:
                existing_user = User.query.filter_by(username=user_data['username']).first()
                
                if existing_user:
                    logger.info(f"User {user_data['username']} already exists, skipping")
                    continue
                
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    role=user_data['role'],
                    is_active=True
                )
                db.session.add(user)
                logger.info(f"Created user: {user_data['username']} ({user_data['role']})")
            
            db.session.commit()
            logger.info("Sample users created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample users: {str(e)}")
        db.session.rollback()
        return False


def create_sample_subjects(app):
    """
    Create sample subjects for all courses/streams.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample subjects...")
        
        with app.app_context():
            subjects_data = [
                # Computer Science
                {'subject_code': 'CS101', 'subject_name': 'Introduction to Programming', 'course': 'Computer Science', 'semester': 1, 'credits': 4},
                {'subject_code': 'CS102', 'subject_name': 'Data Structures', 'course': 'Computer Science', 'semester': 2, 'credits': 4},
                {'subject_code': 'CS201', 'subject_name': 'Database Management Systems', 'course': 'Computer Science', 'semester': 3, 'credits': 3},
                {'subject_code': 'CS202', 'subject_name': 'Operating Systems', 'course': 'Computer Science', 'semester': 4, 'credits': 3},
                {'subject_code': 'CS301', 'subject_name': 'Machine Learning', 'course': 'Computer Science', 'semester': 5, 'credits': 4},
                {'subject_code': 'CS302', 'subject_name': 'Web Development', 'course': 'Computer Science', 'semester': 6, 'credits': 3},
                # Electronics
                {'subject_code': 'EC101', 'subject_name': 'Basic Electronics', 'course': 'Electronics', 'semester': 1, 'credits': 4},
                {'subject_code': 'EC102', 'subject_name': 'Circuit Analysis', 'course': 'Electronics', 'semester': 2, 'credits': 4},
                {'subject_code': 'EC201', 'subject_name': 'Digital Electronics', 'course': 'Electronics', 'semester': 3, 'credits': 3},
                {'subject_code': 'EC202', 'subject_name': 'Microprocessors', 'course': 'Electronics', 'semester': 4, 'credits': 3},
                {'subject_code': 'EC301', 'subject_name': 'Signal Processing', 'course': 'Electronics', 'semester': 5, 'credits': 4},
                {'subject_code': 'EC302', 'subject_name': 'Communication Systems', 'course': 'Electronics', 'semester': 6, 'credits': 3},
                # Mechanical
                {'subject_code': 'ME101', 'subject_name': 'Engineering Mechanics', 'course': 'Mechanical', 'semester': 1, 'credits': 4},
                {'subject_code': 'ME102', 'subject_name': 'Thermodynamics', 'course': 'Mechanical', 'semester': 2, 'credits': 4},
                {'subject_code': 'ME201', 'subject_name': 'Fluid Mechanics', 'course': 'Mechanical', 'semester': 3, 'credits': 3},
                {'subject_code': 'ME202', 'subject_name': 'Machine Design', 'course': 'Mechanical', 'semester': 4, 'credits': 3},
                {'subject_code': 'ME301', 'subject_name': 'Heat Transfer', 'course': 'Mechanical', 'semester': 5, 'credits': 4},
                {'subject_code': 'ME302', 'subject_name': 'Manufacturing Technology', 'course': 'Mechanical', 'semester': 6, 'credits': 3},
                # Civil
                {'subject_code': 'CE101', 'subject_name': 'Building Materials', 'course': 'Civil', 'semester': 1, 'credits': 4},
                {'subject_code': 'CE102', 'subject_name': 'Surveying', 'course': 'Civil', 'semester': 2, 'credits': 4},
                {'subject_code': 'CE201', 'subject_name': 'Structural Analysis', 'course': 'Civil', 'semester': 3, 'credits': 3},
                {'subject_code': 'CE202', 'subject_name': 'Concrete Technology', 'course': 'Civil', 'semester': 4, 'credits': 3},
                {'subject_code': 'CE301', 'subject_name': 'Geotechnical Engineering', 'course': 'Civil', 'semester': 5, 'credits': 4},
                {'subject_code': 'CE302', 'subject_name': 'Transportation Engineering', 'course': 'Civil', 'semester': 6, 'credits': 3},
                # Mathematics
                {'subject_code': 'MA101', 'subject_name': 'Calculus I', 'course': 'Mathematics', 'semester': 1, 'credits': 4},
                {'subject_code': 'MA102', 'subject_name': 'Calculus II', 'course': 'Mathematics', 'semester': 2, 'credits': 4},
                {'subject_code': 'MA201', 'subject_name': 'Linear Algebra', 'course': 'Mathematics', 'semester': 3, 'credits': 3},
                {'subject_code': 'MA202', 'subject_name': 'Differential Equations', 'course': 'Mathematics', 'semester': 4, 'credits': 3},
                {'subject_code': 'MA301', 'subject_name': 'Numerical Methods', 'course': 'Mathematics', 'semester': 5, 'credits': 4},
                {'subject_code': 'MA302', 'subject_name': 'Statistics', 'course': 'Mathematics', 'semester': 6, 'credits': 3},
            ]
            
            for subject_data in subjects_data:
                existing_subject = Subject.query.filter_by(subject_code=subject_data['subject_code']).first()
                
                if existing_subject:
                    continue
                
                subject = Subject(**subject_data)
                db.session.add(subject)
                logger.info(f"Created subject: {subject_data['subject_code']} - {subject_data['subject_name']} ({subject_data['course']})")
            
            db.session.commit()
            logger.info("Sample subjects created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample subjects: {str(e)}")
        db.session.rollback()
        return False


def create_sample_library_books(app):
    """
    Create sample library books.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample library books...")
        
        with app.app_context():
            books_data = [
                {
                    'book_id': 'BK001',
                    'title': 'Introduction to Algorithms',
                    'author': 'Thomas H. Cormen',
                    'isbn': '978-0262033848',
                    'category': 'Computer Science',
                    'total_copies': 5
                },
                {
                    'book_id': 'BK002',
                    'title': 'Clean Code',
                    'author': 'Robert C. Martin',
                    'isbn': '978-0132350884',
                    'category': 'Software Engineering',
                    'total_copies': 3
                },
                {
                    'book_id': 'BK003',
                    'title': 'Database System Concepts',
                    'author': 'Abraham Silberschatz',
                    'isbn': '978-0078022159',
                    'category': 'Database',
                    'total_copies': 4
                },
                {
                    'book_id': 'BK004',
                    'title': 'Operating System Concepts',
                    'author': 'Abraham Silberschatz',
                    'isbn': '978-1119800361',
                    'category': 'Operating Systems',
                    'total_copies': 3
                },
                {
                    'book_id': 'BK005',
                    'title': 'Machine Learning',
                    'author': 'Tom Mitchell',
                    'isbn': '978-0070428072',
                    'category': 'Machine Learning',
                    'total_copies': 2
                }
            ]
            
            for book_data in books_data:
                existing_book = LibraryBook.query.filter_by(book_id=book_data['book_id']).first()
                
                if existing_book:
                    logger.info(f"Book {book_data['book_id']} already exists, skipping")
                    continue
                
                book = LibraryBook(
                    book_id=book_data['book_id'],
                    title=book_data['title'],
                    author=book_data['author'],
                    isbn=book_data.get('isbn'),
                    category=book_data.get('category'),
                    total_copies=book_data['total_copies'],
                    available_copies=book_data['total_copies']
                )
                db.session.add(book)
                logger.info(f"Created book: {book_data['book_id']} - {book_data['title']}")
            
            db.session.commit()
            logger.info("Sample library books created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample library books: {str(e)}")
        db.session.rollback()
        return False


def load_sample_marks(app):
    """
    Load sample marks records from CSV.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Loading sample marks...")
        
        csv_file = Path('datasets/marks_sample.csv')
        
        if not csv_file.exists():
            logger.warning("Marks CSV file not found, creating sample data")
            return create_sample_marks(app)
        
        with app.app_context():
            teacher = User.query.filter_by(role='teacher').first()
            
            if not teacher:
                logger.error("Teacher user not found")
                return False
            
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    student = Student.query.filter_by(student_id=row['student_id']).first()
                    
                    if not student:
                        continue
                    
                    subject_name = row['subject']
                    subject = Subject.query.filter(Subject.subject_name.ilike(f"%{subject_name}%")).first()
                    
                    if not subject:
                        continue
                    
                    existing = Marks.query.filter_by(
                        student_id=student.id,
                        subject_id=subject.id,
                        exam_type=row['exam_type'],
                        exam_date=datetime.strptime(row['exam_date'], '%Y-%m-%d').date()
                    ).first()
                    
                    if existing:
                        continue
                    
                    marks = Marks(
                        student_id=student.id,
                        subject_id=subject.id,
                        exam_type=row['exam_type'],
                        marks_obtained=float(row['marks_obtained']),
                        max_marks=float(row['max_marks']),
                        exam_date=datetime.strptime(row['exam_date'], '%Y-%m-%d').date(),
                        graded_by=teacher.id,
                        remarks=row.get('remarks')
                    )
                    db.session.add(marks)
                
                db.session.commit()
                logger.info("Sample marks loaded successfully")
                
        return True
    except Exception as e:
        logger.error(f"Error loading sample marks: {str(e)}")
        try:
            db.session.rollback()
        except:
            pass
        return False


def create_sample_marks(app):
    """
    Create sample marks records.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample marks...")
        
        with app.app_context():
            # Get teacher user
            teacher = User.query.filter_by(role='teacher').first()
            
            if not teacher:
                logger.error("Teacher user not found")
                return False
            
            # Get all students and subjects
            students = Student.query.all()
            subjects = Subject.query.all()
            
            if not students or not subjects:
                logger.error("No students or subjects found")
                return False
            
            exam_types = ['Midterm', 'Final', 'Assignment', 'Quiz']
            
            for student in students:
                for subject in subjects:
                    for exam_type in exam_types:
                        # Check if marks already exist
                        existing = Marks.query.filter_by(
                            student_id=student.id,
                            subject_id=subject.id,
                            exam_type=exam_type
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Random marks
                        import random
                        marks_obtained = random.randint(40, 100)
                        max_marks = 100
                        
                        marks = Marks(
                            student_id=student.id,
                            subject_id=subject.id,
                            exam_type=exam_type,
                            marks_obtained=marks_obtained,
                            max_marks=max_marks,
                            exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                            graded_by=teacher.id,
                            remarks='Sample marks'
                        )
                        db.session.add(marks)
            
            db.session.commit()
            logger.info("Sample marks created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample marks: {str(e)}")
        db.session.rollback()
        return False


def load_sample_fees(app):
    """
    Load sample fee records.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Loading sample fees...")
        
        csv_file = Path('datasets/fees_sample.csv')
        
        if not csv_file.exists():
            logger.warning("Fees CSV file not found, creating sample data")
            return create_sample_fees(app)
        
        with app.app_context():
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Get student
                    student = Student.query.filter_by(student_id=row['student_id']).first()
                    
                    if not student:
                        logger.warning(f"Student {row['student_id']} not found, skipping")
                        continue
                    
                    # Check if fee already exists
                    existing = Fee.query.filter_by(
                        student_id=student.id,
                        fee_type=row['fee_type'],
                        due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Create fee
                    fee = Fee(
                        student_id=student.id,
                        fee_type=row['fee_type'],
                        amount=float(row['amount']),
                        due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date(),
                        status=row['status'],
                        paid_date=datetime.strptime(row['paid_date'], '%Y-%m-%d').date() if row.get('paid_date') else None,
                        payment_method=row.get('payment_method'),
                        transaction_id=row.get('transaction_id'),
                        receipt_number=row.get('receipt_number')
                    )
                    db.session.add(fee)
                
                db.session.commit()
                logger.info("Sample fees loaded successfully")
                
        return True
    except Exception as e:
        logger.error(f"Error loading sample fees: {str(e)}")
        db.session.rollback()
        return False


def create_sample_fees(app):
    """
    Create sample fee records.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample fees...")
        
        with app.app_context():
            # Get all students
            students = Student.query.all()
            
            if not students:
                logger.error("No students found")
                return False
            
            fee_types = ['Tuition', 'Library', 'Laboratory', 'Hostel']
            
            for student in students:
                for fee_type in fee_types:
                    # Check if fee already exists
                    existing = Fee.query.filter_by(
                        student_id=student.id,
                        fee_type=fee_type
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Random fee data
                    import random
                    amount = random.randint(500, 2000)
                    due_date = date.today() + timedelta(days=random.randint(-30, 30))
                    status = random.choice(['Pending', 'Paid', 'Overdue'])
                    
                    fee = Fee(
                        student_id=student.id,
                        fee_type=fee_type,
                        amount=amount,
                        due_date=due_date,
                        status=status,
                        paid_date=date.today() if status == 'Paid' else None,
                        payment_method='Cash' if status == 'Paid' else None,
                        transaction_id=f'TXN{random.randint(1000, 9999)}' if status == 'Paid' else None,
                        receipt_number=f'RCP{random.randint(1000, 9999)}' if status == 'Paid' else None
                    )
                    db.session.add(fee)
            
            db.session.commit()
            logger.info("Sample fees created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample fees: {str(e)}")
        db.session.rollback()
        return False


def create_sample_complaints(app):
    """
    Create sample complaints.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample complaints...")
        
        with app.app_context():
            # Get all students
            students = Student.query.all()
            
            if not students:
                logger.error("No students found")
                return False
            
            complaints_data = [
                {
                    'subject': 'Library Access Issue',
                    'description': 'Cannot access online library resources',
                    'category': 'Infrastructure',
                    'priority': 'Medium',
                    'status': 'Open'
                },
                {
                    'subject': 'Course Material Missing',
                    'description': 'Course material not uploaded to portal',
                    'category': 'Academic',
                    'priority': 'High',
                    'status': 'In Progress'
                },
                {
                    'subject': 'Fee Payment Problem',
                    'description': 'Payment gateway not working',
                    'category': 'Administrative',
                    'priority': 'Urgent',
                    'status': 'Open'
                },
                {
                    'subject': 'Classroom Equipment',
                    'description': 'Projector not working in classroom',
                    'category': 'Infrastructure',
                    'priority': 'Low',
                    'status': 'Resolved'
                }
            ]
            
            for student in students:
                for complaint_data in complaints_data:
                    # Check if complaint already exists
                    existing = Complaint.query.filter_by(
                        student_id=student.id,
                        subject=complaint_data['subject']
                    ).first()
                    
                    if existing:
                        continue
                    
                    complaint = Complaint(
                        student_id=student.id,
                        **complaint_data
                    )
                    db.session.add(complaint)
            
            db.session.commit()
            logger.info("Sample complaints created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample complaints: {str(e)}")
        db.session.rollback()
        return False


def create_sample_ml_model(app):
    """
    Create a sample ML model.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample ML model...")
        
        with app.app_context():
            existing_model = MLModel.query.filter_by(model_name="Student Risk Predictor").first()
            
            if existing_model:
                logger.info("ML model already exists, skipping")
                return True
            
            ml_model = MLModel(
                model_name="Student Risk Predictor",
                model_version="1.0.0",
                algorithm="Random Forest",
                accuracy=0.85,
                precision_score=0.83,
                recall_score=0.87,
                f1_score=0.85,
                training_date=datetime.now(),
                is_active=True
            )
            db.session.add(ml_model)
            db.session.commit()
            logger.info("Sample ML model created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample ML model: {str(e)}")
        db.session.rollback()
        return False


def create_sample_predictions(app):
    """
    Create sample predictions for students based on risk calculation logic.
    Creates specific distribution: 50 low risk, 10 high risk, 1 critical risk.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample predictions...")
        
        import random
        
        with app.app_context():
            ml_model = MLModel.query.filter_by(is_active=True).first()
            
            if not ml_model:
                logger.error("No active ML model found")
                return False
            
            students = Student.query.all()
            
            if not students:
                logger.error("No students found")
                return False
            
            teacher = User.query.filter_by(role='teacher').first()
            subjects = Subject.query.all()
            
            student_ids_by_risk = {
                'low': [],
                'high': [],
                'critical': []
            }
            
            for i, student in enumerate(students):
                if i < 1:
                    student_ids_by_risk['critical'].append(student.id)
                elif i < 11:
                    student_ids_by_risk['high'].append(student.id)
                elif i < 61:
                    student_ids_by_risk['low'].append(student.id)
            
            logger.info(f"Creating risk distribution: {len(student_ids_by_risk['low'])} low, {len(student_ids_by_risk['high'])} high, {len(student_ids_by_risk['critical'])} critical")
            
            for student in students:
                existing = Prediction.query.filter_by(student_id=student.id).first()
                
                if existing:
                    continue
                
                if student.id in student_ids_by_risk['critical']:
                    risk_level = "Critical"
                    risk_score = 0.95
                    attendance_percentage = random.uniform(20, 35)
                    avg_marks = random.uniform(15, 30)
                    fee_status = "Overdue"
                    has_overdue = True
                    has_pending = False
                elif student.id in student_ids_by_risk['high']:
                    risk_level = "High"
                    risk_score = 0.8
                    attendance_percentage = random.uniform(30, 50)
                    avg_marks = random.uniform(25, 45)
                    fee_status = "Overdue"
                    has_overdue = True
                    has_pending = False
                elif student.id in student_ids_by_risk['low']:
                    risk_level = "Low"
                    risk_score = 0.2
                    attendance_percentage = random.uniform(85, 98)
                    avg_marks = random.uniform(75, 95)
                    fee_status = "Paid"
                    has_overdue = False
                    has_pending = False
                else:
                    attendances = Attendance.query.filter_by(student_id=student.id).all()
                    present_count = sum(1 for a in attendances if a.status == 'Present')
                    total_attendance = len(attendances)
                    attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
                    
                    marks_records = Marks.query.filter_by(student_id=student.id).all()
                    avg_marks = sum(m.marks_obtained for m in marks_records) / len(marks_records) if marks_records else 0
                    
                    fees = Fee.query.filter_by(student_id=student.id).all()
                    has_overdue = any(f.status == 'Overdue' for f in fees)
                    has_pending = any(f.status in ['Pending', 'Overdue'] for f in fees)
                    
                    if attendance_percentage < 50 or avg_marks < 40 or has_overdue:
                        risk_level = "High"
                        risk_score = 0.8
                        fee_status = "Overdue"
                    elif attendance_percentage < 75 or avg_marks < 60 or has_pending:
                        risk_level = "Medium"
                        risk_score = 0.5
                        fee_status = "Pending" if has_pending else "Paid"
                    else:
                        risk_level = "Low"
                        risk_score = 0.2
                        fee_status = "Paid"
                
                prediction = Prediction(
                    student_id=student.id,
                    model_id=ml_model.id,
                    risk_level=risk_level,
                    risk_score=risk_score,
                    probability=risk_score,
                    attendance_percentage=attendance_percentage,
                    average_marks=avg_marks,
                    fee_status=fee_status
                )
                db.session.add(prediction)
            
            db.session.commit()
            logger.info("Sample predictions created successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error creating sample predictions: {str(e)}")
        db.session.rollback()
        return False


def create_high_risk_students_data(app, ml_model):
    """
    Create specific high-risk students with poor attendance, low marks, and overdue fees.
    
    Args:
        app: Flask application instance
        ml_model: Active ML model
        
    Returns:
        List of created high-risk students
    """
    import random
    
    with app.app_context():
        teacher = User.query.filter_by(role='teacher').first()
        if not teacher:
            logger.warning("No teacher found, skipping high-risk student creation")
            return []
        
        subjects = Subject.query.all()
        high_risk_student_ids = []
        
        # Create 5 specific high-risk students
        high_risk_data = [
            {
                'student_id': 'HR001',
                'first_name': 'Alex',
                'last_name': 'Thompson',
                'course': 'Computer Science',
                'semester': 3
            },
            {
                'student_id': 'HR002',
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'course': 'Electronics',
                'semester': 4
            },
            {
                'student_id': 'HR003',
                'first_name': 'John',
                'last_name': 'Miller',
                'course': 'Mechanical',
                'semester': 5
            },
            {
                'student_id': 'HR004',
                'first_name': 'Sarah',
                'last_name': 'Wilson',
                'course': 'Mathematics',
                'semester': 2
            },
            {
                'student_id': 'HR005',
                'first_name': 'David',
                'last_name': 'Brown',
                'course': 'Civil',
                'semester': 4
            }
        ]
        
        for data in high_risk_data:
            # Check if student already exists
            student = Student.query.filter_by(student_id=data['student_id']).first()
            
            if not student:
                # Create user
                user = User(
                    username=data['student_id'],
                    email=f"{data['student_id']}@student.edu",
                    password='student123',
                    role='student',
                    is_active=True
                )
                db.session.add(user)
                db.session.flush()
                
                # Create student
                student = Student(
                    user_id=user.id,
                    student_id=data['student_id'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    date_of_birth=date(2002, random.randint(1, 12), random.randint(1, 28)),
                    gender=random.choice(['Male', 'Female']),
                    course=data['course'],
                    semester=data['semester'],
                    admission_date=date(2023, 8, 1),
                    phone=f"{random.randint(1000000000, 9999999999)}",
                    address=f"{random.randint(1, 999)} Main St",
                    guardian_name="Mr. Thompson",
                    guardian_phone=f"{random.randint(1000000000, 9999999999)}"
                )
                db.session.add(student)
                db.session.flush()
                logger.info(f"Created high-risk student: {data['student_id']}")
            
            high_risk_student_ids.append(student.id)
            
            # Create poor attendance (less than 50%)
            for i in range(30):
                attendance_date = date.today() - timedelta(days=i)
                existing = Attendance.query.filter_by(
                    student_id=student.id,
                    date=attendance_date
                ).first()
                
                if existing:
                    continue
                
                # 70% absent for high-risk students
                status = random.choice(['Absent', 'Absent', 'Absent', 'Late', 'Present'])
                
                attendance = Attendance(
                    student_id=student.id,
                    date=attendance_date,
                    status=status,
                    marked_by=teacher.id,
                    remarks='High-risk student attendance'
                )
                db.session.add(attendance)
            
            # Create low marks (below 40)
            valid_exam_types = ['Midterm', 'Final', 'Assignment', 'Quiz', 'Project']
            for subject in subjects:
                for exam_type in valid_exam_types[:3]:  # Use only first 3 valid types
                    existing = Marks.query.filter_by(
                        student_id=student.id,
                        subject_id=subject.id,
                        exam_type=exam_type
                    ).first()
                    
                    if existing:
                        continue
                    
                    marks_obtained = random.randint(20, 40)  # Low marks
                    
                    marks = Marks(
                        student_id=student.id,
                        subject_id=subject.id,
                        exam_type=exam_type,
                        marks_obtained=marks_obtained,
                        max_marks=100,
                        exam_date=date.today() - timedelta(days=random.randint(1, 90)),
                        graded_by=teacher.id,
                        remarks='Below average performance'
                    )
                    db.session.add(marks)
            
            # Create overdue fees
            fee_types = ['Tuition', 'Laboratory', 'Hostel']
            for fee_type in fee_types:
                existing = Fee.query.filter_by(
                    student_id=student.id,
                    fee_type=fee_type
                ).first()
                
                if existing:
                    continue
                
                fee = Fee(
                    student_id=student.id,
                    fee_type=fee_type,
                    amount=random.randint(1000, 5000),
                    due_date=date.today() - timedelta(days=random.randint(30, 90)),
                    status='Overdue',
                    paid_date=None,
                    payment_method=None,
                    transaction_id=None,
                    receipt_number=None
                )
                db.session.add(fee)
            
            db.session.commit()
        
        return high_risk_student_ids


def create_sample_alerts(app):
    """
    Create sample alerts.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample alerts...")
        
        with app.app_context():
            # Get all students
            students = Student.query.all()
            
            if not students:
                logger.error("No students found")
                return False
            
            alerts_data = [
                {
                    'alert_type': 'Attendance',
                    'severity': 'Warning',
                    'message': 'Attendance below 75%',
                    'suggestion': 'Attend classes regularly',
                    'is_read': False
                },
                {
                    'alert_type': 'Academic',
                    'severity': 'Critical',
                    'message': 'Marks below passing threshold',
                    'suggestion': 'Seek academic support',
                    'is_read': False
                },
                {
                    'alert_type': 'Fee',
                    'severity': 'Warning',
                    'message': 'Fee payment overdue',
                    'suggestion': 'Pay fees immediately',
                    'is_read': True
                },
                {
                    'alert_type': 'General',
                    'severity': 'Info',
                    'message': 'New course registration open',
                    'suggestion': 'Register before deadline',
                    'is_read': False
                }
            ]
            
            for student in students:
                for alert_data in alerts_data:
                    # Check if alert already exists
                    existing = Alert.query.filter_by(
                        student_id=student.id,
                        alert_type=alert_data['alert_type'],
                        message=alert_data['message']
                    ).first()
                    
                    if existing:
                        continue
                    
                    alert = Alert(
                        student_id=student.id,
                        **alert_data
                    )
                    db.session.add(alert)
            
            db.session.commit()
            logger.info("Sample alerts created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample alerts: {str(e)}")
        db.session.rollback()
        return False


def main():
    """Main function to seed data."""
    print("\n" + "="*60)
    print("Data Seeding - Student Risk Monitoring System")
    print("="*60 + "\n")
    
    # Create Flask app
    app = create_app('development')
    
    # Seeding steps
    steps = [
        ("Creating sample users", create_sample_users),
        ("Creating sample subjects", create_sample_subjects),
        ("Creating sample library books", create_sample_library_books),
        ("Creating sample ML model", create_sample_ml_model),
        ("Loading sample students", load_sample_students),
        ("Loading sample attendance", load_sample_attendance),
        ("Loading sample marks", load_sample_marks),
        ("Loading sample fees", load_sample_fees),
        ("Creating sample predictions", create_sample_predictions),
        ("Creating sample complaints", create_sample_complaints),
        ("Creating sample alerts", create_sample_alerts)
    ]
    
    success = True
    
    for step_name, step_function in steps:
        print(f"\n{'='*60}")
        print(f"Step: {step_name}")
        print(f"{'='*60}\n")
        
        if not step_function(app):
            logger.error(f"Failed at step: {step_name}")
            success = False
            break
    
    # Print summary
    print("\n" + "="*60)
    print("Data Seeding Summary")
    print("="*60)
    
    if success:
        print("[OK] Data seeding completed successfully")
        
        with app.app_context():
            users = User.query.count()
            subjects = Subject.query.count()
            students = Student.query.count()
            attendance = Attendance.query.count()
            marks = Marks.query.count()
            fees = Fee.query.count()
            complaints = Complaint.query.count()
            alerts = Alert.query.count()
            library_books = LibraryBook.query.count()
            ml_models = MLModel.query.count()
            predictions = Prediction.query.count()
            
            print(f"\nData summary:")
            print(f"  Users: {users}")
            print(f"  Subjects: {subjects}")
            print(f"  Students: {students}")
            print(f"  Attendance records: {attendance}")
            print(f"  Marks records: {marks}")
            print(f"  Fee records: {fees}")
            print(f"  Complaints: {complaints}")
            print(f"  Alerts: {alerts}")
            print(f"  Library books: {library_books}")
            print(f"  ML Models: {ml_models}")
            print(f"  Predictions: {predictions}")
        
        return 0
    else:
        print("[X] Data seeding failed")
        print("Check seed_data.log for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
