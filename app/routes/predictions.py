"""
Predictions Routes
Intelligent Student Risk Monitoring & Decision Support System
"""

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Prediction, MLModel, Student, User
from app.utils.decorators import role_required, admin_required, teacher_required, log_activity

predictions_bp = Blueprint('predictions', __name__, url_prefix='/predictions')


@predictions_bp.route('/')
@login_required
def dashboard():
    """ML Predictions Dashboard page."""
    
    total_predictions = Prediction.query.count()
    low_risk = Prediction.query.filter_by(risk_level='Low').count()
    medium_risk = Prediction.query.filter_by(risk_level='Medium').count()
    high_risk = Prediction.query.filter_by(risk_level='High').count()
    critical_risk = Prediction.query.filter_by(risk_level='Critical').count()
    
    active_model = MLModel.query.filter_by(is_active=True).first()
    if active_model:
        model_metrics = {
            'accuracy': float(active_model.accuracy * 100) if active_model.accuracy else 0,
            'precision': float(active_model.precision_score * 100) if active_model.precision_score else 0,
            'recall': float(active_model.recall_score * 100) if active_model.recall_score else 0,
            'f1_score': float(active_model.f1_score * 100) if active_model.f1_score else 0,
            'last_trained': active_model.training_date.isoformat() if active_model.training_date else None
        }
    else:
        model_metrics = {
            'accuracy': 0,
            'precision': 0,
            'recall': 0,
            'f1_score': 0,
            'last_trained': None
        }
    
    stats = {
        'total': total_predictions,
        'low_risk': low_risk,
        'medium_risk': medium_risk,
        'high_risk': high_risk,
        'critical_risk': critical_risk,
        'accuracy': model_metrics['accuracy']
    }
    
    high_risk_students = []
    high_risk_predictions = Prediction.query.filter(
        Prediction.risk_level.in_(['High', 'Critical'])
    ).order_by(Prediction.risk_score.desc()).limit(15).all()
    for pred in high_risk_predictions:
        student = Student.query.get(pred.student_id)
        if student:
            high_risk_students.append({
                'id': student.id,
                'student_id': student.student_id,
                'full_name': student.full_name,
                'course': student.course or 'N/A',
                'risk_level': pred.risk_level,
                'risk_score': int(float(pred.risk_score) * 100),
                'is_manual': pred.is_manual,
                'flag_for_review': pred.flag_for_review,
                'factors': 'Attendance, Grades, Fees'
            })
    
    flagged_students = []
    flagged_predictions = Prediction.query.filter_by(flag_for_review=True).join(Student).order_by(
        Prediction.prediction_date.desc()
    ).limit(10).all()
    for pred in flagged_predictions:
        student = pred.student  # This assumes there's a relationship defined
        if not student:
            # Fallback if relationship doesn't exist
            student = Student.query.get(pred.student_id)
        if student:
            flagged_students.append({
                'student_id': student.student_id,
                'full_name': student.full_name,
                'course': student.course or 'N/A',
                'review_note': pred.review_note or 'No note provided'
            })
    
    return render_template('predictions/dashboard.html', 
                          stats=stats, 
                          model=model_metrics,
                          high_risk_students=high_risk_students,
                          flagged_students=flagged_students,
                          critical_risk=critical_risk)


@predictions_bp.route('/<int:student_id>/override', methods=['POST'])
@login_required
@admin_required
@log_activity(action='override', entity_type='prediction')
def manual_override(student_id):
    """Manually override a prediction for a student."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        risk_level = data.get('risk_level')
        risk_score = data.get('risk_score')
        override_reason = data.get('override_reason', 'Manual override by admin')
        
        if not risk_level or risk_score is None:
            return jsonify({'error': 'Risk level and score are required'}), 400
        
        # Validate risk level
        valid_risk_levels = ['Low', 'Medium', 'High', 'Critical']
        if risk_level not in valid_risk_levels:
            return jsonify({'error': f'Invalid risk level. Must be one of {valid_risk_levels}'}), 400
        
        # Validate risk score (should be between 0 and 1)
        try:
            risk_score = float(risk_score)
            if risk_score < 0 or risk_score > 1:
                return jsonify({'error': 'Risk score must be between 0 and 1'}), 400
        except ValueError:
            return jsonify({'error': 'Risk score must be a valid number'}), 400
        
        # Get the latest prediction for the student
        prediction = Prediction.get_latest_prediction(student_id)
        if not prediction:
            return jsonify({'error': 'No prediction found for this student'}), 404
        
        # Get active model
        active_model = MLModel.get_active_model()
        if not active_model:
            return jsonify({'error': 'No active model found'}), 500
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Update prediction with manual override
        prediction.risk_level = risk_level
        prediction.risk_score = risk_score
        prediction.is_manual = True
        prediction.override_by = current_user.id
        prediction.override_reason = override_reason
        prediction.flag_for_review = False  # Clear flag when manually overridden
        prediction.review_note = None
        
        # Update probability to match risk score (simplified)
        prediction.probability = risk_score
        
        db.session.commit()
        
        return jsonify({
            'message': 'Prediction overridden successfully',
            'prediction': prediction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to override prediction: {str(e)}'}), 500


@predictions_bp.route('/<int:student_id>/flag', methods=['POST'])
@login_required
@teacher_required
@log_activity(action='flag', entity_type='prediction')
def flag_for_review(student_id):
    """Flag a prediction for teacher review."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        review_note = data.get('review_note', 'Flagged for review')
        
        # Get the latest prediction for the student
        prediction = Prediction.get_latest_prediction(student_id)
        if not prediction:
            return jsonify({'error': 'No prediction found for this student'}), 404
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Flag for review
        prediction.flag_for_teacher_review(review_note)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Prediction flagged for review successfully',
            'prediction': prediction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to flag prediction: {str(e)}'}), 500


