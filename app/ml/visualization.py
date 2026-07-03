"""
ML Visualization Module

This module provides comprehensive visualization functions for the
Student Risk Monitoring system, including risk distribution plots,
feature importance charts, model comparisons, and confusion matrices.
"""

import logging
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import os

from app.ml.config import (
    RISK_LEVELS,
    RISK_COLORS,
    PLOT_STYLE,
    PLOT_OUTPUT_DIR,
    FEATURE_DISPLAY_NAMES
)

# Configure logging
logger = logging.getLogger(__name__)

# Set plot style
plt.style.use(PLOT_STYLE['style'])
sns.set_palette(PLOT_STYLE['color_palette'])


def plot_risk_distribution(predictions: List[Dict[str, Any]],
                          save_path: Optional[str] = None,
                          show: bool = False) -> plt.Figure:
    """
    Plot the distribution of risk levels.
    
    Args:
        predictions: List of prediction result dictionaries
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting risk distribution...")
        
        # Count risk levels
        risk_counts = {}
        for pred in predictions:
            risk_level = pred.get('risk_level', 'unknown')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        # Prepare data
        levels = list(risk_counts.keys())
        counts = list(risk_counts.values())
        colors = [RISK_COLORS.get(level, '#6c757d') for level in levels]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=PLOT_STYLE['figure_size'])
        
        # Bar chart
        bars = ax1.bar(levels, counts, color=colors, edgecolor='black', linewidth=1)
        ax1.set_xlabel('Risk Level', fontsize=PLOT_STYLE['label_size'])
        ax1.set_ylabel('Number of Students', fontsize=PLOT_STYLE['label_size'])
        ax1.set_title('Risk Level Distribution (Bar Chart)', fontsize=PLOT_STYLE['title_size'])
        ax1.tick_params(axis='both', labelsize=PLOT_STYLE['font_size'])
        
        # Add value labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count}',
                    ha='center', va='bottom', fontsize=PLOT_STYLE['font_size'])
        
        # Pie chart
        ax2.pie(counts, labels=levels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax2.set_title('Risk Level Distribution (Pie Chart)', fontsize=PLOT_STYLE['title_size'])
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Risk distribution plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting risk distribution: {str(e)}")
        raise


def plot_feature_importance(importance: pd.DataFrame,
                          save_path: Optional[str] = None,
                          show: bool = False) -> plt.Figure:
    """
    Plot feature importance.
    
    Args:
        importance: DataFrame containing feature importance scores
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting feature importance...")
        
        # Sort by importance
        importance = importance.sort_values('importance', ascending=True)
        
        # Get display names
        feature_names = importance['feature'].tolist()
        display_names = [FEATURE_DISPLAY_NAMES.get(name, name.replace('_', ' ').title()) 
                        for name in feature_names]
        
        # Create figure
        fig, ax = plt.subplots(figsize=PLOT_STYLE['figure_size'])
        
        # Create horizontal bar chart
        y_pos = np.arange(len(display_names))
        bars = ax.barh(y_pos, importance['importance'], color='steelblue', edgecolor='black', linewidth=1)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(display_names, fontsize=PLOT_STYLE['font_size'])
        ax.set_xlabel('Importance Score', fontsize=PLOT_STYLE['label_size'])
        ax.set_title('Feature Importance', fontsize=PLOT_STYLE['title_size'])
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, importance['importance'])):
            ax.text(value, bar.get_y() + bar.get_height()/2,
                   f'{value:.3f}',
                   ha='left', va='center', fontsize=PLOT_STYLE['font_size']-2)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Feature importance plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting feature importance: {str(e)}")
        raise


def plot_model_comparison(results: pd.DataFrame,
                         metrics: Optional[List[str]] = None,
                         save_path: Optional[str] = None,
                         show: bool = False) -> plt.Figure:
    """
    Plot comparison of multiple models.
    
    Args:
        results: DataFrame containing model comparison results
        metrics: List of metrics to plot. If None, uses default metrics.
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting model comparison...")
        
        if metrics is None:
            metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        # Filter metrics that exist in results
        available_metrics = [m for m in metrics if m in results.columns]
        
        if not available_metrics:
            logger.warning("No metrics available for plotting")
            return None
        
        # Create figure
        n_metrics = len(available_metrics)
        fig, axes = plt.subplots(1, n_metrics, figsize=(5 * n_metrics, 6))
        
        if n_metrics == 1:
            axes = [axes]
        
        # Plot each metric
        for ax, metric in zip(axes, available_metrics):
            # Sort by metric value
            sorted_results = results.sort_values(metric, ascending=False)
            
            # Create bar chart
            x_pos = np.arange(len(sorted_results))
            bars = ax.bar(x_pos, sorted_results[metric], color='steelblue', edgecolor='black', linewidth=1)
            
            ax.set_xticks(x_pos)
            ax.set_xticklabels(sorted_results['model'], rotation=45, ha='right', fontsize=PLOT_STYLE['font_size'])
            ax.set_ylabel(metric.replace('_', ' ').title(), fontsize=PLOT_STYLE['label_size'])
            ax.set_title(f'Model Comparison - {metric.replace("_", " ").title()}', 
                        fontsize=PLOT_STYLE['title_size'])
            
            # Add value labels
            for bar, value in zip(bars, sorted_results[metric]):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.3f}',
                       ha='center', va='bottom', fontsize=PLOT_STYLE['font_size']-2)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Model comparison plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting model comparison: {str(e)}")
        raise


def plot_confusion_matrix(y_true: np.ndarray,
                         y_pred: np.ndarray,
                         labels: Optional[List[str]] = None,
                         save_path: Optional[str] = None,
                         show: bool = False) -> plt.Figure:
    """
    Plot confusion matrix.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        labels: List of label names. If None, uses default.
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting confusion matrix...")
        
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # Create figure
        fig, ax = plt.subplots(figsize=PLOT_STYLE['figure_size'])
        
        # Plot heatmap
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=labels, yticklabels=labels, ax=ax)
        
        ax.set_xlabel('Predicted Label', fontsize=PLOT_STYLE['label_size'])
        ax.set_ylabel('True Label', fontsize=PLOT_STYLE['label_size'])
        ax.set_title('Confusion Matrix', fontsize=PLOT_STYLE['title_size'])
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Confusion matrix plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting confusion matrix: {str(e)}")
        raise


