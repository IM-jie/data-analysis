"""
Excel KPI数据读取器
支持读取部门KPI数据，包含季度、部门名称和多个指标列
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import re
from loguru import logger
from pathlib import Path


class ExcelKPIReader:
    """Excel KPI数据读取器"""
    
    def __init__(self, file_path: str):
        """
        初始化Excel读取器
        
        Args:
            file_path: Excel文件路径
        """
        self.file_path = Path(file_path)
        self.data = None
        self.quarter_columns = []
        self.department_column = None
        self.metric_columns = []
        
    def read_excel(self, sheet_name: Optional[str] = None) -> pd.DataFrame:
        """
        读取Excel文件
        
        Args:
            sheet_name: 工作表名称，如果为None则读取第一个工作表
            
        Returns:
            读取的数据DataFrame
        """
        try:
            if sheet_name:
                self.data = pd.read_excel(self.file_path, sheet_name=sheet_name)
            else:
                self.data = pd.read_excel(self.file_path)
            
            logger.info(f"成功读取Excel文件: {self.file_path}")
            logger.info(f"数据形状: {self.data.shape}")
            logger.info(f"列名: {list(self.data.columns)}")
            
            return self.data
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
    
    def detect_columns(self) -> Dict[str, List[str]]:
        """
        自动检测列类型
        
        Returns:
            包含列分类的字典
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        columns = list(self.data.columns)
        
        # 检测季度列（格式如2025q3, 2025Q3等）
        quarter_pattern = r'^\d{4}[qQ][1-4]$'
        self.quarter_columns = [col for col in columns if re.match(quarter_pattern, col)]
        
        # 检测部门名称列（通常包含"部门"、"部门名称"等关键词）
        department_keywords = ['部门', '部门名称', 'dept', 'department', '组织', '团队']
        self.department_column = None
        for col in columns:
            if any(keyword in str(col).lower() for keyword in department_keywords):
                self.department_column = col
                break
        
        # 如果没找到部门列，假设第一列是部门名称
        if self.department_column is None and len(columns) > 0:
            self.department_column = columns[0]
        
        # 其他列作为指标列
        self.metric_columns = [
            col for col in columns 
            if col not in self.quarter_columns and col != self.department_column
        ]
        
        result = {
            'quarter_columns': self.quarter_columns,
            'department_column': self.department_column,
            'metric_columns': self.metric_columns
        }
        
        logger.info(f"检测到的列分类: {result}")
        return result
    
    def reshape_data(self) -> pd.DataFrame:
        """
        将宽格式数据重塑为长格式，便于分析
        
        Returns:
            重塑后的数据DataFrame
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        if not self.quarter_columns:
            raise ValueError("未检测到季度列")
        
        # 使用melt将宽格式转换为长格式
        id_vars = [self.department_column] if self.department_column else []
        value_vars = self.quarter_columns + self.metric_columns
        
        melted_data = self.data.melt(
            id_vars=id_vars,
            value_vars=value_vars,
            var_name='quarter',
            value_name='value'
        )
        
        # 分离季度列和指标列
        melted_data['metric_type'] = 'quarter'
        melted_data.loc[melted_data['quarter'].isin(self.metric_columns), 'metric_type'] = 'metric'
        
        # 处理季度信息
        melted_data['year'] = None
        melted_data['quarter_num'] = None
        
        for idx, row in melted_data.iterrows():
            quarter = str(row['quarter'])
            if re.match(r'^\d{4}[qQ][1-4]$', quarter):
                year = quarter[:4]
                q_num = quarter[-1]
                melted_data.at[idx, 'year'] = int(year)
                melted_data.at[idx, 'quarter_num'] = int(q_num)
        
        logger.info(f"数据重塑完成，形状: {melted_data.shape}")
        return melted_data
    
    def get_metric_data(self, metric_name: str) -> pd.DataFrame:
        """
        获取特定指标的数据
        
        Args:
            metric_name: 指标名称
            
        Returns:
            该指标的数据DataFrame
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        if metric_name not in self.metric_columns:
            raise ValueError(f"指标 {metric_name} 不存在")
        
        # 选择部门列和该指标的所有季度数据
        columns_to_select = [self.department_column, metric_name] + self.quarter_columns
        metric_data = self.data[columns_to_select].copy()
        
        # 重命名指标列为'value'
        metric_data = metric_data.rename(columns={metric_name: 'value'})
        
        return metric_data
    
    def get_department_data(self, department_name: str) -> pd.DataFrame:
        """
        获取特定部门的数据
        
        Args:
            department_name: 部门名称
            
        Returns:
            该部门的数据DataFrame
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        if self.department_column is None:
            raise ValueError("未检测到部门列")
        
        dept_data = self.data[self.data[self.department_column] == department_name].copy()
        
        if dept_data.empty:
            raise ValueError(f"未找到部门: {department_name}")
        
        return dept_data
    
    def get_summary_stats(self) -> Dict:
        """
        获取数据摘要统计
        
        Returns:
            数据摘要统计字典
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        summary = {
            'total_departments': len(self.data),
            'total_metrics': len(self.metric_columns),
            'quarters': self.quarter_columns,
            'metrics': self.metric_columns,
            'department_column': self.department_column,
            'data_shape': self.data.shape
        }
        
        # 统计每个指标的基本信息
        metric_stats = {}
        for metric in self.metric_columns:
            metric_data = self.data[metric].dropna()
            if len(metric_data) > 0:
                metric_stats[metric] = {
                    'count': len(metric_data),
                    'mean': float(metric_data.mean()),
                    'std': float(metric_data.std()),
                    'min': float(metric_data.min()),
                    'max': float(metric_data.max()),
                    'missing_count': self.data[metric].isna().sum()
                }
        
        summary['metric_stats'] = metric_stats
        return summary
    
    def validate_data(self) -> Dict[str, List[str]]:
        """
        验证数据质量
        
        Returns:
            包含验证结果的字典
        """
        if self.data is None:
            raise ValueError("请先读取Excel文件")
        
        issues = {
            'missing_values': [],
            'invalid_values': [],
            'duplicates': []
        }
        
        # 检查缺失值
        for col in self.data.columns:
            missing_count = self.data[col].isna().sum()
            if missing_count > 0:
                issues['missing_values'].append(f"{col}: {missing_count}个缺失值")
        
        # 检查重复行
        duplicate_count = self.data.duplicated().sum()
        if duplicate_count > 0:
            issues['duplicates'].append(f"发现{duplicate_count}行重复数据")
        
        # 检查数值列的有效性
        for col in self.metric_columns:
            if pd.api.types.is_numeric_dtype(self.data[col]):
                # 检查是否有无穷大或NaN值
                invalid_mask = ~np.isfinite(self.data[col])
                invalid_count = invalid_mask.sum()
                if invalid_count > 0:
                    issues['invalid_values'].append(f"{col}: {invalid_count}个无效值")
        
        return issues


def create_sample_excel(file_path: str = "sample_kpi_data.xlsx"):
    """
    创建示例Excel文件用于测试
    
    Args:
        file_path: 输出文件路径
    """
    # 创建示例数据
    departments = ['技术部', '产品部', '运营部', '市场部', '销售部', '人事部']
    metrics = ['在编人数', '执行用例数', '自动化执行用例数', '代码覆盖率', 'bug修复率', '项目交付率']
    quarters = ['2025Q1', '2025Q2', '2025Q3']
    
    data = []
    for dept in departments:
        row = {'部门名称': dept}
        
        # 为每个指标生成季度数据
        for metric in metrics:
            for quarter in quarters:
                # 生成合理的随机数据
                if '人数' in metric:
                    value = np.random.randint(10, 100)
                elif '用例' in metric:
                    value = np.random.randint(100, 1000)
                elif '率' in metric:
                    value = np.random.uniform(0.6, 0.95)
                else:
                    value = np.random.uniform(50, 200)
                
                row[f"{quarter}_{metric}"] = round(value, 2)
        
        data.append(row)
    
    df = pd.DataFrame(data)
    
    # 保存到Excel
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='KPI数据', index=False)
    
    logger.info(f"示例Excel文件已创建: {file_path}")
    return file_path
