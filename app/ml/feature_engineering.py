"""
Feature Engineering Module

This module provides comprehensive feature engineering functions for the
Student Risk Monitoring system, including calculation of various student
performance metrics and creation of feature vectors for ML models.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from app.ml.config import (
    FEATURE_COLUMNS,
    FEATURE_WEIGHTS,
    ATTENDANCE_ALERT_THRESHOLD,
    ACADEMIC_ALERT_THRESHOLD
)

# Configure logging
logger = logging.getLogger(__name__)


def calculate_attendance_percentage(student_data: Dict[str, Any]) -> float:
    """
    Calculate attendance percentage for a student.
    
    Args:
        student_data: Dictionary containing student attendance data
            Expected keys: 'total_classes', 'attended_classes' or
            'attendance_records' (list of attendance records)
        
    Returns:
        Attendance percentage (0-100)
    """
    try:
        # Method 1: Direct calculation from totals
        if 'total_classes' in student_data and 'attended_classes' in student_data:
            total = student_data['total_classes']
            attended = student_data['attended_classes']
            
            if total == 0:
                logger.warning("Total classes is 0, returning 0 attendance")
                return 0.0
            
            percentage = (attended / total) * 100
            return min(100.0, max(0.0, percentage))
        
        # Method 2: Calculate from attendance records
        elif 'attendance_records' in student_data:
            records = student_data['attendance_records']
            
            if not records:
                logger.warning("No attendance records found")
                return 0.0
            
            # Count present days
            present_count = sum(1 for record in records if record.get('status') == 'present')
            total_count = len(records)
            
            if total_count == 0:
                return 0.0
            
            percentage = (present_count / total_count) * 100
            return min(100.0, max(0.0, percentage))
        
        # Method 3: Calculate from date range
        elif 'start_date' in student_data and 'end_date' in student_data:
            start_date = pd.to_datetime(student_data['start_date'])
            end_date = pd.to_datetime(student_data['end_date'])
            present_dates = student_data.get('present_dates', [])
            
            # Calculate total school days (excluding weekends)
            total_days = np.busday_count(start_date.date(), end_date.date())
            
            if total_days == 0:
                return 0.0
            
            # Count present days
            present_count = len([d for d in present_dates if start_date <= pd.to_datetime(d) <= end_date])
            
            percentage = (present_count / total_days) * 100
            return min(100.0, max(0.0, percentage))
        
        else:
            logger.warning("Insufficient data to calculate attendance percentage")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating attendance percentage: {str(e)}")
        return 0.0


def calculate_average_marks(student_data: Dict[str, Any]) -> float:
    """
    Calculate average marks for a student across all subjects.
    
    Args:
        student_data: Dictionary containing student marks data
            Expected keys: 'marks' (list of mark records) or
            'subject_marks' (dictionary of subject: marks)
        
    Returns:
        Average marks (0-100)
    """
    try:
        # Method 1: Calculate from marks list
        if 'marks' in student_data:
            marks_list = student_data['marks']
            
            if not marks_list:
                logger.warning("No marks records found")
                return 0.0
            
            # Extract marks values
            marks_values = []
            for mark in marks_list:
                if isinstance(mark, dict):
                    marks_values.append(mark.get('marks', 0))
                else:
                    marks_values.append(float(mark))
            
            if not marks_values:
                return 0.0
            
            average = np.mean(marks_values)
            return min(100.0, max(0.0, average))
        
        # Method 2: Calculate from subject marks dictionary
        elif 'subject_marks' in student_data:
            subject_marks = student_data['subject_marks']
            
            if not subject_marks:
                logger.warning("No subject marks found")
                return 0.0
            
            marks_values = list(subject_marks.values())
            average = np.mean(marks_values)
            return min(100.0, max(0.0, average))
        
        # Method 3: Calculate from total and obtained marks
        elif 'total_marks' in student_data and 'obtained_marks' in student_data:
            total = student_data['total_marks']
            obtained = student_data['obtained_marks']
            
            if total == 0:
                logger.warning("Total marks is 0")
                return 0.0
            
            percentage = (obtained / total) * 100
            return min(100.0, max(0.0, percentage))
        
        else:
            logger.warning("Insufficient data to calculate average marks")
            return 0.0
            
    except Exception as e:
        logger.error(f"Error calculating average marks: {str(e)}")
        return 0.0


def calculate_fee_compliance(student_data: Dict[str, Any]) -> float:
    """
    Calculate fee compliance score for a student.
    
    Args:
        student_data: Dictionary containing student fee data
            Expected keys: 'fee_records' (list of fee payment records) or
            'total_fees', 'paid_fees', 'due_date'
        
    Returns:
        Fee compliance score (0-100)
    """
    try:
        # Method 1: Calculate from fee records
        if 'fee_records' in student_data:
            fee_records = student_data['fee_records']
            
            if not fee_records:
                logger.warning("No fee records found")
                return 100.0  # Assume compliant if no records
            
            total_fees = 0
            paid_fees = 0
            on_time_payments = 0
            
            for record in fee_records:
                amount = record.get('amount', 0)
                status = record.get('status', 'pending')
                due_date = pd.to_datetime(record.get('due_date'))
                payment_date = pd.to_datetime(record.get('payment_date')) if record.get('payment_date') else None
                
                total_fees += amount
                
                if status == 'paid':
                    paid_fees += amount
                    # Check if paid on time
                    if payment_date and payment_date <= due_date:
                        on_time_payments += 1
            
            if total_fees == 0:
                return 100.0
            
            # Calculate compliance score (weighted combination of payment and timeliness)
            payment_ratio = paid_fees / total_fees
            timeliness_ratio = on_time_payments / len(fee_records) if fee_records else 0
            
            compliance_score = (payment_ratio * 0.7 + timeliness_ratio * 0.3) * 100
            return min(100.0, max(0.0, compliance_score))
        
        # Method 2: Calculate from total and paid fees
        elif 'total_fees' in student_data and 'paid_fees' in student_data:
            total = student_data['total_fees']
            paid = student_data['paid_fees']
            
            if total == 0:
                return 100.0
            
            payment_ratio = paid / total
            
            # Check if payment was on time
            due_date = student_data.get('due_date')
            payment_date = student_data.get('payment_date')
            
            if due_date and payment_date:
                due_date = pd.to_datetime(due_date)
                payment_date = pd.to_datetime(payment_date)
                
                if payment_date <= due_date:
                    compliance_score = payment_ratio * 100
                else:
                    # Penalty for late payment
                    days_late = (payment_date - due_date).days
                    penalty = min(20, days_late * 0.5)  # Max 20% penalty
                    compliance_score = max(0, (payment_ratio * 100) - penalty)
            else:
                compliance_score = payment_ratio * 100
            
            return min(100.0, max(0.0, compliance_score))
        
        else:
            logger.warning("Insufficient data to calculate fee compliance")
            return 100.0  # Assume compliant if no data
            
    except Exception as e:
        logger.error(f"Error calculating fee compliance: {str(e)}")
        return 100.0


def calculate_behavior_score(student_data: Dict[str, Any]) -> float:
    """
    Calculate behavior score for a student.
    
    Args:
        student_data: Dictionary containing student behavior data
            Expected keys: 'behavior_records' (list of behavior incidents) or
            'disciplinary_incidents', 'positive_feedback'
        
    Returns:
        Behavior score (0-100, higher is better)
    """
    try:
        base_score = 100.0
        
        # Method 1: Calculate from behavior records
        if 'behavior_records' in student_data:
            behavior_records = student_data['behavior_records']
            
            if not behavior_records:
                return base_score
            
            negative_incidents = 0
            positive_incidents = 0
            
            for record in behavior_records:
                incident_type = record.get('type', 'neutral')
                severity = record.get('severity', 'low')
                
                if incident_type == 'negative':
                    # Deduct points based on severity
                    if severity == 'high':
                        negative_incidents += 10
                    elif severity == 'medium':
                        negative_incidents += 5
                    else:
                        negative_incidents += 2
                elif incident_type == 'positive':
                    # Add points for positive behavior
                    if severity == 'high':
                        positive_incidents += 5
                    elif severity == 'medium':
                        positive_incidents += 3
                    else:
                        positive_incidents += 1
            
            score = base_score - negative_incidents + positive_incidents
            return min(100.0, max(0.0, score))
        
        # Method 2: Calculate from incident counts
        elif 'disciplinary_incidents' in student_data:
            incidents = student_data['disciplinary_incidents']
            positive_feedback = student_data.get('positive_feedback', 0)
            
            # Deduct points for disciplinary incidents
            deduction = incidents * 5  # 5 points per incident
            
            # Add points for positive feedback
            addition = positive_feedback * 2  # 2 points per positive feedback
            
            score = base_score - deduction + addition
            return min(100.0, max(0.0, score))
        
        # Method 3: Use provided behavior score
        elif 'behavior_score' in student_data:
            score = student_data['behavior_score']
            return min(100.0, max(0.0, float(score)))
        
        else:
            logger.warning("Insufficient data to calculate behavior score")
            return base_score  # Assume good behavior if no data
            
    except Exception as e:
        logger.error(f"Error calculating behavior score: {str(e)}")
        return 100.0


def create_feature_vector(student_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Create a complete feature vector for a student.
    
    Args:
        student_data: Dictionary containing all student data
        
    Returns:
        Dictionary of feature names and their values
    """
    try:
        logger.info("Creating feature vector for student...")
        
        feature_vector = {}
        
        # Calculate core features
        feature_vector['attendance_percentage'] = calculate_attendance_percentage(student_data)
        feature_vector['average_marks'] = calculate_average_marks(student_data)
        feature_vector['fee_compliance_score'] = calculate_fee_compliance(student_data)
        feature_vector['behavior_score'] = calculate_behavior_score(student_data)
        
        # Add additional features if available
        feature_vector['assignments_submitted'] = student_data.get('assignments_submitted', 0)
        feature_vector['library_usage'] = student_data.get('library_usage', 0)
        feature_vector['extracurricular_score'] = student_data.get('extracurricular_score', 0)
        feature_vector['parent_engagement'] = student_data.get('parent_engagement', 0)
        feature_vector['disciplinary_incidents'] = student_data.get('disciplinary_incidents', 0)
        feature_vector['academic_improvement'] = student_data.get('academic_improvement', 0)
        
        # Add demographic features if available
        if 'age' in student_data:
            feature_vector['age'] = student_data['age']
        if 'previous_year_marks' in student_data:
            feature_vector['previous_year_marks'] = student_data['previous_year_marks']
        
        logger.info(f"Feature vector created with {len(feature_vector)} features")
        return feature_vector
        
    except Exception as e:
        logger.error(f"Error creating feature vector: {str(e)}")
        raise