def plot_roc_curve(model: Any,
                  X_test: pd.DataFrame,
                  y_test: pd.Series,
                  save_path: Optional[str] = None,
                  show: bool = False) -> plt.Figure:
    """
    Plot ROC curve.
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting ROC curve...")
        
        # Check if model supports probability predictions
        if not hasattr(model, 'predict_proba'):
            logger.warning("Model does not support probability predictions")
            return None
        
        # Get probability predictions
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Calculate ROC curve
        from sklearn.metrics import roc_curve, auc
        fpr, tpr, thresholds = roc_curve(y_test, y_prob)
        roc_auc = auc(fpr, tpr)
        
        # Create figure
        fig, ax = plt.subplots(figsize=PLOT_STYLE['figure_size'])
        
        # Plot ROC curve
        ax.plot(fpr, tpr, color='darkorange', lw=2,
               label=f'ROC curve (AUC = {roc_auc:.2f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
               label='Random classifier')
        
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('False Positive Rate', fontsize=PLOT_STYLE['label_size'])
        ax.set_ylabel('True Positive Rate', fontsize=PLOT_STYLE['label_size'])
        ax.set_title('Receiver Operating Characteristic (ROC) Curve',
                    fontsize=PLOT_STYLE['title_size'])
        ax.legend(loc='lower right', fontsize=PLOT_STYLE['font_size'])
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"ROC curve plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting ROC curve: {str(e)}")
        raise


def plot_learning_curve(model: Any,
                       X: pd.DataFrame,
                       y: pd.Series,
                       cv: int = 5,
                       save_path: Optional[str] = None,
                       show: bool = False) -> plt.Figure:
    """
    Plot learning curve.
    
    Args:
        model: Trained model
        X: Features
        y: Labels
        cv: Number of cross-validation folds
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting learning curve...")
        
        from sklearn.model_selection import learning_curve
        
        # Calculate learning curve
        train_sizes, train_scores, test_scores = learning_curve(
            model, X, y, cv=cv, n_jobs=-1,
            train_sizes=np.linspace(0.1, 1.0, 10)
        )
        
        # Calculate mean and std
        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)
        
        # Create figure
        fig, ax = plt.subplots(figsize=PLOT_STYLE['figure_size'])
        
        # Plot learning curve
        ax.fill_between(train_sizes, train_mean - train_std,
                       train_mean + train_std, alpha=0.1, color='blue')
        ax.fill_between(train_sizes, test_mean - test_std,
                       test_mean + test_std, alpha=0.1, color='orange')
        ax.plot(train_sizes, train_mean, 'o-', color='blue',
               label='Training score')
        ax.plot(train_sizes, test_mean, 'o-', color='orange',
               label='Cross-validation score')
        
        ax.set_xlabel('Training Set Size', fontsize=PLOT_STYLE['label_size'])
        ax.set_ylabel('Score', fontsize=PLOT_STYLE['label_size'])
        ax.set_title('Learning Curve', fontsize=PLOT_STYLE['title_size'])
        ax.legend(loc='lower right', fontsize=PLOT_STYLE['font_size'])
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Learning curve plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting learning curve: {str(e)}")
        raise


