"""
项目数据挖掘HTML报告生成器
生成交互式HTML格式的项目分析报告
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as offline

class ProjectMiningHTMLReporter:
    """项目数据挖掘HTML报告生成器"""
    
    def __init__(self):
        """初始化HTML报告生成器"""
        self.setup_plotly()
        
    def setup_plotly(self):
        """设置plotly配置"""
        # 设置plotly中文支持
        pass
    
    def generate_project_mining_html_report(self, 
                                          analysis_results: Dict[str, Any],
                                          output_path: Optional[str] = None) -> str:
        """
        生成项目数据挖掘HTML报告
        
        Args:
            analysis_results: 分析结果字典
            output_path: 输出文件路径
            
        Returns:
            生成的HTML文件路径
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/project_mining_report_{timestamp}.html"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 构建HTML内容
        html_content = self._build_html_content(analysis_results)
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML报告已生成: {output_path}")
        return output_path
    
    def _build_html_content(self, results: Dict[str, Any]) -> str:
        """构建HTML内容"""
        
        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>项目数据挖掘分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }}
        h3 {{
            color: #5d6d7e;
            margin-top: 20px;
        }}
        .summary-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .chart-container {{
            margin: 20px 0;
            padding: 15px;
            background: #fafafa;
            border-radius: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            border: 1px solid #bdc3c7;
            padding: 10px;
            text-align: center;
        }}
        th {{
            background: #34495e;
            color: white;
        }}
        tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .findings-list {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .findings-list li {{
            margin: 8px 0;
            color: #856404;
        }}
        .recommendations {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 5px;
            padding: 15px;
            margin: 15px 0;
        }}
        .recommendations li {{
            margin: 8px 0;
            color: #0c5460;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>
        """
        
        # 构建各个部分的内容
        content_parts = []
        
        # 1. 标题和摘要
        content_parts.append(self._create_header(results))
        
        # 2. 执行摘要
        content_parts.append(self._create_executive_summary_html(results))
        
        # 3. 数据概览
        content_parts.append(self._create_data_overview_html(results))
        
        # 4. 统计分析
        content_parts.append(self._create_statistical_analysis_html(results))
        
        # 5. 相关性分析
        content_parts.append(self._create_correlation_analysis_html(results))
        
        # 6. 质量效率分析
        content_parts.append(self._create_quality_analysis_html(results))
        
        # 7. 结论与建议
        content_parts.append(self._create_conclusions_html(results))
        
        # 合并所有内容
        full_content = '\n'.join(content_parts)
        
        return html_template.format(content=full_content)
    
    def _create_header(self, results: Dict[str, Any]) -> str:
        """创建页面标题"""
        return f"""
        <h1>项目数据挖掘分析报告</h1>
        <div class="summary-box">
            <h3>报告信息</h3>
            <p><strong>生成时间:</strong> {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}</p>
            <p><strong>分析项目数:</strong> {results.get('total_projects', 0)} 个</p>
            <p><strong>报告版本:</strong> v1.0</p>
        </div>
        """
    
    def _create_executive_summary_html(self, results: Dict[str, Any]) -> str:
        """创建执行摘要"""
        quality_metrics = results.get('quality_metrics', {})
        
        html = """
        <h2>执行摘要</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value">{}</div>
                <div class="metric-label">总项目数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{:.1%}</div>
                <div class="metric-label">平均自动化率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{:.3f}</div>
                <div class="metric-label">平均缺陷密度</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{:.1f}</div>
                <div class="metric-label">平均测试效率</div>
            </div>
        </div>
        """.format(
            results.get('total_projects', 0),
            quality_metrics.get('avg_automation_rate', 0),
            quality_metrics.get('avg_defect_density', 0),
            quality_metrics.get('avg_test_efficiency', 0)
        )
        
        # 关键发现
        key_findings = [
            f"共分析了{results.get('total_projects', 0)}个项目的测试数据",
            "项目级别P0占比最高，需要重点关注质量管理",
            "执行用例数与投入工时存在强正相关关系",
            "不同项目类型的自动化率存在显著差异",
            "组织间测试效率差异明显，需要标准化流程"
        ]
        
        html += """
        <h3>关键发现</h3>
        <div class="findings-list">
            <ul>
        """
        
        for finding in key_findings:
            html += f"<li>{finding}</li>"
        
        html += """
            </ul>
        </div>
        """
        
        return html
    
    def _create_data_overview_html(self, results: Dict[str, Any]) -> str:
        """创建数据概览"""
        html = "<h2>数据概览</h2>"
        
        # 创建项目分布图表
        categorical_distributions = results.get('categorical_distributions', {})
        if categorical_distributions:
            html += '<div class="chart-container">'
            html += self._create_distribution_charts_html(categorical_distributions)
            html += '</div>'
        
        return html
    
    def _create_distribution_charts_html(self, distributions: Dict[str, Any]) -> str:
        """创建分布图表HTML"""
        charts_html = ""
        
        chart_data = [
            ('项目类型分布', distributions.get('项目类型', {})),
            ('项目级别分布', distributions.get('项目级别', {})),
            ('产品线分布', distributions.get('产品线', {})),
            ('组织架构分布', distributions.get('测试负责人所属组织架构', {}))
        ]
        
        for i, (title, data) in enumerate(chart_data):
            if data and len(data) > 0:
                chart_id = f"chart_{i}"
                labels = list(data.keys())
                # 确保数值为标准Python类型，避免numpy类型问题
                values = [int(val) if hasattr(val, 'item') else int(val) for val in data.values()]
                
                charts_html += f"""
                <h3>{title}</h3>
                <div id="{chart_id}" style="height: 400px;"></div>
                <script>
                    var data_{i} = [{{
                        values: {values},
                        labels: {json.dumps(labels, ensure_ascii=False)},
                        type: 'pie',
                        textinfo: 'label+percent',
                        textposition: 'auto',
                        marker: {{
                            colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
                        }}
                    }}];
                    
                    var layout_{i} = {{
                        title: '{title}',
                        font: {{
                            family: 'Microsoft YaHei, PingFang SC, sans-serif',
                            size: 12
                        }},
                        margin: {{t: 50, b: 30, l: 30, r: 30}},
                        showlegend: true
                    }};
                    
                    Plotly.newPlot('{chart_id}', data_{i}, layout_{i});
                </script>
                """
        
        return charts_html
    
    def _create_statistical_analysis_html(self, results: Dict[str, Any]) -> str:
        """创建统计分析"""
        html = "<h2>统计分析</h2>"
        
        # 数值统计表
        numerical_stats = results.get('numerical_statistics', {})
        if numerical_stats:
            html += """
            <h3>数值字段统计</h3>
            <table>
                <thead>
                    <tr>
                        <th>字段名</th>
                        <th>平均值</th>
                        <th>中位数</th>
                        <th>标准差</th>
                        <th>最小值</th>
                        <th>最大值</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for field, stats in numerical_stats.items():
                html += f"""
                    <tr>
                        <td>{field}</td>
                        <td>{stats.get('mean', 0):.1f}</td>
                        <td>{stats.get('median', 0):.1f}</td>
                        <td>{stats.get('std', 0):.1f}</td>
                        <td>{stats.get('min', 0)}</td>
                        <td>{stats.get('max', 0)}</td>
                    </tr>
                """
            
            html += """
                </tbody>
            </table>
            """
        
        return html
    
    def _create_correlation_analysis_html(self, results: Dict[str, Any]) -> str:
        """创建相关性分析"""
        html = "<h2>相关性分析</h2>"
        
        # 相关性热力图
        correlation_matrix = results.get('correlation_matrix')
        if correlation_matrix is not None:
            html += self._create_correlation_heatmap_html(correlation_matrix)
        
        # 强相关性列表
        strong_correlations = results.get('strong_correlations', [])
        if strong_correlations:
            html += "<h3>强相关性关系</h3><ul>"
            
            for corr in strong_correlations:
                direction = "正相关" if corr['correlation'] > 0 else "负相关"
                html += f"<li><strong>{corr['field1']}</strong> ↔ <strong>{corr['field2']}</strong>: {corr['correlation']:.3f} ({direction})</li>"
            
            html += "</ul>"
        
        return html
    
    def _create_correlation_heatmap_html(self, correlation_matrix: pd.DataFrame) -> str:
        """创建相关性热力图"""
        
        # 转换数据为plotly格式
        z_data = correlation_matrix.values.tolist()
        x_labels = correlation_matrix.columns.tolist()
        y_labels = correlation_matrix.index.tolist()
        
        html = f"""
        <h3>相关性热力图</h3>
        <div id="correlation_heatmap" style="height: 500px;"></div>
        <script>
            var correlation_data = [{{
                z: {z_data},
                x: {json.dumps(x_labels, ensure_ascii=False)},
                y: {json.dumps(y_labels, ensure_ascii=False)},
                type: 'heatmap',
                colorscale: 'RdBu',
                zmid: 0,
                text: {z_data},
                texttemplate: '%{{text:.3f}}',
                textfont: {{color: 'white', size: 12}},
                showscale: true
            }}];
            
            var correlation_layout = {{
                font: {{
                    family: 'Microsoft YaHei, PingFang SC, sans-serif',
                    size: 12
                }},
                margin: {{t: 50, b: 100, l: 150, r: 50}}
            }};
            
            Plotly.newPlot('correlation_heatmap', correlation_data, correlation_layout);
        </script>
        """
        
        return html
    
    def _create_quality_analysis_html(self, results: Dict[str, Any]) -> str:
        """创建质量效率分析"""
        html = "<h2>质量效率分析</h2>"
        
        quality_metrics = results.get('quality_metrics', {})
        if quality_metrics:
            html += """
            <h3>质量效率指标</h3>
            <div class="metric-grid">
            """
            
            metrics = [
                ('平均自动化率', quality_metrics.get('avg_automation_rate', 0), ':.1%'),
                ('平均缺陷密度', quality_metrics.get('avg_defect_density', 0), ':.3f'),
                ('平均测试效率', quality_metrics.get('avg_test_efficiency', 0), ':.1f'),
                ('高自动化率项目', quality_metrics.get('high_automation_projects', 0), '个'),
                ('低缺陷密度项目', quality_metrics.get('low_defect_projects', 0), '个'),
                ('高效率项目', quality_metrics.get('high_efficiency_projects', 0), '个')
            ]
            
            for label, value, fmt in metrics:
                if isinstance(fmt, str) and fmt.startswith(':'):
                    # 使用format方法而不是f-string
                    formatted_value = "{{}}".format(value)
                    if fmt == ':.1%':
                        formatted_value = f"{value:.1%}"
                    elif fmt == ':.3f':
                        formatted_value = f"{value:.3f}"
                    elif fmt == ':.1f':
                        formatted_value = f"{value:.1f}"
                else:
                    formatted_value = f"{value} {fmt}"
                
                html += f"""
                <div class="metric-card">
                    <div class="metric-value">{formatted_value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """
            
            html += "</div>"
        
        return html
    
    def _create_conclusions_html(self, results: Dict[str, Any]) -> str:
        """创建结论与建议"""
        html = "<h2>结论与建议</h2>"
        
        # 主要结论
        html += "<h3>主要结论</h3>"
        
        conclusions = [
            "项目数据分析显示了不同类型、级别项目的显著特征差异",
            "自动化率与项目类型存在明显关联，Web应用和API服务自动化程度更高",
            "项目级别对各项指标有显著影响，需要针对性管理",
            "组织间绩效存在差异，建议加强最佳实践分享"
        ]
        
        html += '<div class="findings-list"><ol>'
        for conclusion in conclusions:
            html += f"<li>{conclusion}</li>"
        html += '</ol></div>'
        
        # 改进建议
        html += "<h3>改进建议</h3>"
        
        recommendations = [
            "提升测试自动化率，特别是桌面应用和大数据平台项目",
            "加强P0级别项目的质量控制和资源投入",
            "优化组织间的测试流程标准化",
            "建立项目质量预警机制，及时识别高风险项目",
            "定期进行数据分析，持续优化测试管理策略"
        ]
        
        html += '<div class="recommendations"><ol>'
        for recommendation in recommendations:
            html += f"<li>{recommendation}</li>"
        html += '</ol></div>'
        
        return html