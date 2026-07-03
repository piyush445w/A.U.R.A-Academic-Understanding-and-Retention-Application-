# REST API Documentation

## A.U.R.A - Academic Understanding and Retention Application

This document describes the RESTful API endpoints available in the A.U.R.A - Academic Understanding and Retention Application.

### Base URL
```
http://localhost:5000/api
```

All API endpoints are prefixed with `/api` and follow REST principles. The system uses JSON for request and response bodies.

### Authentication
Most endpoints require authentication. The system uses token-based authentication via Flask-Login.

**Login Endpoint:**
```
POST /api/auth/login
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@school.edu",
    "role": "admin",
    "is_active": true
  }
}
```

Include the session cookie in subsequent requests for authentication.

### Error Responses
The API uses standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

Error responses follow this format:
```json
{
  "error": "Error Type",
  "message": "Detailed error message"
}
```

## API Endpoints

### Authentication Endpoints
*Blueprint: `auth_bp`, URL Prefix: `/auth`*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/login` | User login | No |
| POST | `/auth/logout` | User logout | Yes |
| POST | `/auth/register` | User registration | No |
| GET | `/auth/profile` | Get current user profile | Yes |
| PUT | `/auth/profile` | Update current user profile | Yes |
| POST | `/auth/change-password` | Change user password | Yes |

### Admin Endpoints
*Blueprint: `admin_bp`, URL Prefix: `/admin`*

#### User Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/users` | Get all users (with optional role/is_active filters) | Yes (Admin) |
| GET | `/admin/users/<int:user_id>` | Get user by ID | Yes (Admin) |
| POST | `/admin/users/<int:user_id>/toggle-active` | Toggle user active status | Yes (Admin) |

#### Student Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/students` | Get all students (with optional course/semester filters) | Yes (Teacher/Admin) |
| GET | `/admin/students/<int:student_id>` | Get student by ID | Yes (Teacher/Admin) |
| POST | `/admin/students` | Create a new student | Yes (Admin) |

#### Attendance Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/attendance` | Mark attendance for a student | Yes (Teacher/Admin) |

#### Marks Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/marks` | Add marks for a student | Yes (Teacher/Admin) |

#### Fee Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/fees` | Add fee for a student | Yes (Admin) |
| POST | `/admin/fees/<int:fee_id>/pay` | Mark fee as paid | Yes (Admin) |

#### Library Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/library/books` | Get all library books (with optional category/search filters) | Yes (Login) |
| POST | `/admin/library/books` | Add a new library book | Yes (Admin) |
| POST | `/admin/library/issue` | Issue a book to a student | Yes (Teacher/Admin) |
| POST | `/admin/library/return/<int:transaction_id>` | Return a book | Yes (Teacher/Admin) |

#### Complaint Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/complaints` | Get all complaints (with optional status/category/priority filters) | Yes (Teacher/Admin) |
| POST | `/admin/complaints/<int:complaint_id>/assign` | Assign complaint to staff member | Yes (Admin) |

#### Prediction & ML Model Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/predictions` | Get all predictions (with optional student_id/model_id filters) | Yes (Admin) |
| GET | `/admin/ml-models` | Get all ML models | Yes (Admin) |

#### Alert Management
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/alerts` | Get all alerts (with optional student_id/alert_type/severity filters) | Yes (Admin) |

#### Activity Log
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/admin/activity-log` | Get system activity logs (with optional user_id/action filters) | Yes (Admin) |

### Student Endpoints
*Blueprint: `student_bp`, URL Prefix: `/student`*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/student/profile` | Get student profile | Yes (Student) |
| GET | `/student/attendance` | Get student attendance records | Yes (Student) |
| GET | `/student/marks` | Get student marks | Yes (Student) |
| GET | `/student/fees` | Get student fee records | Yes (Student) |
| GET | `/student/library` | Get student library transactions | Yes (Student) |
| GET | `/student/complaints` | Get student complaints (with optional status filter) | Yes (Student) |
| POST | `/student/complaints` | Create a new complaint | Yes (Student) |
| GET | `/student/alerts` | Get student alerts (with optional is_read filter) | Yes (Student) |
| POST | `/student/alerts/<int:alert_id>/read` | Mark alert as read | Yes (Student) |
| GET | `/student/predictions` | Get student predictions (with optional limit) | Yes (Student) |
| GET | `/student/risk-assessment` | Get student risk assessment | Yes (Student) |

### Main Endpoints
*Blueprint: `main_bp`, No URL Prefix*

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/` | System welcome message | No |
| GET | `/health` | Health check endpoint | No |
| GET | `/dashboard` | Dashboard information | Yes (Login) |