def plot_feature_distribution(df: pd.DataFrame,
                            feature: str,
                            target: Optional[str] = None,
                            save_path: Optional[str] = None,
                            show: bool = False) -> plt.Figure:
    """
    Plot distribution of a feature.
    
    Args:
        df: DataFrame containing the data
        feature: Feature column name
        target: Target column name for grouping. If None, no grouping.
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info(f"Plotting distribution for feature: {feature}")
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histogram
        if target and target in df.columns:
            for label in df[target].unique():
                subset = df[df[target] == label][feature]
                ax1.hist(subset, bins=30, alpha=0.5, label=f'{target}={label}')
            ax1.legend()
        else:
            ax1.hist(df[feature], bins=30, color='steelblue', edgecolor='black')
        
        ax1.set_xlabel(feature.replace('_', ' ').title(), fontsize=PLOT_STYLE['label_size'])
        ax1.set_ylabel('Frequency', fontsize=PLOT_STYLE['label_size'])
        ax1.set_title(f'Distribution of {feature.replace("_", " ").title()}',
                     fontsize=PLOT_STYLE['title_size'])
        
        # Box plot
        if target and target in df.columns:
            df.boxplot(column=feature, by=target, ax=ax2)
            ax2.set_title(f'{feature.replace("_", " ").title()} by {target}',
                         fontsize=PLOT_STYLE['title_size'])
        else:
            ax2.boxplot(df[feature])
            ax2.set_title(f'Box Plot of {feature.replace("_", " ").title()}',
                         fontsize=PLOT_STYLE['title_size'])
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Feature distribution plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting feature distribution: {str(e)}")
        raise


def plot_correlation_matrix(df: pd.DataFrame,
                          features: Optional[List[str]] = None,
                          save_path: Optional[str] = None,
                          show: bool = False) -> plt.Figure:
    """
    Plot correlation matrix.
    
    Args:
        df: DataFrame containing the data
        features: List of features to include. If None, uses all numerical features.
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Plotting correlation matrix...")
        
        # Select features
        if features:
            df_subset = df[features]
        else:
            df_subset = df.select_dtypes(include=[np.number])
        
        # Calculate correlation matrix
        corr = df_subset.corr()
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Plot heatmap
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm',
                   center=0, square=True, linewidths=1, ax=ax)
        
        ax.set_title('Feature Correlation Matrix', fontsize=PLOT_STYLE['title_size'])
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Correlation matrix plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error plotting correlation matrix: {str(e)}")
        raise


def create_dashboard(predictions: List[Dict[str, Any]],
                    feature_importance: Optional[pd.DataFrame] = None,
                    model_comparison: Optional[pd.DataFrame] = None,
                    save_path: Optional[str] = None,
                    show: bool = False) -> plt.Figure:
    """
    Create a comprehensive dashboard with multiple visualizations.
    
    Args:
        predictions: List of prediction result dictionaries
        feature_importance: Optional DataFrame containing feature importance
        model_comparison: Optional DataFrame containing model comparison results
        save_path: Path to save the plot. If None, doesn't save.
        show: Whether to display the plot
        
    Returns:
        matplotlib Figure object
    """
    try:
        logger.info("Creating comprehensive dashboard...")
        
        # Determine number of subplots
        n_plots = 2  # Risk distribution (bar + pie)
        if feature_importance is not None:
            n_plots += 1
        if model_comparison is not None:
            n_plots += 1
        
        # Create figure
        fig = plt.figure(figsize=(15, 5 * ((n_plots + 1) // 2)))
        
        # Plot risk distribution
        ax1 = plt.subplot(2, 2, 1)
        risk_counts = {}
        for pred in predictions:
            risk_level = pred.get('risk_level', 'unknown')
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        
        levels = list(risk_counts.keys())
        counts = list(risk_counts.values())
        colors = [RISK_COLORS.get(level, '#6c757d') for level in levels]
        
        ax1.bar(levels, counts, color=colors, edgecolor='black', linewidth=1)
        ax1.set_xlabel('Risk Level')
        ax1.set_ylabel('Number of Students')
        ax1.set_title('Risk Level Distribution')
        
        # Plot pie chart
        ax2 = plt.subplot(2, 2, 2)
        ax2.pie(counts, labels=levels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax2.set_title('Risk Level Distribution')
        
        # Plot feature importance if available
        if feature_importance is not None:
            ax3 = plt.subplot(2, 2, 3)
            importance_sorted = feature_importance.sort_values('importance', ascending=True).tail(10)
            y_pos = np.arange(len(importance_sorted))
            ax3.barh(y_pos, importance_sorted['importance'], color='steelblue')
            ax3.set_yticks(y_pos)
            ax3.set_yticklabels(importance_sorted['feature'])
            ax3.set_xlabel('Importance')
            ax3.set_title('Top 10 Feature Importance')
        
        # Plot model comparison if available
        if model_comparison is not None:
            ax4 = plt.subplot(2, 2, 4)
            if 'accuracy' in model_comparison.columns:
                sorted_results = model_comparison.sort_values('accuracy', ascending=False)
                x_pos = np.arange(len(sorted_results))
                ax4.bar(x_pos, sorted_results['accuracy'], color='steelblue')
                ax4.set_xticks(x_pos)
                ax4.set_xticklabels(sorted_results['model'], rotation=45, ha='right')
                ax4.set_ylabel('Accuracy')
                ax4.set_title('Model Comparison')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.savefig(save_path, dpi=PLOT_STYLE['dpi'], bbox_inches='tight')
            logger.info(f"Dashboard saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating dashboard: {str(e)}")
        raise
