"""
Data Preprocessing Module

This module provides comprehensive data preprocessing functions for the
Student Risk Monitoring system, including data loading, cleaning,
missing value handling, encoding, normalization, and feature preparation.
"""

import logging
import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.impute import SimpleImputer

from app.ml.config import (
    FEATURE_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
    MISSING_VALUE_STRATEGIES,
    NORMALIZATION_METHODS,
    DEFAULT_NORMALIZATION,
    DEFAULT_TEST_SIZE,
    DEFAULT_RANDOM_STATE
)

# Configure logging
logger = logging.getLogger(__name__)


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a dataset from a file.
    
    Supports CSV, Excel, and JSON formats.
    
    Args:
        file_path: Path to the dataset file
        
    Returns:
        pandas DataFrame containing the dataset
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file format is not supported
        Exception: For other loading errors
    """
    try:
        logger.info(f"Loading dataset from: {file_path}")
        
        # Determine file format
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            df = pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        logger.info(f"Dataset loaded successfully. Shape: {df.shape}")
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the dataset by removing duplicates and handling outliers.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Cleaned DataFrame
    """
    try:
        logger.info("Starting data cleaning...")
        initial_shape = df.shape
        
        # Remove duplicate rows
        df = df.drop_duplicates()
        logger.info(f"Removed {initial_shape[0] - df.shape[0]} duplicate rows")
        
        # Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # Clean column names (remove whitespace, convert to lowercase)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # Remove any unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^unnamed')]
        
        logger.info(f"Data cleaning completed. Final shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Error during data cleaning: {str(e)}")
        raise


