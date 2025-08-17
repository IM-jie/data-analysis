"""
KPI报告生成器
支持生成HTML和PDF格式的分析报告
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import jinja2
import os
from datetime import datetime
from pathlib import Path
from loguru import logger

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class KPIReportGenerator:
    """KPI报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 设置模板环境
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader('templates'),
            autoescape=True
        )
        
        # 设置颜色主题
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b'
        }
    
    def generate_comprehensive_report(self, 
                                    data: pd.DataFrame,
                                    analysis_results: Dict[str, Any],
                                    report_title: str = "KPI数据分析报告") -> str:
        """
        生成综合分析报告
        
        Args:
            data: 原始数据
            analysis_results: 分析结果
            report_title: 报告标题
            
        Returns:
            报告文件路径
        """
        # 生成图表
        charts = self._generate_charts(data, analysis_results)
        
        # 生成HTML报告
        html_path = self._generate_html_report(data, analysis_results, charts, report_title)
        
        # 生成PDF报告（可选）
        pdf_path = self._generate_pdf_report(html_path, report_title)
        
        logger.info(f"报告生成完成: {html_path}")
        if pdf_path:
            logger.info(f"PDF报告生成完成: {pdf_path}")
        
        return html_path
    
    def _generate_charts(self, data: pd.DataFrame, 
                        analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成各种图表"""
        charts = {}
        
        # 1. 数据概览图表
        charts['overview'] = self._create_overview_charts(data, analysis_results)
        
        # 2. 异常检测图表
        charts['anomalies'] = self._create_anomaly_charts(data, analysis_results)
        
        # 3. 趋势分析图表
        charts['trends'] = self._create_trend_charts(data, analysis_results)
        
        # 4. 部门对比图表
        charts['comparison'] = self._create_comparison_charts(data, analysis_results)
        
        return charts
    
    def _create_overview_charts(self, data: pd.DataFrame, 
                               analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据概览图表"""
        charts = {}
        
        # 数据质量热力图
        summary = analysis_results.get('summary', {})
        data_quality = summary.get('data_quality', {})
        
        if data_quality:
            quality_df = pd.DataFrame.from_dict(data_quality, orient='index')
            
            fig = px.imshow(
                quality_df[['missing_percentage']].T,
                title="数据质量热力图 - 缺失值比例",
                color_continuous_scale='RdYlGn_r',
                aspect='auto'
            )
            fig.update_layout(height=400)
            charts['data_quality_heatmap'] = fig.to_html(full_html=False)
        
        # 指标分布直方图
        metric_columns = summary.get('metrics', [])
        if metric_columns:
            # 选择前几个指标进行展示
            sample_metrics = metric_columns[:6]
            
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=sample_metrics,
                specs=[[{"secondary_y": False}] * 3] * 2
            )
            
            for i, metric in enumerate(sample_metrics):
                if metric in data.columns:
                    row = i // 3 + 1
                    col = i % 3 + 1
                    
                    metric_data = data[metric].dropna()
                    if len(metric_data) > 0:
                        fig.add_trace(
                            go.Histogram(x=metric_data, name=metric, showlegend=False),
                            row=row, col=col
                        )
            
            fig.update_layout(
                title="指标分布直方图",
                height=600,
                showlegend=False
            )
            charts['metric_distributions'] = fig.to_html(full_html=False)
        
        return charts
    
    def _create_anomaly_charts(self, data: pd.DataFrame, 
                              analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建异常检测图表"""
        charts = {}
        
        anomalies = analysis_results.get('anomalies', {})
        
        if anomalies:
            # 异常检测结果汇总
            anomaly_summary = []
            for metric, methods in anomalies.items():
                for method, result in methods.items():
                    if result.get('anomalies'):
                        anomaly_count = sum(result['anomalies'])
                        if anomaly_count > 0:
                            anomaly_summary.append({
                                'metric': metric,
                                'method': method,
                                'anomaly_count': anomaly_count
                            })
            
            if anomaly_summary:
                summary_df = pd.DataFrame(anomaly_summary)
                
                fig = px.bar(
                    summary_df,
                    x='metric',
                    y='anomaly_count',
                    color='method',
                    title="异常检测结果汇总",
                    barmode='group'
                )
                fig.update_layout(height=400)
                charts['anomaly_summary'] = fig.to_html(full_html=False)
            
            # 异常值散点图
            for metric, methods in anomalies.items():
                if metric in data.columns:
                    metric_data = data[metric].dropna()
                    if len(metric_data) > 0:
                        # 使用IQR方法的结果进行可视化
                        if 'iqr' in methods:
                            iqr_result = methods['iqr']
                            if iqr_result.get('anomalies'):
                                anomalies_mask = iqr_result['anomalies']
                                
                                fig = px.scatter(
                                    x=range(len(metric_data)),
                                    y=metric_data,
                                    color=anomalies_mask,
                                    title=f"{metric} - 异常值检测 (IQR方法)",
                                    labels={'x': '数据点', 'y': metric}
                                )
                                fig.update_layout(height=400)
                                charts[f'anomaly_scatter_{metric}'] = fig.to_html(full_html=False)
                                break
        
        return charts
    
    def _create_trend_charts(self, data: pd.DataFrame, 
                            analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建趋势分析图表"""
        charts = {}
        
        trends = analysis_results.get('trends', {})
        
        if trends:
            # 趋势斜率对比
            trend_slopes = []
            for metric, trend_result in trends.items():
                slope = trend_result.get('trend_slope', 0)
                trend_slopes.append({
                    'metric': metric,
                    'slope': slope,
                    'direction': '上升' if slope > 0 else '下降'
                })
            
            if trend_slopes:
                slopes_df = pd.DataFrame(trend_slopes)
                
                fig = px.bar(
                    slopes_df,
                    x='metric',
                    y='slope',
                    color='direction',
                    title="指标趋势斜率对比",
                    color_discrete_map={'上升': 'green', '下降': 'red'}
                )
                fig.update_layout(height=400)
                charts['trend_slopes'] = fig.to_html(full_html=False)
            
            # 时间序列趋势图
            for metric, trend_result in trends.items():
                if 'data' in trend_result:
                    trend_data = trend_result['data']
                    if len(trend_data) > 0:
                        fig = px.line(
                            trend_data,
                            x='time',
                            y='value',
                            title=f"{metric} - 时间序列趋势",
                            labels={'time': '时间', 'value': metric}
                        )
                        
                        # 添加移动平均线
                        if 'moving_average' in trend_result:
                            fig.add_trace(
                                go.Scatter(
                                    x=trend_data['time'],
                                    y=trend_result['moving_average'],
                                    mode='lines',
                                    name='移动平均',
                                    line=dict(color='red', dash='dash')
                                )
                            )
                        
                        fig.update_layout(height=400)
                        charts[f'trend_line_{metric}'] = fig.to_html(full_html=False)
                        break  # 只显示第一个指标的趋势图
        
        return charts
    
    def _create_comparison_charts(self, data: pd.DataFrame, 
                                 analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """创建部门对比图表"""
        charts = {}
        
        summary = analysis_results.get('summary', {})
        department_column = summary.get('department_column', '部门名称')
        metric_columns = summary.get('metrics', [])
        
        if department_column in data.columns and metric_columns:
            # 部门指标对比热力图
            dept_metrics = data.set_index(department_column)[metric_columns[:10]]  # 限制指标数量
            
            fig = px.imshow(
                dept_metrics,
                title="部门指标对比热力图",
                color_continuous_scale='RdYlBu',
                aspect='auto'
            )
            fig.update_layout(height=500)
            charts['department_comparison_heatmap'] = fig.to_html(full_html=False)
            
            # 部门排名图
            for metric in metric_columns[:5]:  # 只显示前5个指标
                if metric in data.columns:
                    metric_data = data[[department_column, metric]].dropna()
                    if len(metric_data) > 0:
                        # 按指标值排序
                        metric_data_sorted = metric_data.sort_values(metric, ascending=False)
                        
                        fig = px.bar(
                            metric_data_sorted,
                            x=department_column,
                            y=metric,
                            title=f"{metric} - 部门排名",
                            color=metric,
                            color_continuous_scale='viridis'
                        )
                        fig.update_layout(height=400)
                        charts[f'ranking_{metric}'] = fig.to_html(full_html=False)
        
        return charts
    
    def _generate_html_report(self, data: pd.DataFrame, 
                             analysis_results: Dict[str, Any],
                             charts: Dict[str, Any],
                             report_title: str) -> str:
        """生成HTML报告"""
        
        # 准备报告数据
        report_data = {
            'title': report_title,
            'generated_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_summary': analysis_results.get('summary', {}),
            'anomalies': analysis_results.get('anomalies', {}),
            'trends': analysis_results.get('trends', {}),
            'recommendations': analysis_results.get('recommendations', []),
            'charts': charts
        }
        
        # 生成HTML内容
        html_content = self._create_html_content(report_data)
        
        # 保存HTML文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f"kpi_report_{timestamp}.html"
        html_path = self.output_dir / html_filename
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(html_path)
    
    def _create_html_content(self, report_data: Dict[str, Any]) -> str:
        """创建HTML内容"""
        
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            border-bottom: 3px solid #1f77b4;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #1f77b4;
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            color: #666;
            margin: 10px 0 0 0;
        }
        .section {
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
            background-color: #fafafa;
        }
        .section h2 {
            color: #1f77b4;
            border-bottom: 2px solid #1f77b4;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .summary-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #1f77b4;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #1f77b4;
        }
        .summary-card p {
            margin: 0;
            font-size: 1.2em;
            font-weight: bold;
        }
        .recommendations {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
        }
        .recommendations h3 {
            color: #856404;
            margin-top: 0;
        }
        .recommendations ul {
            margin: 0;
            padding-left: 20px;
        }
        .recommendations li {
            margin-bottom: 10px;
            color: #856404;
        }
        .chart-container {
            margin: 20px 0;
            text-align: center;
        }
        .chart-container iframe {
            border: none;
            width: 100%;
            height: 500px;
        }
        .alert {
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .alert-warning {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }
        .alert-info {
            background-color: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
        }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .table th, .table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        .table th {
            background-color: #1f77b4;
            color: white;
        }
        .table tr:nth-child(even) {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>生成时间: {{ generated_time }}</p>
        </div>

        <!-- 数据摘要 -->
        <div class="section">
            <h2>📊 数据摘要</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>部门数量</h3>
                    <p>{{ data_summary.total_departments }}</p>
                </div>
                <div class="summary-card">
                    <h3>指标数量</h3>
                    <p>{{ data_summary.total_metrics }}</p>
                </div>
                <div class="summary-card">
                    <h3>数据行数</h3>
                    <p>{{ data_summary.data_shape[0] if data_summary.data_shape else 'N/A' }}</p>
                </div>
                <div class="summary-card">
                    <h3>数据列数</h3>
                    <p>{{ data_summary.data_shape[1] if data_summary.data_shape else 'N/A' }}</p>
                </div>
            </div>
            
            {% if data_summary.departments %}
            <h3>部门列表</h3>
            <p>{{ data_summary.departments | join(', ') }}</p>
            {% endif %}
            
            {% if data_summary.metrics %}
            <h3>指标列表</h3>
            <p>{{ data_summary.metrics | join(', ') }}</p>
            {% endif %}
        </div>

        <!-- 数据质量 -->
        {% if data_summary.data_quality %}
        <div class="section">
            <h2>🔍 数据质量分析</h2>
            <table class="table">
                <thead>
                    <tr>
                        <th>列名</th>
                        <th>数据类型</th>
                        <th>缺失值比例</th>
                        <th>状态</th>
                    </tr>
                </thead>
                <tbody>
                    {% for col, quality in data_summary.data_quality.items() %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ quality.data_type }}</td>
                        <td>{{ "%.2f"|format(quality.missing_percentage) }}%</td>
                        <td>
                            {% if quality.missing_percentage > 20 %}
                            <span style="color: red;">⚠️ 缺失值较多</span>
                            {% elif quality.missing_percentage > 5 %}
                            <span style="color: orange;">⚠️ 部分缺失</span>
                            {% else %}
                            <span style="color: green;">✅ 良好</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}

        <!-- 异常检测结果 -->
        {% if anomalies %}
        <div class="section">
            <h2>🚨 异常检测结果</h2>
            {% for metric, methods in anomalies.items() %}
            <h3>{{ metric }}</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>检测方法</th>
                        <th>异常数量</th>
                        <th>异常比例</th>
                    </tr>
                </thead>
                <tbody>
                    {% for method, result in methods.items() %}
                    {% if result.anomalies %}
                    <tr>
                        <td>{{ method }}</td>
                        <td>{{ result.anomalies | sum }}</td>
                        <td>{{ "%.2f"|format((result.anomalies | sum) / result.anomalies | length * 100) }}%</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
            {% endfor %}
            
            {% if charts.anomalies %}
            {% for chart_name, chart_html in charts.anomalies.items() %}
            <div class="chart-container">
                {{ chart_html | safe }}
            </div>
            {% endfor %}
            {% endif %}
        </div>
        {% endif %}

        <!-- 趋势分析结果 -->
        {% if trends %}
        <div class="section">
            <h2>📈 趋势分析结果</h2>
            {% for metric, trend_result in trends.items() %}
            <h3>{{ metric }}</h3>
            <ul>
                <li><strong>趋势斜率:</strong> {{ "%.3f"|format(trend_result.trend_slope) }}</li>
                <li><strong>波动性:</strong> {{ "%.3f"|format(trend_result.volatility) }}</li>
                {% if trend_result.seasonality.has_seasonality %}
                <li><strong>季节性:</strong> 存在 (周期: {{ "%.1f"|format(trend_result.seasonality.period) }})</li>
                {% else %}
                <li><strong>季节性:</strong> 不明显</li>
                {% endif %}
            </ul>
            {% endfor %}
            
            {% if charts.trends %}
            {% for chart_name, chart_html in charts.trends.items() %}
            <div class="chart-container">
                {{ chart_html | safe }}
            </div>
            {% endfor %}
            {% endif %}
        </div>
        {% endif %}

        <!-- 部门对比 -->
        {% if charts.comparison %}
        <div class="section">
            <h2>🏢 部门对比分析</h2>
            {% for chart_name, chart_html in charts.comparison.items() %}
            <div class="chart-container">
                {{ chart_html | safe }}
            </div>
            {% endfor %}
        </div>
        {% endif %}

        <!-- 建议 -->
        {% if recommendations %}
        <div class="section">
            <h2>💡 分析建议</h2>
            <div class="recommendations">
                <ul>
                    {% for recommendation in recommendations %}
                    <li>{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
        {% endif %}

        <!-- 图表概览 -->
        {% if charts.overview %}
        <div class="section">
            <h2>📊 数据概览图表</h2>
            {% for chart_name, chart_html in charts.overview.items() %}
            <div class="chart-container">
                {{ chart_html | safe }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
        """
        
        template = jinja2.Template(html_template)
        return template.render(**report_data)
    
    def _generate_pdf_report(self, html_path: str, report_title: str) -> Optional[str]:
        """生成PDF报告"""
        try:
            # 这里可以集成wkhtmltopdf或其他PDF生成工具
            # 暂时返回None，表示不生成PDF
            logger.info("PDF生成功能暂未实现，请手动将HTML转换为PDF")
            return None
        except Exception as e:
            logger.warning(f"PDF生成失败: {e}")
            return None
    
    def generate_simple_report(self, data: pd.DataFrame, 
                              analysis_results: Dict[str, Any]) -> str:
        """生成简化版报告"""
        
        # 创建简化版HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>KPI数据分析报告</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
        .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>KPI数据分析报告</h1>
    <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="section">
        <h2>数据摘要</h2>
        <p>总部门数: {analysis_results.get('summary', {}).get('total_departments', 0)}</p>
        <p>总指标数: {analysis_results.get('summary', {}).get('total_metrics', 0)}</p>
    </div>
    
    <div class="section">
        <h2>异常检测结果</h2>
        {self._format_anomalies_simple(analysis_results.get('anomalies', {}))}
    </div>
    
    <div class="section">
        <h2>分析建议</h2>
        <div class="highlight">
            {self._format_recommendations_simple(analysis_results.get('recommendations', []))}
        </div>
    </div>
</body>
</html>
        """
        
        # 保存文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"simple_kpi_report_{timestamp}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _format_anomalies_simple(self, anomalies: Dict[str, Any]) -> str:
        """格式化异常检测结果为简单HTML"""
        if not anomalies:
            return "<p>未检测到异常</p>"
        
        html = "<ul>"
        for metric, methods in anomalies.items():
            for method, result in methods.items():
                if result.get('anomalies'):
                    count = sum(result['anomalies'])
                    if count > 0:
                        html += f"<li>{metric} ({method}): {count}个异常</li>"
        html += "</ul>"
        return html
    
    def _format_recommendations_simple(self, recommendations: List[str]) -> str:
        """格式化建议为简单HTML"""
        if not recommendations:
            return "<p>暂无建议</p>"
        
        html = "<ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        return html
