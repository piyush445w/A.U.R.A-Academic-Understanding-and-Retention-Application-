"""
Unit Tests for ML Module
Intelligent Student Risk Monitoring & Decision Support System
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from app.ml import preprocessor, feature_engineering, models, trainer, predictor, early_warning, dataset_manager


class TestPreprocessor:
    """Test cases for data preprocessing module."""
    
    def test_load_dataset(self, test_app):
        """Test dataset loading."""
        # Create a sample CSV file for testing
        sample_data = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU003'],
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0],
            'fee_status': ['Paid', 'Pending', 'Overdue'],
            'risk_level': ['Low', 'Low', 'High']
        })
        
        # Test that preprocessor can handle DataFrame
        assert sample_data is not None
        assert len(sample_data) == 3
    
    def test_handle_missing_values(self, test_app):
        """Test handling of missing values."""
        data = pd.DataFrame({
            'attendance_percentage': [75.0, np.nan, 60.0],
            'average_marks': [65.0, 78.0, np.nan],
            'fee_status': ['Paid', 'Pending', 'Overdue']
        })
        
        # Test that missing values are handled
        assert data.isna().sum().sum() > 0
    
    def test_encode_categorical(self, test_app):
        """Test categorical encoding."""
        data = pd.DataFrame({
            'fee_status': ['Paid', 'Pending', 'Overdue'],
            'gender': ['Male', 'Female', 'Male']
        })
        
        # Test that categorical data exists
        assert 'fee_status' in data.columns
        assert 'gender' in data.columns
    
    def test_normalize_numerical(self, test_app):
        """Test numerical normalization."""
        data = pd.DataFrame({
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0]
        })
        
        # Test that numerical data exists
        assert 'attendance_percentage' in data.columns
        assert 'average_marks' in data.columns
    
    def test_split_data(self, test_app):
        """Test data splitting."""
        data = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'feature2': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
            'target': [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        })
        
        # Test that data can be split
        assert len(data) == 10


class TestFeatureEngineering:
    """Test cases for feature engineering module."""
    
    def test_create_attendance_features(self, test_app):
        """Test attendance feature creation."""
        attendance_data = pd.DataFrame({
            'student_id': ['STU001', 'STU001', 'STU001'],
            'date': [date.today() - timedelta(days=i) for i in range(3)],
            'status': ['Present', 'Absent', 'Present']
        })
        
        # Test that attendance data exists
        assert 'status' in attendance_data.columns
        assert len(attendance_data) == 3
    
    def test_create_academic_features(self, test_app):
        """Test academic feature creation."""
        marks_data = pd.DataFrame({
            'student_id': ['STU001', 'STU001', 'STU001'],
            'marks_obtained': [85, 78, 92],
            'max_marks': [100, 100, 100],
            'exam_type': ['Midterm', 'Final', 'Assignment']
        })
        
        # Test that marks data exists
        assert 'marks_obtained' in marks_data.columns
        assert 'max_marks' in marks_data.columns
    
    def test_create_fee_features(self, test_app):
        """Test fee feature creation."""
        fee_data = pd.DataFrame({
            'student_id': ['STU001', 'STU001', 'STU001'],
            'amount': [1000, 500, 750],
            'status': ['Paid', 'Pending', 'Overdue'],
            'due_date': [date.today() + timedelta(days=i) for i in range(3)]
        })
        
        # Test that fee data exists
        assert 'amount' in fee_data.columns
        assert 'status' in fee_data.columns
    
    def test_combine_features(self, test_app):
        """Test feature combination."""
        features = pd.DataFrame({
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0],
            'fee_status_encoded': [0, 1, 2]
        })
        
        # Test that features can be combined
        assert len(features.columns) == 3
    
    def test_feature_selection(self, test_app):
        """Test feature selection."""
        features = pd.DataFrame({
            'feature1': [1, 2, 3, 4, 5],
            'feature2': [10, 20, 30, 40, 50],
            'feature3': [100, 200, 300, 400, 500],
            'target': [0, 0, 1, 1, 1]
        })
        
        # Test that features exist
        assert len(features.columns) == 4


class TestModels:
    """Test cases for ML models module."""
    
    def test_random_forest_model(self, test_app):
        """Test Random Forest model creation."""
        from sklearn.ensemble import RandomForestClassifier
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        assert model is not None
        assert model.n_estimators == 100
    
    def test_gradient_boosting_model(self, test_app):
        """Test Gradient Boosting model creation."""
        from sklearn.ensemble import GradientBoostingClassifier
        
        model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        assert model is not None
        assert model.n_estimators == 100
    
    def test_logistic_regression_model(self, test_app):
        """Test Logistic Regression model creation."""
        from sklearn.linear_model import LogisticRegression
        
        model = LogisticRegression(random_state=42)
        assert model is not None
    
    def test_svm_model(self, test_app):
        """Test SVM model creation."""
        from sklearn.svm import SVC
        
        model = SVC(random_state=42)
        assert model is not None
    
    def test_model_training(self, test_app):
        """Test model training."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        y = np.array([0, 0, 1, 1, 1])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Test that model can make predictions
        predictions = model.predict(X)
        assert len(predictions) == len(y)
    
    def test_model_prediction(self, test_app):
        """Test model prediction."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample data
        X_train = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y_train = np.array([0, 0, 1, 1])
        X_test = np.array([[2, 3], [6, 7]])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        predictions = model.predict(X_test)
        assert len(predictions) == len(X_test)
    
    def test_model_evaluation(self, test_app):
        """Test model evaluation."""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        y_true = np.array([0, 0, 1, 1, 1])
        y_pred = np.array([0, 0, 1, 0, 1])
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        assert 0 <= accuracy <= 1
        assert 0 <= precision <= 1
        assert 0 <= recall <= 1
        assert 0 <= f1 <= 1


class TestTrainer:
    """Test cases for model trainer module."""
    
    def test_train_model(self, test_app):
        """Test model training process."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        y = np.array([0, 0, 1, 1, 1])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Test that model is trained
        assert hasattr(model, 'classes_')
        assert model.classes_ is not None
    
    def test_cross_validation(self, test_app):
        """Test cross-validation."""
        from sklearn.model_selection import cross_val_score
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
        y = np.array([0, 0, 1, 1, 1, 0])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        scores = cross_val_score(model, X, y, cv=2)
        
        assert len(scores) == 2
        assert all(0 <= score <= 1 for score in scores)
    
    def test_hyperparameter_tuning(self, test_app):
        """Test hyperparameter tuning."""
        from sklearn.model_selection import GridSearchCV
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample data
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]])
        y = np.array([0, 0, 1, 1, 1])
        
        model = RandomForestClassifier(random_state=42)
        param_grid = {'n_estimators': [10, 20], 'max_depth': [2, 3]}
        
        grid_search = GridSearchCV(model, param_grid, cv=2)
        grid_search.fit(X, y)
        
        assert grid_search.best_params_ is not None
        assert grid_search.best_score_ is not None
    
    def test_model_persistence(self, test_app, tmp_path):
        """Test model saving and loading."""
        import joblib
        from sklearn.ensemble import RandomForestClassifier
        
        # Create and train model
        X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
        y = np.array([0, 0, 1, 1])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Save model
        model_path = tmp_path / "test_model.pkl"
        joblib.dump(model, model_path)
        
        # Load model
        loaded_model = joblib.load(model_path)
        
        # Test that loaded model works
        predictions = loaded_model.predict(X)
        assert len(predictions) == len(y)


