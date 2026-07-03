# Level 0 Data Flow Diagram

## A.U.R.A - Academic Understanding and Retention Application

This diagram shows the system context, illustrating the system as a single process interacting with external entities.

```mermaid
flowchart TD
    %% External Entities
    Admin[Admin]:::external
    Teacher[Teacher]:::external
    Student[Student]:::external
    
    %% System Process
    subgraph System[A.U.R.A - Academic Understanding and Retention Application]
        direction TB
        Process[System Process]:::process
    end
    
    %% Data Stores
    subgraph DataStores[Data Stores]
        direction TB
        StudentDB[(Student Database)]:::datastore
        MLModels[(ML Models)]:::datastore
        SystemLogs[(System Logs)]:::datastore
    end
    
    %% Data Flows - Admin
    Admin -->|Login Credentials, System Config, User Management| Process
    Process -->|Authentication Response, System Status, Reports| Admin
    Process -->|Student Records, Risk Reports, Alerts| Admin
    Admin -->|Fee Updates, Disciplinary Actions| StudentDB
    StudentDB -->|Student Information, Fee Records| Admin
    
    %% Data Flows - Teacher
    Teacher -->|Login Credentials, Attendance, Grades, Feedback| Process
    Process -->|Authentication Response, Class Lists, Student Progress| Teacher
    Process -->|Attendance Reports, Performance Analytics| Teacher
    Teacher -->|Attendance Records, Grade Entries| StudentDB
    StudentDB -->|Student Information, Attendance History| Teacher
    
    %% Data Flows - Student
    Student -->|Login Credentials, Profile Updates, Complaints| Process
    Process -->|Authentication Response, Dashboard, Alerts, Reports| Student
    Process -->|Fee Status, Library Info, Academic Progress| Student
    Student -->|Complaint Details, Fee Payments| StudentDB
    StudentDB -->|Personal Information, Fee Status, Library Records| Student
    
    %% Internal Data Flows
    Process -->|Student Data for Analysis| StudentDB
    StudentDB -->|Historical Student Data| Process
    Process -->|Features for ML Model| MLModels
    MLModels -->|Trained Model, Predictions| Process
    Process -->|Risk Predictions, Alerts| SystemLogs
    SystemLogs -->|Audit Trail, System Metrics| Process
    Process -->|Updated ML Models| MLModels
    MLModels -->|Model Metadata| Process
    
    %% Styling
    classDef external fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef process fill:#fff3e0,stroke:#bf360c,stroke-width:2px;
    classDef datastore fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;
```

## Description

### External Entities
- **Admin**: System administrators who manage users, system configuration, and oversee operations
- **Teacher**: Educators who input attendance, grades, and monitor student progress
- **Student**: Learners who access their personal information, submit complaints, and view their risk status

### System Process
The A.U.R.A - Academic Understanding and Retention Application as a single automated process that:
- Authenticates users based on role
- Processes academic, attendance, financial, and behavioral data
- Applies machine learning models to predict student risk levels
- Generates early warning alerts and recommendations
- Provides role-appropriate views and reports
- Maintains system logs and audit trails

### Data Stores
- **Student Database**: Contains all persistent data including student profiles, attendance records, academic marks, fee transactions, library transactions, complaints, predictions, and alerts
- **ML Models**: Stores machine learning model metadata, trained model files, and performance metrics
- **System Logs**: Captures system activity, user actions, error logs, and audit trails for security and compliance

### Data Flows
The diagram illustrates how information flows between external entities and the system:
- Authentication credentials flow in both directions for login/logout processes
- Academic data (attendance, grades) flows from teachers to the system
- Financial data (fee payments) flows from admin and students to the system
- Behavioral data (complaints) flows from students to the system
- Processed information (risk predictions, alerts, reports) flows from the system to all user types
- Internal data flows support the machine learning pipeline and system maintenance

## Level 0 DFD Characteristics
- Shows the system as a single bubble (process)
- Focuses on inputs/outputs between system and external entities
- Does not show internal processes or detailed data flows
- Provides context for understanding system boundaries
- Serves as foundation for more detailed DFD levels