def extract_features_from_db(student_id: int, db_session=None) -> Dict[str, float]:
    """
    Extract features for a student from the database.
    
    Args:
        student_id: ID of the student
        db_session: Database session object (optional)
        
    Returns:
        Dictionary of feature names and their values
    """
    try:
        logger.info(f"Extracting features for student ID: {student_id}")
        
        # This is a placeholder implementation
        # In a real application, this would query the database
        
        # For now, return a default feature vector
        # This should be replaced with actual database queries
        
        feature_vector = {
            'attendance_percentage': 0.0,
            'average_marks': 0.0,
            'fee_compliance_score': 100.0,
            'behavior_score': 100.0,
            'assignments_submitted': 0,
            'library_usage': 0,
            'extracurricular_score': 0,
            'parent_engagement': 0,
            'disciplinary_incidents': 0,
            'academic_improvement': 0
        }
        
        logger.warning("Using default feature vector - implement database extraction")
        return feature_vector
        
    except Exception as e:
        logger.error(f"Error extracting features from database: {str(e)}")
        raise


def calculate_risk_score(feature_vector: Dict[str, float]) -> float:
    """
    Calculate an overall risk score based on feature weights.
    
    Args:
        feature_vector: Dictionary of feature names and their values
        
    Returns:
        Risk score (0-1, higher means higher risk)
    """
    try:
        risk_score = 0.0
        
        for feature, value in feature_vector.items():
            if feature in FEATURE_WEIGHTS:
                weight = FEATURE_WEIGHTS[feature]
                
                # Normalize value to 0-1 range
                if feature == 'attendance_percentage':
                    # Lower attendance = higher risk
                    normalized_value = 1.0 - (value / 100.0)
                elif feature == 'average_marks':
                    # Lower marks = higher risk
                    normalized_value = 1.0 - (value / 100.0)
                elif feature == 'fee_compliance_score':
                    # Lower compliance = higher risk
                    normalized_value = 1.0 - (value / 100.0)
                elif feature == 'behavior_score':
                    # Lower behavior score = higher risk
                    normalized_value = 1.0 - (value / 100.0)
                elif feature == 'disciplinary_incidents':
                    # More incidents = higher risk
                    normalized_value = min(1.0, value / 10.0)
                else:
                    # For other features, assume higher value = lower risk
                    normalized_value = 1.0 - min(1.0, value / 100.0)
                
                risk_score += weight * normalized_value
        
        return min(1.0, max(0.0, risk_score))
        
    except Exception as e:
        logger.error(f"Error calculating risk score: {str(e)}")
        return 0.5


