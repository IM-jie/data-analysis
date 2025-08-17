"""
KPI指标计算模块
"""
import os
import yaml
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from loguru import logger
from ..database.connection import ClickHouseConnector


class KPICalculator:
    """KPI指标计算器"""
    
    def __init__(self, connector: ClickHouseConnector, config_path: str = "config/kpi_config.yaml"):
        """
        初始化KPI计算器
        
        Args:
            connector: 数据库连接器
            config_path: KPI配置文件路径
        """
        self.connector = connector
        self.config = self._load_config(config_path)
        self.sql_dir = "sql"
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载KPI配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.error(f"KPI配置文件不存在: {config_path}")
            raise
        except Exception as e:
            logger.error(f"加载KPI配置文件失败: {e}")
            raise
    
    def _load_sql_file(self, sql_file: str) -> str:
        """加载SQL文件内容"""
        sql_path = os.path.join(self.sql_dir, sql_file)
        try:
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            return sql_content
        except FileNotFoundError:
            logger.error(f"SQL文件不存在: {sql_path}")
            raise
        except Exception as e:
            logger.error(f"读取SQL文件失败: {e}")
            raise
    
    def get_available_kpis(self) -> List[str]:
        """
        获取可用的KPI指标列表
        
        Returns:
            KPI指标名称列表
        """
        return list(self.config.get('kpi_metrics', {}).keys())
    
    def get_kpi_config(self, kpi_name: str) -> Dict[str, Any]:
        """
        获取KPI配置信息
        
        Args:
            kpi_name: KPI指标名称
            
        Returns:
            KPI配置字典
        """
        kpi_metrics = self.config.get('kpi_metrics', {})
        if kpi_name not in kpi_metrics:
            raise ValueError(f"KPI指标 '{kpi_name}' 不存在")
        return kpi_metrics[kpi_name]
    
    def calculate_kpi(self, kpi_name: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        计算KPI指标
        
        Args:
            kpi_name: KPI指标名称
            params: 查询参数
            
        Returns:
            包含KPI数据的DataFrame
        """
        try:
            # 获取KPI配置
            kpi_config = self.get_kpi_config(kpi_name)
            sql_file = kpi_config['sql_file']
            
            # 加载SQL文件
            sql = self._load_sql_file(sql_file)
            
            # 设置默认参数
            if params is None:
                params = {}
            
            # 添加默认时间参数
            if 'start_date' not in params:
                params['start_date'] = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if 'end_date' not in params:
                params['end_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # 执行查询
            df = self.connector.execute_query_pandas(sql, params)
            
            # 添加KPI元数据
            df.attrs['kpi_name'] = kpi_name
            df.attrs['kpi_config'] = kpi_config
            df.attrs['calculation_time'] = datetime.now()
            
            logger.info(f"成功计算KPI指标: {kpi_name}, 数据行数: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"计算KPI指标失败: {kpi_name}, 错误: {e}")
            raise
    
    def calculate_multiple_kpis(self, kpi_names: List[str], params: Optional[Dict[str, Any]] = None) -> Dict[str, pd.DataFrame]:
        """
        计算多个KPI指标
        
        Args:
            kpi_names: KPI指标名称列表
            params: 查询参数
            
        Returns:
            KPI名称到DataFrame的映射
        """
        results = {}
        for kpi_name in kpi_names:
            try:
                results[kpi_name] = self.calculate_kpi(kpi_name, params)
            except Exception as e:
                logger.error(f"计算KPI指标失败: {kpi_name}, 错误: {e}")
                continue
        
        return results
    
    def validate_kpi_data(self, df: pd.DataFrame, kpi_name: str) -> Dict[str, Any]:
        """
        验证KPI数据质量
        
        Args:
            df: KPI数据DataFrame
            kpi_name: KPI指标名称
            
        Returns:
            验证结果字典
        """
        kpi_config = self.get_kpi_config(kpi_name)
        validation_result = {
            'kpi_name': kpi_name,
            'total_rows': len(df),
            'null_count': df.isnull().sum().to_dict(),
            'duplicate_count': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict(),
            'value_range': {},
            'threshold_check': {}
        }
        
        # 检查数值范围
        numeric_columns = df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            validation_result['value_range'][col] = {
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'std': df[col].std()
            }
        
        # 检查阈值
        thresholds = kpi_config.get('threshold', {})
        for threshold_type, threshold_value in thresholds.items():
            if len(numeric_columns) > 0:
                main_col = numeric_columns[0]  # 假设第一个数值列是主要指标
                if threshold_type == 'warning':
                    validation_result['threshold_check']['warning'] = df[main_col] < threshold_value
                elif threshold_type == 'critical':
                    validation_result['threshold_check']['critical'] = df[main_col] < threshold_value
        
        return validation_result
    
    def get_kpi_summary(self, df: pd.DataFrame, kpi_name: str) -> Dict[str, Any]:
        """
        获取KPI数据摘要
        
        Args:
            df: KPI数据DataFrame
            kpi_name: KPI指标名称
            
        Returns:
            KPI摘要信息
        """
        kpi_config = self.get_kpi_config(kpi_name)
        
        summary = {
            'kpi_name': kpi_name,
            'description': kpi_config.get('description', ''),
            'unit': kpi_config.get('unit', ''),
            'data_type': kpi_config.get('data_type', ''),
            'total_records': len(df),
            'date_range': {},
            'statistics': {}
        }
        
        # 获取日期范围
        date_columns = df.select_dtypes(include=['datetime64']).columns
        if len(date_columns) > 0:
            date_col = date_columns[0]
            summary['date_range'] = {
                'start_date': df[date_col].min(),
                'end_date': df[date_col].max(),
                'total_days': (df[date_col].max() - df[date_col].min()).days
            }
        
        # 获取数值统计
        numeric_columns = df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            summary['statistics'][col] = {
                'count': df[col].count(),
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max(),
                'median': df[col].median(),
                'q25': df[col].quantile(0.25),
                'q75': df[col].quantile(0.75)
            }
        
        return summary
