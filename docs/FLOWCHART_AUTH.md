# Authentication Process Flowchart

## A.U.R.A - Academic Understanding and Retention Application

This flowchart illustrates the user authentication process in the system.

```mermaid
flowchart TD
    %% Start
    Start[Start: User Accesses Application]:::start
    
    %% Initial Check
    IsAuthenticated{Is User Already Authenticated?}:::decision
    
    %% If already authenticated
    GetRole[Get User Role from Session]:::process
    RouteToDashboard[Route to Role-Based Dashboard]:::process
    EndSuccess[End: User in Dashboard]:::end
    
    %% If not authenticated
    ShowLoginPage[Show Login Page]:::process
    EnterCredentials[Enter Username/Email and Password]:::io
    SubmitForm[Submit Login Form]:::process
    
    %% Form Validation
    ValidateForm{Validate Form Input}:::decision
    ShowValidationErrors[Display Validation Errors]:::process
    BackToLogin[Return to Login Page]:::process
    
    %% Database Lookup
    FindUser{Find User by Username/Email}:::process
    UserNotFound{User Found?}:::decision
    ShowInvalidCreds[Display Invalid Credentials]:::process
    
    %% Password Verification
    VerifyPassword{Verify Password Hash}:::process
    PasswordCorrect{Password Correct?}:::decision
    ShowInvalidCreds2[Display Invalid Credentials]:::process
    
    %% Successful Authentication
    CreateSession[Create User Session]:::process
    UpdateLastLogin[Update Last Login Timestamp]:::process
    LogActivity[Log Login Activity]:::process
    DetermineRole[Determine User Role]:::process
    RedirectDashboard[Redirect to Role-Based Dashboard]:::process
    
    %% Role-based routing
    IsAdmin{Is Role Admin?}:::decision
    GoToAdminDashboard[Go to Admin Dashboard]:::process
    IsTeacher{Is Role Teacher?}:::decision
    GoToTeacherDashboard[Go to Teacher Dashboard]:::process
    GoToStudentDashboard[Go to Student Dashboard]:::process
    
    %% End states
    EndSuccess[End: Authenticated Successfully]:::end
    EndFailure[End: Authentication Failed]:::end
    
    %% Connections
    Start --> IsAuthenticated
    IsAuthenticated -- Yes --> GetRole
    GetRole --> RouteToDashboard
    RouteToDashboard --> EndSuccess
    
    IsAuthenticated -- No --> ShowLoginPage
    ShowLoginPage --> EnterCredentials
    EnterCredentials --> SubmitForm
    SubmitForm --> ValidateForm
    
    ValidateForm -- No --> ShowValidationErrors
    ShowValidationErrors --> BackToLogin
    BackToLogin --> ShowLoginPage
    
    ValidateForm -- Yes --> FindUser
    FindUser --> UserNotFound
    UserNotFound -- No --> ShowInvalidCreds
    ShowInvalidCreds --> BackToLogin
    
    UserNotFound -- Yes --> VerifyPassword
    VerifyPassword --> PasswordCorrect
    PasswordCorrect -- No --> ShowInvalidCreds2
    ShowInvalidCreds2 --> BackToLogin
    
    PasswordCorrect -- Yes --> CreateSession
    CreateSession --> UpdateLastLogin
    UpdateLastLogin --> LogActivity
    LogActivity --> DetermineRole
    DetermineRole --> RedirectDashboard
    
    RedirectDashboard --> IsAdmin
    IsAdmin -- Yes --> GoToAdminDashboard
    GoToAdminDashboard --> EndSuccess
    IsAdmin -- No --> IsTeacher
    IsTeacher -- Yes --> GoToTeacherDashboard
    GoToTeacherDashboard --> EndSuccess
    IsTeacher -- No --> GoToStudentDashboard
    GoToStudentDashboard --> EndSuccess
    
    %% Styling
    classDef start fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef end fill:#f8d7da,stroke:#721c24,stroke-width:2px;
    classDef process fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef decision fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef io fill:#d1ecf1,stroke:#0c5460,stroke-width:2px;
```

## Description

### Authentication Process Steps

1. **Start**: User accesses the application
2. **Authentication Check**: System checks if user already has a valid session
3. **If Authenticated**: 
   - Retrieve user role from session
   - Route to appropriate dashboard based on role (admin/teacher/student)
   - End process successfully
   
4. **If Not Authenticated**:
   - Display login page
   - User enters username/email and password
   - Submit login form
   
5. **Form Validation**:
   - Validate input fields (required fields, email format, etc.)
   - If validation fails: show errors and return to login page
   - If validation passes: proceed to database lookup
   
6. **Database Lookup**:
   - Query database for user with provided username/email
   - If user not found: show invalid credentials error
   - If user found: proceed to password verification
   
7. **Password Verification**:
   - Verify provided password against stored hash using bcrypt
   - If password incorrect: show invalid credentials error
   - If password correct: proceed to session creation
   
8. **Successful Authentication**:
   - Create user session with user ID and role
   - Update last login timestamp in database
   - Log login activity for audit trail
   - Determine user role for routing
   - Redirect to role-based dashboard
   
9. **Role-Based Routing**:
   - Admin users: redirected to admin dashboard
   - Teacher users: redirected to teacher dashboard
   - Student users: redirected to student dashboard
   - End process successfully

### Security Features
- Passwords are stored as bcrypt hashes (never in plain text)
- Session management prevents unauthorized access
- Input validation protects against common web vulnerabilities
- Login attempts are logged for security monitoring
- Role-based access control ensures users only see authorized content

### Error Handling
- Invalid credentials: Generic error message (does not reveal if username or password is wrong)
- Form validation: Specific field-level errors
- System errors: Generic error messages with logging for debugging
- Account lockout: Not implemented in basic version but can be added

### Technical Implementation
Based on the codebase:
- Uses Flask-Login for session management
- WTForms for form validation and CSRF protection
- bcrypt for password hashing (via Werkzeug security utilities)
- Custom decorators in `app/utils/decorators.py` for role-based access control
- Login routes defined in `app/routes/auth.py`
- Login templates in `app/templates/auth/`