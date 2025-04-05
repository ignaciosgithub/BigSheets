"""
Chart Engine Module

This module provides functionality for creating and managing charts and graphs.
"""

from typing import Dict, List, Any, Optional, Union, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from io import BytesIO
import base64


class ChartEngine:
    """
    Provides functionality for creating and managing charts and graphs.
    """
    
    def __init__(self):
        """Initialize the chart engine."""
        self.supported_chart_types = [
            "bar", "line", "scatter", "pie", "area", "histogram"
        ]
    
    def create_chart(
        self,
        chart_type: str,
        data: Union[pd.DataFrame, List[Dict[str, Any]]],
        x_column: str,
        y_columns: List[str],
        title: str = "",
        x_label: str = "",
        y_label: str = "",
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a chart based on the provided data and options.
        
        Args:
            chart_type: Type of chart to create (bar, line, scatter, pie, etc.)
            data: Data to use for the chart
            x_column: Column to use for the x-axis
            y_columns: Columns to use for the y-axis
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
            options: Additional chart options
            
        Returns:
            Dictionary containing chart data and metadata
        """
        if chart_type not in self.supported_chart_types:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        if isinstance(data, list):
            data = pd.DataFrame(data)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.set_title(title)
        ax.set_xlabel(x_label or x_column)
        ax.set_ylabel(y_label)
        
        options = options or {}
        
        if chart_type == "bar":
            self._create_bar_chart(ax, data, x_column, y_columns, options)
        elif chart_type == "line":
            self._create_line_chart(ax, data, x_column, y_columns, options)
        elif chart_type == "scatter":
            self._create_scatter_chart(ax, data, x_column, y_columns, options)
        elif chart_type == "pie":
            self._create_pie_chart(ax, data, x_column, y_columns, options)
        elif chart_type == "area":
            self._create_area_chart(ax, data, x_column, y_columns, options)
        elif chart_type == "histogram":
            self._create_histogram(ax, data, y_columns, options)
        
        if len(y_columns) > 1:
            ax.legend()
        
        buffer = BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        plt.close(fig)
        
        return {
            "type": chart_type,
            "title": title,
            "image": f"data:image/png;base64,{image_base64}",
            "x_column": x_column,
            "y_columns": y_columns,
            "options": options
        }
    
    def _create_bar_chart(
        self,
        ax,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create a bar chart."""
        bar_width = options.get("bar_width", 0.8 / len(y_columns))
        
        for i, y_column in enumerate(y_columns):
            x = np.arange(len(data))
            offset = (i - len(y_columns) / 2 + 0.5) * bar_width
            ax.bar(x + offset, data[y_column], width=bar_width, label=y_column)
        
        ax.set_xticks(np.arange(len(data)))
        ax.set_xticklabels(data[x_column])
    
    def _create_line_chart(
        self,
        ax,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create a line chart."""
        for y_column in y_columns:
            ax.plot(data[x_column], data[y_column], label=y_column, 
                   marker=options.get("marker", "o"),
                   linestyle=options.get("linestyle", "-"))
    
    def _create_scatter_chart(
        self,
        ax,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create a scatter chart."""
        for y_column in y_columns:
            ax.scatter(data[x_column], data[y_column], label=y_column,
                      alpha=options.get("alpha", 0.7),
                      s=options.get("point_size", 50))
    
    def _create_pie_chart(
        self,
        ax,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create a pie chart."""
        y_column = y_columns[0]
        
        ax.pie(data[y_column], labels=data[x_column],
              autopct=options.get("autopct", "%1.1f%%"),
              shadow=options.get("shadow", False),
              startangle=options.get("startangle", 90))
        ax.axis("equal")  # Equal aspect ratio ensures that pie is drawn as a circle
    
    def _create_area_chart(
        self,
        ax,
        data: pd.DataFrame,
        x_column: str,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create an area chart."""
        for y_column in y_columns:
            ax.fill_between(data[x_column], data[y_column], alpha=options.get("alpha", 0.3), label=y_column)
            ax.plot(data[x_column], data[y_column], alpha=options.get("line_alpha", 0.7))
    
    def _create_histogram(
        self,
        ax,
        data: pd.DataFrame,
        y_columns: List[str],
        options: Dict[str, Any]
    ) -> None:
        """Create a histogram."""
        bins = options.get("bins", 10)
        
        for y_column in y_columns:
            ax.hist(data[y_column], bins=bins, alpha=0.7, label=y_column)
