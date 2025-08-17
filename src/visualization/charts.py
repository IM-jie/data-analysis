"""
数据可视化模块 - 图表生成器
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import warnings
from loguru import logger

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 设置seaborn样式
sns.set_style("whitegrid")
sns.set_palette("husl")

# 忽略警告
warnings.filterwarnings('ignore')


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, style: str = 'plotly'):
        """
        初始化图表生成器
        
        Args:
            style: 图表样式 ('plotly', 'matplotlib')
        """
        self.style = style
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#8c564b',
            'dark': '#e377c2'
        }
    
    def create_distribution_chart(self, df: pd.DataFrame, target_column: str, 
                                analysis_result: Dict[str, Any] = None) -> go.Figure:
        """
        创建分布图表
        
        Args:
            df: 数据DataFrame
            target_column: 目标列名
            analysis_result: 分布分析结果
            
        Returns:
            Plotly图表对象
        """
        try:
            data = df[target_column].dropna()
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('数据分布直方图', '箱线图', 'Q-Q图', '统计信息'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"type": "table"}]]
            )
            
            # 直方图
            fig.add_trace(
                go.Histogram(
                    x=data,
                    nbinsx=30,
                    name='数据分布',
                    marker_color=self.colors['primary'],
                    opacity=0.7
                ),
                row=1, col=1
            )
            
            # 箱线图
            fig.add_trace(
                go.Box(
                    y=data,
                    name='数据分布',
                    marker_color=self.colors['secondary'],
                    boxpoints='outliers'
                ),
                row=1, col=2
            )
            
            # Q-Q图
            from scipy import stats
            theoretical_quantiles = stats.probplot(data, dist="norm")
            fig.add_trace(
                go.Scatter(
                    x=theoretical_quantiles[0][0],
                    y=theoretical_quantiles[0][1],
                    mode='markers',
                    name='Q-Q图',
                    marker_color=self.colors['info']
                ),
                row=2, col=1
            )
            
            # 添加理论线
            fig.add_trace(
                go.Scatter(
                    x=theoretical_quantiles[0][0],
                    y=theoretical_quantiles[0][0] * theoretical_quantiles[1][0] + theoretical_quantiles[1][1],
                    mode='lines',
                    name='理论线',
                    line=dict(color='red', dash='dash')
                ),
                row=2, col=1
            )
            
            # 统计信息表格
            if analysis_result:
                stats_info = analysis_result.get('basic_stats', {})
                table_data = [
                    ['统计量', '值'],
                    ['样本数', f"{stats_info.get('count', len(data)):,}"],
                    ['均值', f"{stats_info.get('mean', data.mean()):.2f}"],
                    ['标准差', f"{stats_info.get('std', data.std()):.2f}"],
                    ['最小值', f"{stats_info.get('min', data.min()):.2f}"],
                    ['最大值', f"{stats_info.get('max', data.max()):.2f}"],
                    ['中位数', f"{stats_info.get('median', data.median()):.2f}"],
                    ['偏度', f"{stats_info.get('skewness', data.skew()):.2f}"],
                    ['峰度', f"{stats_info.get('kurtosis', data.kurtosis()):.2f}"]
                ]
            else:
                table_data = [
                    ['统计量', '值'],
                    ['样本数', f"{len(data):,}"],
                    ['均值', f"{data.mean():.2f}"],
                    ['标准差', f"{data.std():.2f}"],
                    ['最小值', f"{data.min():.2f}"],
                    ['最大值', f"{data.max():.2f}"],
                    ['中位数', f"{data.median():.2f}"],
                    ['偏度', f"{data.skew():.2f}"],
                    ['峰度', f"{data.kurtosis():.2f}"]
                ]
            
            fig.add_trace(
                go.Table(
                    header=dict(values=table_data[0], fill_color='lightblue'),
                    cells=dict(values=[row[0] for row in table_data[1:]] + [row[1] for row in table_data[1:]], 
                              fill_color='white')
                ),
                row=2, col=2
            )
            
            # 更新布局
            fig.update_layout(
                title=f'{target_column} 数据分布分析',
                height=800,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建分布图表失败: {e}")
            raise
    
    def create_trend_chart(self, df: pd.DataFrame, date_column: str, value_column: str,
                          analysis_result: Dict[str, Any] = None) -> go.Figure:
        """
        创建趋势图表
        
        Args:
            df: 数据DataFrame
            date_column: 日期列名
            value_column: 数值列名
            analysis_result: 趋势分析结果
            
        Returns:
            Plotly图表对象
        """
        try:
            # 确保数据按日期排序
            df_sorted = df.sort_values(date_column).copy()
            df_sorted = df_sorted[[date_column, value_column]].dropna()
            
            # 创建子图
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('时间序列趋势', '时间序列分解'),
                vertical_spacing=0.1
            )
            
            # 原始数据
            fig.add_trace(
                go.Scatter(
                    x=df_sorted[date_column],
                    y=df_sorted[value_column],
                    mode='lines+markers',
                    name='原始数据',
                    line=dict(color=self.colors['primary'], width=2),
                    marker=dict(size=4)
                ),
                row=1, col=1
            )
            
            # 移动平均线
            if analysis_result and 'moving_averages' in analysis_result:
                ma_data = analysis_result['moving_averages']
                for window, values in ma_data.items():
                    if len(values) == len(df_sorted):
                        fig.add_trace(
                            go.Scatter(
                                x=df_sorted[date_column],
                                y=values,
                                mode='lines',
                                name=f'移动平均({window.split("_")[1]})',
                                line=dict(dash='dash', width=1)
                            ),
                            row=1, col=1
                        )
            
            # 时间序列分解
            if analysis_result and 'decomposition' in analysis_result:
                decomp = analysis_result['decomposition']
                
                if decomp.get('trend') and len(decomp['trend']) == len(df_sorted):
                    fig.add_trace(
                        go.Scatter(
                            x=df_sorted[date_column],
                            y=decomp['trend'],
                            mode='lines',
                            name='趋势',
                            line=dict(color=self.colors['success'], width=2)
                        ),
                        row=2, col=1
                    )
                
                if decomp.get('seasonal') and len(decomp['seasonal']) == len(df_sorted):
                    fig.add_trace(
                        go.Scatter(
                            x=df_sorted[date_column],
                            y=decomp['seasonal'],
                            mode='lines',
                            name='季节性',
                            line=dict(color=self.colors['warning'], width=2)
                        ),
                        row=2, col=1
                    )
                
                if decomp.get('residual') and len(decomp['residual']) == len(df_sorted):
                    fig.add_trace(
                        go.Scatter(
                            x=df_sorted[date_column],
                            y=decomp['residual'],
                            mode='lines',
                            name='残差',
                            line=dict(color=self.colors['info'], width=2)
                        ),
                        row=2, col=1
                    )
            
            # 更新布局
            fig.update_layout(
                title=f'{value_column} 时间序列趋势分析',
                height=800,
                showlegend=True
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建趋势图表失败: {e}")
            raise
    
    def create_anomaly_chart(self, df: pd.DataFrame, target_column: str,
                           analysis_result: Dict[str, Any]) -> go.Figure:
        """
        创建异常检测图表
        
        Args:
            df: 数据DataFrame
            target_column: 目标列名
            analysis_result: 异常检测结果
            
        Returns:
            Plotly图表对象
        """
        try:
            data = df[target_column].dropna()
            anomaly_indices = analysis_result.get('anomaly_indices', [])
            anomaly_values = analysis_result.get('anomaly_values', [])
            
            # 创建图表
            fig = go.Figure()
            
            # 正常数据点
            normal_mask = ~data.index.isin(anomaly_indices)
            normal_data = data[normal_mask]
            
            fig.add_trace(
                go.Scatter(
                    x=normal_data.index,
                    y=normal_data.values,
                    mode='markers',
                    name='正常数据',
                    marker=dict(color=self.colors['primary'], size=6)
                )
            )
            
            # 异常数据点
            if anomaly_indices:
                fig.add_trace(
                    go.Scatter(
                        x=anomaly_indices,
                        y=anomaly_values,
                        mode='markers',
                        name='异常数据',
                        marker=dict(color=self.colors['warning'], size=10, symbol='x')
                    )
                )
            
            # 添加统计信息
            stats = analysis_result.get('anomaly_stats', {})
            if stats:
                fig.add_annotation(
                    x=0.02, y=0.98,
                    xref='paper', yref='paper',
                    text=f"总数据点: {stats.get('total_points', 0)}<br>"
                         f"异常点: {stats.get('anomaly_count', 0)}<br>"
                         f"异常比例: {stats.get('anomaly_percentage', 0):.2f}%",
                    showarrow=False,
                    bgcolor='rgba(255,255,255,0.8)',
                    bordercolor='black',
                    borderwidth=1
                )
            
            # 更新布局
            fig.update_layout(
                title=f'{target_column} 异常检测结果 (方法: {analysis_result.get("method", "unknown")})',
                xaxis_title='数据点索引',
                yaxis_title=target_column,
                height=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建异常检测图表失败: {e}")
            raise
    
    def create_correlation_matrix(self, df: pd.DataFrame, numeric_columns: List[str] = None) -> go.Figure:
        """
        创建相关性矩阵图表
        
        Args:
            df: 数据DataFrame
            numeric_columns: 数值列名列表
            
        Returns:
            Plotly图表对象
        """
        try:
            if numeric_columns is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_columns) < 2:
                raise ValueError("需要至少两个数值列来计算相关性")
            
            # 计算相关性矩阵
            corr_matrix = df[numeric_columns].corr()
            
            # 创建热力图
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.round(3).values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title='相关性矩阵',
                height=600,
                width=600
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建相关性矩阵失败: {e}")
            raise
    
    def create_summary_dashboard(self, kpi_data: Dict[str, pd.DataFrame], 
                               analysis_results: Dict[str, Dict[str, Any]]) -> go.Figure:
        """
        创建KPI摘要仪表板
        
        Args:
            kpi_data: KPI数据字典
            analysis_results: 分析结果字典
            
        Returns:
            Plotly图表对象
        """
        try:
            n_kpis = len(kpi_data)
            if n_kpis == 0:
                raise ValueError("没有KPI数据")
            
            # 创建子图布局
            fig = make_subplots(
                rows=n_kpis, cols=2,
                subplot_titles=[f"{kpi_name} - 趋势" for kpi_name in kpi_data.keys()] +
                              [f"{kpi_name} - 分布" for kpi_name in kpi_data.keys()],
                specs=[[{"type": "scatter"}, {"type": "histogram"}] for _ in range(n_kpis)]
            )
            
            for i, (kpi_name, df) in enumerate(kpi_data.items(), 1):
                # 趋势图
                if len(df) > 1:
                    # 尝试找到日期列
                    date_col = None
                    for col in df.columns:
                        if df[col].dtype == 'datetime64[ns]':
                            date_col = col
                            break
                    
                    if date_col:
                        value_col = df.select_dtypes(include=[np.number]).columns[0]
                        df_sorted = df.sort_values(date_col)
                        
                        fig.add_trace(
                            go.Scatter(
                                x=df_sorted[date_col],
                                y=df_sorted[value_col],
                                mode='lines+markers',
                                name=f'{kpi_name} 趋势',
                                line=dict(color=self.colors['primary'])
                            ),
                            row=i, col=1
                        )
                
                # 分布图
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    value_col = numeric_cols[0]
                    fig.add_trace(
                        go.Histogram(
                            x=df[value_col],
                            name=f'{kpi_name} 分布',
                            marker_color=self.colors['secondary'],
                            opacity=0.7
                        ),
                        row=i, col=2
                    )
            
            fig.update_layout(
                title='KPI指标摘要仪表板',
                height=300 * n_kpis,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"创建摘要仪表板失败: {e}")
            raise
    
    def save_chart(self, fig: go.Figure, filepath: str, format: str = 'html'):
        """
        保存图表
        
        Args:
            fig: Plotly图表对象
            filepath: 文件路径
            format: 文件格式 ('html', 'png', 'jpg', 'svg', 'pdf')
        """
        try:
            if format == 'html':
                fig.write_html(filepath)
            elif format in ['png', 'jpg', 'svg', 'pdf']:
                fig.write_image(filepath)
            else:
                raise ValueError(f"不支持的文件格式: {format}")
            
            logger.info(f"图表已保存到: {filepath}")
            
        except Exception as e:
            logger.error(f"保存图表失败: {e}")
            raise