## Data Models

### User Object
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@school.edu",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z"
}
```

### Student Object
```json
{
  "id": 1,
  "user_id": 1,
  "student_id": "STU001",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "2002-05-15",
  "gender": "Male",
  "phone": "+1234567890",
  "address": "123 Main St, City",
  "course": "Computer Science",
  "semester": 4,
  "admission_date": "2024-08-01",
  "guardian_name": "Robert Doe",
  "guardian_phone": "+1234567891",
  "created_at": "2026-03-26T10:00:00Z",
  "updated_at": "2026-03-26T10:00:00Z"
}
```

### Attendance Object
```json
{
  "id": 1,
  "student_id": 1,
  "date": "2026-03-01",
  "status": "Present",
  "marked_by": 2,
  "remarks": null,
  "created_at": "2026-03-01T08:00:00Z"
}
```

### Marks Object
```json
{
  "id": 1,
  "student_id": 1,
  "subject_id": 1,
  "exam_type": "Midterm",
  "marks_obtained": 85.50,
  "max_marks": 100.00,
  "exam_date": "2026-03-15",
  "graded_by": 2,
  "remarks": "Good performance",
  "created_at": "2026-03-15T10:00:00Z"
}
```

### Fee Object
```json
{
  "id": 1,
  "student_id": 1,
  "fee_type": "Tuition",
  "amount": 5000.00,
  "due_date": "2026-03-31",
  "paid_date": null,
  "status": "Pending",
  "payment_method": null,
  "transaction_id": null,
  "receipt_number": null,
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-01T10:00:00Z"
}
```

### Prediction Object
```json
{
  "id": 1,
  "student_id": 1,
  "model_id": 1,
  "risk_level": "Medium",
  "risk_score": 0.65,
  "probability": 0.65,
  "attendance_percentage": 85.50,
  "average_marks": 78.25,
  "fee_status": "Pending",
  "prediction_date": "2026-03-26T10:00:00Z",
  "recommendations": "Monitor attendance and provide academic support"
}
```

### Alert Object
```json
{
  "id": 1,
  "student_id": 1,
  "alert_type": "Attendance",
  "severity": "Warning",
  "message": "Student has 3 consecutive absences",
  "suggestion": "Contact student and parents to discuss attendance issues",
  "is_read": false,
  "created_at": "2026-03-26T10:00:00Z"
}
```

## Usage Examples

### 1. User Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Get Student Profile (after login)
```bash
curl -X GET http://localhost:5000/api/student/profile \
  -H "Cookie: session=your_session_cookie"
```

### 3. Mark Attendance (Teacher/Admin)
```bash
curl -X POST http://localhost:5000/api/admin/attendance \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "student_id": 1,
    "date": "2026-03-26",
    "status": "Present",
    "remarks": "On time"
  }'
```

### 4. Create Fee Record (Admin)
```bash
curl -X POST http://localhost:5000/api/admin/fees \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "student_id": 1,
    "fee_type": "Tuition",
    "amount": 5000.00,
    "due_date": "2026-04-30",
    "status": "Pending"
  }'
```

### 5. Get Student Risk Assessment
```bash
curl -X GET http://localhost:5000/api/student/risk-assessment \
  -H "Cookie: session=your_session_cookie"
```

## Rate Limiting
The API implements basic rate limiting to prevent abuse:
- Authentication endpoints: 5 attempts per minute per IP
- General endpoints: 100 requests per minute per authenticated user
- Exceeding limits returns HTTP 429 (Too Many Requests)

## Versioning
This documentation refers to API version 1.0.0. Future versions will maintain backward compatibility where possible.

## Contact
For API support or questions, contact the development team at: api-support@studentrisksystem.edu