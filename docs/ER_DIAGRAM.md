# Entity Relationship Diagram

## A.U.R.A - Academic Understanding and Retention Application

This diagram illustrates the database schema for the A.U.R.A - Academic Understanding and Retention Application, showing all tables, their relationships, and cardinality.

```mermaid
erDiagram
    %% Users Table
    USERS {
        int id PK
        varchar(50) username
        varchar(100) email
        varchar(255) password_hash
        enum role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    %% ML Models Table
    ML_MODELS {
        int id PK
        varchar(100) model_name
        varchar(20) model_version
        varchar(100) algorithm
        decimal(5,4) accuracy
        decimal(5,4) precision_score
        decimal(5,4) recall_score
        decimal(5,4) f1_score
        timestamp training_date
        varchar(500) model_path
        boolean is_active
        timestamp created_at
    }
    
    %% Students Table
    STUDENTS {
        int id PK
        int user_id FK
        varchar(20) student_id
        varchar(50) first_name
        varchar(50) last_name
        date date_of_birth
        enum gender
        varchar(20) phone
        text address
        varchar(100) course
        int semester
        date admission_date
        varchar(100) guardian_name
        varchar(20) guardian_phone
        timestamp created_at
        timestamp updated_at
    }
    
    %% Subjects Table
    SUBJECTS {
        int id PK
        varchar(20) subject_code
        varchar(100) subject_name
        varchar(100) course
        int semester
        int credits
        timestamp created_at
    }
    
    %% Attendance Table
    ATTENDANCE {
        int id PK
        int student_id FK
        date date
        enum status
        int marked_by FK
        text remarks
        timestamp created_at
    }
    
    %% Marks Table
    MARKS {
        int id PK
        int student_id FK
        int subject_id FK
        enum exam_type
        decimal(5,2) marks_obtained
        decimal(5,2) max_marks
        date exam_date
        int graded_by FK
        text remarks
        timestamp created_at
    }
    
    %% Fees Table
    FEES {
        int id PK
        int student_id FK
        enum fee_type
        decimal(10,2) amount
        date due_date
        date paid_date
        enum status
        varchar(50) payment_method
        varchar(100) transaction_id
        varchar(50) receipt_number
        timestamp created_at
        timestamp updated_at
    }
    
    %% Library Books Table
    LIBRARY_BOOKS {
        int id PK
        varchar(20) book_id
        varchar(255) title
        varchar(200) author
        varchar(20) isbn
        varchar(100) category
        int total_copies
        int available_copies
        timestamp created_at
    }
    
    %% Library Transactions Table
    LIBRARY_TRANSACTIONS {
        int id PK
        int student_id FK
        int book_id FK
        date issue_date
        date due_date
        date return_date
        enum status
        decimal(10,2) fine_amount
        int issued_by FK
        int returned_to FK
        timestamp created_at
    }
    
    %% Complaints Table
    COMPLAINTS {
        int id PK
        int student_id FK
        varchar(200) subject
        text description
        enum category
        enum priority
        enum status
        int assigned_to FK
        text resolution
        timestamp created_at
        timestamp updated_at
    }
    
    %% Predictions Table
    PREDICTIONS {
        int id PK
        int student_id FK
        int model_id FK
        enum risk_level
        decimal(5,4) risk_score
        decimal(5,4) probability
        decimal(5,2) attendance_percentage
        decimal(5,2) average_marks
        varchar(50) fee_status
        timestamp prediction_date
        text recommendations
    }
    
    %% Alerts Table
    ALERTS {
        int id PK
        int student_id FK
        enum alert_type
        enum severity
        text message
        text suggestion
        boolean is_read
        timestamp created_at
    }
    
    %% Activity Log Table
    ACTIVITY_LOG {
        int id PK
        int user_id FK
        varchar(100) action
        varchar(50) entity_type
        int entity_id
        text details
        varchar(45) ip_address
        timestamp created_at
    }
    
    %% Relationships
    USERS ||..|| STUDENTS : "has"
    USERS ||..|| ATTENDANCE : "marks"
    USERS ||..|| MARKS : "grades"
    USERS ||..|| LIBRARY_TRANSACTIONS : "issues"
    USERS ||..|| LIBRARY_TRANSACTIONS : "returns"
    USERS ||..|| COMPLAINTS : "assigns"
    USERS ||..|| ACTIVITY_LOG : "performs"
    
    STUDENTS ||..|| ATTENDANCE : "has"
    STUDENTS ||..|| MARKS : "earns"
    STUDENTS ||..|| FEES : "owes"
    STUDENTS ||..|| LIBRARY_TRANSACTIONS : "makes"
    STUDENTS ||..|| COMPLAINTS : "files"
    STUDENTS ||..|| PREDICTIONS : "receives"
    STUDENTS ||..|| ALERTS : "triggers"
    
    SUBJECTS ||..|| MARKS : "contains"
    
    ML_MODELS ||..|| PREDICTIONS : "generates"
    
    LIBRARY_BOOKS ||..|| LIBRARY_TRANSACTIONS : "tracked by"
```

## Table Descriptions

### Core Entities
- **Users**: System users with roles (admin, teacher, student)
- **Students**: Student personal and academic information linked to users
- **Subjects**: Academic subjects/courses offered

### Academic Tracking
- **Attendance**: Daily attendance records for students
- **Marks**: Academic performance records for students in subjects

### Financial Management
- **Fees**: Fee payment information and transaction details

### Library Management
- **Library_Books**: Library book inventory
- **Library_Transactions**: Book issue and return records

### Student Support
- **Complaints**: Student grievances and resolution tracking
- **Predictions**: ML model predictions for student risk assessment
- **Alerts**: System-generated alerts for student risk monitoring
- **Activity_Log**: System audit trail for security and compliance

### Machine Learning
- **ML_Models**: Metadata for machine learning models used in risk prediction

## Relationship Cardinality Notation
- `||..||` : One-to-one or one-to-many relationship
- `}o..||` : Zero-or-one to one/many relationship
- `}o..}o` : Zero-or-many to zero-or-many relationship

## Indexes and Constraints
Each table includes appropriate indexes for performance and foreign key constraints for data integrity. Check constraints ensure data validity (e.g., non-negative amounts, valid score ranges).

## Notes
1. All tables use InnoDB engine with UTF-8 encoding for internationalization support
2. Timestamps are automatically managed for creation and updates
3. Soft deletes are not implemented; hard deletes cascade where appropriate
4. Passwords are stored as hashes using bcrypt algorithm