"""
基本测试文件
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analysis.analyzer import DataAnalyzer
from src.visualization.charts import ChartGenerator


class TestDataAnalyzer(unittest.TestCase):
    """测试数据分析器"""
    
    def setUp(self):
        """设置测试数据"""
        # 生成测试数据
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                             end=datetime.now(), freq='D')
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'value': np.random.normal(100, 20, len(dates)) + 10 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7),
            'category': np.random.choice(['A', 'B', 'C'], len(dates))
        })
        
        self.analyzer = DataAnalyzer()
    
    def test_analyze_distribution(self):
        """测试分布分析"""
        result = self.analyzer.analyze_distribution(self.test_data, 'value')
        
        self.assertIn('target_column', result)
        self.assertIn('basic_stats', result)
        self.assertIn('distribution_type', result)
        self.assertIn('outliers', result)
        
        self.assertEqual(result['target_column'], 'value')
        self.assertIsInstance(result['basic_stats']['mean'], (int, float))
        self.assertIsInstance(result['basic_stats']['std'], (int, float))
    
    def test_analyze_trend(self):
        """测试趋势分析"""
        result = self.analyzer.analyze_trend(self.test_data, 'date', 'value')
        
        self.assertIn('date_column', result)
        self.assertIn('value_column', result)
        self.assertIn('trend_direction', result)
        self.assertIn('data_points', result)
        
        self.assertEqual(result['date_column'], 'date')
        self.assertEqual(result['value_column'], 'value')
        self.assertIn(result['trend_direction'], ['increasing', 'decreasing', 'stable', 'insufficient_data'])
    
    def test_detect_anomalies(self):
        """测试异常检测"""
        result = self.analyzer.detect_anomalies(self.test_data, 'value', 'isolation_forest')
        
        self.assertIn('target_column', result)
        self.assertIn('method', result)
        self.assertIn('anomaly_stats', result)
        self.assertIn('anomaly_indices', result)
        
        self.assertEqual(result['target_column'], 'value')
        self.assertEqual(result['method'], 'isolation_forest')
        self.assertIsInstance(result['anomaly_stats']['total_points'], int)
        self.assertIsInstance(result['anomaly_stats']['anomaly_count'], int)


class TestChartGenerator(unittest.TestCase):
    """测试图表生成器"""
    
    def setUp(self):
        """设置测试数据"""
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                             end=datetime.now(), freq='D')
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'value': np.random.normal(100, 20, len(dates))
        })
        
        self.chart_generator = ChartGenerator()
    
    def test_create_distribution_chart(self):
        """测试创建分布图表"""
        chart = self.chart_generator.create_distribution_chart(self.test_data, 'value')
        
        self.assertIsNotNone(chart)
        # 检查是否是Plotly图表对象
        self.assertTrue(hasattr(chart, 'add_trace'))
        self.assertTrue(hasattr(chart, 'update_layout'))
    
    def test_create_trend_chart(self):
        """测试创建趋势图表"""
        chart = self.chart_generator.create_trend_chart(self.test_data, 'date', 'value')
        
        self.assertIsNotNone(chart)
        self.assertTrue(hasattr(chart, 'add_trace'))
        self.assertTrue(hasattr(chart, 'update_layout'))
    
    def test_create_anomaly_chart(self):
        """测试创建异常检测图表"""
        # 先生成异常检测结果
        analyzer = DataAnalyzer()
        anomaly_result = analyzer.detect_anomalies(self.test_data, 'value')
        
        chart = self.chart_generator.create_anomaly_chart(self.test_data, 'value', anomaly_result)
        
        self.assertIsNotNone(chart)
        self.assertTrue(hasattr(chart, 'add_trace'))
        self.assertTrue(hasattr(chart, 'update_layout'))


if __name__ == '__main__':
    unittest.main()
