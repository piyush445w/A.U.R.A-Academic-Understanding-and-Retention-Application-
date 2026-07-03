"""
ML Configuration Module

This module contains all configuration constants for the Machine Learning pipeline,
including risk thresholds, feature columns, model parameters, and algorithm settings.
"""

import os
from typing import Dict, List, Any

# =============================================================================
# RISK THRESHOLDS
# =============================================================================

RISK_THRESHOLDS = {
    'low': 0.3,           # Probability below 0.3 is low risk
    'medium': 0.6,        # Probability between 0.3 and 0.6 is medium risk
    'high': 0.8,          # Probability between 0.6 and 0.8 is high risk
    'critical': 1.0       # Probability above 0.8 is critical risk
}

# Risk level labels
RISK_LEVELS = {
    'low': 'Low Risk',
    'medium': 'Medium Risk',
    'high': 'High Risk',
    'critical': 'Critical Risk'
}

# Risk level colors for visualization
RISK_COLORS = {
    'low': '#28a745',      # Green
    'medium': '#ffc107',   # Yellow
    'high': '#fd7e14',     # Orange
    'critical': '#dc3545'  # Red
}

# =============================================================================
# FEATURE COLUMNS
# =============================================================================

# Core feature columns used for prediction
FEATURE_COLUMNS = [
    'attendance_percentage',
    'average_marks',
    'fee_compliance_score',
    'behavior_score',
    'assignments_submitted',
    'library_usage',
    'extracurricular_score',
    'parent_engagement',
    'disciplinary_incidents',
    'academic_improvement'
]

# Feature display names
FEATURE_DISPLAY_NAMES = {
    'attendance_percentage': 'Attendance %',
    'average_marks': 'Average Marks',
    'fee_compliance_score': 'Fee Compliance',
    'behavior_score': 'Behavior Score',
    'assignments_submitted': 'Assignments Submitted',
    'library_usage': 'Library Usage',
    'extracurricular_score': 'Extracurricular Activities',
    'parent_engagement': 'Parent Engagement',
    'disciplinary_incidents': 'Disciplinary Incidents',
    'academic_improvement': 'Academic Improvement'
}

# Feature importance weights (can be adjusted based on domain knowledge)
FEATURE_WEIGHTS = {
    'attendance_percentage': 0.20,
    'average_marks': 0.25,
    'fee_compliance_score': 0.10,
    'behavior_score': 0.15,
    'assignments_submitted': 0.10,
    'library_usage': 0.05,
    'extracurricular_score': 0.05,
    'parent_engagement': 0.05,
    'disciplinary_incidents': 0.03,
    'academic_improvement': 0.02
}

# Categorical features that need encoding
CATEGORICAL_FEATURES = [
    'gender',
    'category',
    'parent_education',
    'family_income_level'
]

# Numerical features
NUMERICAL_FEATURES = [
    'attendance_percentage',
    'average_marks',
    'fee_compliance_score',
    'behavior_score',
    'assignments_submitted',
    'library_usage',
    'extracurricular_score',
    'parent_engagement',
    'disciplinary_incidents',
    'academic_improvement',
    'age',
    'previous_year_marks'
]

# =============================================================================
# MODEL PARAMETERS
# =============================================================================

# Random Forest parameters
RANDOM_FOREST_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': 42,
    'n_jobs': -1,
    'class_weight': 'balanced'
}

# Logistic Regression parameters
LOGISTIC_REGRESSION_PARAMS = {
    'C': 1.0,
    'penalty': 'l2',
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced',
    'n_jobs': -1
}

# Decision Tree parameters
DECISION_TREE_PARAMS = {
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'max_features': 'sqrt',
    'random_state': 42,
    'class_weight': 'balanced'
}

# Gradient Boosting parameters (optional advanced model)
GRADIENT_BOOSTING_PARAMS = {
    'n_estimators': 100,
    'learning_rate': 0.1,
    'max_depth': 5,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'subsample': 0.8,
    'random_state': 42
}

# Support Vector Machine parameters (optional advanced model)
SVM_PARAMS = {
    'C': 1.0,
    'kernel': 'rbf',
    'gamma': 'scale',
    'probability': True,
    'random_state': 42,
    'class_weight': 'balanced'
}

# Combined model parameters for all algorithms
MODEL_PARAMS = {
    'random_forest': RANDOM_FOREST_PARAMS,
    'logistic_regression': LOGISTIC_REGRESSION_PARAMS,
    'decision_tree': DECISION_TREE_PARAMS,
    'gradient_boosting': GRADIENT_BOOSTING_PARAMS,
    'svm': SVM_PARAMS
}

