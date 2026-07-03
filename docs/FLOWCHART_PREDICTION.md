# Dropout Risk Prediction Process Flowchart

## A.U.R.A - Academic Understanding and Retention Application

This flowchart illustrates the dropout risk prediction process in the system.

```mermaid
flowchart TD
    %% Start
    Start[Start: Prediction Triggered]:::start
    
    %% Trigger Conditions
    TriggerScheduled{Is Prediction Scheduled?}:::decision
    TriggerManual{Manual Prediction Request?}:::decision
    TriggerEvent{Event-Based Trigger?}:::decision
    
    %% Data Collection Phase
    CollectStudentData[Collect Student Demographics]:::process
    CollectAttendanceData[Collect Attendance Records]:::process
    CollectAcademicData[Collect Academic Performance]:::process
    CollectFeeData[Collect Fee Payment Status]:::process
    CollectLibraryData[Collect Library Usage]:::process
    CollectComplaintData[Collect Complaint History]:::process
    
    %% Data Validation
    ValidateData{Validate Data Completeness}:::decision
    HandleMissingData[Handle Missing/Incomplete Data]:::process
    LogDataIssues[Log Data Quality Issues]:::process
    
    %% Feature Engineering
    CalculateAttendancePct[Calculate Attendance Percentage]:::process
    CalculateAvgMarks[Calculate Average Marks/Grades]:::process
    DetermineFeeStatus[Determine Fee Payment Status]:::process
    AssessLibraryUsage[Assess Library Engagement]:::process
    CountComplaints[Count Recent Complaints]:::process
    ExtractDemographics[Extract Demographic Features]:::process
    EngineerFeatures[Engineer Additional Features]:::process
    
    %% Feature Vector Creation
    CreateFeatureVector[Create Feature Vector for Model]:::process
    NormalizeFeatures[Normalize/Scale Features]:::process
    
    %% Model Loading
    LoadActiveModel[Load Active ML Model]:::process
    ModelValid{Model Loaded Successfully?}:::decision
    LogModelError[Log Model Loading Error]:::process
    UseFallbackModel[Use Fallback/Default Model]:::process
    
    %% Prediction Execution
    ExecutePrediction[Run Prediction Model]:::process
    GetRiskScore[Get Risk Score (0-1)]:::process
    GetRiskLevel[Determine Risk Level (Low/Medium/High)]:::process
    GetProbability[Get Probability of Dropout]:::process
    
    %% Post-processing
    ApplyThresholds[Apply Risk Thresholds]:::process
    GenerateRecommendations[Generate Recommendations]:::process
    StorePrediction[Store Prediction in Database]:::process
    
    %% Notification Trigger
    CheckAlertThreshold{Does Risk Warrant Alert?}:::decision
    TriggerAlert[Trigger Alert Generation Process]:::process
    
    %% Reporting
    UpdateDashboard[Update Risk Dashboard]:::process
    LogPrediction[Log Prediction Activity]:::process
    
    %% End
    EndSuccess[End: Prediction Completed Successfully]:::end
    EndFailure[End: Prediction Failed]:::end
    
    %% Connections
    Start --> TriggerScheduled
    Start --> TriggerManual
    Start --> TriggerEvent
    
    TriggerScheduled -- Yes --> CollectStudentData
    TriggerManual -- Yes --> CollectStudentData
    TriggerEvent -- Yes --> CollectStudentData
    
    CollectStudentData --> CollectAttendanceData
    CollectAttendanceData --> CollectAcademicData
    CollectAcademicData --> CollectFeeData
    CollectFeeData --> CollectLibraryData
    CollectLibraryData --> CollectComplaintData
    
    CollectComplaintData --> ValidateData
    ValidateData -- No --> HandleMissingData
    HandleMissingData --> LogDataIssues
    LogDataIssues --> ValidateData
    ValidateData -- Yes --> CalculateAttendancePct
    
    CalculateAttendancePct --> CalculateAvgMarks
    CalculateAvgMarks --> DetermineFeeStatus
    DetermineFeeStatus --> AssessLibraryUsage
    AssessLibraryUsage --> CountComplaints
    CountComplaints --> ExtractDemographics
    ExtractDemographics --> EngineerFeatures
    EngineerFeatures --> CreateFeatureVector
    CreateFeatureVector --> NormalizeFeatures
    
    NormalizeFeatures --> LoadActiveModel
    LoadActiveModel --> ModelValid
    ModelValid -- No --> LogModelError
    LogModelError --> UseFallbackModel
    UseFallbackModel --> ExecutePrediction
    ModelValid -- Yes --> ExecutePrediction
    
    ExecutePrediction --> GetRiskScore
    GetRiskScore --> GetRiskLevel
    GetRiskLevel --> GetProbability
    GetProbability --> ApplyThresholds
    ApplyThresholds --> GenerateRecommendations
    GenerateRecommendations --> StorePrediction
    
    StorePrediction --> CheckAlertThreshold
    CheckAlertThreshold -- Yes --> TriggerAlert
    TriggerAlert --> UpdateDashboard
    CheckAlertThreshold -- No --> UpdateDashboard
    UpdateDashboard --> LogPrediction
    LogPrediction --> EndSuccess
    
    %% Error paths
    LogModelError --> EndFailure
    LogDataIssues --> EndFailure
    
    %% Styling
    classDef start fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef end fill:#f8d7da,stroke:#721c24,stroke-width:2px;
    classDef process fill:#fff3cd,stroke:#856404,stroke-width:2px;
    classDef decision fill:#cce5ff,stroke:#004085,stroke-width:2px;
```

