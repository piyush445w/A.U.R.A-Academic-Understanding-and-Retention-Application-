"""
Early Warning System Module

This module provides comprehensive early warning functions for the
Student Risk Monitoring system, including attendance, academic, and fee alerts.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

from app.ml.config import (
    ATTENDANCE_ALERT_THRESHOLD,
    ACADEMIC_ALERT_THRESHOLD,
    FEE_GRACE_PERIOD,
    ALERT_SEVERITY,
    ALERT_TYPES,
    RECOMMENDATIONS
)

# Configure logging
logger = logging.getLogger(__name__)


def check_attendance_alert(student_id: int,
                          threshold: float = ATTENDANCE_ALERT_THRESHOLD,
                          student_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check if a student has attendance below the threshold.
    
    Args:
        student_id: ID of the student
        threshold: Attendance percentage threshold (default: 75)
        student_data: Optional dictionary containing student data
        
    Returns:
        Dictionary containing alert information
    """
    try:
        logger.info(f"Checking attendance alert for student {student_id}")
        
        # Get attendance data
        if student_data and 'attendance_percentage' in student_data:
            attendance = student_data['attendance_percentage']
        else:
            # In a real application, this would query the database
            logger.warning("No attendance data provided, using default")
            attendance = 0.0
        
        # Check if below threshold
        is_alert = attendance < threshold
        
        # Determine severity
        if attendance < 50:
            severity = 'critical'
        elif attendance < 65:
            severity = 'warning'
        elif attendance < threshold:
            severity = 'info'
        else:
            severity = None
        
        # Get suggestions
        suggestions = []
        if is_alert:
            suggestions = get_suggestions('attendance', severity)
        
        result = {
            'student_id': student_id,
            'alert_type': 'attendance',
            'is_alert': is_alert,
            'severity': severity,
            'severity_label': ALERT_SEVERITY.get(severity, 'None') if severity else 'None',
            'current_value': attendance,
            'threshold': threshold,
            'difference': threshold - attendance if is_alert else 0,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_alert:
            logger.warning(f"Attendance alert for student {student_id}: "
                          f"{attendance:.1f}% (threshold: {threshold}%)")
        else:
            logger.info(f"No attendance alert for student {student_id}: {attendance:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking attendance alert: {str(e)}")
        raise


def check_academic_alert(student_id: int,
                        threshold: float = ACADEMIC_ALERT_THRESHOLD,
                        student_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check if a student has academic performance below the threshold.
    
    Args:
        student_id: ID of the student
        threshold: Marks threshold (default: 50)
        student_data: Optional dictionary containing student data
        
    Returns:
        Dictionary containing alert information
    """
    try:
        logger.info(f"Checking academic alert for student {student_id}")
        
        # Get academic data
        if student_data and 'average_marks' in student_data:
            marks = student_data['average_marks']
        else:
            # In a real application, this would query the database
            logger.warning("No academic data provided, using default")
            marks = 0.0
        
        # Check if below threshold
        is_alert = marks < threshold
        
        # Determine severity
        if marks < 30:
            severity = 'critical'
        elif marks < 40:
            severity = 'warning'
        elif marks < threshold:
            severity = 'info'
        else:
            severity = None
        
        # Get suggestions
        suggestions = []
        if is_alert:
            suggestions = get_suggestions('academic', severity)
        
        result = {
            'student_id': student_id,
            'alert_type': 'academic',
            'is_alert': is_alert,
            'severity': severity,
            'severity_label': ALERT_SEVERITY.get(severity, 'None') if severity else 'None',
            'current_value': marks,
            'threshold': threshold,
            'difference': threshold - marks if is_alert else 0,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_alert:
            logger.warning(f"Academic alert for student {student_id}: "
                          f"{marks:.1f} marks (threshold: {threshold})")
        else:
            logger.info(f"No academic alert for student {student_id}: {marks:.1f} marks")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking academic alert: {str(e)}")
        raise


def check_fee_alert(student_id: int,
                   student_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check if a student has fee payment issues.
    
    Args:
        student_id: ID of the student
        student_data: Optional dictionary containing student data
        
    Returns:
        Dictionary containing alert information
    """
    try:
        logger.info(f"Checking fee alert for student {student_id}")
        
        # Get fee data
        if student_data:
            fee_compliance = student_data.get('fee_compliance_score', 100.0)
            due_date = student_data.get('fee_due_date')
            payment_date = student_data.get('fee_payment_date')
            total_fees = student_data.get('total_fees', 0)
            paid_fees = student_data.get('paid_fees', 0)
        else:
            # In a real application, this would query the database
            logger.warning("No fee data provided, using default")
            fee_compliance = 100.0
            due_date = None
            payment_date = None
            total_fees = 0
            paid_fees = 0
        
        # Check for overdue payment
        is_overdue = False
        days_overdue = 0
        
        if due_date and not payment_date:
            due_date = pd.to_datetime(due_date)
            current_date = pd.now()
            
            if current_date > due_date:
                is_overdue = True
                days_overdue = (current_date - due_date).days
        
        # Check if below compliance threshold
        is_alert = fee_compliance < 70 or is_overdue
        
        # Determine severity
        if fee_compliance < 50 or days_overdue > 60:
            severity = 'critical'
        elif fee_compliance < 60 or days_overdue > 30:
            severity = 'warning'
        elif fee_compliance < 70 or days_overdue > 0:
            severity = 'info'
        else:
            severity = None
        
        # Get suggestions
        suggestions = []
        if is_alert:
            suggestions = get_suggestions('fee', severity)
        
        result = {
            'student_id': student_id,
            'alert_type': 'fee',
            'is_alert': is_alert,
            'severity': severity,
            'severity_label': ALERT_SEVERITY.get(severity, 'None') if severity else 'None',
            'current_value': fee_compliance,
            'threshold': 70.0,
            'is_overdue': is_overdue,
            'days_overdue': days_overdue,
            'total_fees': total_fees,
            'paid_fees': paid_fees,
            'outstanding_fees': total_fees - paid_fees,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_alert:
            logger.warning(f"Fee alert for student {student_id}: "
                          f"compliance {fee_compliance:.1f}%, overdue {days_overdue} days")
        else:
            logger.info(f"No fee alert for student {student_id}: compliance {fee_compliance:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking fee alert: {str(e)}")
        raise


def generate_alerts(student_id: int,
                   student_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Generate all alerts for a student.
    
    Args:
        student_id: ID of the student
        student_data: Optional dictionary containing student data
        
    Returns:
        List of alert dictionaries
    """
    try:
        logger.info(f"Generating alerts for student {student_id}")
        
        alerts = []
        
        # Check attendance alert
        attendance_alert = check_attendance_alert(student_id, student_data=student_data)
        if attendance_alert['is_alert']:
            alerts.append(attendance_alert)
        
        # Check academic alert
        academic_alert = check_academic_alert(student_id, student_data=student_data)
        if academic_alert['is_alert']:
            alerts.append(academic_alert)
        
        # Check fee alert
        fee_alert = check_fee_alert(student_id, student_data=student_data)
        if fee_alert['is_alert']:
            alerts.append(fee_alert)
        
        # Sort by severity (critical first)
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: severity_order.get(x['severity'], 3))
        
        logger.info(f"Generated {len(alerts)} alerts for student {student_id}")
        return alerts
        
    except Exception as e:
        logger.error(f"Error generating alerts: {str(e)}")
        raise


def get_suggestions(alert_type: str,
                   severity: str) -> List[str]:
    """
    Get suggestions for addressing an alert.
    
    Args:
        alert_type: Type of alert ('attendance', 'academic', 'fee', 'behavior')
        severity: Severity level ('info', 'warning', 'critical')
        
    Returns:
        List of suggestion strings
    """
    try:
        suggestions = []
        
        if alert_type in RECOMMENDATIONS:
            type_recommendations = RECOMMENDATIONS[alert_type]
            
            if severity in type_recommendations:
                suggestions = type_recommendations[severity]
            elif 'medium' in type_recommendations:
                # Fall back to medium severity
                suggestions = type_recommendations['medium']
        
        # Add general suggestions if none found
        if not suggestions:
            suggestions = [
                "Contact the student's advisor",
                "Schedule a meeting with the student",
                "Review the student's recent performance"
            ]
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        return ["Contact administrator for assistance"]


def check_behavior_alert(student_id: int,
                        student_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Check if a student has behavior issues.
    
    Args:
        student_id: ID of the student
        student_data: Optional dictionary containing student data
        
    Returns:
        Dictionary containing alert information
    """
    try:
        logger.info(f"Checking behavior alert for student {student_id}")
        
        # Get behavior data
        if student_data:
            behavior_score = student_data.get('behavior_score', 100.0)
            disciplinary_incidents = student_data.get('disciplinary_incidents', 0)
        else:
            # In a real application, this would query the database
            logger.warning("No behavior data provided, using default")
            behavior_score = 100.0
            disciplinary_incidents = 0
        
        # Check if below threshold
        is_alert = behavior_score < 70 or disciplinary_incidents > 3
        
        # Determine severity
        if behavior_score < 50 or disciplinary_incidents > 5:
            severity = 'critical'
        elif behavior_score < 60 or disciplinary_incidents > 3:
            severity = 'warning'
        elif behavior_score < 70 or disciplinary_incidents > 1:
            severity = 'info'
        else:
            severity = None
        
        # Get suggestions
        suggestions = []
        if is_alert:
            suggestions = get_suggestions('behavior', severity)
        
        result = {
            'student_id': student_id,
            'alert_type': 'behavior',
            'is_alert': is_alert,
            'severity': severity,
            'severity_label': ALERT_SEVERITY.get(severity, 'None') if severity else 'None',
            'current_value': behavior_score,
            'threshold': 70.0,
            'disciplinary_incidents': disciplinary_incidents,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
        
        if is_alert:
            logger.warning(f"Behavior alert for student {student_id}: "
                          f"score {behavior_score:.1f}, incidents {disciplinary_incidents}")
        else:
            logger.info(f"No behavior alert for student {student_id}: score {behavior_score:.1f}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking behavior alert: {str(e)}")
        raise


def get_alert_summary(alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a summary of alerts.
    
    Args:
        alerts: List of alert dictionaries
        
    Returns:
        Dictionary containing alert summary
    """
    try:
        total_alerts = len(alerts)
        
        # Count by severity
        severity_counts = {}
        for alert in alerts:
            severity = alert.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by type
        type_counts = {}
        for alert in alerts:
            alert_type = alert.get('alert_type', 'unknown')
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # Get critical alerts
        critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
        
        summary = {
            'total_alerts': total_alerts,
            'severity_counts': severity_counts,
            'type_counts': type_counts,
            'critical_count': len(critical_alerts),
            'has_critical': len(critical_alerts) > 0,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating alert summary: {str(e)}")
        raise


def prioritize_alerts(alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prioritize alerts based on severity and impact.
    
    Args:
        alerts: List of alert dictionaries
        
    Returns:
        List of prioritized alert dictionaries
    """
    try:
        # Define priority weights
        priority_weights = {
            'critical': 3,
            'warning': 2,
            'info': 1
        }
        
        # Calculate priority score for each alert
        for alert in alerts:
            severity = alert.get('severity', 'info')
            alert_type = alert.get('alert_type', 'unknown')
            
            # Base priority from severity
            priority = priority_weights.get(severity, 0)
            
            # Adjust based on alert type
            if alert_type == 'academic':
                priority *= 1.2  # Academic issues are high priority
            elif alert_type == 'attendance':
                priority *= 1.1  # Attendance issues are important
            elif alert_type == 'fee':
                priority *= 1.0  # Fee issues are standard priority
            
            alert['priority_score'] = priority
        
        # Sort by priority (highest first)
        prioritized = sorted(alerts, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return prioritized
        
    except Exception as e:
        logger.error(f"Error prioritizing alerts: {str(e)}")
        return alerts


def get_escalation_path(alert: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get the escalation path for an alert.
    
    Args:
        alert: Alert dictionary
        
    Returns:
        List of escalation steps
    """
    try:
        severity = alert.get('severity', 'info')
        alert_type = alert.get('alert_type', 'unknown')
        
        escalation_path = []
        
        if severity == 'critical':
            escalation_path = [
                {'step': 1, 'action': 'Immediate notification to class teacher', 'timeline': 'Within 1 hour'},
                {'step': 2, 'action': 'Contact parents/guardians', 'timeline': 'Within 4 hours'},
                {'step': 3, 'action': 'Schedule emergency meeting', 'timeline': 'Within 24 hours'},
                {'step': 4, 'action': 'Involve principal if needed', 'timeline': 'Within 48 hours'}
            ]
        elif severity == 'warning':
            escalation_path = [
                {'step': 1, 'action': 'Notify class teacher', 'timeline': 'Within 24 hours'},
                {'step': 2, 'action': 'Monitor student progress', 'timeline': 'Weekly'},
                {'step': 3, 'action': 'Contact parents if no improvement', 'timeline': 'Within 1 week'}
            ]
        else:  # info
            escalation_path = [
                {'step': 1, 'action': 'Log alert for monitoring', 'timeline': 'Immediate'},
                {'step': 2, 'action': 'Review during next counseling session', 'timeline': 'Within 2 weeks'}
            ]
        
        return escalation_path
        
    except Exception as e:
        logger.error(f"Error getting escalation path: {str(e)}")
        return []
