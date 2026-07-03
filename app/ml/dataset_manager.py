"""
Dataset Management Module

This module provides comprehensive functions for managing datasets in the
Student Risk Monitoring system, including uploading, merging, validating,
and generating sample datasets.
"""

import logging
import pandas as pd
import numpy as np
import os
import shutil
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from pathlib import Path

from app.ml.config import (
    DATASET_DIR,
    SUPPORTED_FORMATS,
    DEFAULT_DATASET_FORMAT,
    DATASET_VALIDATION_RULES,
    FEATURE_COLUMNS
)
from app.ml.preprocessor import clean_data, handle_missing_values

# Configure logging
logger = logging.getLogger(__name__)


def upload_dataset(file: Any,
                  filename: str,
                  merge: bool = False,
                  validate: bool = True) -> Dict[str, Any]:
    """
    Upload a dataset file.
    
    Args:
        file: File object or file path
        filename: Name of the file
        merge: Whether to merge with existing dataset
        validate: Whether to validate the dataset
        
    Returns:
        Dictionary containing upload results
    """
    try:
        logger.info(f"Uploading dataset: {filename}")
        
        # Ensure dataset directory exists
        os.makedirs(DATASET_DIR, exist_ok=True)
        
        # Determine file path
        file_path = os.path.join(DATASET_DIR, filename)
        
        # Save file
        if hasattr(file, 'save'):
            # Flask file upload
            file.save(file_path)
        elif hasattr(file, 'read'):
            # File-like object
            with open(file_path, 'wb') as f:
                f.write(file.read())
        else:
            # Assume it's a path
            shutil.copy(file, file_path)
        
        logger.info(f"File saved to: {file_path}")
        
        # Load dataset
        df = load_dataset_by_format(file_path)
        
        # Validate if requested
        validation_result = None
        if validate:
            validation_result = validate_dataset(df)
            if not validation_result['is_valid']:
                logger.warning(f"Dataset validation failed: {validation_result['issues']}")
        
        # Merge if requested
        if merge:
            existing_path = find_existing_dataset()
            if existing_path:
                logger.info(f"Merging with existing dataset: {existing_path}")
                df = merge_datasets(existing_path, file_path)
                # Save merged dataset
                df.to_csv(existing_path, index=False)
                file_path = existing_path
        
        # Get dataset info
        info = get_dataset_info(df)
        info['file_path'] = file_path
        info['validation'] = validation_result
        
        logger.info(f"Dataset uploaded successfully. Shape: {df.shape}")
        return info
        
    except Exception as e:
        logger.error(f"Error uploading dataset: {str(e)}")
        raise


def merge_datasets(existing_path: str,
                  new_path: str,
                  on: Optional[List[str]] = None,
                  how: str = 'outer') -> pd.DataFrame:
    """
    Merge two datasets.
    
    Args:
        existing_path: Path to existing dataset
        new_path: Path to new dataset
        on: Columns to merge on. If None, uses index.
        how: Type of merge ('inner', 'outer', 'left', 'right')
        
    Returns:
        Merged DataFrame
    """
    try:
        logger.info(f"Merging datasets: {existing_path} and {new_path}")
        
        # Load datasets
        df_existing = load_dataset_by_format(existing_path)
        df_new = load_dataset_by_format(new_path)
        
        logger.info(f"Existing dataset shape: {df_existing.shape}")
        logger.info(f"New dataset shape: {df_new.shape}")
        
        # Merge datasets
        if on:
            df_merged = pd.merge(df_existing, df_new, on=on, how=how, suffixes=('_existing', '_new'))
        else:
            df_merged = pd.concat([df_existing, df_new], ignore_index=True)
        
        # Remove duplicates
        initial_shape = df_merged.shape
        df_merged = df_merged.drop_duplicates()
        
        logger.info(f"Merged dataset shape: {df_merged.shape}")
        logger.info(f"Removed {initial_shape[0] - df_merged.shape[0]} duplicate rows")
        
        return df_merged
        
    except Exception as e:
        logger.error(f"Error merging datasets: {str(e)}")
        raise


def replace_dataset(old_path: str,
                   new_path: str,
                   backup: bool = True) -> str:
    """
    Replace an existing dataset with a new one.
    
    Args:
        old_path: Path to existing dataset
        new_path: Path to new dataset
        backup: Whether to create a backup of the old dataset
        
    Returns:
        Path to the new dataset
    """
    try:
        logger.info(f"Replacing dataset: {old_path} with {new_path}")
        
        # Create backup if requested
        if backup and os.path.exists(old_path):
            backup_path = f"{old_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(old_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Replace dataset
        shutil.copy(new_path, old_path)
        
        logger.info(f"Dataset replaced successfully")
        return old_path
        
    except Exception as e:
        logger.error(f"Error replacing dataset: {str(e)}")
        raise


