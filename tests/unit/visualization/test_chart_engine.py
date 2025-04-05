"""
Unit tests for the Chart Engine module.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from src.bigsheets.visualization.chart_engine import ChartEngine


class TestChartEngine(unittest.TestCase):
    """Test cases for the ChartEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = ChartEngine()
        
        self.test_data = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12]
        ]
        
        self.temp_dir = tempfile.TemporaryDirectory()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
        plt.close('all')  # Close all figures
    
    def test_create_bar_chart(self):
        """Test creating a bar chart."""
        chart = self.engine.create_chart(
            chart_type="bar_chart",
            data=self.test_data,
            title="Test Bar Chart",
            x_label="X Axis",
            y_label="Y Axis"
        )
        
        self.assertEqual(chart["type"], "bar_chart")
        self.assertEqual(chart["title"], "Test Bar Chart")
        self.assertEqual(chart["x_label"], "X Axis")
        self.assertEqual(chart["y_label"], "Y Axis")
        self.assertEqual(chart["data"], self.test_data)
        self.assertIsNotNone(chart["figure"])
    
    def test_create_line_chart(self):
        """Test creating a line chart."""
        chart = self.engine.create_chart(
            chart_type="line_chart",
            data=self.test_data,
            title="Test Line Chart",
            x_label="X Axis",
            y_label="Y Axis"
        )
        
        self.assertEqual(chart["type"], "line_chart")
        self.assertEqual(chart["title"], "Test Line Chart")
        self.assertEqual(chart["x_label"], "X Axis")
        self.assertEqual(chart["y_label"], "Y Axis")
        self.assertEqual(chart["data"], self.test_data)
        self.assertIsNotNone(chart["figure"])
    
    def test_create_pie_chart(self):
        """Test creating a pie chart."""
        pie_data = [[1, 2, 3, 4]]
        
        chart = self.engine.create_chart(
            chart_type="pie_chart",
            data=pie_data,
            title="Test Pie Chart"
        )
        
        self.assertEqual(chart["type"], "pie_chart")
        self.assertEqual(chart["title"], "Test Pie Chart")
        self.assertEqual(chart["data"], pie_data)
        self.assertIsNotNone(chart["figure"])
    
    def test_create_scatter_plot(self):
        """Test creating a scatter plot."""
        chart = self.engine.create_chart(
            chart_type="scatter_plot",
            data=self.test_data,
            title="Test Scatter Plot",
            x_label="X Axis",
            y_label="Y Axis"
        )
        
        self.assertEqual(chart["type"], "scatter_plot")
        self.assertEqual(chart["title"], "Test Scatter Plot")
        self.assertEqual(chart["x_label"], "X Axis")
        self.assertEqual(chart["y_label"], "Y Axis")
        self.assertEqual(chart["data"], self.test_data)
        self.assertIsNotNone(chart["figure"])
    
    def test_invalid_chart_type(self):
        """Test creating a chart with an invalid type."""
        with self.assertRaises(ValueError):
            self.engine.create_chart(
                chart_type="invalid_type",
                data=self.test_data,
                title="Test Chart"
            )
    
    def test_update_chart(self):
        """Test updating a chart."""
        chart = self.engine.create_chart(
            chart_type="bar_chart",
            data=self.test_data,
            title="Original Title"
        )
        
        new_data = [[10, 20, 30, 40]]
        updated_chart = self.engine.update_chart(
            chart,
            data=new_data,
            title="Updated Title"
        )
        
        self.assertEqual(updated_chart["title"], "Updated Title")
        self.assertEqual(updated_chart["data"], new_data)
        self.assertIsNotNone(updated_chart["figure"])
    
    def test_save_chart(self):
        """Test saving a chart."""
        chart = self.engine.create_chart(
            chart_type="bar_chart",
            data=self.test_data,
            title="Test Chart"
        )
        
        save_path = os.path.join(self.temp_dir.name, "test_chart.png")
        self.engine.save_chart(chart, save_path)
        
        self.assertTrue(os.path.exists(save_path))
        self.assertTrue(os.path.getsize(save_path) > 0)
    
    def test_get_chart_data(self):
        """Test getting chart data."""
        chart = self.engine.create_chart(
            chart_type="bar_chart",
            data=self.test_data,
            title="Test Chart"
        )
        
        data = self.engine.get_chart_data(chart)
        
        self.assertEqual(data, self.test_data)


if __name__ == "__main__":
    unittest.main()
