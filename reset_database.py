#!/usr/bin/env python3
"""
Database Reset Script
Intelligent Student Risk Monitoring & Decision Support System

This script resets the database and recreates all users with properly hashed passwords.
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert, ActivityLog


def reset_database():
    """Reset the database and recreate default users."""
    print("\n" + "=" * 60)
    print("Database Reset - Student Risk Monitoring System")
    print("=" * 60 + "\n")

    app = create_app('development')

    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        print("All tables dropped.\n")

        # Recreate all tables
        print("Creating all tables...")
        db.create_all()
        print("All tables created.\n")

        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@studentrisk.edu',
            password='admin123',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        print(f"  Admin: admin / admin123\n")

        # Create teacher users
        print("Creating teacher users...")
        teacher1 = User(
            username='teacher1',
            email='teacher1@studentrisk.edu',
            password='teacher123',
            role='teacher',
            is_active=True
        )
        teacher2 = User(
            username='teacher2',
            email='teacher2@studentrisk.edu',
            password='teacher123',
            role='teacher',
            is_active=True
        )
        db.session.add_all([teacher1, teacher2])
        print(f"  Teacher1: teacher1 / teacher123")
        print(f"  Teacher2: teacher2 / teacher123\n")

        # Create sample subjects
        print("Creating sample subjects...")
        subjects_data = [
            {'subject_code': 'CS101', 'subject_name': 'Introduction to Programming', 'course': 'Computer Science', 'semester': 1, 'credits': 4},
            {'subject_code': 'CS102', 'subject_name': 'Data Structures', 'course': 'Computer Science', 'semester': 2, 'credits': 4},
            {'subject_code': 'CS201', 'subject_name': 'Database Management Systems', 'course': 'Computer Science', 'semester': 3, 'credits': 3},
            {'subject_code': 'EC101', 'subject_name': 'Basic Electronics', 'course': 'Electronics', 'semester': 1, 'credits': 4},
            {'subject_code': 'ME101', 'subject_name': 'Engineering Mechanics', 'course': 'Mechanical', 'semester': 1, 'credits': 4},
            {'subject_code': 'CE101', 'subject_name': 'Building Materials', 'course': 'Civil', 'semester': 1, 'credits': 4},
            {'subject_code': 'MA101', 'subject_name': 'Calculus I', 'course': 'Mathematics', 'semester': 1, 'credits': 4},
        ]
        for subject_data in subjects_data:
            subject = Subject(**subject_data)
            db.session.add(subject)
        print(f"  Created {len(subjects_data)} subjects.\n")

        # Create sample library books
        print("Creating sample library books...")
        books_data = [
            {'book_id': 'BK001', 'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'isbn': '978-0262033848', 'category': 'Computer Science', 'total_copies': 5, 'available_copies': 5},
            {'book_id': 'BK002', 'title': 'Clean Code', 'author': 'Robert C. Martin', 'isbn': '978-0132350884', 'category': 'Software Engineering', 'total_copies': 3, 'available_copies': 3},
            {'book_id': 'BK003', 'title': 'Database System Concepts', 'author': 'Abraham Silberschatz', 'isbn': '978-0078022159', 'category': 'Database', 'total_copies': 4, 'available_copies': 4},
        ]
        for book_data in books_data:
            book = LibraryBook(**book_data)
            db.session.add(book)
        print(f"  Created {len(books_data)} library books.\n")

        # Create sample ML model
        print("Creating sample ML model...")
        ml_model = MLModel(
            model_name="Student Risk Predictor",
            model_version="1.0.0",
            algorithm="Random Forest",
            accuracy=0.85,
            precision_score=0.83,
            recall_score=0.87,
            f1_score=0.85,
            is_active=True
        )
        db.session.add(ml_model)
        print("  Created ML model.\n")

        # Commit everything
        print("Committing changes...")
        db.session.commit()
        print("Database reset complete!\n")

        # Verify users
        print("Verifying users:")
        users = User.query.all()
        for user in users:
            print(f"  - {user.username} ({user.role}) - password_hash: {user.password_hash[:20]}...")

    print("\n" + "=" * 60)
    print("Reset complete! Default credentials:")
    print("  Admin:    admin / admin123")
    print("  Teacher:  teacher1 / teacher123")
    print("  Teacher:  teacher2 / teacher123")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    confirm = input("This will DELETE ALL DATA and reset the database. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Reset cancelled.")
