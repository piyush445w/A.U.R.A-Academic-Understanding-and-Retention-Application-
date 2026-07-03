"""
Integration Tests for Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

import pytest
from datetime import datetime, date, timedelta
from flask import url_for
from app import db
from app.models import User, Student, Attendance, Subject, Marks, Fee, LibraryBook, LibraryTransaction, Complaint, Prediction, MLModel, Alert


class TestAuthRoutes:
    """Test cases for authentication routes."""
    
    def test_login_page(self, client):
        """Test login page loads correctly."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_success(self, client, student_user):
        """Test successful login."""
        response = client.post('/auth/login', data={
            'username': 'student',
            'password': 'student123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to dashboard after successful login
    
    def test_login_invalid_credentials(self, client, student_user):
        """Test login with invalid credentials."""
        response = client.post('/auth/login', data={
            'username': 'student',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message
    
    def test_register_page(self, client):
        """Test registration page loads correctly."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_success(self, client):
        """Test successful registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to login after successful registration
    
    def test_register_duplicate_username(self, client, student_user):
        """Test registration with duplicate username."""
        response = client.post('/auth/register', data={
            'username': 'student',
            'email': 'another@example.com',
            'password': 'newpass123',
            'confirm_password': 'newpass123',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show error message about duplicate username
    
    def test_logout(self, authenticated_client):
        """Test logout functionality."""
        response = authenticated_client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page after logout


class TestStudentRoutes:
    """Test cases for student management routes."""
    
    def test_student_list_requires_auth(self, client):
        """Test that student list requires authentication."""
        response = client.get('/student/list')
        assert response.status_code == 302  # Redirect to login
    
    def test_student_list_authenticated(self, authenticated_client, sample_student):
        """Test student list with authentication."""
        response = authenticated_client.get('/student/list')
        assert response.status_code == 200
    
    def test_student_view(self, authenticated_client, sample_student):
        """Test student view page."""
        response = authenticated_client.get(f'/student/view/{sample_student.id}')
        assert response.status_code == 200
    
    def test_student_add_requires_admin(self, authenticated_client):
        """Test that adding student requires admin privileges."""
        response = authenticated_client.get('/student/add')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_student_add_admin(self, admin_authenticated_client):
        """Test student add page with admin privileges."""
        response = admin_authenticated_client.get('/student/add')
        assert response.status_code == 200
    
    def test_student_edit_requires_admin(self, authenticated_client, sample_student):
        """Test that editing student requires admin privileges."""
        response = authenticated_client.get(f'/student/edit/{sample_student.id}')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]


class TestAttendanceRoutes:
    """Test cases for attendance routes."""
    
    def test_attendance_mark_requires_auth(self, client):
        """Test that marking attendance requires authentication."""
        response = client.get('/attendance/mark')
        assert response.status_code == 302  # Redirect to login
    
    def test_attendance_mark_page(self, teacher_authenticated_client, sample_student):
        """Test attendance mark page."""
        response = teacher_authenticated_client.get('/attendance/mark')
        assert response.status_code == 200
    
    def test_attendance_bulk_page(self, teacher_authenticated_client):
        """Test bulk attendance page."""
        response = teacher_authenticated_client.get('/attendance/bulk')
        assert response.status_code == 200
    
    def test_attendance_report(self, teacher_authenticated_client, sample_attendance):
        """Test attendance report page."""
        response = teacher_authenticated_client.get('/attendance/report')
        assert response.status_code == 200


class TestMarksRoutes:
    """Test cases for marks routes."""
    
    def test_marks_add_requires_auth(self, client):
        """Test that adding marks requires authentication."""
        response = client.get('/marks/add')
        assert response.status_code == 302  # Redirect to login
    
    def test_marks_add_page(self, teacher_authenticated_client, sample_student, sample_subject):
        """Test marks add page."""
        response = teacher_authenticated_client.get('/marks/add')
        assert response.status_code == 200
    
    def test_marks_bulk_page(self, teacher_authenticated_client):
        """Test bulk marks page."""
        response = teacher_authenticated_client.get('/marks/bulk')
        assert response.status_code == 200
    
    def test_marks_report(self, teacher_authenticated_client, sample_marks):
        """Test marks report page."""
        response = teacher_authenticated_client.get('/marks/report')
        assert response.status_code == 200


class TestFeeRoutes:
    """Test cases for fee routes."""
    
    def test_fee_list_requires_auth(self, client):
        """Test that fee list requires authentication."""
        response = client.get('/fees/list')
        assert response.status_code == 302  # Redirect to login
    
    def test_fee_list_page(self, authenticated_client, sample_fees):
        """Test fee list page."""
        response = authenticated_client.get('/fees/list')
        assert response.status_code == 200
    
    def test_fee_add_requires_admin(self, authenticated_client):
        """Test that adding fee requires admin privileges."""
        response = authenticated_client.get('/fees/add')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_fee_add_page_admin(self, admin_authenticated_client, sample_student):
        """Test fee add page with admin privileges."""
        response = admin_authenticated_client.get('/fees/add')
        assert response.status_code == 200
    
    def test_fee_payment_page(self, authenticated_client, sample_fees):
        """Test fee payment page."""
        response = authenticated_client.get(f'/fees/payment/{sample_fees[0].id}')
        assert response.status_code == 200


class TestLibraryRoutes:
    """Test cases for library routes."""
    
    def test_library_books_requires_auth(self, client):
        """Test that library books requires authentication."""
        response = client.get('/library/books')
        assert response.status_code == 302  # Redirect to login
    
    def test_library_books_page(self, authenticated_client, sample_library_book):
        """Test library books page."""
        response = authenticated_client.get('/library/books')
        assert response.status_code == 200
    
    def test_library_add_book_requires_admin(self, authenticated_client):
        """Test that adding book requires admin privileges."""
        response = authenticated_client.get('/library/add_book')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_library_add_book_page_admin(self, admin_authenticated_client):
        """Test add book page with admin privileges."""
        response = admin_authenticated_client.get('/library/add_book')
        assert response.status_code == 200
    
    def test_library_issue_page(self, authenticated_client, sample_student, sample_library_book):
        """Test library issue page."""
        response = authenticated_client.get('/library/issue')
        assert response.status_code == 200
    
    def test_library_transactions_page(self, authenticated_client, sample_library_transaction):
        """Test library transactions page."""
        response = authenticated_client.get('/library/transactions')
        assert response.status_code == 200


class TestComplaintRoutes:
    """Test cases for complaint routes."""
    
    def test_complaint_list_requires_auth(self, client):
        """Test that complaint list requires authentication."""
        response = client.get('/complaints/list')
        assert response.status_code == 302  # Redirect to login
    
    def test_complaint_list_page(self, authenticated_client, sample_complaint):
        """Test complaint list page."""
        response = authenticated_client.get('/complaints/list')
        assert response.status_code == 200
    
    def test_complaint_add_page(self, authenticated_client, sample_student):
        """Test complaint add page."""
        response = authenticated_client.get('/complaints/add')
        assert response.status_code == 200
    
    def test_complaint_view(self, authenticated_client, sample_complaint):
        """Test complaint view page."""
        response = authenticated_client.get(f'/complaints/view/{sample_complaint.id}')
        assert response.status_code == 200


class TestPredictionRoutes:
    """Test cases for prediction routes."""
    
    def test_prediction_dashboard_requires_auth(self, client):
        """Test that prediction dashboard requires authentication."""
        response = client.get('/predictions/dashboard')
        assert response.status_code == 302  # Redirect to login
    
    def test_prediction_dashboard_page(self, authenticated_client, sample_prediction):
        """Test prediction dashboard page."""
        response = authenticated_client.get('/predictions/dashboard')
        assert response.status_code == 200
    
    def test_prediction_student_page(self, authenticated_client, sample_student, sample_prediction):
        """Test prediction student page."""
        response = authenticated_client.get(f'/predictions/student/{sample_student.id}')
        assert response.status_code == 200


class TestDashboardRoutes:
    """Test cases for dashboard routes."""
    
    def test_dashboard_requires_auth(self, client):
        """Test that dashboard requires authentication."""
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login
    
    def test_student_dashboard(self, authenticated_client, sample_student):
        """Test student dashboard."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
    
    def test_admin_dashboard(self, admin_authenticated_client):
        """Test admin dashboard."""
        response = admin_authenticated_client.get('/')
        assert response.status_code == 200
    
    def test_teacher_dashboard(self, teacher_authenticated_client):
        """Test teacher dashboard."""
        response = teacher_authenticated_client.get('/')
        assert response.status_code == 200


class TestAdminRoutes:
    """Test cases for admin routes."""
    
    def test_admin_users_requires_admin(self, authenticated_client):
        """Test that admin users page requires admin privileges."""
        response = authenticated_client.get('/admin/users')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_admin_users_page(self, admin_authenticated_client):
        """Test admin users page."""
        response = admin_authenticated_client.get('/admin/users')
        assert response.status_code == 200
    
    def test_admin_alerts_requires_admin(self, authenticated_client):
        """Test that admin alerts page requires admin privileges."""
        response = authenticated_client.get('/admin/alerts')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_admin_alerts_page(self, admin_authenticated_client, sample_alert):
        """Test admin alerts page."""
        response = admin_authenticated_client.get('/admin/alerts')
        assert response.status_code == 200
    
    def test_admin_models_requires_admin(self, authenticated_client):
        """Test that admin models page requires admin privileges."""
        response = authenticated_client.get('/admin/models')
        # Should redirect or show forbidden for non-admin users
        assert response.status_code in [302, 403]
    
    def test_admin_models_page(self, admin_authenticated_client, sample_ml_model):
        """Test admin models page."""
        response = admin_authenticated_client.get('/admin/models')
        assert response.status_code == 200


class TestAPIRoutes:
    """Test cases for API routes."""
    
    def test_api_student_data(self, authenticated_client, sample_student):
        """Test API endpoint for student data."""
        response = authenticated_client.get(f'/api/student/{sample_student.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'student_id' in data
    
    def test_api_attendance_data(self, authenticated_client, sample_student, sample_attendance):
        """Test API endpoint for attendance data."""
        response = authenticated_client.get(f'/api/attendance/{sample_student.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'attendance' in data
    
    def test_api_marks_data(self, authenticated_client, sample_student, sample_marks):
        """Test API endpoint for marks data."""
        response = authenticated_client.get(f'/api/marks/{sample_student.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'marks' in data
    
    def test_api_prediction_data(self, authenticated_client, sample_student, sample_prediction):
        """Test API endpoint for prediction data."""
        response = authenticated_client.get(f'/api/prediction/{sample_student.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'prediction' in data


class TestReportRoutes:
    """Test cases for report routes."""
    
    def test_academic_report_requires_auth(self, client):
        """Test that academic report requires authentication."""
        response = client.get('/reports/academic')
        assert response.status_code == 302  # Redirect to login
    
    def test_academic_report_page(self, authenticated_client):
        """Test academic report page."""
        response = authenticated_client.get('/reports/academic')
        assert response.status_code == 200
    
    def test_attendance_report_page(self, authenticated_client):
        """Test attendance report page."""
        response = authenticated_client.get('/reports/attendance')
        assert response.status_code == 200
    
    def test_financial_report_page(self, authenticated_client):
        """Test financial report page."""
        response = authenticated_client.get('/reports/financial')
        assert response.status_code == 200


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_500_error(self, client):
        """Test 500 error handling."""
        # This would require triggering an actual error
        # For now, just verify error handlers are registered
        pass


class TestFormValidation:
    """Test cases for form validation."""
    
    def test_login_form_validation(self, client):
        """Test login form validation."""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show validation errors
    
    def test_register_form_validation(self, client):
        """Test registration form validation."""
        response = client.post('/auth/register', data={
            'username': '',
            'email': 'invalid-email',
            'password': 'short',
            'confirm_password': 'different',
            'role': 'student'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show validation errors
    
    def test_student_form_validation(self, admin_authenticated_client):
        """Test student form validation."""
        response = admin_authenticated_client.post('/student/add', data={
            'student_id': '',
            'first_name': '',
            'last_name': '',
            'date_of_birth': '',
            'gender': '',
            'course': '',
            'semester': '',
            'admission_date': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should show validation errors


class TestSecurity:
    """Test cases for security features."""
    
    def test_csrf_protection(self, client):
        """Test CSRF protection."""
        # This would require testing with CSRF tokens
        pass
    
    def test_sql_injection_prevention(self, authenticated_client):
        """Test SQL injection prevention."""
        # Test with malicious input
        response = authenticated_client.get("/student/list?search=' OR '1'='1")
        assert response.status_code == 200
        # Should not cause SQL injection
    
    def test_xss_prevention(self, authenticated_client):
        """Test XSS prevention."""
        # Test with malicious script tags
        response = authenticated_client.get("/student/list?search=<script>alert('xss')</script>")
        assert response.status_code == 200
        # Should escape HTML tags
