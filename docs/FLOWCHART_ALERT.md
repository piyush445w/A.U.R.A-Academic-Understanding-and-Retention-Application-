# Early Warning Alert Generation Flowchart

## A.U.R.A - Academic Understanding and Retention Application

This flowchart illustrates the early warning alert generation process in the system.

```mermaid
flowchart TD
    %% Start
    Start[Start: Alert Trigger Condition Met]:::start
    
    %% Alert Sources
    PredictionAlert{Risk Prediction Trigger?}:::decision
    FeeAlert{Fee Payment Trigger?}:::decision
    LibraryAlert{Library Book Trigger?}:::decision
    AttendanceAlert{Attendance Issue Trigger?}:::decision
    AcademicAlert{Academic Performance Trigger?}:::decision
    ComplaintAlert{Complaint Trigger?}:::decision
    
    %% Alert Processing
    DetermineAlertType[Determine Alert Type]:::process
    AssessSeverity[Assess Alert Severity]:::process
    CheckDuplicate{Check for Duplicate Alerts}:::decision
    HandleDuplicate[Handle Duplicate Alert]:::process
    GenerateAlertID[Generate Unique Alert ID]:::process
    
    %% Alert Content Creation
    SelectTemplate[Select Alert Template]:::process
    PersonalizeMessage[Personalize Alert Message]:::process
    GenerateSuggestions[Generate Actionable Suggestions]:::process
    
    %% Alert Storage
    StoreAlert[Store Alert in Database]:::process
    LinkToStudent[Link Alert to Student Record]:::process
    
    %% Notification Dispatch
    DetermineChannels[Determine Notification Channels]:::process
    SendInAppNotification[Send In-App Notification]:::process
    SendEmailNotification[Send Email Notification]:::process
    SendSMSNotification[Send SMS Notification]:::process
    
    %% Tracking & Escalation
    LogAlertActivity[Log Alert Activity]:::process
    UpdateStudentRisk[Update Student Risk Profile]:::process
    CheckEscalation{Check if Escalation Needed?}:::decision
    TriggerEscalation[Trigger Escalation Process]:::process
    
    %% End
    EndSuccess[End: Alert Generated and Sent Successfully]:::end
    EndFailure[End: Alert Generation Failed]:::end
    
    %% Connections
    Start --> PredictionAlert
    Start --> FeeAlert
    Start --> LibraryAlert
    Start --> AttendanceAlert
    Start --> AcademicAlert
    Start --> ComplaintAlert
    
    PredictionAlert -- Yes --> DetermineAlertType
    FeeAlert -- Yes --> DetermineAlertType
    LibraryAlert -- Yes --> DetermineAlertType
    AttendanceAlert -- Yes --> DetermineAlertType
    AcademicAlert -- Yes --> DetermineAlertType
    ComplaintAlert -- Yes --> DetermineAlertType
    
    DetermineAlertType --> AssessSeverity
    AssessSeverity --> CheckDuplicate
    CheckDuplicate -- Yes --> HandleDuplicate
    HandleDuplicate --> DetermineAlertType
    CheckDuplicate -- No --> GenerateAlertID
    GenerateAlertID --> SelectTemplate
    SelectTemplate --> PersonalizeMessage
    PersonalizeMessage --> GenerateSuggestions
    GenerateSuggestions --> StoreAlert
    StoreAlert --> LinkToStudent
    LinkToStudent --> DetermineChannels
    DetermineChannels --> SendInAppNotification
    DetermineChannels --> SendEmailNotification
    DetermineChannels --> SendSMSNotification
    SendInAppNotification --> LogAlertActivity
    SendEmailNotification --> LogAlertActivity
    SendSMSNotification --> LogAlertActivity
    LogAlertActivity --> UpdateStudentRisk
    UpdateStudentRisk --> CheckEscalation
    CheckEscalation -- Yes --> TriggerEscalation
    CheckEscalation -- No --> EndSuccess
    TriggerEscalation --> EndSuccess
    
    %% Error paths
    HandleDuplicate --> EndFailure
    StoreAlert --> EndFailure
    LogAlertActivity --> EndFailure
    
    %% Styling
    classDef start fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef end fill:#f8d7da,stroke:#721c24,stroke-width:2px;
    classDef process fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef decision fill:#cce5ff,stroke:#004085,stroke-width:2px;
```