# =============================================================================
# ALGORITHMS
# =============================================================================

# Available algorithms for training
ALGORITHMS = {
    'random_forest': {
        'name': 'Random Forest',
        'description': 'Ensemble method using multiple decision trees',
        'params': RANDOM_FOREST_PARAMS,
        'type': 'ensemble',
        'supports_feature_importance': True,
        'supports_probability': True
    },
    'logistic_regression': {
        'name': 'Logistic Regression',
        'description': 'Linear model for binary classification',
        'params': LOGISTIC_REGRESSION_PARAMS,
        'type': 'linear',
        'supports_feature_importance': True,
        'supports_probability': True
    },
    'decision_tree': {
        'name': 'Decision Tree',
        'description': 'Tree-based model for classification',
        'params': DECISION_TREE_PARAMS,
        'type': 'tree',
        'supports_feature_importance': True,
        'supports_probability': True
    },
    'gradient_boosting': {
        'name': 'Gradient Boosting',
        'description': 'Ensemble method using boosting',
        'params': GRADIENT_BOOSTING_PARAMS,
        'type': 'ensemble',
        'supports_feature_importance': True,
        'supports_probability': True
    },
    'svm': {
        'name': 'Support Vector Machine',
        'description': 'Kernel-based classification model',
        'params': SVM_PARAMS,
        'type': 'kernel',
        'supports_feature_importance': False,
        'supports_probability': True
    }
}

# Default algorithm for training
DEFAULT_ALGORITHM = 'random_forest'

# =============================================================================
# DATA PREPROCESSING
# =============================================================================

# Missing value handling strategies
MISSING_VALUE_STRATEGIES = {
    'numerical': 'median',  # Options: 'mean', 'median', 'mode', 'constant'
    'categorical': 'mode'   # Options: 'mode', 'constant', 'drop'
}

# Normalization methods
NORMALIZATION_METHODS = {
    'standard': 'StandardScaler',      # Zero mean, unit variance
    'minmax': 'MinMaxScaler',          # Scale to [0, 1]
    'robust': 'RobustScaler',          # Robust to outliers
    'none': None                       # No normalization
}

# Default normalization method
DEFAULT_NORMALIZATION = 'standard'

# Test/train split ratio
DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42

# =============================================================================
# MODEL PERSISTENCE
# =============================================================================

# Model storage directory
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'trained')

# Model file naming convention
MODEL_NAMING_CONVENTION = '{algorithm}_v{version}_{timestamp}.joblib'

# Model metadata file naming convention
METADATA_NAMING_CONVENTION = '{algorithm}_v{version}_{timestamp}_metadata.json'

# Maximum number of model versions to keep
MAX_MODEL_VERSIONS = 10

# =============================================================================
# DATASET CONFIGURATION
# =============================================================================

# Dataset storage directory
DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'datasets')

# Supported dataset formats
SUPPORTED_FORMATS = ['csv', 'xlsx', 'json']

# Default dataset format
DEFAULT_DATASET_FORMAT = 'csv'

# Dataset validation rules
DATASET_VALIDATION_RULES = {
    'min_samples': 50,
    'max_missing_percentage': 0.3,
    'required_columns': FEATURE_COLUMNS + ['risk_label']
}

# =============================================================================
# EARLY WARNING SYSTEM
# =============================================================================

# Attendance alert threshold (percentage)
ATTENDANCE_ALERT_THRESHOLD = 75

# Academic alert threshold (marks)
ACADEMIC_ALERT_THRESHOLD = 50

# Fee payment grace period (days)
FEE_GRACE_PERIOD = 30

# Alert severity levels
ALERT_SEVERITY = {
    'info': 'Information',
    'warning': 'Warning',
    'critical': 'Critical'
}

# Alert types
ALERT_TYPES = {
    'attendance': 'Attendance Alert',
    'academic': 'Academic Alert',
    'fee': 'Fee Payment Alert',
    'behavior': 'Behavior Alert',
    'engagement': 'Engagement Alert'
}

# =============================================================================
# VISUALIZATION
# =============================================================================

# Plot style settings
PLOT_STYLE = {
    'figure_size': (10, 6),
    'dpi': 100,
    'style': 'seaborn-v0_8-darkgrid',
    'color_palette': 'viridis',
    'font_size': 12,
    'title_size': 14,
    'label_size': 12
}