@predictions_bp.route('/<int:student_id>/override', methods=['DELETE'])
@login_required
@admin_required
@log_activity(action='remove_override', entity_type='prediction')
def remove_override(student_id):
    """Remove manual override and restore original prediction."""
    try:
        # Get the latest prediction for the student
        prediction = Prediction.get_latest_prediction(student_id)
        if not prediction:
            return jsonify({'error': 'No prediction found for this student'}), 404
        
        # Check if it's actually a manual override
        if not prediction.is_manual:
            return jsonify({'error': 'Prediction is not manually overridden'}), 400
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Reset to original values (we would need to store original values)
        # For now, we'll just mark it as not manual and clear override fields
        prediction.is_manual = False
        prediction.override_by = None
        prediction.override_reason = None
        
        # Note: In a real system, we would restore the original ML prediction values
        # This would require storing the original prediction when overridden
        
        db.session.commit()
        
        return jsonify({
            'message': 'Manual override removed successfully',
            'prediction': prediction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove override: {str(e)}'}), 500


@predictions_bp.route('/<int:student_id>/flag', methods=['DELETE'])
@login_required
@teacher_required
@log_activity(action='unflag', entity_type='prediction')
def remove_flag(student_id):
    """Remove review flag from a prediction."""
    try:
        # Get the latest prediction for the student
        prediction = Prediction.get_latest_prediction(student_id)
        if not prediction:
            return jsonify({'error': 'No prediction found for this student'}), 404
        
        # Check if it's actually flagged
        if not prediction.flag_for_review:
            return jsonify({'error': 'Prediction is not flagged for review'}), 400
        
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Clear review flag
        prediction.clear_review_flag()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Review flag removed successfully',
            'prediction': prediction.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to remove flag: {str(e)}'}), 500


@predictions_bp.route('/<int:student_id>/history', methods=['GET'])
@login_required
def prediction_history(student_id):
    """Get prediction history for a student."""
    try:
        # Get limit from query params (default 10)
        limit = request.args.get('limit', 10, type=int)
        
        # Get predictions for the student
        predictions = Prediction.get_predictions_by_student(student_id, limit=limit)
        
        if not predictions:
            return jsonify({
                'message': 'No predictions found for this student',
                'predictions': []
            }), 200
        
        # Get student info
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Format response
        prediction_list = []
        for pred in predictions:
            pred_dict = pred.to_dict()
            # Add student info
            pred_dict['student'] = {
                'student_id': student.student_id,
                'full_name': student.full_name,
                'course': student.course
            }
            prediction_list.append(pred_dict)
        
        return jsonify({
            'predictions': prediction_list,
            'count': len(prediction_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to retrieve prediction history: {str(e)}'}), 500


@predictions_bp.route('/train_model', methods=['POST'])
@login_required
@admin_required
@log_activity(action='train_model', entity_type='ml_model')
def train_model():
    """Trigger model training (placeholder - would integrate with actual ML pipeline)."""
    try:
        # In a real implementation, this would trigger the ML training pipeline
        # For now, we'll return a placeholder response
        
        return jsonify({
            'message': 'Model training initiated successfully',
            'note': 'This is a placeholder endpoint. Actual training would be handled by background jobs.'
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Failed to initiate model training: {str(e)}'}), 500


@predictions_bp.route('/predict_student/<int:student_id>', methods=['POST'])
@login_required
@role_required('admin', 'teacher')
@log_activity(action='predict', entity_type='prediction')
def predict_student(student_id):
    """Generate a prediction for a specific student."""
    try:
        # Get student
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        
        # Get active model
        active_model = MLModel.get_active_model()
        if not active_model:
            return jsonify({'error': 'No active model found'}), 500
        
        # In a real implementation, we would:
        # 1. Extract features for the student (attendance, grades, fees, etc.)
        # 2. Run the ML model to get prediction
        # 3. Save the prediction
        
        # For now, we'll return a placeholder response
        return jsonify({
            'message': f'Prediction generated for student {student.full_name}',
            'note': 'This is a placeholder endpoint. Actual prediction would use the ML model.',
            'student_id': student_id,
            'model_used': active_model.model_name
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate prediction: {str(e)}'}), 500


@predictions_bp.route('/batch_predict', methods=['POST'])
@login_required
@role_required('admin', 'teacher')
@log_activity(action='batch_predict', entity_type='prediction')
def batch_predict():
    """Generate predictions for multiple students or all students."""
    try:
        data = request.get_json() or {}
        student_ids = data.get('student_ids', [])  # If empty, predict for all
        
        # Get active model
        active_model = MLModel.get_active_model()
        if not active_model:
            return jsonify({'error': 'No active model found'}), 500
        
        # In a real implementation, we would:
        # 1. Get list of students (either provided or all)
        # 2. Extract features for each student
        # 3. Run the ML model to get predictions
        # 4. Save the predictions
        
        # For now, we'll return a placeholder response
        if student_ids:
            message = f'Batch prediction initiated for {len(student_ids)} students'
        else:
            # Count all students
            total_students = Student.query.count()
            message = f'Batch prediction initiated for all {total_students} students'
        
        return jsonify({
            'message': message,
            'note': 'This is a placeholder endpoint. Actual batch prediction would use the ML model.',
            'model_used': active_model.model_name,
            'student_count': len(student_ids) if student_ids else 'all'
        }), 202
        
    except Exception as e:
        return jsonify({'error': f'Failed to initiate batch prediction: {str(e)}'}), 500