def validate_dataset(df: pd.DataFrame,
                    rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Validate a dataset against defined rules.
    
    Args:
        df: DataFrame to validate
        rules: Validation rules. If None, uses default from config.
        
    Returns:
        Dictionary containing validation results
    """
    try:
        logger.info("Validating dataset...")
        
        if rules is None:
            rules = DATASET_VALIDATION_RULES
        
        issues = []
        warnings = []
        
        # Check minimum samples
        min_samples = rules.get('min_samples', 50)
        if len(df) < min_samples:
            issues.append(f"Dataset has {len(df)} samples, minimum required is {min_samples}")
        
        # Check missing percentage
        max_missing = rules.get('max_missing_percentage', 0.3)
        missing_percentage = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
        if missing_percentage > max_missing:
            issues.append(f"Dataset has {missing_percentage:.1%} missing values, maximum allowed is {max_missing:.1%}")
        
        # Check required columns
        required_columns = rules.get('required_columns', FEATURE_COLUMNS)
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            warnings.append(f"Missing recommended columns: {missing_columns}")
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append(f"Dataset contains {duplicates} duplicate rows")
        
        # Check data types
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if it should be numeric
                try:
                    pd.to_numeric(df[col], errors='raise')
                except:
                    pass  # It's truly categorical
        
        is_valid = len(issues) == 0
        
        result = {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'shape': df.shape,
            'missing_percentage': missing_percentage,
            'duplicate_rows': duplicates,
            'columns': df.columns.tolist()
        }
        
        if is_valid:
            logger.info("Dataset validation passed")
        else:
            logger.warning(f"Dataset validation failed: {issues}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error validating dataset: {str(e)}")
        raise


def generate_sample_dataset(num_students: int = 100,
                          output_path: Optional[str] = None) -> pd.DataFrame:
    """
    Generate a sample dataset for testing.
    
    Args:
        num_students: Number of students to generate
        output_path: Path to save the dataset. If None, doesn't save.
        
    Returns:
        Generated DataFrame
    """
    try:
        logger.info(f"Generating sample dataset with {num_students} students...")
        
        np.random.seed(42)  # For reproducibility
        
        # Generate student IDs
        student_ids = [f"STU{i:04d}" for i in range(1, num_students + 1)]
        
        # Generate features
        data = {
            'student_id': student_ids,
            'attendance_percentage': np.random.normal(80, 15, num_students).clip(0, 100),
            'average_marks': np.random.normal(65, 15, num_students).clip(0, 100),
            'fee_compliance_score': np.random.normal(85, 10, num_students).clip(0, 100),
            'behavior_score': np.random.normal(90, 8, num_students).clip(0, 100),
            'assignments_submitted': np.random.poisson(8, num_students).clip(0, 15),
            'library_usage': np.random.poisson(5, num_students).clip(0, 20),
            'extracurricular_score': np.random.normal(60, 20, num_students).clip(0, 100),
            'parent_engagement': np.random.normal(70, 15, num_students).clip(0, 100),
            'disciplinary_incidents': np.random.poisson(1, num_students).clip(0, 10),
            'academic_improvement': np.random.normal(5, 10, num_students).clip(-20, 20),
            'age': np.random.randint(14, 19, num_students),
            'previous_year_marks': np.random.normal(65, 15, num_students).clip(0, 100)
        }
        
        df = pd.DataFrame(data)
        
        # Generate risk labels based on features
        risk_score = (
            (100 - df['attendance_percentage']) * 0.2 +
            (100 - df['average_marks']) * 0.25 +
            (100 - df['fee_compliance_score']) * 0.1 +
            (100 - df['behavior_score']) * 0.15 +
            df['disciplinary_incidents'] * 2
        )
        
        # Normalize risk score to 0-1
        risk_score = (risk_score - risk_score.min()) / (risk_score.max() - risk_score.min())
        
        # Assign risk labels
        df['risk_label'] = (risk_score > 0.5).astype(int)
        
        # Add some noise to make it more realistic
        noise = np.random.normal(0, 0.1, num_students)
        risk_score = (risk_score + noise).clip(0, 1)
        df['risk_probability'] = risk_score
        
        # Save if path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
            df.to_csv(output_path, index=False)
            logger.info(f"Sample dataset saved to: {output_path}")
        
        logger.info(f"Sample dataset generated successfully. Shape: {df.shape}")
        logger.info(f"Risk distribution: {df['risk_label'].value_counts().to_dict()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error generating sample dataset: {str(e)}")
        raise


def export_dataset(df: pd.DataFrame,
                  format: str = DEFAULT_DATASET_FORMAT,
                  output_path: Optional[str] = None) -> str:
    """
    Export a dataset to a file.
    
    Args:
        df: DataFrame to export
        format: Export format ('csv', 'xlsx', 'json')
        output_path: Path to save the file. If None, generates automatically.
        
    Returns:
        Path where the file was saved
    """
    try:
        logger.info(f"Exporting dataset to {format} format...")
        
        # Validate format
        if format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {format}. Supported: {SUPPORTED_FORMATS}")
        
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = os.path.join(DATASET_DIR, f"dataset_{timestamp}.{format}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Export based on format
        if format == 'csv':
            df.to_csv(output_path, index=False)
        elif format == 'xlsx':
            df.to_excel(output_path, index=False)
        elif format == 'json':
            df.to_json(output_path, orient='records', indent=2)
        
        logger.info(f"Dataset exported to: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error exporting dataset: {str(e)}")
        raise


def load_dataset_by_format(file_path: str) -> pd.DataFrame:
    """
    Load a dataset based on its file format.
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        Loaded DataFrame
    """
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
            
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


def find_existing_dataset() -> Optional[str]:
    """
    Find an existing dataset in the dataset directory.
    
    Returns:
        Path to existing dataset, or None if not found
    """
    try:
        if not os.path.exists(DATASET_DIR):
            return None
        
        # Look for dataset files
        for filename in os.listdir(DATASET_DIR):
            if any(filename.endswith(f'.{fmt}') for fmt in SUPPORTED_FORMATS):
                return os.path.join(DATASET_DIR, filename)
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding existing dataset: {str(e)}")
        return None


def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get information about a dataset.
    
    Args:
        df: DataFrame to analyze
        
    Returns:
        Dictionary containing dataset information
    """
    try:
        info = {
            'shape': df.shape,
            'rows': df.shape[0],
            'columns': df.shape[1],
            'column_names': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numerical_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist()
        }
        
        # Add statistics for numerical columns
        if info['numerical_columns']:
            info['numerical_statistics'] = df[info['numerical_columns']].describe().to_dict()
        
        # Add value counts for categorical columns
        if info['categorical_columns']:
            info['categorical_statistics'] = {
                col: df[col].value_counts().head(10).to_dict()
                for col in info['categorical_columns']
            }
        
        return info
        
    except Exception as e:
        logger.error(f"Error getting dataset info: {str(e)}")
        raise


def list_datasets() -> List[Dict[str, Any]]:
    """
    List all available datasets.
    
    Returns:
        List of dictionaries containing dataset information
    """
    try:
        logger.info("Listing available datasets...")
        
        if not os.path.exists(DATASET_DIR):
            return []
        
        datasets = []
        
        for filename in os.listdir(DATASET_DIR):
            if any(filename.endswith(f'.{fmt}') for fmt in SUPPORTED_FORMATS):
                file_path = os.path.join(DATASET_DIR, filename)
                
                # Get file info
                file_stat = os.stat(file_path)
                
                dataset_info = {
                    'filename': filename,
                    'path': file_path,
                    'size': file_stat.st_size,
                    'size_mb': file_stat.st_size / (1024 * 1024),
                    'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                    'format': filename.split('.')[-1]
                }
                
                datasets.append(dataset_info)
        
        # Sort by last modified (newest first)
        datasets.sort(key=lambda x: x['last_modified'], reverse=True)
        
        logger.info(f"Found {len(datasets)} datasets")
        return datasets
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise


def delete_dataset(file_path: str,
                  backup: bool = True) -> bool:
    """
    Delete a dataset file.
    
    Args:
        file_path: Path to the dataset file
        backup: Whether to create a backup before deleting
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Deleting dataset: {file_path}")
        
        # Create backup if requested
        if backup and os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(file_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
        
        # Delete file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Dataset deleted: {file_path}")
            return True
        else:
            logger.warning(f"Dataset not found: {file_path}")
            return False
        
    except Exception as e:
        logger.error(f"Error deleting dataset: {str(e)}")
        return False