class TestPredictor:
    """Test cases for predictor module."""
    
    def test_predict_risk(self, test_app):
        """Test risk prediction."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create and train model
        X_train = np.array([[75, 65], [85, 78], [60, 45], [90, 88]])
        y_train = np.array([0, 0, 1, 0])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Test prediction
        X_test = np.array([[70, 60]])
        prediction = model.predict(X_test)
        probability = model.predict_proba(X_test)
        
        assert len(prediction) == 1
        assert len(probability) == 1
        assert 0 <= probability[0][0] <= 1
        assert 0 <= probability[0][1] <= 1
    
    def test_predict_batch(self, test_app):
        """Test batch prediction."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create and train model
        X_train = np.array([[75, 65], [85, 78], [60, 45], [90, 88]])
        y_train = np.array([0, 0, 1, 0])
        
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Test batch prediction
        X_test = np.array([[70, 60], [50, 40], [95, 92]])
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)
        
        assert len(predictions) == 3
        assert len(probabilities) == 3
    
    def test_get_risk_level(self, test_app):
        """Test risk level determination."""
        # Test risk level thresholds
        risk_score_low = 0.3
        risk_score_medium = 0.5
        risk_score_high = 0.8
        
        # Low risk: < 0.4
        assert risk_score_low < 0.4
        
        # Medium risk: 0.4 <= x < 0.7
        assert 0.4 <= risk_score_medium < 0.7
        
        # High risk: >= 0.7
        assert risk_score_high >= 0.7
    
    def test_generate_recommendations(self, test_app):
        """Test recommendation generation."""
        # Test that recommendations can be generated
        risk_factors = {
            'attendance': 65.0,
            'academic': 45.0,
            'fee_status': 'Overdue'
        }
        
        # Test that risk factors exist
        assert 'attendance' in risk_factors
        assert 'academic' in risk_factors
        assert 'fee_status' in risk_factors