def handle_missing_values(df: pd.DataFrame, 
                         strategy: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Handle missing values in the dataset.
    
    Args:
        df: Input DataFrame
        strategy: Dictionary specifying strategy for each column type
                 (numerical, categorical). If None, uses default from config.
        
    Returns:
        DataFrame with missing values handled
    """
    try:
        logger.info("Handling missing values...")
        
        if strategy is None:
            strategy = MISSING_VALUE_STRATEGIES
        
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Handle numerical features
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numerical_cols:
            num_strategy = strategy.get('numerical', 'median')
            
            if num_strategy == 'mean':
                imputer = SimpleImputer(strategy='mean')
            elif num_strategy == 'median':
                imputer = SimpleImputer(strategy='median')
            elif num_strategy == 'mode':
                imputer = SimpleImputer(strategy='most_frequent')
            elif num_strategy == 'constant':
                imputer = SimpleImputer(strategy='constant', fill_value=0)
            else:
                imputer = SimpleImputer(strategy='median')
            
            df[numerical_cols] = imputer.fit_transform(df[numerical_cols])
            logger.info(f"Handled missing values in {len(numerical_cols)} numerical columns")
        
        # Handle categorical features
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            cat_strategy = strategy.get('categorical', 'mode')
            
            if cat_strategy == 'mode':
                imputer = SimpleImputer(strategy='most_frequent')
                df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
            elif cat_strategy == 'constant':
                imputer = SimpleImputer(strategy='constant', fill_value='Unknown')
                df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
            elif cat_strategy == 'drop':
                df = df.dropna(subset=categorical_cols)
            
            logger.info(f"Handled missing values in {len(categorical_cols)} categorical columns")
        
        # Log remaining missing values
        remaining_missing = df.isnull().sum().sum()
        if remaining_missing > 0:
            logger.warning(f"Remaining missing values: {remaining_missing}")
        else:
            logger.info("No missing values remaining")
        
        return df
        
    except Exception as e:
        logger.error(f"Error handling missing values: {str(e)}")
        raise


def encode_categorical(df: pd.DataFrame, 
                      columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Encode categorical variables using label encoding.
    
    Args:
        df: Input DataFrame
        columns: List of columns to encode. If None, encodes all categorical columns.
        
    Returns:
        DataFrame with encoded categorical variables
    """
    try:
        logger.info("Encoding categorical variables...")
        
        df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        label_encoders = {}
        
        for col in columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
                logger.info(f"Encoded column: {col}")
        
        logger.info(f"Encoded {len(label_encoders)} categorical columns")
        return df
        
    except Exception as e:
        logger.error(f"Error encoding categorical variables: {str(e)}")
        raise


def normalize_features(df: pd.DataFrame,
                      method: str = DEFAULT_NORMALIZATION,
                      columns: Optional[List[str]] = None) -> Tuple[pd.DataFrame, Any]:
    """
    Normalize numerical features.
    
    Args:
        df: Input DataFrame
        method: Normalization method ('standard', 'minmax', 'robust', 'none')
        columns: List of columns to normalize. If None, normalizes all numerical columns.
        
    Returns:
        Tuple of (normalized DataFrame, fitted scaler object)
    """
    try:
        logger.info(f"Normalizing features using {method} method...")
        
        df = df.copy()
        
        if method == 'none' or method is None:
            logger.info("No normalization applied")
            return df, None
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Select scaler based on method
        if method == 'standard':
            scaler = StandardScaler()
        elif method == 'minmax':
            scaler = MinMaxScaler()
        elif method == 'robust':
            scaler = RobustScaler()
        else:
            logger.warning(f"Unknown normalization method: {method}. Using StandardScaler.")
            scaler = StandardScaler()
        
        # Fit and transform
        df[columns] = scaler.fit_transform(df[columns])
        
        logger.info(f"Normalized {len(columns)} numerical columns")
        return df, scaler
        
    except Exception as e:
        logger.error(f"Error normalizing features: {str(e)}")
        raise


def prepare_features(df: pd.DataFrame,
                    target_column: str = 'risk_label',
                    feature_columns: Optional[List[str]] = None,
                    normalize: bool = True,
                    encode: bool = True) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepare features for model training.
    
    This function performs comprehensive feature preparation including:
    - Selecting relevant features
    - Encoding categorical variables
    - Normalizing numerical features
    - Separating features and target
    
    Args:
        df: Input DataFrame
        target_column: Name of the target column
        feature_columns: List of feature columns to use. If None, uses default from config.
        normalize: Whether to normalize features
        encode: Whether to encode categorical features
        
    Returns:
        Tuple of (features DataFrame, target Series)
    """
    try:
        logger.info("Preparing features for model training...")
        
        df = df.copy()
        
        # Use default feature columns if not specified
        if feature_columns is None:
            feature_columns = FEATURE_COLUMNS
        
        # Check if target column exists
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in dataset")
        
        # Select only available feature columns
        available_features = [col for col in feature_columns if col in df.columns]
        
        if len(available_features) == 0:
            raise ValueError("No valid feature columns found in dataset")
        
        logger.info(f"Using {len(available_features)} feature columns")
        
        # Encode categorical features if requested
        if encode:
            categorical_cols = [col for col in available_features 
                              if col in CATEGORICAL_FEATURES and col in df.columns]
            if categorical_cols:
                df = encode_categorical(df, columns=categorical_cols)
        
        # Select features and target
        X = df[available_features]
        y = df[target_column]
        
        # Normalize features if requested
        if normalize:
            X, scaler = normalize_features(X, method=DEFAULT_NORMALIZATION)
        
        logger.info(f"Features prepared. Shape: {X.shape}")
        return X, y
        
    except Exception as e:
        logger.error(f"Error preparing features: {str(e)}")
        raise


def split_data(X: pd.DataFrame,
              y: pd.Series,
              test_size: float = DEFAULT_TEST_SIZE,
              random_state: int = DEFAULT_RANDOM_STATE,
              stratify: bool = True) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Split data into training and testing sets.
    
    Args:
        X: Features DataFrame
        y: Target Series
        test_size: Proportion of data to use for testing (0.0 to 1.0)
        random_state: Random seed for reproducibility
        stratify: Whether to stratify the split based on target distribution
        
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    try:
        logger.info(f"Splitting data with test_size={test_size}...")
        
        # Validate inputs
        if not 0 < test_size < 1:
            raise ValueError("test_size must be between 0 and 1")
        
        # Stratify based on target distribution if requested
        stratify_col = y if stratify else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=stratify_col
        )
        
        logger.info(f"Data split completed:")
        logger.info(f"  Training set: {X_train.shape[0]} samples")
        logger.info(f"  Testing set: {X_test.shape[0]} samples")
        
        return X_train, X_test, y_train, y_test
        
    except Exception as e:
        logger.error(f"Error splitting data: {str(e)}")
        raise


def get_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate a summary of the dataset.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary containing dataset summary statistics
    """
    try:
        summary = {
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numerical_summary': df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else {},
            'categorical_summary': {
                col: df[col].value_counts().to_dict() 
                for col in df.select_dtypes(include=['object', 'category']).columns
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating data summary: {str(e)}")
        raise


def validate_features(df: pd.DataFrame,
                     required_columns: Optional[List[str]] = None) -> Tuple[bool, List[str]]:
    """
    Validate that the dataset contains required features.
    
    Args:
        df: Input DataFrame
        required_columns: List of required columns. If None, uses default from config.
        
    Returns:
        Tuple of (is_valid, list of missing columns)
    """
    try:
        if required_columns is None:
            required_columns = FEATURE_COLUMNS
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        is_valid = len(missing_columns) == 0
        
        if not is_valid:
            logger.warning(f"Missing required columns: {missing_columns}")
        else:
            logger.info("All required columns present")
        
        return is_valid, missing_columns
        
    except Exception as e:
        logger.error(f"Error validating features: {str(e)}")
        raise
