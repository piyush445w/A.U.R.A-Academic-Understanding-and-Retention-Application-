#!/usr/bin/env python3
"""
Database Setup Script
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import sys
import logging
from datetime import datetime, date

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup_database.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_database(app):
    """
    Create database tables.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        is_mysql = 'mysql' in db_uri
        
        logger.info(f"Creating database tables for {'MySQL' if is_mysql else 'SQLite'}...")
        
        with app.app_context():
            if not is_mysql:
                # SQLite dev: safe to drop/recreate
                db.drop_all()
                logger.info("Dropped existing SQLite tables")
            
            # Create all tables
            db.create_all()
            logger.info("Created all database tables")
            
            # Verify tables were created
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"DB tables: {', '.join(tables)}")
            
        return True
    except Exception as e:
        logger.error(f"Error creating database: {str(e)}")
        return False


def create_admin_user(app):
    """
    Create admin user.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating admin user...")
        
        with app.app_context():
            # Check if admin already exists
            admin = User.query.filter_by(username='admin').first()
            
            if admin:
                logger.info("Admin user already exists")
                return True
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@studentrisk.edu',
                password='admin123',
                role='admin',
                is_active=True
            )
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info(f"Created admin user: {admin.username} (ID: {admin.id})")
            
        return True
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.session.rollback()
        return False


def create_teacher_user(app):
    """
    Create teacher user.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating teacher user...")
        
        with app.app_context():
            # Check if teacher already exists
            teacher = User.query.filter_by(username='teacher').first()
            
            if teacher:
                logger.info("Teacher user already exists")
                return True
            
            # Create teacher user
            teacher = User(
                username='teacher',
                email='teacher@studentrisk.edu',
                password='teacher123',
                role='teacher',
                is_active=True
            )
            
            db.session.add(teacher)
            db.session.commit()
            
            logger.info(f"Created teacher user: {teacher.username} (ID: {teacher.id})")
            
        return True
    except Exception as e:
        logger.error(f"Error creating teacher user: {str(e)}")
        db.session.rollback()
        return False


def create_sample_subjects(app):
    """
    Create sample subjects.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample subjects...")
        
        with app.app_context():
            subjects_data = [
                {
                    'subject_code': 'CS101',
                    'subject_name': 'Introduction to Programming',
                    'course': 'Computer Science',
                    'semester': 1,
                    'credits': 3
                },
                {
                    'subject_code': 'CS102',
                    'subject_name': 'Data Structures',
                    'course': 'Computer Science',
                    'semester': 2,
                    'credits': 4
                },
                {
                    'subject_code': 'CS103',
                    'subject_name': 'Database Systems',
                    'course': 'Computer Science',
                    'semester': 3,
                    'credits': 3
                },
                {
                    'subject_code': 'MATH101',
                    'subject_name': 'Calculus I',
                    'course': 'Mathematics',
                    'semester': 1,
                    'credits': 4
                },
                {
                    'subject_code': 'ENG101',
                    'subject_name': 'English Composition',
                    'course': 'English',
                    'semester': 1,
                    'credits': 2
                }
            ]
            
            for subject_data in subjects_data:
                subject = Subject.query.filter_by(subject_code=subject_data['subject_code']).first()
                
                if not subject:
                    subject = Subject(**subject_data)
                    db.session.add(subject)
                    logger.info(f"Created subject: {subject_data['subject_name']}")
            
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
                    'title': 'Python Programming',
                    'author': 'John Smith',
                    'isbn': '978-0-123456-78-9',
                    'category': 'Programming',
                    'total_copies': 5,
                    'available_copies': 5
                },
                {
                    'book_id': 'BK002',
                    'title': 'Data Structures and Algorithms',
                    'author': 'Jane Doe',
                    'isbn': '978-0-234567-89-0',
                    'category': 'Computer Science',
                    'total_copies': 3,
                    'available_copies': 3
                },
                {
                    'book_id': 'BK003',
                    'title': 'Database Management Systems',
                    'author': 'Bob Johnson',
                    'isbn': '978-0-345678-90-1',
                    'category': 'Database',
                    'total_copies': 4,
                    'available_copies': 4
                },
                {
                    'book_id': 'BK004',
                    'title': 'Calculus Made Easy',
                    'author': 'Alice Williams',
                    'isbn': '978-0-456789-01-2',
                    'category': 'Mathematics',
                    'total_copies': 2,
                    'available_copies': 2
                },
                {
                    'book_id': 'BK005',
                    'title': 'English Grammar Guide',
                    'author': 'Charlie Brown',
                    'isbn': '978-0-567890-12-3',
                    'category': 'English',
                    'total_copies': 3,
                    'available_copies': 3
                }
            ]
            
            for book_data in books_data:
                book = LibraryBook.query.filter_by(book_id=book_data['book_id']).first()
                
                if not book:
                    book = LibraryBook(**book_data)
                    db.session.add(book)
                    logger.info(f"Created library book: {book_data['title']}")
            
            db.session.commit()
            logger.info("Sample library books created successfully")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample library books: {str(e)}")
        db.session.rollback()
        return False


def create_sample_ml_model(app):
    """
    Create sample ML model.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Creating sample ML model...")
        
        with app.app_context():
            # Check if model already exists
            model = MLModel.query.filter_by(model_name='risk_model_v1').first()
            
            if model:
                logger.info("Sample ML model already exists")
                return True
            
            # Create sample ML model
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
            
            logger.info(f"Created sample ML model: {model.model_name} v{model.model_version}")
            
        return True
    except Exception as e:
        logger.error(f"Error creating sample ML model: {str(e)}")
        db.session.rollback()
        return False


