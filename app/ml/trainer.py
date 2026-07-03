"""
Model Training Orchestration Module

This module provides comprehensive functions for orchestrating model training,
saving/loading models, and managing model versions for the Student Risk Monitoring system.
"""

import logging
import joblib
import json
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

from app.ml.config import (
    ALGORITHMS,
    DEFAULT_ALGORITHM,
    MODEL_DIR,
    MODEL_NAMING_CONVENTION,
    METADATA_NAMING_CONVENTION,
    MAX_MODEL_VERSIONS,
    DEFAULT_TEST_SIZE,
    DEFAULT_RANDOM_STATE
)
from app.ml.preprocessor import (
    load_dataset,
    clean_data,
    handle_missing_values,
    prepare_features,
    split_data
)
from app.ml.models import (
    train_random_forest,
    train_logistic_regression,
    train_decision_tree,
    train_gradient_boosting,
    train_svm,
    evaluate_model,
    cross_validate_model,
    get_feature_importance,
    get_model_info
)

# Configure logging
logger = logging.getLogger(__name__)


def train_model(algorithm: str = DEFAULT_ALGORITHM,
               dataset_path: Optional[str] = None,
               test_size: float = DEFAULT_TEST_SIZE,
               params: Optional[Dict[str, Any]] = None,
               cross_validate: bool = True,
               save: bool = True) -> Dict[str, Any]:
    """
    Train a model using the specified algorithm and dataset.
    
    Args:
        algorithm: Algorithm to use for training
        dataset_path: Path to the dataset file. If None, uses default dataset.
        test_size: Proportion of data to use for testing
        params: Optional parameters for the model
        cross_validate: Whether to perform cross-validation
        save: Whether to save the trained model
        
    Returns:
        Dictionary containing training results and model information
    """
    try:
        logger.info(f"Starting model training with algorithm: {algorithm}")
        
        # Validate algorithm
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}. "
                           f"Supported algorithms: {list(ALGORITHMS.keys())}")
        
        # Load and preprocess data
        if dataset_path:
            logger.info(f"Loading dataset from: {dataset_path}")
            df = load_dataset(dataset_path)
        else:
            logger.warning("No dataset path provided, using default dataset")
            # In a real application, this would load a default dataset
            raise ValueError("Dataset path is required for training")
        
        # Clean and preprocess data
        df = clean_data(df)
        df = handle_missing_values(df)
        
        # Prepare features
        X, y = prepare_features(df)
        
        # Split data
        X_train, X_test, y_train, y_test = split_data(X, y, test_size=test_size)
        
        logger.info(f"Data split: {X_train.shape[0]} training, {X_test.shape[0]} testing")
        
        # Train model
        if algorithm == 'random_forest':
            model = train_random_forest(X_train, y_train, params)
        elif algorithm == 'logistic_regression':
            model = train_logistic_regression(X_train, y_train, params)
        elif algorithm == 'decision_tree':
            model = train_decision_tree(X_train, y_train, params)
        elif algorithm == 'gradient_boosting':
            model = train_gradient_boosting(X_train, y_train, params)
        elif algorithm == 'svm':
            model = train_svm(X_train, y_train, params)
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Evaluate model
        logger.info("Evaluating model...")
        evaluation_results = evaluate_model(model, X_test, y_test)
        
        # Cross-validate if requested
        cv_results = None
        if cross_validate:
            logger.info("Performing cross-validation...")
            cv_results = cross_validate_model(model, X, y)
        
        # Get feature importance
        feature_importance = None
        if hasattr(model, 'feature_importances_') or hasattr(model, 'coef_'):
            feature_importance = get_feature_importance(model, X.columns.tolist())
        
        # Get model info
        model_info = get_model_info(model)
        
        # Save model if requested
        model_path = None
        if save:
            model_path = save_model(model, algorithm)
        
        # Prepare results
        results = {
            'algorithm': algorithm,
            'model_info': model_info,
            'evaluation': evaluation_results,
            'cross_validation': cv_results,
            'feature_importance': feature_importance.to_dict() if feature_importance is not None else None,
            'model_path': model_path,
            'training_samples': X_train.shape[0],
            'testing_samples': X_test.shape[0],
            'features_used': X.columns.tolist(),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Model training completed successfully")
        logger.info(f"Test accuracy: {evaluation_results.get('accuracy', 'N/A'):.4f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise


def save_model(model: Any,
              model_name: str,
              version: Optional[str] = None) -> str:
    """
    Save a trained model to disk.
    
    Args:
        model: Trained model to save
        model_name: Name of the model (e.g., 'random_forest')
        version: Version string. If None, generates automatically.
        
    Returns:
        Path where the model was saved
    """
    try:
        # Generate version if not provided
        if version is None:
            version = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = MODEL_NAMING_CONVENTION.format(
            algorithm=model_name,
            version=version,
            timestamp=timestamp
        )
        
        # Ensure model directory exists
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        # Full path
        model_path = os.path.join(MODEL_DIR, filename)
        
        # Save model
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata_filename = METADATA_NAMING_CONVENTION.format(
            algorithm=model_name,
            version=version,
            timestamp=timestamp
        )
        metadata_path = os.path.join(MODEL_DIR, metadata_filename)
        
        metadata = {
            'model_name': model_name,
            'version': version,
            'timestamp': timestamp,
            'model_type': type(model).__name__,
            'model_path': model_path,
            'parameters': model.get_params() if hasattr(model, 'get_params') else {}
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Model saved to: {model_path}")
        logger.info(f"Metadata saved to: {metadata_path}")
        
        # Clean up old versions
        cleanup_old_versions(model_name)
        
        return model_path
        
    except Exception as e:
        logger.error(f"Error saving model: {str(e)}")
        raise


def load_latest_model(model_name: Optional[str] = None) -> Tuple[Any, Dict[str, Any]]:
    """
    Load the latest trained model.
    
    Args:
        model_name: Name of the model to load. If None, loads the most recent model.
        
    Returns:
        Tuple of (loaded model, metadata dictionary)
    """
    try:
        logger.info("Loading latest model...")
        
        # Ensure model directory exists
        if not os.path.exists(MODEL_DIR):
            raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")
        
        # Find all model files
        model_files = []
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith('.joblib'):
                if model_name is None or filename.startswith(model_name):
                    model_files.append(filename)
        
        if not model_files:
            raise FileNotFoundError(f"No model files found in {MODEL_DIR}")
        
        # Sort by modification time (newest first)
        model_files.sort(key=lambda x: os.path.getmtime(os.path.join(MODEL_DIR, x)), reverse=True)
        
        # Load the latest model
        latest_model_file = model_files[0]
        model_path = os.path.join(MODEL_DIR, latest_model_file)
        
        model = joblib.load(model_path)
        
        # Load metadata if available
        metadata_file = latest_model_file.replace('.joblib', '_metadata.json')
        metadata_path = os.path.join(MODEL_DIR, metadata_file)
        
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        logger.info(f"Loaded model: {latest_model_file}")
        
        return model, metadata
        
    except Exception as e:
        logger.error(f"Error loading latest model: {str(e)}")
        raise


def get_model_metadata(model_path: str) -> Dict[str, Any]:
    """
    Get metadata for a specific model.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        Dictionary containing model metadata
    """
    try:
        logger.info(f"Getting metadata for model: {model_path}")
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Look for metadata file
        metadata_path = model_path.replace('.joblib', '_metadata.json')
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        else:
            # Generate basic metadata from model file
            model = joblib.load(model_path)
            metadata = {
                'model_path': model_path,
                'model_type': type(model).__name__,
                'file_size': os.path.getsize(model_path),
                'last_modified': datetime.fromtimestamp(
                    os.path.getmtime(model_path)
                ).isoformat()
            }
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error getting model metadata: {str(e)}")
        raise


def retrain_model(new_data_path: str,
                 algorithm: Optional[str] = None,
                 test_size: float = DEFAULT_TEST_SIZE) -> Dict[str, Any]:
    """
    Retrain a model with new data.
    
    Args:
        new_data_path: Path to the new dataset
        algorithm: Algorithm to use. If None, uses the same algorithm as the previous model.
        test_size: Proportion of data to use for testing
        
    Returns:
        Dictionary containing retraining results
    """
    try:
        logger.info(f"Retraining model with new data from: {new_data_path}")
        
        # Load latest model to get algorithm
        if algorithm is None:
            try:
                _, metadata = load_latest_model()
                algorithm = metadata.get('model_name', DEFAULT_ALGORITHM)
                logger.info(f"Using algorithm from previous model: {algorithm}")
            except:
                algorithm = DEFAULT_ALGORITHM
                logger.info(f"Using default algorithm: {algorithm}")
        
        # Train new model
        results = train_model(
            algorithm=algorithm,
            dataset_path=new_data_path,
            test_size=test_size,
            save=True
        )
        
        logger.info("Model retraining completed successfully")
        return results
        
    except Exception as e:
        logger.error(f"Error retraining model: {str(e)}")
        raise


def cleanup_old_versions(model_name: str,
                        max_versions: int = MAX_MODEL_VERSIONS) -> None:
    """
    Clean up old model versions, keeping only the most recent ones.
    
    Args:
        model_name: Name of the model
        max_versions: Maximum number of versions to keep
    """
    try:
        logger.info(f"Cleaning up old versions for model: {model_name}")
        
        # Find all model files for this model
        model_files = []
        for filename in os.listdir(MODEL_DIR):
            if filename.startswith(model_name) and filename.endswith('.joblib'):
                model_files.append(filename)
        
        # Sort by modification time (oldest first)
        model_files.sort(key=lambda x: os.path.getmtime(os.path.join(MODEL_DIR, x)))
        
        # Delete old versions
        if len(model_files) > max_versions:
            files_to_delete = model_files[:-max_versions]
            
            for filename in files_to_delete:
                model_path = os.path.join(MODEL_DIR, filename)
                metadata_path = model_path.replace('.joblib', '_metadata.json')
                
                # Delete model file
                if os.path.exists(model_path):
                    os.remove(model_path)
                    logger.info(f"Deleted old model: {filename}")
                
                # Delete metadata file
                if os.path.exists(metadata_path):
                    os.remove(metadata_path)
                    logger.info(f"Deleted metadata: {os.path.basename(metadata_path)}")
        
        logger.info(f"Cleanup completed. Kept {min(len(model_files), max_versions)} versions.")
        
    except Exception as e:
        logger.error(f"Error cleaning up old versions: {str(e)}")
        # Don't raise - cleanup is not critical


def list_saved_models() -> List[Dict[str, Any]]:
    """
    List all saved models with their metadata.
    
    Returns:
        List of dictionaries containing model information
    """
    try:
        logger.info("Listing saved models...")
        
        if not os.path.exists(MODEL_DIR):
            return []
        
        models = []
        
        for filename in os.listdir(MODEL_DIR):
            if filename.endswith('.joblib'):
                model_path = os.path.join(MODEL_DIR, filename)
                
                # Get metadata
                metadata = get_model_metadata(model_path)
                metadata['filename'] = filename
                
                models.append(metadata)
        
        # Sort by timestamp (newest first)
        models.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        logger.info(f"Found {len(models)} saved models")
        return models
        
    except Exception as e:
        logger.error(f"Error listing saved models: {str(e)}")
        raise


def delete_model(model_path: str) -> bool:
    """
    Delete a saved model and its metadata.
    
    Args:
        model_path: Path to the model file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Deleting model: {model_path}")
        
        # Delete model file
        if os.path.exists(model_path):
            os.remove(model_path)
            logger.info(f"Deleted model file: {model_path}")
        
        # Delete metadata file
        metadata_path = model_path.replace('.joblib', '_metadata.json')
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
            logger.info(f"Deleted metadata file: {metadata_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error deleting model: {str(e)}")
        return False