# Output directory for plots
PLOT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'plots')

# =============================================================================
# EVALUATION METRICS
# =============================================================================

# Metrics to calculate during evaluation
EVALUATION_METRICS = [
    'accuracy',
    'precision',
    'recall',
    'f1_score',
    'roc_auc',
    'confusion_matrix'
]

# Cross-validation settings
CROSS_VALIDATION = {
    'n_splits': 5,
    'shuffle': True,
    'random_state': 42
}

# =============================================================================
# RECOMMENDATIONS
# =============================================================================

# Recommendations based on risk level and factors
RECOMMENDATIONS = {
    'attendance': {
        'low': [
            'Continue monitoring attendance',
            'Encourage consistent attendance'
        ],
        'medium': [
            'Schedule meeting with student',
            'Identify attendance barriers',
            'Implement attendance tracking'
        ],
        'high': [
            'Immediate parent notification',
            'Develop attendance improvement plan',
            'Consider counseling support'
        ],
        'critical': [
            'Urgent intervention required',
            'Schedule emergency meeting with parents',
            'Consider academic probation',
            'Assign mentor for daily check-ins'
        ]
    },
    'academic': {
        'low': [
            'Maintain current study habits',
            'Provide additional resources for enrichment'
        ],
        'medium': [
            'Arrange tutoring sessions',
            'Provide study materials',
            'Schedule regular progress checks'
        ],
        'high': [
            'Intensive academic support',
            'One-on-one mentoring',
            'Modified curriculum if needed',
            'Regular parent updates'
        ],
        'critical': [
            'Emergency academic intervention',
            'Consider grade retention',
            'Develop individualized education plan',
            'Weekly progress meetings'
        ]
    },
    'fee': {
        'low': [
            'Continue regular payment schedule'
        ],
        'medium': [
            'Send payment reminder',
            'Offer flexible payment options'
        ],
        'high': [
            'Schedule meeting with finance office',
            'Develop payment plan',
            'Check for scholarship eligibility'
        ],
        'critical': [
            'Urgent financial review',
            'Consider fee waiver or scholarship',
            'Emergency financial aid assessment'
        ]
    },
    'behavior': {
        'low': [
            'Positive reinforcement',
            'Continue monitoring'
        ],
        'medium': [
            'Behavior counseling',
            'Set clear expectations',
            'Regular check-ins'
        ],
        'high': [
            'Intensive behavior intervention',
            'Parent conference',
            'Behavior contract',
            'Consider counseling referral'
        ],
        'critical': [
            'Immediate disciplinary action',
            'Mandatory counseling',
            'Behavior improvement plan',
            'Consider suspension if necessary'
        ]
    }
}

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs', 'ml.log'),
            'mode': 'a'
        }
    },
    'loggers': {
        'app.ml': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        }
    }
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_risk_threshold(risk_level: str) -> float:
    """
    Get the threshold value for a specific risk level.
    
    Args:
        risk_level: The risk level ('low', 'medium', 'high', 'critical')
        
    Returns:
        The threshold value for the specified risk level
    """
    return RISK_THRESHOLDS.get(risk_level, 0.5)

def get_algorithm_params(algorithm: str) -> Dict[str, Any]:
    """
    Get the parameters for a specific algorithm.
    
    Args:
        algorithm: The algorithm name
        
    Returns:
        Dictionary of algorithm parameters
    """
    if algorithm in ALGORITHMS:
        return ALGORITHMS[algorithm]['params'].copy()
    return {}

def get_feature_display_name(feature: str) -> str:
    """
    Get the display name for a feature.
    
    Args:
        feature: The feature column name
        
    Returns:
        The display name for the feature
    """
    return FEATURE_DISPLAY_NAMES.get(feature, feature.replace('_', ' ').title())

def validate_algorithm(algorithm: str) -> bool:
    """
    Validate if an algorithm is supported.
    
    Args:
        algorithm: The algorithm name
        
    Returns:
        True if the algorithm is supported, False otherwise
    """
    return algorithm in ALGORITHMS

def get_supported_algorithms() -> List[str]:
    """
    Get a list of all supported algorithms.
    
    Returns:
        List of supported algorithm names
    """
    return list(ALGORITHMS.keys())

def ensure_directories():
    """
    Ensure all required directories exist.
    """
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(PLOT_OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(LOGGING_CONFIG['handlers']['file']['filename']), exist_ok=True)

# Initialize directories on module import
ensure_directories()
