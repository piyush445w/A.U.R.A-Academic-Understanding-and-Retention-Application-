"""
Model Training and Evaluation Module

This module provides comprehensive functions for training, evaluating, and
comparing machine learning models for the Student Risk Monitoring system.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve
)
from sklearn.model_selection import cross_val_score, StratifiedKFold

from app.ml.config import (
    ALGORITHMS,
    RANDOM_FOREST_PARAMS,
    LOGISTIC_REGRESSION_PARAMS,
    DECISION_TREE_PARAMS,
    GRADIENT_BOOSTING_PARAMS,
    SVM_PARAMS,
    CROSS_VALIDATION,
    EVALUATION_METRICS
)

# Configure logging
logger = logging.getLogger(__name__)


def train_random_forest(X_train: pd.DataFrame,
                       y_train: pd.Series,
                       params: Optional[Dict[str, Any]] = None) -> RandomForestClassifier:
    """
    Train a Random Forest classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model. If None, uses default from config.
        
    Returns:
        Trained RandomForestClassifier model
    """
    try:
        logger.info("Training Random Forest model...")
        
        if params is None:
            params = RANDOM_FOREST_PARAMS
        
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)
        
        logger.info(f"Random Forest trained with {model.n_estimators} estimators")
        logger.info(f"Training accuracy: {model.score(X_train, y_train):.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Random Forest: {str(e)}")
        raise


def train_logistic_regression(X_train: pd.DataFrame,
                             y_train: pd.Series,
                             params: Optional[Dict[str, Any]] = None) -> LogisticRegression:
    """
    Train a Logistic Regression classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model. If None, uses default from config.
        
    Returns:
        Trained LogisticRegression model
    """
    try:
        logger.info("Training Logistic Regression model...")
        
        if params is None:
            params = LOGISTIC_REGRESSION_PARAMS
        
        model = LogisticRegression(**params)
        model.fit(X_train, y_train)
        
        logger.info("Logistic Regression trained successfully")
        logger.info(f"Training accuracy: {model.score(X_train, y_train):.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Logistic Regression: {str(e)}")
        raise


def train_decision_tree(X_train: pd.DataFrame,
                       y_train: pd.Series,
                       params: Optional[Dict[str, Any]] = None) -> DecisionTreeClassifier:
    """
    Train a Decision Tree classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model. If None, uses default from config.
        
    Returns:
        Trained DecisionTreeClassifier model
    """
    try:
        logger.info("Training Decision Tree model...")
        
        if params is None:
            params = DECISION_TREE_PARAMS
        
        model = DecisionTreeClassifier(**params)
        model.fit(X_train, y_train)
        
        logger.info("Decision Tree trained successfully")
        logger.info(f"Training accuracy: {model.score(X_train, y_train):.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Decision Tree: {str(e)}")
        raise


def train_gradient_boosting(X_train: pd.DataFrame,
                           y_train: pd.Series,
                           params: Optional[Dict[str, Any]] = None) -> GradientBoostingClassifier:
    """
    Train a Gradient Boosting classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model. If None, uses default from config.
        
    Returns:
        Trained GradientBoostingClassifier model
    """
    try:
        logger.info("Training Gradient Boosting model...")
        
        if params is None:
            params = GRADIENT_BOOSTING_PARAMS
        
        model = GradientBoostingClassifier(**params)
        model.fit(X_train, y_train)
        
        logger.info("Gradient Boosting trained successfully")
        logger.info(f"Training accuracy: {model.score(X_train, y_train):.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training Gradient Boosting: {str(e)}")
        raise


def train_svm(X_train: pd.DataFrame,
              y_train: pd.Series,
              params: Optional[Dict[str, Any]] = None) -> SVC:
    """
    Train a Support Vector Machine classifier.
    
    Args:
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model. If None, uses default from config.
        
    Returns:
        Trained SVC model
    """
    try:
        logger.info("Training SVM model...")
        
        if params is None:
            params = SVM_PARAMS
        
        model = SVC(**params)
        model.fit(X_train, y_train)
        
        logger.info("SVM trained successfully")
        logger.info(f"Training accuracy: {model.score(X_train, y_train):.4f}")
        
        return model
        
    except Exception as e:
        logger.error(f"Error training SVM: {str(e)}")
        raise


def evaluate_model(model: Any,
                  X_test: pd.DataFrame,
                  y_test: pd.Series,
                  metrics: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Evaluate a trained model on test data.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        metrics: List of metrics to calculate. If None, uses default from config.
        
    Returns:
        Dictionary containing evaluation metrics
    """
    try:
        logger.info("Evaluating model...")
        
        if metrics is None:
            metrics = EVALUATION_METRICS
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Get probability predictions if available
        y_prob = None
        if hasattr(model, 'predict_proba'):
            y_prob = model.predict_proba(X_test)[:, 1]
        
        results = {}
        
        # Calculate requested metrics
        if 'accuracy' in metrics:
            results['accuracy'] = accuracy_score(y_test, y_pred)
        
        if 'precision' in metrics:
            results['precision'] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        
        if 'recall' in metrics:
            results['recall'] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        
        if 'f1_score' in metrics:
            results['f1_score'] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        if 'roc_auc' in metrics and y_prob is not None:
            try:
                results['roc_auc'] = roc_auc_score(y_test, y_prob)
            except ValueError:
                logger.warning("Could not calculate ROC AUC - may need binary classification")
                results['roc_auc'] = None
        
        if 'confusion_matrix' in metrics:
            results['confusion_matrix'] = confusion_matrix(y_test, y_pred).tolist()
        
        # Generate classification report
        results['classification_report'] = classification_report(y_test, y_pred, output_dict=True)
        
        # Store predictions for later use
        results['predictions'] = y_pred.tolist()
        if y_prob is not None:
            results['probabilities'] = y_prob.tolist()
        
        logger.info(f"Model evaluation completed:")
        logger.info(f"  Accuracy: {results.get('accuracy', 'N/A'):.4f}")
        logger.info(f"  Precision: {results.get('precision', 'N/A'):.4f}")
        logger.info(f"  Recall: {results.get('recall', 'N/A'):.4f}")
        logger.info(f"  F1 Score: {results.get('f1_score', 'N/A'):.4f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error evaluating model: {str(e)}")
        raise


