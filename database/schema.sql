-- =====================================================
-- Database Schema
-- Version: 1.0
-- Description: Comprehensive database schema for student
--              risk monitoring, academic tracking, and
--              decision support system
-- =====================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS student_risk_monitoring;
USE student_risk_monitoring;

-- =====================================================
-- DROP TABLES (in reverse order of dependencies)
-- =====================================================

DROP TABLE IF EXISTS activity_log;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS predictions;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS library_transactions;
DROP TABLE IF EXISTS library_books;
DROP TABLE IF EXISTS fees;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS subjects;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS ml_models;
DROP TABLE IF EXISTS users;

-- =====================================================
-- TABLE: users
-- Description: Stores user authentication and role information
-- =====================================================

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_users_username (username),
    INDEX idx_users_email (email),
    INDEX idx_users_role (role),
    INDEX idx_users_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE users COMMENT = 'Stores user authentication and role information for system access';

-- =====================================================
-- TABLE: ml_models
-- Description: Stores machine learning model metadata
-- =====================================================

CREATE TABLE ml_models (
    id INT PRIMARY KEY AUTO_INCREMENT,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(20) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    accuracy DECIMAL(5, 4),
    precision_score DECIMAL(5, 4),
    recall_score DECIMAL(5, 4),
    f1_score DECIMAL(5, 4),
    training_date TIMESTAMP NOT NULL,
    model_path VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_ml_models_name (model_name),
    INDEX idx_ml_models_version (model_version),
    INDEX idx_ml_models_is_active (is_active),
    INDEX idx_ml_models_training_date (training_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE ml_models COMMENT = 'Stores metadata for machine learning models used in risk prediction';

-- =====================================================
-- TABLE: students
-- Description: Stores student personal and academic information
-- =====================================================

CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    course VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    admission_date DATE NOT NULL,
    guardian_name VARCHAR(100),
    guardian_phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_students_user_id (user_id),
    INDEX idx_students_student_id (student_id),
    INDEX idx_students_course (course),
    INDEX idx_students_semester (semester),
    INDEX idx_students_admission_date (admission_date),
    INDEX idx_students_name (first_name, last_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE students COMMENT = 'Stores student personal and academic information';

-- =====================================================
-- TABLE: subjects
-- Description: Stores subject/course information
-- =====================================================

CREATE TABLE subjects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subject_code VARCHAR(20) NOT NULL UNIQUE,
    subject_name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_subjects_subject_code (subject_code),
    INDEX idx_subjects_course (course),
    INDEX idx_subjects_semester (semester)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE subjects COMMENT = 'Stores subject/course information and credit details';

-- =====================================================
-- TABLE: attendance
-- Description: Stores daily attendance records for students
-- =====================================================

CREATE TABLE attendance (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late', 'Excused') NOT NULL,
    marked_by INT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (marked_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Unique constraint to prevent duplicate attendance entries
    UNIQUE KEY uk_attendance_student_date (student_id, date),
    
    -- Indexes
    INDEX idx_attendance_student_id (student_id),
    INDEX idx_attendance_date (date),
    INDEX idx_attendance_status (status),
    INDEX idx_attendance_marked_by (marked_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE attendance COMMENT = 'Stores daily attendance records for students';

-- =====================================================
-- TABLE: marks
-- Description: Stores academic marks/grades for students
-- =====================================================

CREATE TABLE marks (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    exam_type ENUM('Midterm', 'Final', 'Assignment', 'Quiz', 'Project') NOT NULL,
    marks_obtained DECIMAL(5, 2) NOT NULL,
    max_marks DECIMAL(5, 2) NOT NULL,
    exam_date DATE NOT NULL,
    graded_by INT NOT NULL,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (graded_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    
    -- Check constraint to ensure marks are valid
    CONSTRAINT chk_marks_valid CHECK (marks_obtained >= 0 AND marks_obtained <= max_marks),
    
    -- Indexes
    INDEX idx_marks_student_id (student_id),
    INDEX idx_marks_subject_id (subject_id),
    INDEX idx_marks_exam_type (exam_type),
    INDEX idx_marks_exam_date (exam_date),
    INDEX idx_marks_graded_by (graded_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE marks COMMENT = 'Stores academic marks/grades for students across different exam types';

-- =====================================================
-- TABLE: fees
-- Description: Stores fee payment information for students
-- =====================================================

CREATE TABLE fees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    fee_type ENUM('Tuition', 'Library', 'Laboratory', 'Hostel', 'Other') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    due_date DATE NOT NULL,
    paid_date DATE,
    status ENUM('Pending', 'Paid', 'Overdue', 'Partial') NOT NULL DEFAULT 'Pending',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(100),
    receipt_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Check constraint to ensure amount is positive
    CONSTRAINT chk_fees_amount CHECK (amount > 0),
    
    -- Indexes
    INDEX idx_fees_student_id (student_id),
    INDEX idx_fees_fee_type (fee_type),
    INDEX idx_fees_due_date (due_date),
    INDEX idx_fees_status (status),
    INDEX idx_fees_paid_date (paid_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE fees COMMENT = 'Stores fee payment information and transaction details for students';

-- =====================================================
-- TABLE: library_books
-- Description: Stores library book inventory information
-- =====================================================

CREATE TABLE library_books (
    id INT PRIMARY KEY AUTO_INCREMENT,
    book_id VARCHAR(20) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(200) NOT NULL,
    isbn VARCHAR(20) UNIQUE,
    category VARCHAR(100),
    total_copies INT NOT NULL DEFAULT 1,
    available_copies INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Check constraint to ensure available copies don't exceed total
    CONSTRAINT chk_library_books_copies CHECK (available_copies >= 0 AND available_copies <= total_copies),
    
    -- Indexes
    INDEX idx_library_books_book_id (book_id),
    INDEX idx_library_books_title (title),
    INDEX idx_library_books_author (author),
    INDEX idx_library_books_isbn (isbn),
    INDEX idx_library_books_category (category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE library_books COMMENT = 'Stores library book inventory and availability information';

-- =====================================================
-- TABLE: library_transactions
-- Description: Stores library book issue and return records
-- =====================================================

CREATE TABLE library_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    book_id INT NOT NULL,
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    status ENUM('Issued', 'Returned', 'Overdue') NOT NULL DEFAULT 'Issued',
    fine_amount DECIMAL(10, 2) DEFAULT 0.00,
    issued_by INT NOT NULL,
    returned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (book_id) REFERENCES library_books(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (issued_by) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (returned_to) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Check constraint to ensure fine is non-negative
    CONSTRAINT chk_library_transactions_fine CHECK (fine_amount >= 0),
    
    -- Indexes
    INDEX idx_library_transactions_student_id (student_id),
    INDEX idx_library_transactions_book_id (book_id),
    INDEX idx_library_transactions_issue_date (issue_date),
    INDEX idx_library_transactions_due_date (due_date),
    INDEX idx_library_transactions_status (status),
    INDEX idx_library_transactions_issued_by (issued_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE library_transactions COMMENT = 'Stores library book issue and return transaction records';

-- =====================================================
-- TABLE: complaints
-- Description: Stores student complaints and their resolution status
-- =====================================================

CREATE TABLE complaints (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category ENUM('Academic', 'Administrative', 'Infrastructure', 'Other') NOT NULL,
    priority ENUM('Low', 'Medium', 'High', 'Urgent') NOT NULL DEFAULT 'Medium',
    status ENUM('Open', 'In Progress', 'Resolved', 'Closed') NOT NULL DEFAULT 'Open',
    assigned_to INT,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_complaints_student_id (student_id),
    INDEX idx_complaints_category (category),
    INDEX idx_complaints_priority (priority),
    INDEX idx_complaints_status (status),
    INDEX idx_complaints_assigned_to (assigned_to),
    INDEX idx_complaints_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE complaints COMMENT = 'Stores student complaints and their resolution tracking';

-- =====================================================
-- TABLE: predictions
-- Description: Stores ML model predictions for student risk assessment
-- =====================================================

CREATE TABLE predictions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    model_id INT NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    risk_score DECIMAL(5, 4) NOT NULL,
    probability DECIMAL(5, 4) NOT NULL,
    attendance_percentage DECIMAL(5, 2),
    average_marks DECIMAL(5, 2),
    fee_status VARCHAR(50),
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendations TEXT,
    override_by INT,
    is_manual BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    flag_for_review BOOLEAN DEFAULT FALSE,
    review_note TEXT,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (model_id) REFERENCES ml_models(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (override_by) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_predictions_risk_score CHECK (risk_score >= 0 AND risk_score <= 1),
    CONSTRAINT chk_predictions_probability CHECK (probability >= 0 AND probability <= 1),
    
    -- Indexes
    INDEX idx_predictions_student_id (student_id),
    INDEX idx_predictions_model_id (model_id),
    INDEX idx_predictions_risk_level (risk_level),
    INDEX idx_predictions_prediction_date (prediction_date),
    INDEX idx_predictions_risk_score (risk_score),
    INDEX idx_predictions_flag_for_review (flag_for_review)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE predictions COMMENT = 'Stores ML model predictions for student risk assessment and recommendations';

-- =====================================================
-- TABLE: alerts
-- Description: Stores system-generated alerts for students
-- =====================================================

CREATE TABLE alerts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    alert_type ENUM('Attendance', 'Academic', 'Fee', 'Behavior', 'General') NOT NULL,
    severity ENUM('Info', 'Warning', 'Critical') NOT NULL DEFAULT 'Info',
    message TEXT NOT NULL,
    suggestion TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_alerts_student_id (student_id),
    INDEX idx_alerts_alert_type (alert_type),
    INDEX idx_alerts_severity (severity),
    INDEX idx_alerts_is_read (is_read),
    INDEX idx_alerts_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE alerts COMMENT = 'Stores system-generated alerts for student risk monitoring';

-- =====================================================
-- TABLE: activity_log
-- Description: Stores system activity and audit trail
-- =====================================================

CREATE TABLE activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INT,
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- Indexes
    INDEX idx_activity_log_user_id (user_id),
    INDEX idx_activity_log_action (action),
    INDEX idx_activity_log_entity_type (entity_type),
    INDEX idx_activity_log_entity_id (entity_id),
    INDEX idx_activity_log_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table comment
ALTER TABLE activity_log COMMENT = 'Stores system activity logs and audit trail for security and compliance';

-- =====================================================
-- SAMPLE DATA INSERTS
-- =====================================================

-- Insert admin user
INSERT INTO users (username, email, password_hash, role, is_active) VALUES
('admin', 'admin@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'admin', TRUE);

-- Insert teacher users
INSERT INTO users (username, email, password_hash, role, is_active) VALUES
('teacher1', 'teacher1@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'teacher', TRUE),
('teacher2', 'teacher2@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'teacher', TRUE);

-- Insert student users
INSERT INTO users (username, email, password_hash, role, is_active) VALUES
('student1', 'student1@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'student', TRUE),
('student2', 'student2@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'student', TRUE),
('student3', 'student3@school.edu', '$2b$12$LJ3m4ys3Gl4GcUP7V8YKuOQK9X5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx5Vx', 'student', TRUE);

-- Insert ML model
INSERT INTO ml_models (model_name, model_version, algorithm, accuracy, precision_score, recall_score, f1_score, training_date, model_path, is_active) VALUES
('Student Risk Predictor', '1.0.0', 'Random Forest', 0.8750, 0.8600, 0.8900, 0.8748, '2026-03-20 10:00:00', '/models/risk_predictor_v1.pkl', TRUE);

-- Insert students
INSERT INTO students (user_id, student_id, first_name, last_name, date_of_birth, gender, phone, address, course, semester, admission_date, guardian_name, guardian_phone) VALUES
(4, 'STU001', 'John', 'Doe', '2002-05-15', 'Male', '+1234567890', '123 Main St, City', 'Computer Science', 4, '2024-08-01', 'Robert Doe', '+1234567891'),
(5, 'STU002', 'Jane', 'Smith', '2002-08-22', 'Female', '+1234567892', '456 Oak Ave, Town', 'Computer Science', 4, '2024-08-01', 'Mary Smith', '+1234567893'),
(6, 'STU003', 'Michael', 'Johnson', '2001-12-10', 'Male', '+1234567894', '789 Pine Rd, Village', 'Information Technology', 6, '2023-08-01', 'David Johnson', '+1234567895');

-- Insert subjects
INSERT INTO subjects (subject_code, subject_name, course, semester, credits) VALUES
('CS101', 'Introduction to Programming', 'Computer Science', 1, 4),
('CS102', 'Data Structures', 'Computer Science', 2, 4),
('CS201', 'Database Management Systems', 'Computer Science', 3, 3),
('CS202', 'Operating Systems', 'Computer Science', 4, 3),
('CS301', 'Machine Learning', 'Computer Science', 5, 4),
('IT101', 'Web Development', 'Information Technology', 1, 3),
('IT201', 'Network Security', 'Information Technology', 3, 3),
('IT301', 'Cloud Computing', 'Information Technology', 5, 4);

-- Insert sample attendance records
INSERT INTO attendance (student_id, date, status, marked_by, remarks) VALUES
(1, '2026-03-01', 'Present', 2, NULL),
(1, '2026-03-02', 'Present', 2, NULL),
(1, '2026-03-03', 'Absent', 2, 'Sick leave'),
(1, '2026-03-04', 'Present', 2, NULL),
(1, '2026-03-05', 'Late', 2, 'Traffic delay'),
(2, '2026-03-01', 'Present', 2, NULL),
(2, '2026-03-02', 'Present', 2, NULL),
(2, '2026-03-03', 'Present', 2, NULL),
(2, '2026-03-04', 'Present', 2, NULL),
(2, '2026-03-05', 'Present', 2, NULL),
(3, '2026-03-01', 'Present', 3, NULL),
(3, '2026-03-02', 'Absent', 3, NULL),
(3, '2026-03-03', 'Absent', 3, NULL),
(3, '2026-03-04', 'Present', 3, NULL),
(3, '2026-03-05', 'Excused', 3, 'Medical appointment');

-- Insert sample marks
INSERT INTO marks (student_id, subject_id, exam_type, marks_obtained, max_marks, exam_date, graded_by, remarks) VALUES
(1, 1, 'Midterm', 85.50, 100.00, '2026-02-15', 2, 'Good performance'),
(1, 1, 'Final', 78.00, 100.00, '2026-03-10', 2, 'Satisfactory'),
(1, 2, 'Midterm', 92.00, 100.00, '2026-02-16', 2, 'Excellent'),
(2, 1, 'Midterm', 88.00, 100.00, '2026-02-15', 2, 'Very good'),
(2, 1, 'Final', 91.50, 100.00, '2026-03-10', 2, 'Excellent'),
(2, 2, 'Midterm', 85.00, 100.00, '2026-02-16', 2, 'Good'),
(3, 6, 'Midterm', 65.00, 100.00, '2026-02-15', 3, 'Needs improvement'),
(3, 6, 'Final', 58.00, 100.00, '2026-03-10', 3, 'Below average'),
(3, 7, 'Midterm', 72.00, 100.00, '2026-02-16', 3, 'Average');

-- Insert sample fees
INSERT INTO fees (student_id, fee_type, amount, due_date, paid_date, status, payment_method, transaction_id, receipt_number) VALUES
(1, 'Tuition', 5000.00, '2026-01-15', '2026-01-10', 'Paid', 'Bank Transfer', 'TXN001234', 'RCP001'),
(1, 'Library', 200.00, '2026-01-15', '2026-01-10', 'Paid', 'Bank Transfer', 'TXN001234', 'RCP001'),
(2, 'Tuition', 5000.00, '2026-01-15', '2026-01-12', 'Paid', 'Credit Card', 'TXN001235', 'RCP002'),
(2, 'Library', 200.00, '2026-01-15', NULL, 'Pending', NULL, NULL, NULL),
(3, 'Tuition', 5000.00, '2026-01-15', NULL, 'Overdue', NULL, NULL, NULL),
(3, 'Laboratory', 500.00, '2026-01-15', NULL, 'Overdue', NULL, NULL, NULL);

-- Insert sample library books
INSERT INTO library_books (book_id, title, author, isbn, category, total_copies, available_copies) VALUES
('BK001', 'Introduction to Algorithms', 'Thomas H. Cormen', '978-0262033848', 'Computer Science', 5, 3),
('BK002', 'Clean Code', 'Robert C. Martin', '978-0132350884', 'Software Engineering', 3, 2),
('BK003', 'Database System Concepts', 'Abraham Silberschatz', '978-0078022159', 'Database', 4, 4),
('BK004', 'Operating System Concepts', 'Abraham Silberschatz', '978-1119800361', 'Operating Systems', 3, 1),
('BK005', 'Machine Learning', 'Tom Mitchell', '978-0070428072', 'Machine Learning', 2, 2);

-- Insert sample library transactions
INSERT INTO library_transactions (student_id, book_id, issue_date, due_date, return_date, status, fine_amount, issued_by, returned_to) VALUES
(1, 1, '2026-02-01', '2026-02-15', '2026-02-14', 'Returned', 0.00, 2, 2),
(1, 2, '2026-03-01', '2026-03-15', NULL, 'Issued', 0.00, 2, NULL),
(2, 3, '2026-02-10', '2026-02-24', '2026-02-23', 'Returned', 0.00, 2, 2),
(2, 4, '2026-03-05', '2026-03-19', NULL, 'Issued', 0.00, 2, NULL),
(3, 5, '2026-01-15', '2026-01-29', NULL, 'Overdue', 15.00, 3, NULL);

-- Insert sample complaints
INSERT INTO complaints (student_id, subject, description, category, priority, status, assigned_to, resolution) VALUES
(1, 'Library Access Issue', 'Unable to access online library resources from home', 'Infrastructure', 'Medium', 'Resolved', 2, 'VPN access granted for remote library access'),
(2, 'Course Registration', 'Unable to register for elective course due to system error', 'Administrative', 'High', 'In Progress', 2, NULL),
(3, 'Classroom Temperature', 'Classroom AC not working properly', 'Infrastructure', 'Low', 'Open', NULL, NULL);

-- Insert sample predictions
INSERT INTO predictions (student_id, model_id, risk_level, risk_score, probability, attendance_percentage, average_marks, fee_status, recommendations) VALUES
(1, 1, 'Low', 0.2500, 0.8500, 92.50, 85.17, 'Paid', 'Continue monitoring. Student is performing well.'),
(2, 1, 'Low', 0.1500, 0.9200, 100.00, 88.17, 'Partial', 'Excellent performance. Consider for academic awards.'),
(3, 1, 'High', 0.7800, 0.8800, 60.00, 65.00, 'Overdue', 'Immediate intervention required. Schedule meeting with student and guardian.');

-- Insert sample alerts
INSERT INTO alerts (student_id, alert_type, severity, message, suggestion, is_read) VALUES
(1, 'Attendance', 'Info', 'Attendance is above 90%', 'Keep up the good work!', TRUE),
(2, 'Academic', 'Info', 'Consistent academic performance', 'Consider advanced courses', FALSE),
(3, 'Attendance', 'Critical', 'Attendance below 75%', 'Schedule meeting with student immediately', FALSE),
(3, 'Fee', 'Warning', 'Fee payment overdue', 'Send payment reminder to guardian', FALSE),
(3, 'Academic', 'Warning', 'Marks declining in recent exams', 'Provide additional tutoring support', FALSE);

-- Insert sample activity logs
INSERT INTO activity_log (user_id, action, entity_type, entity_id, details, ip_address) VALUES
(1, 'LOGIN', 'User', 1, 'Admin logged in', '192.168.1.100'),
(2, 'MARK_ATTENDANCE', 'Attendance', 1, 'Marked attendance for student STU001', '192.168.1.101'),
(2, 'GRADE_EXAM', 'Marks', 1, 'Graded midterm exam for CS101', '192.168.1.101'),
(1, 'VIEW_PREDICTIONS', 'Prediction', 3, 'Viewed risk prediction for student STU003', '192.168.1.100'),
(3, 'LOGIN', 'User', 3, 'Teacher logged in', '192.168.1.102');

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for student risk summary
CREATE OR REPLACE VIEW v_student_risk_summary AS
SELECT 
    s.id,
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.course,
    s.semester,
    p.risk_level,
    p.risk_score,
    p.prediction_date,
    ROUND(
        (SELECT COUNT(*) FROM attendance a WHERE a.student_id = s.id AND a.status = 'Present') * 100.0 / 
        NULLIF((SELECT COUNT(*) FROM attendance a WHERE a.student_id = s.id), 0), 2
    ) AS attendance_percentage,
    (SELECT ROUND(AVG(m.marks_obtained), 2) FROM marks m WHERE m.student_id = s.id) AS average_marks,
    (SELECT COUNT(*) FROM fees f WHERE f.student_id = s.id AND f.status = 'Overdue') AS overdue_fees
FROM students s
LEFT JOIN predictions p ON s.id = p.student_id
    AND p.prediction_date = (
        SELECT MAX(prediction_date) 
        FROM predictions 
        WHERE student_id = s.id
    );

-- View for attendance statistics
CREATE OR REPLACE VIEW v_attendance_statistics AS
SELECT 
    s.id,
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.course,
    s.semester,
    COUNT(a.id) AS total_days,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_days,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_days,
    SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS late_days,
    SUM(CASE WHEN a.status = 'Excused' THEN 1 ELSE 0 END) AS excused_days,
    ROUND(
        SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(a.id), 0), 2
    ) AS attendance_percentage
FROM students s
LEFT JOIN attendance a ON s.id = a.student_id
GROUP BY s.id, s.student_id, s.first_name, s.last_name, s.course, s.semester;

-- View for academic performance
CREATE OR REPLACE VIEW v_academic_performance AS
SELECT 
    s.id,
    s.student_id,
    CONCAT(s.first_name, ' ', s.last_name) AS student_name,
    s.course,
    s.semester,
    sub.subject_name,
    sub.subject_code,
    ROUND(AVG(m.marks_obtained), 2) AS average_marks,
    ROUND(AVG(m.marks_obtained * 100.0 / m.max_marks), 2) AS percentage,
    COUNT(DISTINCT m.exam_type) AS exams_taken
FROM students s
JOIN marks m ON s.id = m.student_id
JOIN subjects sub ON m.subject_id = sub.id
GROUP BY s.id, s.student_id, s.first_name, s.last_name, s.course, s.semester, sub.subject_name, sub.subject_code;

-- =====================================================
-- STORED PROCEDURES
-- =====================================================

DELIMITER //

-- Procedure to calculate student risk score
CREATE PROCEDURE sp_calculate_risk_score(
    IN p_student_id INT,
    OUT p_risk_score DECIMAL(5,4),
    OUT p_risk_level VARCHAR(10)
)
BEGIN
    DECLARE v_attendance_pct DECIMAL(5,2);
    DECLARE v_avg_marks DECIMAL(5,2);
    DECLARE v_overdue_fees INT;
    DECLARE v_attendance_score DECIMAL(5,4);
    DECLARE v_academic_score DECIMAL(5,4);
    DECLARE v_fee_score DECIMAL(5,4);
    
    -- Calculate attendance percentage
    SELECT 
        ROUND(
            COUNT(CASE WHEN status = 'Present' THEN 1 END) * 100.0 / 
            NULLIF(COUNT(*), 0), 2
        ) INTO v_attendance_pct
    FROM attendance 
    WHERE student_id = p_student_id;
    
    -- Calculate average marks
    SELECT ROUND(AVG(marks_obtained), 2) INTO v_avg_marks
    FROM marks 
    WHERE student_id = p_student_id;
    
    -- Count overdue fees
    SELECT COUNT(*) INTO v_overdue_fees
    FROM fees 
    WHERE student_id = p_student_id AND status = 'Overdue';
    
    -- Calculate risk scores (inverse relationship - lower is better)
    SET v_attendance_score = GREATEST(0, 1 - (v_attendance_pct / 100));
    SET v_academic_score = GREATEST(0, 1 - (v_avg_marks / 100));
    SET v_fee_score = LEAST(1, v_overdue_fees * 0.3);
    
    -- Calculate overall risk score (weighted average)
    SET p_risk_score = (v_attendance_score * 0.4) + (v_academic_score * 0.4) + (v_fee_score * 0.2);
    
    -- Determine risk level
    IF p_risk_score >= 0.85 THEN
        SET p_risk_level = 'Critical';
    ELSEIF p_risk_score >= 0.7 THEN
        SET p_risk_level = 'High';
    ELSEIF p_risk_score >= 0.4 THEN
        SET p_risk_level = 'Medium';
    ELSE
        SET p_risk_level = 'Low';
    END IF;
END //

-- Procedure to get student dashboard data
CREATE PROCEDURE sp_get_student_dashboard(IN p_student_id INT)
BEGIN
    -- Student basic info
    SELECT 
        s.*,
        u.email,
        u.username
    FROM students s
    JOIN users u ON s.user_id = u.id
    WHERE s.id = p_student_id;
    
    -- Attendance summary
    SELECT 
        COUNT(*) AS total_days,
        SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_days,
        ROUND(
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) * 100.0 / 
            NULLIF(COUNT(*), 0), 2
        ) AS attendance_percentage
    FROM attendance 
    WHERE student_id = p_student_id;
    
    -- Academic performance
    SELECT 
        sub.subject_name,
        ROUND(AVG(m.marks_obtained), 2) AS average_marks,
        ROUND(AVG(m.marks_obtained * 100.0 / m.max_marks), 2) AS percentage
    FROM marks m
    JOIN subjects sub ON m.subject_id = sub.id
    WHERE m.student_id = p_student_id
    GROUP BY sub.subject_name;
    
    -- Fee status
    SELECT 
        fee_type,
        amount,
        due_date,
        status
    FROM fees 
    WHERE student_id = p_student_id
    ORDER BY due_date DESC;
    
    -- Recent alerts
    SELECT 
        alert_type,
        severity,
        message,
        created_at
    FROM alerts 
    WHERE student_id = p_student_id
    ORDER BY created_at DESC
    LIMIT 5;
END //

DELIMITER ;

-- =====================================================
-- TRIGGERS
-- =====================================================

DELIMITER //

-- Trigger to update library book availability when a book is issued
CREATE TRIGGER trg_library_issue_after_insert
AFTER INSERT ON library_transactions
FOR EACH ROW
BEGIN
    IF NEW.status = 'Issued' THEN
        UPDATE library_books 
        SET available_copies = available_copies - 1
        WHERE id = NEW.book_id;
    END IF;
END //

-- Trigger to update library book availability when a book is returned
CREATE TRIGGER trg_library_return_after_update
AFTER UPDATE ON library_transactions
FOR EACH ROW
BEGIN
    IF OLD.status = 'Issued' AND NEW.status = 'Returned' THEN
        UPDATE library_books 
        SET available_copies = available_copies + 1
        WHERE id = NEW.book_id;
    END IF;
END //

-- Trigger to log activity when marks are inserted
CREATE TRIGGER trg_marks_after_insert
AFTER INSERT ON marks
FOR EACH ROW
BEGIN
    INSERT INTO activity_log (user_id, action, entity_type, entity_id, details)
    VALUES (NEW.graded_by, 'GRADE_EXAM', 'Marks', NEW.id, 
            CONCAT('Graded ', NEW.exam_type, ' exam for student_id: ', NEW.student_id));
END //

-- Trigger to create alert when attendance is low
CREATE TRIGGER trg_attendance_after_insert
AFTER INSERT ON attendance
FOR EACH ROW
BEGIN
    DECLARE v_attendance_pct DECIMAL(5,2);
    
    -- Calculate current attendance percentage
    SELECT 
        ROUND(
            COUNT(CASE WHEN status = 'Present' THEN 1 END) * 100.0 / 
            NULLIF(COUNT(*), 0), 2
        ) INTO v_attendance_pct
    FROM attendance 
    WHERE student_id = NEW.student_id;
    
    -- Create alert if attendance is below 75%
    IF v_attendance_pct < 75 THEN
        INSERT INTO alerts (student_id, alert_type, severity, message, suggestion)
        VALUES (NEW.student_id, 'Attendance', 'Warning', 
                CONCAT('Attendance dropped to ', v_attendance_pct, '%'),
                'Schedule meeting with student to discuss attendance issues');
    END IF;
END //

DELIMITER ;

-- =====================================================
-- GRANTS (Adjust based on your security requirements)
-- =====================================================

-- Create application user (adjust password as needed)
-- CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON student_risk_monitoring.* TO 'app_user'@'localhost';
-- FLUSH PRIVILEGES;

-- =====================================================
-- END OF SCHEMA
-- =====================================================