def get_feature_statistics(feature_vector: Dict[str, float]) -> Dict[str, Any]:
    """
    Get statistics about a feature vector.
    
    Args:
        feature_vector: Dictionary of feature names and their values
        
    Returns:
        Dictionary containing feature statistics
    """
    try:
        values = list(feature_vector.values())
        
        statistics = {
            'count': len(values),
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'median': np.median(values),
            'risk_score': calculate_risk_score(feature_vector)
        }
        
        return statistics
        
    except Exception as e:
        logger.error(f"Error calculating feature statistics: {str(e)}")
        raise


def validate_feature_vector(feature_vector: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Validate a feature vector for completeness and correctness.
    
    Args:
        feature_vector: Dictionary of feature names and their values
        
    Returns:
        Tuple of (is_valid, list of issues)
    """
    try:
        issues = []
        
        # Check for required features
        required_features = ['attendance_percentage', 'average_marks', 
                           'fee_compliance_score', 'behavior_score']
        
        for feature in required_features:
            if feature not in feature_vector:
                issues.append(f"Missing required feature: {feature}")
        
        # Check for invalid values
        for feature, value in feature_vector.items():
            if not isinstance(value, (int, float)):
                issues.append(f"Invalid value type for {feature}: {type(value)}")
            elif np.isnan(value) or np.isinf(value):
                issues.append(f"Invalid value for {feature}: {value}")
            elif value < 0:
                issues.append(f"Negative value for {feature}: {value}")
        
        is_valid = len(issues) == 0
        
        if not is_valid:
            logger.warning(f"Feature vector validation failed: {issues}")
        else:
            logger.info("Feature vector validation passed")
        
        return is_valid, issues
        
    except Exception as e:
        logger.error(f"Error validating feature vector: {str(e)}")
        raise