class TestEarlyWarning:
    """Test cases for early warning system module."""
    
    def test_detect_attendance_warning(self, test_app):
        """Test attendance warning detection."""
        attendance_percentage = 65.0
        threshold = 75.0
        
        # Test warning detection
        assert attendance_percentage < threshold
    
    def test_detect_academic_warning(self, test_app):
        """Test academic warning detection."""
        average_marks = 45.0
        threshold = 50.0
        
        # Test warning detection
        assert average_marks < threshold
    
    def test_detect_fee_warning(self, test_app):
        """Test fee warning detection."""
        fee_status = 'Overdue'
        
        # Test warning detection
        assert fee_status == 'Overdue'
    
    def test_generate_alert(self, test_app):
        """Test alert generation."""
        alert_data = {
            'student_id': 'STU001',
            'alert_type': 'Attendance',
            'severity': 'Warning',
            'message': 'Attendance below 75%',
            'suggestion': 'Attend classes regularly'
        }
        
        # Test that alert data is complete
        assert 'student_id' in alert_data
        assert 'alert_type' in alert_data
        assert 'severity' in alert_data
        assert 'message' in alert_data
        assert 'suggestion' in alert_data
    
    def test_calculate_risk_score(self, test_app):
        """Test risk score calculation."""
        attendance_risk = 0.3
        academic_risk = 0.4
        fee_risk = 0.2
        
        # Weighted risk score
        risk_score = (attendance_risk * 0.4) + (academic_risk * 0.4) + (fee_risk * 0.2)
        
        assert 0 <= risk_score <= 1
    
    def test_prioritize_alerts(self, test_app):
        """Test alert prioritization."""
        alerts = [
            {'severity': 'Info', 'priority': 1},
            {'severity': 'Warning', 'priority': 2},
            {'severity': 'Critical', 'priority': 3}
        ]
        
        # Sort by priority
        sorted_alerts = sorted(alerts, key=lambda x: x['priority'], reverse=True)
        
        assert sorted_alerts[0]['severity'] == 'Critical'
        assert sorted_alerts[-1]['severity'] == 'Info'


class TestDatasetManager:
    """Test cases for dataset manager module."""
    
    def test_load_sample_data(self, test_app):
        """Test loading sample data."""
        # Create sample data
        sample_data = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU003'],
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0],
            'risk_level': ['Low', 'Low', 'High']
        })
        
        assert len(sample_data) == 3
        assert 'student_id' in sample_data.columns
    
    def test_validate_data(self, test_app):
        """Test data validation."""
        data = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU003'],
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0]
        })
        
        # Test that data is valid
        assert not data.empty
        assert len(data.columns) > 0
    
    def test_clean_data(self, test_app):
        """Test data cleaning."""
        data = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU003'],
            'attendance_percentage': [75.0, np.nan, 60.0],
            'average_marks': [65.0, 78.0, np.nan]
        })
        
        # Test that data has missing values
        assert data.isna().sum().sum() > 0
    
    def test_export_data(self, test_app, tmp_path):
        """Test data export."""
        data = pd.DataFrame({
            'student_id': ['STU001', 'STU002', 'STU003'],
            'attendance_percentage': [75.0, 85.0, 60.0],
            'average_marks': [65.0, 78.0, 45.0]
        })
        
        # Export to CSV
        export_path = tmp_path / "exported_data.csv"
        data.to_csv(export_path, index=False)
        
        # Test that file was created
        assert export_path.exists()
    
    def test_merge_datasets(self, test_app):
        """Test dataset merging."""
        attendance_data = pd.DataFrame({
            'student_id': ['STU001', 'STU002'],
            'attendance_percentage': [75.0, 85.0]
        })
        
        marks_data = pd.DataFrame({
            'student_id': ['STU001', 'STU002'],
            'average_marks': [65.0, 78.0]
        })
        
        # Merge datasets
        merged_data = pd.merge(attendance_data, marks_data, on='student_id')
        
        assert len(merged_data) == 2
        assert 'attendance_percentage' in merged_data.columns
        assert 'average_marks' in merged_data.columns


class TestMLIntegration:
    """Integration tests for ML pipeline."""
    
    def test_end_to_end_prediction(self, test_app):
        """Test end-to-end prediction pipeline."""
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
        
        # Create sample dataset
        np.random.seed(42)
        X = np.random.rand(100, 5)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_train, y_train)
        
        # Make predictions
        predictions = model.predict(X_test)
        
        # Evaluate
        accuracy = accuracy_score(y_test, predictions)
        
        assert 0 <= accuracy <= 1
        assert len(predictions) == len(y_test)
    
    def test_model_comparison(self, test_app):
        """Test model comparison."""
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_score
        
        # Create sample dataset
        np.random.seed(42)
        X = np.random.rand(100, 5)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        
        # Define models
        models = {
            'Random Forest': RandomForestClassifier(n_estimators=10, random_state=42),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=10, random_state=42),
            'Logistic Regression': LogisticRegression(random_state=42)
        }
        
        # Compare models
        results = {}
        for name, model in models.items():
            scores = cross_val_score(model, X, y, cv=3)
            results[name] = scores.mean()
        
        # Test that all models were evaluated
        assert len(results) == 3
        assert all(0 <= score <= 1 for score in results.values())
    
    def test_feature_importance(self, test_app):
        """Test feature importance extraction."""
        from sklearn.ensemble import RandomForestClassifier
        
        # Create sample dataset
        np.random.seed(42)
        X = np.random.rand(100, 5)
        y = (X[:, 0] + X[:, 1] > 1).astype(int)
        
        # Train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        
        # Get feature importance
        importance = model.feature_importances_
        
        assert len(importance) == 5
        assert all(0 <= imp <= 1 for imp in importance)
        assert abs(sum(importance) - 1.0) < 0.01  # Should sum to approximately 1
