# User Manual

## A.U.R.A - Academic Understanding and Retention Application

This manual provides comprehensive guidance for users of the A.U.R.A - Academic Understanding and Retention Application. The system supports three user roles: Administrator, Teacher, and Student.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Administrator Guide](#administrator-guide)
3. [Teacher Guide](#teacher-guide)
4. [Student Guide](#student-guide)
5. [Common Features](#common-features)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Accessing the System
1. Open your web browser
2. Navigate to the system URL (e.g., http://localhost:5000)
3. You will see the login page

### Login Process
1. Enter your username
2. Enter your password
3. Click "Login"
4. You will be redirected to your role-specific dashboard

### First-Time Login
- **Important**: Change your default password immediately after first login
- Navigate to Profile → Change Password
- Enter current password and new password
- Click "Update Password"

### Navigation
- **Dashboard**: Main overview page with key metrics
- **Sidebar Menu**: Access different system modules
- **Top Bar**: User profile, notifications, logout
- **Breadcrumbs**: Track your location in the system

## Administrator Guide

### Dashboard Overview
The admin dashboard provides:
- Total students, teachers, and users
- Risk distribution (Low, Medium, High)
- Recent alerts and activities
- System statistics and charts

### User Management
#### Viewing Users
1. Navigate to **Users** in the sidebar
2. View list of all users with filters:
   - Role (Admin, Teacher, Student)
   - Status (Active, Inactive)
3. Click on a user to view details

#### Creating Users
1. Click **Add User** button
2. Fill in required fields:
   - Username (unique)
   - Email (unique)
   - Password
   - Role
3. Click **Save**

#### Managing User Status
1. Navigate to user details
2. Click **Toggle Active** to activate/deactivate
3. Confirm the action

### Student Management
#### Viewing Students
1. Navigate to **Students** in the sidebar
2. View list with filters:
   - Course
   - Semester
   - Risk Level
3. Click on a student to view full profile

#### Adding Students
1. Click **Add Student** button
2. Fill in student information:
   - Personal details (name, DOB, gender)
   - Contact information
   - Academic details (course, semester)
   - Guardian information
3. Click **Save**

#### Editing Students
1. Navigate to student profile
2. Click **Edit** button
3. Modify information
4. Click **Update**

### Attendance Management
#### Marking Attendance
1. Navigate to **Attendance** → **Mark Attendance**
2. Select date
3. Select class/course
4. Mark each student as Present/Absent/Late/Excused
5. Add remarks if needed
6. Click **Save Attendance**

#### Attendance Reports
1. Navigate to **Attendance** → **Reports**
2. Select date range
3. Filter by course/semester
4. View attendance statistics and trends
5. Export to CSV/PDF if needed

### Academic Management
#### Adding Subjects
1. Navigate to **Subjects** → **Add Subject**
2. Enter subject details:
   - Subject code
   - Subject name
   - Course
   - Semester
   - Credits
3. Click **Save**

#### Recording Marks
1. Navigate to **Marks** → **Add Marks**
2. Select student
3. Select subject
4. Enter exam details:
   - Exam type (Midterm, Final, Assignment, etc.)
   - Marks obtained
   - Maximum marks
   - Exam date
5. Add remarks
6. Click **Save**

#### Grade Reports
1. Navigate to **Marks** → **Reports**
2. Select student or class
3. View grade summaries and trends
4. Export reports

### Fee Management
#### Adding Fees
1. Navigate to **Fees** → **Add Fee**
2. Select student
3. Enter fee details:
   - Fee type (Tuition, Library, etc.)
   - Amount
   - Due date
   - Status
4. Click **Save**

#### Processing Payments
1. Navigate to **Fees** → **List**
2. Find pending fee
3. Click **Pay**
4. Enter payment details:
   - Payment method
   - Transaction ID
   - Receipt number
5. Click **Confirm Payment**

#### Fee Reports
1. Navigate to **Fees** → **Reports**
2. View payment status, overdue fees
3. Filter by date range, fee type
4. Export financial reports

### Library Management
#### Adding Books
1. Navigate to **Library** → **Add Book**
2. Enter book details:
   - Book ID
   - Title
   - Author
   - ISBN
   - Category
   - Total copies
3. Click **Save**

#### Issuing Books
1. Navigate to **Library** → **Issue Book**
2. Select student
3. Select book
4. Set due date
5. Click **Issue**

#### Returning Books
1. Navigate to **Library** → **Transactions**
2. Find issued book
3. Click **Return**
4. System calculates fines if overdue
5. Confirm return

### Complaint Management
#### Viewing Complaints
1. Navigate to **Complaints** → **List**
2. View all complaints with filters:
   - Status (Open, In Progress, Resolved, Closed)
   - Category
   - Priority
3. Click on complaint to view details

#### Assigning Complaints
1. Open complaint details
2. Click **Assign**
3. Select staff member
4. Add assignment notes
5. Click **Assign**

#### Resolving Complaints
1. Open complaint details
2. Click **Resolve**
3. Enter resolution details
4. Click **Mark as Resolved**

### Risk Prediction & Alerts
#### Viewing Predictions
1. Navigate to **Predictions** → **Dashboard**
2. View risk distribution across students
3. See high-risk students list
4. Monitor prediction trends

#### Managing Alerts
1. Navigate to **Alerts** → **List**
2. View all alerts with filters:
   - Type (Attendance, Academic, Fee, etc.)
   - Severity (Info, Warning, Critical)
   - Read status
3. Click on alert to view details
4. Mark alerts as read

#### Generating Reports
1. Navigate to **Reports**
2. Select report type:
   - Academic Performance
   - Attendance Analysis
   - Financial Status
   - Risk Assessment
3. Set parameters (date range, filters)
4. Generate and export report

### System Configuration
#### ML Model Management
1. Navigate to **Admin** → **ML Models**
2. View model performance metrics
3. Activate/deactivate models
4. View model training history

#### Activity Logs
1. Navigate to **Admin** → **Activity Log**
2. View all system activities
3. Filter by user, action, date
4. Monitor for security issues

## Teacher Guide

### Dashboard Overview
The teacher dashboard shows:
- Classes assigned
- Student attendance summary
- Recent marks entered
- Alerts for students in your classes

### Attendance Management
#### Marking Attendance
1. Navigate to **Attendance** → **Mark Attendance**
2. Select your class
3. Select date
4. Mark each student's status
5. Add remarks for absences
6. Click **Save**

#### Viewing Attendance
1. Navigate to **Attendance** → **Reports**
2. Select your class
3. View attendance trends
4. Identify students with poor attendance

### Academic Management
#### Recording Marks
1. Navigate to **Marks** → **Add Marks**
2. Select student from your class
3. Enter exam details
4. Save marks

#### Viewing Student Progress
1. Navigate to **Students** → **List**
2. Filter by your classes
3. Click on student to view:
   - Attendance records
   - Academic performance
   - Fee status
   - Risk level

### Student Support
#### Viewing At-Risk Students
1. Navigate to **Predictions** → **Dashboard**
2. View students in your classes with risk levels
3. See specific risk factors
4. Access intervention suggestions

#### Managing Alerts
1. Navigate to **Alerts**
2. View alerts for students in your classes
3. Take appropriate action based on alert type
4. Mark alerts as addressed

### Reports
#### Generating Class Reports
1. Navigate to **Reports**
2. Select report type
3. Filter by your classes
4. Generate and export

## Student Guide

### Dashboard Overview
Your dashboard shows:
- Your attendance percentage
- Current academic performance
- Fee payment status
- Recent alerts and notifications
- Risk assessment summary

### Viewing Your Information
#### Attendance
1. Navigate to **My Attendance**
2. View attendance records by date
3. See attendance percentage
4. Identify patterns of absence

#### Academic Performance
1. Navigate to **My Marks**
2. View marks by subject
3. See exam-wise breakdown
4. Calculate average performance

#### Fee Status
1. Navigate to **My Fees**
2. View all fee records
3. Check payment status
4. See pending amounts

#### Library Transactions
1. Navigate to **My Library**
2. View issued books
3. Check due dates
4. See any fines

### Submitting Complaints
#### Creating a Complaint
1. Navigate to **My Complaints** → **New Complaint**
2. Enter complaint details:
   - Subject
   - Description
   - Category (Academic, Administrative, etc.)
   - Priority
3. Click **Submit**

#### Tracking Complaints
1. Navigate to **My Complaints**
2. View all your complaints
3. Check status updates
4. View resolution details

### Alerts & Notifications
#### Viewing Alerts
1. Navigate to **My Alerts**
2. View all notifications
3. Mark alerts as read
4. See alert details and suggestions

#### Understanding Risk Assessment
1. Navigate to **My Risk Assessment**
2. View your risk score and level
3. See contributing factors:
   - Attendance percentage
   - Academic performance
   - Fee payment status
4. Read recommendations for improvement

### Profile Management
#### Updating Profile
1. Click on your username (top right)
2. Select **Profile**
3. Update allowed fields:
   - Email
   - Phone number
   - Address
4. Click **Save**

#### Changing Password
1. Navigate to **Profile** → **Change Password**
2. Enter current password
3. Enter new password
4. Confirm new password
5. Click **Update**

## Common Features

### Search Functionality
- Available in most list views
- Search by name, ID, or keyword
- Real-time filtering

### Export Options
- **CSV**: For data analysis
- **PDF**: For reports and printing
- **Excel**: For detailed spreadsheets

### Notifications
- **In-App**: Real-time notifications in the system
- **Email**: Sent for important alerts (if configured)
- **Dashboard**: Summary of pending items

### Help & Support
- **Help Icon**: Context-sensitive help
- **Documentation**: Access to this manual
- **Contact Support**: Email support team

## Troubleshooting

### Login Issues
**Problem**: Cannot login
**Solutions**:
1. Verify username and password
2. Check if account is active
3. Clear browser cache
4. Try different browser
5. Contact administrator

### Page Not Loading
**Problem**: Pages load slowly or not at all
**Solutions**:
1. Check internet connection
2. Refresh the page
3. Clear browser cache
4. Try different browser
5. Check if system is under maintenance

### Data Not Saving
**Problem**: Changes not saved
**Solutions**:
1. Check required fields are filled
2. Verify data format (dates, numbers)
3. Check for error messages
4. Try again after refreshing
5. Contact support if persists

### Export Issues
**Problem**: Cannot export reports
**Solutions**:
1. Check browser pop-up settings
2. Ensure sufficient disk space
3. Try different export format
4. Check file permissions
5. Contact administrator

### Performance Issues
**Problem**: System is slow
**Solutions**:
1. Close unnecessary browser tabs
2. Clear browser cache
3. Check internet speed
4. Try during off-peak hours
5. Report to administrator

## Best Practices

### For Administrators
1. Regularly backup database
2. Monitor system logs
3. Review user access periodically
4. Keep system updated
5. Train users on new features

### For Teachers
1. Mark attendance daily
2. Enter marks promptly
3. Review student alerts
4. Communicate with at-risk students
5. Use reports for insights

### For Students
1. Check dashboard regularly
2. Address alerts promptly
3. Maintain good attendance
4. Keep contact information updated
5. Submit complaints when needed

## Keyboard Shortcuts
- **Ctrl + S**: Save current form
- **Ctrl + P**: Print current page
- **Ctrl + F**: Find on page
- **Esc**: Close modal/dialog
- **Tab**: Navigate between fields

## Accessibility Features
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode (browser setting)
- Adjustable text size (browser setting)
- Alternative text for images

## Privacy & Security
- Never share your password
- Log out when using public computers
- Report suspicious activity
- Keep personal information updated
- Review privacy settings regularly

## Contact Information
- **Technical Support**: support@studentrisksystem.edu
- **Administrator**: admin@studentrisksystem.edu
- **Emergency**: +1-800-STUDENT

## Version Information
- **Manual Version**: 1.0.0
- **System Version**: 1.0.0
- **Last Updated**: March 2026

For the latest version of this manual, visit the system documentation portal.