def compare_models(models: Dict[str, Any],
                  X_test: pd.DataFrame,
                  y_test: pd.Series) -> pd.DataFrame:
    """
    Compare multiple models on the same test data.
    
    Args:
        models: Dictionary of model name to trained model
        X_test: Test features
        y_test: Test labels
        
    Returns:
        DataFrame containing comparison results
    """
    try:
        logger.info(f"Comparing {len(models)} models...")
        
        comparison_results = []
        
        for name, model in models.items():
            logger.info(f"Evaluating {name}...")
            
            # Evaluate model
            results = evaluate_model(model, X_test, y_test)
            
            # Add model name
            results['model'] = name
            
            comparison_results.append(results)
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_results)
        
        # Reorder columns to put model name first
        cols = ['model'] + [col for col in comparison_df.columns if col != 'model']
        comparison_df = comparison_df[cols]
        
        # Sort by accuracy (descending)
        comparison_df = comparison_df.sort_values('accuracy', ascending=False)
        
        logger.info("Model comparison completed")
        logger.info(f"Best model: {comparison_df.iloc[0]['model']} "
                   f"(Accuracy: {comparison_df.iloc[0]['accuracy']:.4f})")
        
        return comparison_df
        
    except Exception as e:
        logger.error(f"Error comparing models: {str(e)}")
        raise


