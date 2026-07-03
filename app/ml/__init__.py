"""
Machine Learning Module for Intelligent Student Risk Monitoring & Decision Support System

This module provides comprehensive ML capabilities for:
- Data preprocessing and feature engineering
- Model training, evaluation, and comparison
- Risk prediction and early warning system
- Dataset management and visualization
"""

import logging
from typing import Optional, Dict, Any, List, Tuple

# Configure logging for ML module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

# Module version
__version__ = "1.0.0"

# Import main components for easy access
from app.ml.config import (
    RISK_THRESHOLDS,
    FEATURE_COLUMNS,
    MODEL_PARAMS,
    ALGORITHMS
)

from app.ml.preprocessor import (
    load_dataset,
    clean_data,
    handle_missing_values,
    encode_categorical,
    normalize_features,
    prepare_features,
    split_data
)

from app.ml.feature_engineering import (
    calculate_attendance_percentage,
    calculate_average_marks,
    calculate_fee_compliance,
    calculate_behavior_score,
    create_feature_vector,
    extract_features_from_db
)

from app.ml.models import (
    train_random_forest,
    train_logistic_regression,
    train_decision_tree,
    evaluate_model,
    compare_models,
    cross_validate_model,
    get_feature_importance
)

from app.ml.predictor import (
    load_model,
    predict_risk,
    predict_batch,
    get_risk_level,
    get_recommendations
)

from app.ml.trainer import (
    train_model,
    save_model,
    load_latest_model,
    get_model_metadata,
    retrain_model
)

from app.ml.dataset_manager import (
    upload_dataset,
    merge_datasets,
    replace_dataset,
    validate_dataset,
    generate_sample_dataset,
    export_dataset
)

from app.ml.early_warning import (
    check_attendance_alert,
    check_academic_alert,
    check_fee_alert,
    generate_alerts,
    get_suggestions
)

from app.ml.visualization import (
    plot_risk_distribution,
    plot_feature_importance,
    plot_model_comparison,
    plot_confusion_matrix,
    plot_roc_curve
)

__all__ = [
    # Config
    'RISK_THRESHOLDS',
    'FEATURE_COLUMNS',
    'MODEL_PARAMS',
    'ALGORITHMS',
    
    # Preprocessor
    'load_dataset',
    'clean_data',
    'handle_missing_values',
    'encode_categorical',
    'normalize_features',
    'prepare_features',
    'split_data',
    
    # Feature Engineering
    'calculate_attendance_percentage',
    'calculate_average_marks',
    'calculate_fee_compliance',
    'calculate_behavior_score',
    'create_feature_vector',
    'extract_features_from_db',
    
    # Models
    'train_random_forest',
    'train_logistic_regression',
    'train_decision_tree',
    'evaluate_model',
    'compare_models',
    'cross_validate_model',
    'get_feature_importance',
    
    # Predictor
    'load_model',
    'predict_risk',
    'predict_batch',
    'get_risk_level',
    'get_recommendations',
    
    # Trainer
    'train_model',
    'save_model',
    'load_latest_model',
    'get_model_metadata',
    'retrain_model',
    
    # Dataset Manager
    'upload_dataset',
    'merge_datasets',
    'replace_dataset',
    'validate_dataset',
    'generate_sample_dataset',
    'export_dataset',
    
    # Early Warning
    'check_attendance_alert',
    'check_academic_alert',
    'check_fee_alert',
    'generate_alerts',
    'get_suggestions',
    
    # Visualization
    'plot_risk_distribution',
    'plot_feature_importance',
    'plot_model_comparison',
    'plot_confusion_matrix',
    'plot_roc_curve'
]

logger.info(f"ML Module v{__version__} initialized successfully")
