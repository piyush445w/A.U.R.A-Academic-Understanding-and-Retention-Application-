#!/usr/bin/env python3
"""
Initial ML Model Training Script
Intelligent Student Risk Monitoring & Decision Support System
"""

import os
import sys
import logging
import pickle
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import joblib

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import MLModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('train_model.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """Class for training and managing ML models."""
    
    def __init__(self, model_dir='models/trained_models'):
        """
        Initialize model trainer.
        
        Args:
            model_dir: Directory to save trained models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = []
        
    def load_dataset(self, dataset_path):
        """
        Load dataset from CSV file.
        
        Args:
            dataset_path: Path to dataset CSV file
            
        Returns:
            DataFrame with loaded data
        """
        try:
            logger.info(f"Loading dataset from {dataset_path}")
            
            if not Path(dataset_path).exists():
                logger.error(f"Dataset file not found: {dataset_path}")
                return None
            
            df = pd.read_csv(dataset_path)
            logger.info(f"Loaded dataset with {len(df)} rows and {len(df.columns)} columns")
            
            return df
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            return None
    
    def create_sample_dataset(self):
        """
        Create a sample dataset for training.
        
        Returns:
            DataFrame with sample data
        """
        try:
            logger.info("Creating sample dataset...")
            
            np.random.seed(42)
            n_samples = 1000
            
            # Generate features
            attendance_percentage = np.random.normal(75, 15, n_samples)
            attendance_percentage = np.clip(attendance_percentage, 0, 100)
            
            average_marks = np.random.normal(65, 15, n_samples)
            average_marks = np.clip(average_marks, 0, 100)
            
            fee_status = np.random.choice(['Paid', 'Pending', 'Overdue'], n_samples, p=[0.6, 0.3, 0.1])
            
            # Generate target based on features
            risk_score = np.zeros(n_samples)
            
            for i in range(n_samples):
                # Attendance risk (40% weight)
                if attendance_percentage[i] < 75:
                    risk_score[i] += 0.4 * (75 - attendance_percentage[i]) / 75
                
                # Academic risk (40% weight)
                if average_marks[i] < 50:
                    risk_score[i] += 0.4 * (50 - average_marks[i]) / 50
                
                # Fee risk (20% weight)
                if fee_status[i] == 'Overdue':
                    risk_score[i] += 0.2
                elif fee_status[i] == 'Pending':
                    risk_score[i] += 0.1
            
            # Determine risk level
            risk_level = np.where(risk_score >= 0.7, 'High',
                         np.where(risk_score >= 0.4, 'Medium', 'Low'))
            
            # Create DataFrame
            df = pd.DataFrame({
                'attendance_percentage': attendance_percentage,
                'average_marks': average_marks,
                'fee_status': fee_status,
                'risk_level': risk_level
            })
            
            logger.info(f"Created sample dataset with {len(df)} rows")
            logger.info(f"Risk level distribution:\n{df['risk_level'].value_counts()}")
            
            return df
        except Exception as e:
            logger.error(f"Error creating sample dataset: {str(e)}")
            return None
    
    def preprocess_data(self, df):
        """
        Preprocess data for training.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (X, y) where X is features and y is target
        """
        try:
            logger.info("Preprocessing data...")
            
            # Make a copy
            data = df.copy()
            
            # Handle missing values
            data['attendance_percentage'].fillna(data['attendance_percentage'].median(), inplace=True)
            data['average_marks'].fillna(data['average_marks'].median(), inplace=True)
            data['fee_status'].fillna('Pending', inplace=True)
            
            # Encode categorical variables
            if 'fee_status' in data.columns:
                le = LabelEncoder()
                data['fee_status_encoded'] = le.fit_transform(data['fee_status'])
                self.label_encoders['fee_status'] = le
            
            # Select features
            feature_columns = ['attendance_percentage', 'average_marks', 'fee_status_encoded']
            self.feature_names = feature_columns
            
            X = data[feature_columns].values
            y = data['risk_level'].values
            
            # Encode target variable
            le_target = LabelEncoder()
            y = le_target.fit_transform(y)
            self.label_encoders['risk_level'] = le_target
            
            # Scale features
            X = self.scaler.fit_transform(X)
            
            logger.info(f"Preprocessed data: X shape {X.shape}, y shape {y.shape}")
            logger.info(f"Feature names: {self.feature_names}")
            
            return X, y
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            return None, None
    
    def train_model(self, X, y, model_type='random_forest'):
        """
        Train a model.
        
        Args:
            X: Feature matrix
            y: Target vector
            model_type: Type of model to train
            
        Returns:
            Trained model
        """
        try:
            logger.info(f"Training {model_type} model...")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Select model
            if model_type == 'random_forest':
                model = RandomForestClassifier(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42,
                    n_jobs=-1
                )
            elif model_type == 'gradient_boosting':
                model = GradientBoostingClassifier(
                    n_estimators=100,
                    max_depth=5,
                    random_state=42
                )
            elif model_type == 'logistic_regression':
                model = LogisticRegression(
                    random_state=42,
                    max_iter=1000
                )
            elif model_type == 'svm':
                model = SVC(
                    random_state=42,
                    probability=True
                )
            else:
                logger.error(f"Unknown model type: {model_type}")
                return None
            
            # Train model
            model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = model.predict(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            logger.info(f"Model performance:")
            logger.info(f"  Accuracy: {accuracy:.4f}")
            logger.info(f"  Precision: {precision:.4f}")
            logger.info(f"  Recall: {recall:.4f}")
            logger.info(f"  F1 Score: {f1:.4f}")
            
            # Cross-validation
            cv_scores = cross_val_score(model, X, y, cv=5)
            logger.info(f"Cross-validation scores: {cv_scores}")
            logger.info(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            # Classification report
            logger.info("\nClassification Report:")
            logger.info(classification_report(y_test, y_pred))
            
            return model, {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std()
            }
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return None, None
    
    def hyperparameter_tuning(self, X, y):
        """
        Perform hyperparameter tuning.
        
        Args:
            X: Feature matrix
            y: Target vector
            
        Returns:
            Best model and parameters
        """
        try:
            logger.info("Performing hyperparameter tuning...")
            
            # Define parameter grid
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            # Create model
            model = RandomForestClassifier(random_state=42, n_jobs=-1)
            
            # Perform grid search
            grid_search = GridSearchCV(
                model, param_grid, cv=5, scoring='f1_weighted', n_jobs=-1, verbose=1
            )
            grid_search.fit(X, y)
            
            logger.info(f"Best parameters: {grid_search.best_params_}")
            logger.info(f"Best score: {grid_search.best_score_:.4f}")
            
            return grid_search.best_estimator_, grid_search.best_params_
        except Exception as e:
            logger.error(f"Error in hyperparameter tuning: {str(e)}")
            return None, None
    
    def save_model(self, model, model_name, metrics):
        """
        Save trained model and metadata.
        
        Args:
            model: Trained model
            model_name: Name for the model
            metrics: Model performance metrics
            
        Returns:
            Path to saved model
        """
        try:
            logger.info(f"Saving model {model_name}...")
            
            # Create model filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            model_filename = f"{model_name}_{timestamp}.pkl"
            model_path = self.model_dir / model_filename
            
            # Save model
            joblib.dump(model, model_path)
            
            # Save scaler
            scaler_path = self.model_dir / f"{model_name}_{timestamp}_scaler.pkl"
            joblib.dump(self.scaler, scaler_path)
            
            # Save label encoders
            encoders_path = self.model_dir / f"{model_name}_{timestamp}_encoders.pkl"
            joblib.dump(self.label_encoders, encoders_path)
            
            # Save metadata
            metadata = {
                'model_name': model_name,
                'model_version': timestamp,
                'algorithm': type(model).__name__,
                'training_date': datetime.now().isoformat(),
                'feature_names': self.feature_names,
                'metrics': metrics,
                'model_path': str(model_path),
                'scaler_path': str(scaler_path),
                'encoders_path': str(encoders_path)
            }
            
            metadata_path = self.model_dir / f"{model_name}_{timestamp}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Model saved to {model_path}")
            logger.info(f"Scaler saved to {scaler_path}")
            logger.info(f"Encoders saved to {encoders_path}")
            logger.info(f"Metadata saved to {metadata_path}")
            
            return model_path, metadata
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            return None, None
    
    def register_model_in_db(self, app, model_name, model_version, algorithm, metrics, model_path):
        """
        Register model in database.
        
        Args:
            app: Flask application instance
            model_name: Model name
            model_version: Model version
            algorithm: Algorithm used
            metrics: Model metrics
            model_path: Path to model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Registering model in database...")
            
            with app.app_context():
                # Deactivate all existing models
                MLModel.query.update({'is_active': False})
                
                # Create new model record
                model = MLModel(
                    model_name=model_name,
                    model_version=model_version,
                    algorithm=algorithm,
                    training_date=datetime.utcnow(),
                    accuracy=metrics['accuracy'],
                    precision_score=metrics['precision'],
                    recall_score=metrics['recall'],
                    f1_score=metrics['f1_score'],
                    model_path=str(model_path),
                    is_active=True
                )
                
                db.session.add(model)
                db.session.commit()
                
                logger.info(f"Model registered in database: {model.model_name} v{model.model_version}")
                
            return True
        except Exception as e:
            logger.error(f"Error registering model in database: {str(e)}")
            db.session.rollback()
            return False
    
    def generate_performance_report(self, metrics, model_name):
        """
        Generate performance report.
        
        Args:
            metrics: Model metrics
            model_name: Model name
            
        Returns:
            Report as string
        """
        try:
            report = f"""
{'='*60}
Model Performance Report
{'='*60}

Model Name: {model_name}
Algorithm: Random Forest
Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Performance Metrics:
  Accuracy: {metrics['accuracy']:.4f}
  Precision: {metrics['precision']:.4f}
  Recall: {metrics['recall']:.4f}
  F1 Score: {metrics['f1_score']:.4f}

Cross-Validation:
  Mean CV Score: {metrics['cv_mean']:.4f}
  CV Std: {metrics['cv_std']:.4f}
  CV Scores: {metrics['cv_scores']}

{'='*60}
"""
            return report
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            return ""


def main():
    """Main function to train initial model."""
    print("\n" + "="*60)
    print("Initial Model Training - Student Risk Monitoring System")
    print("="*60 + "\n")
    
    # Create Flask app
    app = create_app('development')
    
    # Create model trainer
    trainer = ModelTrainer()
    
    # Load or create dataset
    dataset_path = 'datasets/students_sample.csv'
    df = trainer.load_dataset(dataset_path)
    
    if df is None:
        logger.info("Creating sample dataset...")
        df = trainer.create_sample_dataset()
    
    if df is None:
        logger.error("Failed to load or create dataset")
        return 1
    
    # Preprocess data
    X, y = trainer.preprocess_data(df)
    
    if X is None or y is None:
        logger.error("Failed to preprocess data")
        return 1
    
    # Train model
    model, metrics = trainer.train_model(X, y, model_type='random_forest')
    
    if model is None:
        logger.error("Failed to train model")
        return 1
    
    # Save model
    model_name = 'risk_model_v1'
    model_path, metadata = trainer.save_model(model, model_name, metrics)
    
    if model_path is None:
        logger.error("Failed to save model")
        return 1
    
    # Register model in database
    if not trainer.register_model_in_db(
        app,
        model_name,
        metadata['model_version'],
        metadata['algorithm'],
        metrics,
        model_path
    ):
        logger.error("Failed to register model in database")
        return 1
    
    # Generate performance report
    report = trainer.generate_performance_report(metrics, model_name)
    print(report)
    
    # Save report to file
    report_path = Path('models/trained_models') / f"{model_name}_performance_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    
    logger.info(f"Performance report saved to {report_path}")
    
    print("\n" + "="*60)
    print("Model Training Summary")
    print("="*60)
    print("✓ Model training completed successfully")
    print(f"✓ Model saved to: {model_path}")
    print(f"✓ Model registered in database")
    print(f"✓ Performance report saved to: {report_path}")
    print("\nYou can now use the model for predictions.")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