def run_schema_file(app):
    """
    Skip SQL schema file execution for SQLite since SQLAlchemy creates tables automatically.
    MySQL schema is handled by mysql_setup.py.
    
    Args:
        app: Flask application instance
        
    Returns:
        True always, as SQLite doesn't need schema file execution
    """
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    is_mysql = 'mysql' in db_uri
    
    if is_mysql:
        logger.info("MySQL: Schema already handled by mysql_setup.py, skipping")
    else:
        logger.info("SQLite: Tables created automatically by SQLAlchemy, skipping schema file")
    
    return True


def migrate_sqlite_columns(app):
    """
    Add missing columns to SQLite database for schema updates.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Only run for SQLite
        if 'mysql' in db_uri:
            return True
            
        logger.info("Running SQLite column migration...")
        
        with app.app_context():
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            
            # Get existing columns for predictions table
            if 'predictions' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('predictions')]
                
                # Add missing columns to predictions table
                # Note: SQLite has limited ALTER TABLE support, so we add columns without FK constraints
                migrations = [
                    ('override_by', 'ALTER TABLE predictions ADD COLUMN override_by INTEGER'),
                    ('is_manual', 'ALTER TABLE predictions ADD COLUMN is_manual INTEGER DEFAULT 0'),
                    ('override_reason', 'ALTER TABLE predictions ADD COLUMN override_reason TEXT'),
                    ('flag_for_review', 'ALTER TABLE predictions ADD COLUMN flag_for_review INTEGER DEFAULT 0'),
                    ('review_note', 'ALTER TABLE predictions ADD COLUMN review_note TEXT'),
                ]
                
                for col_name, sql in migrations:
                    if col_name not in columns:
                        try:
                            db.session.execute(text(sql))
                            db.session.commit()
                            logger.info(f"Added column: {col_name}")
                        except Exception as e:
                            # Column might already exist
                            db.session.rollback()
                            logger.debug(f"Column {col_name} migration: {str(e)}")
            
            logger.info("SQLite migration completed")
            
        return True
    except Exception as e:
        logger.error(f"Error during SQLite migration: {str(e)}")
        return True  # Return True to not block startup


def verify_database(app):
    """
    Verify database setup.
    
    Args:
        app: Flask application instance
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Verifying database setup...")
        
        with app.app_context():
            # Check if tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = [
                'users', 'students', 'attendance', 'subjects', 'marks',
                'fees', 'library_books', 'library_transactions', 'complaints',
                'predictions', 'ml_models', 'alerts', 'activity_log'
            ]
            
            missing_tables = [table for table in expected_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {', '.join(missing_tables)}")
                return False
            
            logger.info(f"All expected tables exist: {', '.join(tables)}")
            
            # Check if admin user exists
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                logger.error("Admin user not found")
                return False
            
            logger.info(f"Admin user exists: {admin.username}")
            
            # Check if subjects exist
            subjects = Subject.query.count()
            logger.info(f"Number of subjects: {subjects}")
            
            # Check if library books exist
            books = LibraryBook.query.count()
            logger.info(f"Number of library books: {books}")
            
            # Check if ML model exists
            models = MLModel.query.count()
            logger.info(f"Number of ML models: {models}")
            
        logger.info("Database verification completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error verifying database: {str(e)}")
        return False


def main():
    """Main function to setup database."""
    print("\n" + "="*60)
    print("Database Setup - Student Risk Monitoring System")
    print("="*60 + "\n")
    
    # Create Flask app
    app = create_app('development')
    
    # Setup steps
    steps = [
        ("Creating database tables", create_database),
        ("Running schema file", run_schema_file),
        ("Migrating SQLite columns", migrate_sqlite_columns),
        ("Creating admin user", create_admin_user),
        ("Creating teacher user", create_teacher_user),
        ("Creating sample subjects", create_sample_subjects),
        ("Creating sample library books", create_sample_library_books),
        ("Creating sample ML model", create_sample_ml_model),
        ("Verifying database", verify_database)
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
    print("Database Setup Summary")
    print("="*60)
    
    if success:
        print("[OK] Database setup completed successfully")
        print("\nDefault credentials:")
        print("  Admin: admin / admin123")
        print("  Teacher: teacher / teacher123")
        print("\nYou can now run the application using: python main.py")
        return 0
    else:
        print("[FAIL] Database setup failed")
        print("Check setup_database.log for details")
        return 1


if __name__ == '__main__':
    sys.exit(main())