## Description

### Alert Generation Process Overview
The early warning alert generation process creates and delivers notifications when the system detects conditions that may indicate a student is at risk. The process handles multiple trigger sources and ensures alerts are properly formatted, deduplicated, and delivered through appropriate channels.

### 1. Alert Sources (Triggers)
Alerts can be triggered by various system components:
- **Risk Prediction**: High/medium risk scores from ML model
- **Fee Payment**: Overdue fees, payment defaults
- **Library**: Overdue books, excessive fines
- **Attendance**: Excessive absences, patterns of lateness
- **Academic Performance**: Declining grades, failing subjects
- **Complaints**: Unresolved complaints, multiple complaints

### 2. Alert Processing
- **Determine Alert Type**: Categorizes alert (Attendance, Academic, Fee, Behavior, General)
- **Assess Severity**: Assigns severity level (Info, Warning, Critical) based on risk factors
- **Check for Duplicates**: Prevents alert fatigue by checking for similar recent alerts
- **Handle Duplicate**: Either suppresses duplicate or updates existing alert
- **Generate Alert ID**: Creates unique identifier for tracking

### 3. Alert Content Creation
- **Select Template**: Chooses appropriate message template based on alert type and severity
- **Personalize Message**: Inserts student-specific details (name, ID, specific metrics)
- **Generate Suggestions**: Creates actionable recommendations for intervention

### 4. Alert Storage
- **Store Alert**: Saves alert record in database with timestamp and status
- **Link to Student**: Associates alert with specific student record for tracking

### 5. Notification Dispatch
- **Determine Channels**: Selects delivery methods based on user preferences and alert severity
- **In-App Notification**: Displays notification within the application interface
- **Email Notification**: Sends detailed alert via email (configurable)
- **SMS Notification**: Sends brief alert via SMS for critical issues (if configured)

### 6. Tracking & Escalation
- **Log Alert Activity**: Records alert generation for audit and analytics
- **Update Student Risk**: Modifies student's risk profile based on alert
- **Check Escalation**: Determines if alert requires administrative escalation
- **Trigger Escalation**: Notifies supervisors or initiates intervention workflow

### Alert Types and Severity Levels

#### Alert Types:
1. **Attendance**: Related to attendance patterns (absences, lateness)
2. **Academic**: Related to academic performance (grades, subject failures)
3. **Fee**: Related to payment status (overdue, pending payments)
4. **Behavior**: Related to conduct (complaints, disciplinary issues)
5. **General**: Other risk factors not covered above

#### Severity Levels:
1. **Info**: Informational, low priority (e.g., first minor absence)
2. **Warning**: Moderate concern requiring attention (e.g., repeated absences)
3. **Critical**: High risk requiring immediate intervention (e.g., multiple risk factors)

### Deduplication Logic
To prevent alert fatigue, the system checks for:
- Same alert type for same student within configurable time window
- Similar severity and trigger conditions
- Updates existing alert timestamp instead of creating new one
- Escalates frequency if same issue persists

### Notification Channels
- **In-App**: Real-time notifications visible in user dashboard
- **Email**: Detailed alerts sent to registered email addresses
- **SMS**: Brief critical alerts sent to phone numbers (opt-in)
- **Portal Alerts**: Visible in student/parent portals

### Technical Implementation
Based on the codebase:
- Alert model: `app/models/alert.py`
- Alert generation logic: `app/ml/early_warning.py`
- Notification services: `app/utils/helpers.py` (email/SMS functions)
- Alert routes: `app/routes/admin.py` (alert management views)
- Alert templates: Located in template directories for customization

### Configuration Options
Alert behavior can be configured through:
- Time windows for duplicate checking
- Severity thresholds for each alert type
- Notification channel preferences per user role
- Escalation rules based on alert frequency and severity
- Template customization for different languages/formats

This process ensures that stakeholders receive timely, relevant, and actionable information to support student success while minimizing notification overload.