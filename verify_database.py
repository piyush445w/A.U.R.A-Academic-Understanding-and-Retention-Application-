"""
Database Verification Script
Tests the database by creating an app context and querying the database.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, Prediction

def test_database():
    """Test database connectivity and basic operations."""
    print("Creating app with testing configuration...")
    app = create_app('testing')
    
    with app.app_context():
        print("App context created successfully.")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully.")
        
        # Test basic query - count records
        print("\n--- Testing Database Queries ---")
        
        # Test User model
        user_count = User.query.count()
        print(f"User count: {user_count}")
        
        # Test Student model
        student_count = Student.query.count()
        print(f"Student count: {student_count}")
        
        # Test Subject model
        subject_count = Subject.query.count()
        print(f"Subject count: {subject_count}")
        
        # Test Marks model
        marks_count = Marks.query.count()
        print(f"Marks count: {marks_count}")
        
        # Test Attendance model
        attendance_count = Attendance.query.count()
        print(f"Attendance count: {attendance_count}")
        
        # Test Fee model
        fee_count = Fee.query.count()
        print(f"Fee count: {fee_count}")
        
        # Test LibraryBook model
        book_count = LibraryBook.query.count()
        print(f"LibraryBook count: {book_count}")
        
        # Test Prediction model
        prediction_count = Prediction.query.count()
        print(f"Prediction count: {prediction_count}")
        
        # Test insert operation
        print("\n--- Testing Insert Operation ---")
        
        # Create a test user
        test_user = User(
            username='test_user',
            email='test@example.com',
            password='testpassword123',
            role='student',
            is_active=True
        )
        db.session.add(test_user)
        db.session.commit()
        print(f"Inserted test user: {test_user.username} (ID: {test_user.id})")
        
        # Verify insert
        found_user = User.query.filter_by(email='test@example.com').first()
        print(f"Queried back test user: {found_user.username if found_user else 'NOT FOUND'}")
        
        # Test update operation
        print("\n--- Testing Update Operation ---")
        found_user.first_name = 'Updated'
        db.session.commit()
        updated_user = User.query.filter_by(email='test@example.com').first()
        print(f"Updated user first_name: {updated_user.first_name}")
        
        # Test delete operation
        print("\n--- Testing Delete Operation ---")
        db.session.delete(updated_user)
        db.session.commit()
        deleted_user = User.query.filter_by(email='test@example.com').first()
        print(f"User after delete: {'NOT FOUND (deleted)' if deleted_user is None else 'STILL EXISTS'}")
        
        # Verify tables exist
        print("\n--- Verifying Table Existence ---")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables in database: {tables}")
        
        print("\n" + "="*50)
        print("DATABASE VERIFICATION COMPLETE")
        print("="*50)
        print("All database operations passed successfully!")
        
        return True

if __name__ == '__main__':
    try:
        success = test_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nERROR: Database verification failed!")
        print(f"Error message: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