## Description

### Prediction Process Overview
The dropout risk prediction process is triggered periodically or on-demand to assess student risk levels using machine learning models. The process follows these main phases:

### 1. Trigger Conditions
- **Scheduled**: Automatic predictions run at regular intervals (daily/weekly)
- **Manual**: Admin/teacher requests prediction for specific student or group
- **Event-Based**: Triggered by significant events (e.g., new grade entry, fee default)

### 2. Data Collection
The system collects comprehensive data from multiple sources:
- **Student Demographics**: Age, gender, course, semester, etc.
- **Attendance Records**: Attendance percentage, patterns of absences/lateness
- **Academic Performance**: Average marks, grade trends, subject performance
- **Fee Payment Status**: Payment history, overdue amounts, payment consistency
- **Library Usage**: Book issue/return frequency, overdue books
- **Complaint History**: Number and nature of complaints filed

### 3. Data Validation
- Checks for data completeness and consistency
- Handles missing data through imputation or flagging
- Logs data quality issues for administrative review

### 4. Feature Engineering
Transforms raw data into meaningful features for the ML model:
- **Attendance Percentage**: Present days / total working days
- **Average Marks**: Weighted average across subjects
- **Fee Status**: Categorical (Paid, Pending, Overdue, Partial)
- **Library Engagement**: Books issued vs returned, overdue frequency
- **Complaint Frequency**: Count of recent complaints
- **Demographic Features**: Age, course, semester, etc.
- **Additional Features**: Interaction terms, trend analysis

### 5. Model Execution
- Loads the active ML model from storage
- Validates model integrity and freshness
- Falls back to default model if primary model unavailable
- Executes prediction to generate risk score (0-1)

### 6. Risk Classification
- Converts risk score to risk level using configurable thresholds:
  - Low Risk: Score < 0.4
  - Medium Risk: 0.4 ≤ Score < 0.7
  - High Risk: Score ≥ 0.7
- Generates probability of dropout
- Creates actionable recommendations based on risk factors

### 7. Post-processing & Storage
- Stores prediction results in database for historical tracking
- Updates student risk profile
- Determines if alert generation is warranted based on risk level changes

### 8. Notification & Reporting
- Triggers alert generation process for high/medium risk students
- Updates risk dashboard for real-time monitoring
- Logs prediction activity for audit and model performance tracking

### Technical Implementation Details
Based on the codebase:
- ML model loading: `app/ml/predictor.py`
- Feature engineering: `app/ml/feature_engineering.py`
- Prediction execution: `app/ml/predictor.py`
- Risk thresholds: Defined in `config.py` (HIGH_RISK_THRESHOLD=0.7, MEDIUM_RISK_THRESHOLD=0.4)
- Database storage: `app/models/prediction.py`
- Integration with alert system: `app/ml/early_warning.py`

### Model Information
The system currently uses a Random Forest classifier with:
- Accuracy: 87.50%
- Precision: 86.00%
- Recall: 89.00%
- F1-Score: 87.48%
- Features: 15+ engineered features from multiple data domains