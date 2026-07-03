"""
Prediction Module

This module provides comprehensive prediction functions for the
Student Risk Monitoring system, including model loading, risk prediction,
and recommendation generation.
"""

import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from app.ml.config import (
    RISK_THRESHOLDS,
    RISK_LEVELS,
    RISK_COLORS,
    RECOMMENDATIONS,
    MODEL_DIR,
    FEATURE_COLUMNS
)

# Configure logging
logger = logging.getLogger(__name__)


def load_model(model_path: str) -> Any:
    """
    Load a trained model from disk.
    
    Args:
        model_path: Path to the saved model file
        
    Returns:
        Loaded model object
        
    Raises:
        FileNotFoundError: If the model file does not exist
        Exception: For other loading errors
    """
    try:
        logger.info(f"Loading model from: {model_path}")
        
        # Check if file exists
        if not Path(model_path).exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model
        model = joblib.load(model_path)
        
        logger.info(f"Model loaded successfully: {type(model).__name__}")
        return model
        
    except FileNotFoundError:
        logger.error(f"Model file not found: {model_path}")
        raise
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise


def predict_risk(model: Any,
                student_features: Dict[str, float],
                feature_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Predict risk level for a single student.
    
    Args:
        model: Trained model
        student_features: Dictionary of feature names and values
        feature_columns: List of feature columns to use. If None, uses default from config.
        
    Returns:
        Dictionary containing prediction results
    """
    try:
        logger.info("Predicting risk for student...")
        
        if feature_columns is None:
            feature_columns = FEATURE_COLUMNS
        
        # Prepare features
        features = []
        for col in feature_columns:
            if col in student_features:
                features.append(student_features[col])
            else:
                logger.warning(f"Missing feature: {col}, using default value 0")
                features.append(0.0)
        
        # Convert to numpy array
        X = np.array(features).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Get probability if available
        probability = None
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(X)[0]
            probability = float(proba[1]) if len(proba) > 1 else float(proba[0])
        
        # Determine risk level
        risk_level = get_risk_level(probability) if probability is not None else get_risk_level(prediction)
        
        # Get recommendations
        recommendations = get_recommendations(risk_level, student_features)
        
        # Prepare result
        result = {
            'prediction': int(prediction),
            'probability': probability,
            'risk_level': risk_level,
            'risk_label': RISK_LEVELS.get(risk_level, 'Unknown'),
            'risk_color': RISK_COLORS.get(risk_level, '#6c757d'),
            'recommendations': recommendations,
            'features_used': feature_columns,
            'feature_values': student_features
        }
        
        logger.info(f"Risk prediction completed: {risk_level} (probability: {probability:.4f})")
        return result
        
    except Exception as e:
        logger.error(f"Error predicting risk: {str(e)}")
        raise


def predict_batch(model: Any,
                 students_features: List[Dict[str, float]],
                 feature_columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Predict risk levels for multiple students.
    
    Args:
        model: Trained model
        students_features: List of dictionaries containing student features
        feature_columns: List of feature columns to use. If None, uses default from config.
        
    Returns:
        List of dictionaries containing prediction results for each student
    """
    try:
        logger.info(f"Predicting risk for {len(students_features)} students...")
        
        if feature_columns is None:
            feature_columns = FEATURE_COLUMNS
        
        results = []
        
        for i, student_features in enumerate(students_features):
            try:
                result = predict_risk(model, student_features, feature_columns)
                result['student_index'] = i
                results.append(result)
            except Exception as e:
                logger.error(f"Error predicting for student {i}: {str(e)}")
                # Add error result
                results.append({
                    'student_index': i,
                    'error': str(e),
                    'prediction': None,
                    'probability': None,
                    'risk_level': 'unknown',
                    'risk_label': 'Error',
                    'risk_color': '#6c757d',
                    'recommendations': []
                })
        
        # Log summary
        risk_counts = {}
        for result in results:
            risk_level = result.get('risk_level', 'unknown')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        logger.info(f"Batch prediction completed:")
        for level, count in risk_counts.items():
            logger.info(f"  {level}: {count} students")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        raise


def get_risk_level(probability: float) -> str:
    """
    Determine risk level based on probability.
    
    Args:
        probability: Risk probability (0-1)
        
    Returns:
        Risk level string ('low', 'medium', 'high', 'critical')
    """
    try:
        if probability < RISK_THRESHOLDS['low']:
            return 'low'
        elif probability < RISK_THRESHOLDS['medium']:
            return 'medium'
        elif probability < RISK_THRESHOLDS['high']:
            return 'high'
        else:
            return 'critical'
            
    except Exception as e:
        logger.error(f"Error determining risk level: {str(e)}")
        return 'medium'  # Default to medium risk


def get_recommendations(risk_level: str,
                       factors: Optional[Dict[str, float]] = None) -> List[str]:
    """
    Get recommendations based on risk level and contributing factors.
    
    Args:
        risk_level: Risk level ('low', 'medium', 'high', 'critical')
        factors: Dictionary of feature values that contributed to the risk
        
    Returns:
        List of recommendation strings
    """
    try:
        recommendations = []
        
        # Get general recommendations for risk level
        if risk_level in RECOMMENDATIONS:
            # Add recommendations based on primary factors
            if factors:
                # Identify primary risk factors
                risk_factors = identify_risk_factors(factors)
                
                for factor in risk_factors[:3]:  # Top 3 factors
                    if factor in RECOMMENDATIONS:
                        factor_recommendations = RECOMMENDATIONS[factor].get(risk_level, [])
                        recommendations.extend(factor_recommendations)
            
            # Add general recommendations if no specific ones
            if not recommendations:
                recommendations = RECOMMENDATIONS.get('attendance', {}).get(risk_level, [])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
        
        return unique_recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        return ["Contact administrator for personalized recommendations"]


def identify_risk_factors(feature_values: Dict[str, float]) -> List[str]:
    """
    Identify primary risk factors from feature values.
    
    Args:
        feature_values: Dictionary of feature names and values
        
    Returns:
        List of risk factor names, sorted by severity
    """
    try:
        risk_factors = []
        
        # Check attendance
        if 'attendance_percentage' in feature_values:
            attendance = feature_values['attendance_percentage']
            if attendance < 75:
                risk_factors.append('attendance')
        
        # Check academic performance
        if 'average_marks' in feature_values:
            marks = feature_values['average_marks']
            if marks < 50:
                risk_factors.append('academic')
        
        # Check fee compliance
        if 'fee_compliance_score' in feature_values:
            fee_score = feature_values['fee_compliance_score']
            if fee_score < 70:
                risk_factors.append('fee')
        
        # Check behavior
        if 'behavior_score' in feature_values:
            behavior = feature_values['behavior_score']
            if behavior < 70:
                risk_factors.append('behavior')
        
        # Check disciplinary incidents
        if 'disciplinary_incidents' in feature_values:
            incidents = feature_values['disciplinary_incidents']
            if incidents > 3:
                risk_factors.append('behavior')
        
        return risk_factors
        
    except Exception as e:
        logger.error(f"Error identifying risk factors: {str(e)}")
        return []


def get_prediction_explanation(prediction_result: Dict[str, Any]) -> str:
    """
    Generate a human-readable explanation of the prediction.
    
    Args:
        prediction_result: Dictionary containing prediction results
        
    Returns:
        Explanation string
    """
    try:
        risk_level = prediction_result.get('risk_level', 'unknown')
        probability = prediction_result.get('probability')
        recommendations = prediction_result.get('recommendations', [])
        
        explanation = f"Risk Assessment: {RISK_LEVELS.get(risk_level, 'Unknown')}\n"
        
        if probability is not None:
            explanation += f"Confidence: {probability:.1%}\n"
        
        explanation += "\nKey Recommendations:\n"
        for i, rec in enumerate(recommendations[:5], 1):
            explanation += f"{i}. {rec}\n"
        
        return explanation
        
    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        return "Unable to generate explanation"


def validate_prediction_input(student_features: Dict[str, float],
                            feature_columns: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate input features for prediction.
    
    Args:
        student_features: Dictionary of feature names and values
        feature_columns: List of required feature columns
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    try:
        issues = []
        
        if feature_columns is None:
            feature_columns = FEATURE_COLUMNS
        
        # Check for missing features
        missing_features = [col for col in feature_columns if col not in student_features]
        if missing_features:
            issues.append(f"Missing features: {missing_features}")
        
        # Check for invalid values
        for feature, value in student_features.items():
            if not isinstance(value, (int, float)):
                issues.append(f"Invalid value type for {feature}: {type(value)}")
            elif np.isnan(value) or np.isinf(value):
                issues.append(f"Invalid value for {feature}: {value}")
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Prediction input validation failed: {issues}")
        else:
            logger.info("Prediction input validation passed")
        
        return is_valid, issues
        
    except Exception as e:
        logger.error(f"Error validating prediction input: {str(e)}")
        raise


def get_risk_statistics(predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics from a list of predictions.
    
    Args:
        predictions: List of prediction result dictionaries
        
    Returns:
        Dictionary containing risk statistics
    """
    try:
        total = len(predictions)
        
        if total == 0:
            return {
                'total': 0,
                'risk_distribution': {},
                'average_probability': None
            }
        
        # Count risk levels
        risk_counts = {}
        probabilities = []
        
        for pred in predictions:
            risk_level = pred.get('risk_level', 'unknown')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
            
            if pred.get('probability') is not None:
                probabilities.append(pred['probability'])
        
        # Calculate percentages
        risk_distribution = {
            level: {
                'count': count,
                'percentage': (count / total) * 100
            }
            for level, count in risk_counts.items()
        }
        
        # Calculate average probability
        avg_probability = np.mean(probabilities) if probabilities else None
        
        statistics = {
            'total': total,
            'risk_distribution': risk_distribution,
            'average_probability': avg_probability,
            'high_risk_count': risk_counts.get('high', 0) + risk_counts.get('critical', 0),
            'low_risk_count': risk_counts.get('low', 0)
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error calculating risk statistics: {str(e)}")
        raise
