"""
charts_engine.py — Lightweight Basira Charts Engine
====================================================
Provides basic chart configuration generation for Basira visualizations.
This is a minimal implementation that works without heavy dependencies.
"""

from typing import Dict, List, Any, Optional
import json


def generate_chart_config(
    chart_type: str,
    data: List[Dict[str, Any]],
    x_field: str,
    y_field: str,
    title: str = "",
    **kwargs
) -> Dict[str, Any]:
    """
    Generate a basic chart configuration.
    
    Args:
        chart_type: Type of chart (bar, line, scatter, pie, etc.)
        data: List of data dictionaries
        x_field: Field name for X-axis
        y_field: Field name for Y-axis
        title: Chart title
        **kwargs: Additional chart options
    
    Returns:
        Dictionary with chart configuration
    """
    
    base_config = {
        "type": chart_type,
        "title": title or f"{y_field} vs {x_field}",
        "data": data,
        "encoding": {
            "x": {"field": x_field, "type": "nominal"},
            "y": {"field": y_field, "type": "quantitative"}
        },
        "width": kwargs.get("width", 800),
        "height": kwargs.get("height", 400),
    }
    
    # Add color encoding if provided
    if "color_field" in kwargs:
        base_config["encoding"]["color"] = {
            "field": kwargs["color_field"],
            "type": "nominal"
        }
    
    return base_config


def create_bar_chart(data: List[Dict], x: str, y: str, title: str = "") -> Dict:
    """Create a bar chart configuration."""
    return generate_chart_config("bar", data, x, y, title)


def create_line_chart(data: List[Dict], x: str, y: str, title: str = "") -> Dict:
    """Create a line chart configuration."""
    return generate_chart_config("line", data, x, y, title)


def create_scatter_plot(data: List[Dict], x: str, y: str, title: str = "", **kwargs) -> Dict:
    """Create a scatter plot configuration."""
    return generate_chart_config("point", data, x, y, title, **kwargs)


def create_pie_chart(data: List[Dict], label_field: str, value_field: str, title: str = "") -> Dict:
    """Create a pie chart configuration."""
    return {
        "type": "arc",
        "title": title or "Pie Chart",
        "data": data,
        "encoding": {
            "theta": {"field": value_field, "type": "quantitative"},
            "color": {"field": label_field, "type": "nominal"}
        },
        "mark": {"type": "arc", "outerRadius": 120}
    }


def create_heatmap(data: List[Dict], x: str, y: str, value: str, title: str = "") -> Dict:
    """Create a heatmap configuration."""
    return {
        "type": "rect",
        "title": title or "Heatmap",
        "data": data,
        "encoding": {
            "x": {"field": x, "type": "nominal"},
            "y": {"field": y, "type": "nominal"},
            "color": {"field": value, "type": "quantitative"}
        }
    }


def get_chart_recommendations(
    data_summary: Dict[str, Any],
    task_type: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Recommend appropriate chart types based on data characteristics.
    
    Args:
        data_summary: Summary statistics of the dataset
        task_type: Type of analysis task (classification, regression, clustering, etc.)
    
    Returns:
        List of recommended chart configurations with descriptions
    """
    recommendations = []
    
    n_numeric = data_summary.get("n_numeric_cols", 0)
    n_categorical = data_summary.get("n_categorical_cols", 0)
    
    # Distribution charts for numeric data
    if n_numeric > 0:
        recommendations.append({
            "type": "histogram",
            "title": "Distribution Analysis",
            "description": "Show distribution of numeric features"
        })
    
    # Bar charts for categorical data
    if n_categorical > 0:
        recommendations.append({
            "type": "bar",
            "title": "Category Comparison",
            "description": "Compare categorical feature frequencies"
        })
    
    # Scatter plots for regression or correlation analysis
    if n_numeric >= 2:
        recommendations.append({
            "type": "scatter",
            "title": "Correlation Analysis",
            "description": "Explore relationships between numeric features"
        })
    
    # Classification-specific charts
    if task_type == "classification":
        recommendations.append({
            "type": "confusion_matrix",
            "title": "Confusion Matrix",
            "description": "Model prediction performance breakdown"
        })
        recommendations.append({
            "type": "roc_curve",
            "title": "ROC Curve",
            "description": "True positive vs false positive rate"
        })
    
    # Clustering-specific charts
    if task_type == "clustering":
        recommendations.append({
            "type": "cluster_scatter",
            "title": "Cluster Visualization",
            "description": "2D projection of cluster assignments"
        })
    
    # Time series charts if datetime columns exist
    if data_summary.get("has_datetime", False):
        recommendations.append({
            "type": "line",
            "title": "Time Series Analysis",
            "description": "Trends over time"
        })
    
    return recommendations


# Minimal API compatibility layer
class ChartsEngine:
    """Compatibility wrapper for the charts engine."""
    
    @staticmethod
    def generate_chart(chart_type: str, **kwargs) -> Dict:
        """Generate a chart configuration."""
        if chart_type == "bar":
            return create_bar_chart(
                kwargs.get("data", []),
                kwargs.get("x", "x"),
                kwargs.get("y", "y"),
                kwargs.get("title", "")
            )
        elif chart_type == "line":
            return create_line_chart(
                kwargs.get("data", []),
                kwargs.get("x", "x"),
                kwargs.get("y", "y"),
                kwargs.get("title", "")
            )
        elif chart_type == "scatter":
            return create_scatter_plot(
                kwargs.get("data", []),
                kwargs.get("x", "x"),
                kwargs.get("y", "y"),
                kwargs.get("title", "")
            )
        elif chart_type == "pie":
            return create_pie_chart(
                kwargs.get("data", []),
                kwargs.get("label_field", "label"),
                kwargs.get("value_field", "value"),
                kwargs.get("title", "")
            )
        elif chart_type == "heatmap":
            return create_heatmap(
                kwargs.get("data", []),
                kwargs.get("x", "x"),
                kwargs.get("y", "y"),
                kwargs.get("value", "value"),
                kwargs.get("title", "")
            )
        else:
            return {"type": chart_type, "data": kwargs.get("data", [])}
    
    @staticmethod
    def get_recommendations(data_summary: Dict, task_type: Optional[str] = None) -> List[Dict]:
        """Get chart recommendations."""
        return get_chart_recommendations(data_summary, task_type)


if __name__ == "__main__":
    # Test examples
    sample_data = [
        {"category": "A", "value": 10},
        {"category": "B", "value": 20},
        {"category": "C", "value": 15},
    ]
    
    bar_config = create_bar_chart(sample_data, "category", "value", "Sample Bar Chart")
    print(json.dumps(bar_config, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50)
    print("Charts Engine loaded successfully ✅")