def cross_validate_model(model: Any,
                        X: pd.DataFrame,
                        y: pd.Series,
                        cv: int = CROSS_VALIDATION['n_splits'],
                        scoring: str = 'accuracy') -> Dict[str, Any]:
    """
    Perform cross-validation on a model.
    
    Args:
        model: Model to cross-validate
        X: Features
        y: Labels
        cv: Number of cross-validation folds
        scoring: Scoring metric
        
    Returns:
        Dictionary containing cross-validation results
    """
    try:
        logger.info(f"Performing {cv}-fold cross-validation...")
        
        # Create stratified k-fold
        skf = StratifiedKFold(
            n_splits=cv,
            shuffle=CROSS_VALIDATION['shuffle'],
            random_state=CROSS_VALIDATION['random_state']
        )
        
        # Perform cross-validation
        cv_scores = cross_val_score(
            model, X, y,
            cv=skf,
            scoring=scoring,
            n_jobs=-1
        )
        
        results = {
            'cv_scores': cv_scores.tolist(),
            'mean_score': cv_scores.mean(),
            'std_score': cv_scores.std(),
            'min_score': cv_scores.min(),
            'max_score': cv_scores.max(),
            'scoring_metric': scoring,
            'n_folds': cv
        }
        
        logger.info(f"Cross-validation completed:")
        logger.info(f"  Mean {scoring}: {results['mean_score']:.4f} (+/- {results['std_score']:.4f})")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in cross-validation: {str(e)}")
        raise


def get_feature_importance(model: Any,
                          feature_names: List[str]) -> pd.DataFrame:
    """
    Get feature importance from a trained model.
    
    Args:
        model: Trained model
        feature_names: List of feature names
        
    Returns:
        DataFrame containing feature importance scores
    """
    try:
        logger.info("Extracting feature importance...")
        
        # Check if model has feature_importances_ attribute
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        elif hasattr(model, 'coef_'):
            # For linear models, use absolute coefficients
            importances = np.abs(model.coef_[0])
        else:
            logger.warning("Model does not support feature importance extraction")
            return pd.DataFrame()
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        })
        
        # Sort by importance (descending)
        importance_df = importance_df.sort_values('importance', ascending=False)
        
        # Add rank
        importance_df['rank'] = range(1, len(importance_df) + 1)
        
        # Normalize importance to sum to 1
        importance_df['importance_normalized'] = importance_df['importance'] / importance_df['importance'].sum()
        
        logger.info("Feature importance extracted successfully")
        logger.info(f"Top 3 features: {importance_df.head(3)['feature'].tolist()}")
        
        return importance_df
        
    except Exception as e:
        logger.error(f"Error extracting feature importance: {str(e)}")
        raise


def train_model_by_algorithm(algorithm: str,
                            X_train: pd.DataFrame,
                            y_train: pd.Series,
                            params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Train a model using the specified algorithm.
    
    Args:
        algorithm: Algorithm name ('random_forest', 'logistic_regression', etc.)
        X_train: Training features
        y_train: Training labels
        params: Optional parameters for the model
        
    Returns:
        Trained model
    """
    try:
        logger.info(f"Training model using {algorithm} algorithm...")
        
        if algorithm not in ALGORITHMS:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        # Get default params if not provided
        if params is None:
            params = ALGORITHMS[algorithm]['params']
        
        # Train model based on algorithm
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
        
        logger.info(f"Model trained successfully using {algorithm}")
        return model
        
    except Exception as e:
        logger.error(f"Error training model with {algorithm}: {str(e)}")
        raise


def get_model_info(model: Any) -> Dict[str, Any]:
    """
    Get information about a trained model.
    
    Args:
        model: Trained model
        
    Returns:
        Dictionary containing model information
    """
    try:
        info = {
            'model_type': type(model).__name__,
            'parameters': model.get_params() if hasattr(model, 'get_params') else {},
        }
        
        # Add model-specific information
        if hasattr(model, 'n_estimators'):
            info['n_estimators'] = model.n_estimators
        
        if hasattr(model, 'max_depth'):
            info['max_depth'] = model.max_depth
        
        if hasattr(model, 'n_features_in_'):
            info['n_features'] = model.n_features_in_
        
        if hasattr(model, 'classes_'):
            info['classes'] = model.classes_.tolist()
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise
