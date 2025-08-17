"""
ClickHouse数据库连接器
支持从ClickHouse数据库读取KPI数据进行指标分析和数据挖掘
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union
import clickhouse_connect
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
import warnings
from loguru import logger


class ClickHouseConnector:
    """ClickHouse数据库连接器"""
    
    def __init__(self, 
                 host: str = 'localhost',
                 port: int = 8123,
                 username: str = 'default',
                 password: str = '',
                 database: str = 'default',
                 secure: bool = False,
                 verify: bool = True,
                 **kwargs):
        """
        初始化ClickHouse连接器
        
        Args:
            host: ClickHouse服务器地址
            port: ClickHouse端口
            username: 用户名
            password: 密码
            database: 数据库名
            secure: 是否使用SSL连接
            verify: 是否验证SSL证书
            **kwargs: 其他连接参数
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.secure = secure
        self.verify = verify
        self.kwargs = kwargs
        
        self.client = None
        self.engine = None
        self._connect()
    
    def _connect(self):
        """建立数据库连接"""
        try:
            # 使用clickhouse-connect客户端
            self.client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                database=self.database,
                secure=self.secure,
                verify=self.verify,
                **self.kwargs
            )
            
            # 使用SQLAlchemy引擎（用于复杂查询）
            connection_string = f"clickhouse+clickhouse-connect://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
            self.engine = create_engine(connection_string)
            
            logger.info(f"成功连接到ClickHouse数据库: {self.host}:{self.port}/{self.database}")
            
        except Exception as e:
            logger.error(f"连接ClickHouse数据库失败: {e}")
            raise
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            result = self.client.query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_databases(self) -> List[str]:
        """获取所有数据库列表"""
        try:
            result = self.client.query("SHOW DATABASES")
            return [row[0] for row in result.result_rows]
        except Exception as e:
            logger.error(f"获取数据库列表失败: {e}")
            return []
    
    def get_tables(self, database: Optional[str] = None) -> List[str]:
        """获取指定数据库的所有表"""
        try:
            db = database or self.database
            result = self.client.query(f"SHOW TABLES FROM {db}")
            return [row[0] for row in result.result_rows]
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def get_table_schema(self, table_name: str, database: Optional[str] = None) -> pd.DataFrame:
        """获取表结构"""
        try:
            db = database or self.database
            result = self.client.query(f"DESCRIBE {db}.{table_name}")
            
            schema_data = []
            for row in result.result_rows:
                schema_data.append({
                    'column_name': row[0],
                    'data_type': row[1],
                    'default_type': row[2],
                    'default_expression': row[3],
                    'comment': row[4],
                    'codec_expression': row[5],
                    'ttl_expression': row[6]
                })
            
            return pd.DataFrame(schema_data)
            
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            return pd.DataFrame()
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """执行SQL查询并返回DataFrame"""
        try:
            result = self.client.query(query)
            df = result.df()
            logger.info(f"查询执行成功，返回 {len(df)} 行数据")
            return df
        except Exception as e:
            logger.error(f"查询执行失败: {e}")
            raise
    
    def get_kpi_data(self, 
                    table_name: str,
                    department_column: str = 'department_name',
                    time_column: str = 'quarter',
                    metric_columns: Optional[List[str]] = None,
                    where_condition: Optional[str] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """
        获取KPI数据
        
        Args:
            table_name: 表名
            department_column: 部门列名
            time_column: 时间列名
            metric_columns: 指标列名列表
            where_condition: WHERE条件
            limit: 限制返回行数
            
        Returns:
            KPI数据DataFrame
        """
        try:
            # 构建查询语句
            select_columns = [department_column, time_column]
            if metric_columns:
                select_columns.extend(metric_columns)
            else:
                # 如果没有指定指标列，获取所有数值列
                schema = self.get_table_schema(table_name)
                numeric_columns = schema[
                    schema['data_type'].str.contains('Int|Float|Decimal', na=False)
                ]['column_name'].tolist()
                select_columns.extend(numeric_columns)
            
            query = f"SELECT {', '.join(select_columns)} FROM {self.database}.{table_name}"
            
            if where_condition:
                query += f" WHERE {where_condition}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            logger.info(f"执行KPI数据查询: {query}")
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"获取KPI数据失败: {e}")
            raise
    
    def get_department_kpi_data(self, 
                               table_name: str,
                               department_name: str,
                               time_column: str = 'quarter',
                               metric_columns: Optional[List[str]] = None,
                               time_range: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        获取特定部门的KPI数据
        
        Args:
            table_name: 表名
            department_name: 部门名称
            time_column: 时间列名
            metric_columns: 指标列名列表
            time_range: 时间范围 {'start': '2025Q1', 'end': '2025Q3'}
            
        Returns:
            部门KPI数据DataFrame
        """
        try:
            where_conditions = [f"department_name = '{department_name}'"]
            
            if time_range:
                if 'start' in time_range:
                    where_conditions.append(f"{time_column} >= '{time_range['start']}'")
                if 'end' in time_range:
                    where_conditions.append(f"{time_column} <= '{time_range['end']}'")
            
            where_clause = " AND ".join(where_conditions)
            
            return self.get_kpi_data(
                table_name=table_name,
                time_column=time_column,
                metric_columns=metric_columns,
                where_condition=where_clause
            )
            
        except Exception as e:
            logger.error(f"获取部门KPI数据失败: {e}")
            raise
    
    def get_metric_trend_data(self, 
                             table_name: str,
                             metric_name: str,
                             time_column: str = 'quarter',
                             department_column: str = 'department_name',
                             group_by_department: bool = True) -> pd.DataFrame:
        """
        获取指标趋势数据
        
        Args:
            table_name: 表名
            metric_name: 指标名称
            time_column: 时间列名
            department_column: 部门列名
            group_by_department: 是否按部门分组
            
        Returns:
            指标趋势数据DataFrame
        """
        try:
            if group_by_department:
                query = f"""
                SELECT 
                    {department_column},
                    {time_column},
                    AVG({metric_name}) as avg_value,
                    MIN({metric_name}) as min_value,
                    MAX({metric_name}) as max_value,
                    COUNT(*) as data_count
                FROM {self.database}.{table_name}
                WHERE {metric_name} IS NOT NULL
                GROUP BY {department_column}, {time_column}
                ORDER BY {department_column}, {time_column}
                """
            else:
                query = f"""
                SELECT 
                    {time_column},
                    AVG({metric_name}) as avg_value,
                    MIN({metric_name}) as min_value,
                    MAX({metric_name}) as max_value,
                    COUNT(*) as data_count
                FROM {self.database}.{table_name}
                WHERE {metric_name} IS NOT NULL
                GROUP BY {time_column}
                ORDER BY {time_column}
                """
            
            logger.info(f"执行指标趋势查询: {query}")
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"获取指标趋势数据失败: {e}")
            raise
    
    def get_anomaly_data(self, 
                        table_name: str,
                        metric_name: str,
                        time_column: str = 'quarter',
                        anomaly_threshold: float = 2.0) -> pd.DataFrame:
        """
        获取异常数据（基于Z-score）
        
        Args:
            table_name: 表名
            metric_name: 指标名称
            time_column: 时间列名
            anomaly_threshold: 异常阈值（Z-score）
            
        Returns:
            异常数据DataFrame
        """
        try:
            query = f"""
            WITH stats AS (
                SELECT 
                    AVG({metric_name}) as mean_value,
                    STDDEV({metric_name}) as std_value
                FROM {self.database}.{table_name}
                WHERE {metric_name} IS NOT NULL
            )
            SELECT 
                t.*,
                (t.{metric_name} - s.mean_value) / s.std_value as z_score
            FROM {self.database}.{table_name} t
            CROSS JOIN stats s
            WHERE t.{metric_name} IS NOT NULL
            AND ABS((t.{metric_name} - s.mean_value) / s.std_value) > {anomaly_threshold}
            ORDER BY ABS((t.{metric_name} - s.mean_value) / s.std_value) DESC
            """
            
            logger.info(f"执行异常数据查询: {query}")
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"获取异常数据失败: {e}")
            raise
    
    def get_correlation_data(self, 
                           table_name: str,
                           metric_columns: List[str],
                           time_column: str = 'quarter',
                           department_column: str = 'department_name') -> pd.DataFrame:
        """
        获取用于相关性分析的数据
        
        Args:
            table_name: 表名
            metric_columns: 指标列名列表
            time_column: 时间列名
            department_column: 部门列名
            
        Returns:
            相关性分析数据DataFrame
        """
        try:
            # 构建查询，按时间和部门聚合指标数据
            select_columns = [department_column, time_column]
            select_columns.extend([f"AVG({col}) as {col}" for col in metric_columns])
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM {self.database}.{table_name}
            WHERE {' AND '.join([f"{col} IS NOT NULL" for col in metric_columns])}
            GROUP BY {department_column}, {time_column}
            ORDER BY {department_column}, {time_column}
            """
            
            logger.info(f"执行相关性数据查询: {query}")
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"获取相关性数据失败: {e}")
            raise
    
    def get_association_data(self, 
                           table_name: str,
                           metric_columns: List[str],
                           time_column: str = 'quarter',
                           department_column: str = 'department_name',
                           sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        获取用于关联关系挖掘的数据
        
        Args:
            table_name: 表名
            metric_columns: 指标列名列表
            time_column: 时间列名
            department_column: 部门列名
            sample_size: 采样大小
            
        Returns:
            关联关系挖掘数据DataFrame
        """
        try:
            # 构建查询，获取完整的指标数据
            select_columns = [department_column, time_column]
            select_columns.extend(metric_columns)
            
            query = f"""
            SELECT {', '.join(select_columns)}
            FROM {self.database}.{table_name}
            WHERE {' AND '.join([f"{col} IS NOT NULL" for col in metric_columns])}
            """
            
            if sample_size:
                query += f" ORDER BY rand() LIMIT {sample_size}"
            else:
                query += f" ORDER BY {department_column}, {time_column}"
            
            logger.info(f"执行关联关系数据查询: {query}")
            return self.execute_query(query)
            
        except Exception as e:
            logger.error(f"获取关联关系数据失败: {e}")
            raise
    
    def get_data_summary(self, table_name: str) -> Dict[str, Any]:
        """获取数据摘要信息"""
        try:
            # 获取表的基本信息
            schema = self.get_table_schema(table_name)
            
            # 获取行数
            count_result = self.client.query(f"SELECT COUNT(*) as total_rows FROM {self.database}.{table_name}")
            total_rows = count_result.result_rows[0][0]
            
            # 获取列数
            total_columns = len(schema)
            
            # 获取数值列
            numeric_columns = schema[
                schema['data_type'].str.contains('Int|Float|Decimal', na=False)
            ]['column_name'].tolist()
            
            # 获取字符串列
            string_columns = schema[
                schema['data_type'].str.contains('String|FixedString', na=False)
            ]['column_name'].tolist()
            
            # 获取日期列
            date_columns = schema[
                schema['data_type'].str.contains('Date|DateTime', na=False)
            ]['column_name'].tolist()
            
            summary = {
                'table_name': table_name,
                'database': self.database,
                'total_rows': total_rows,
                'total_columns': total_columns,
                'numeric_columns': numeric_columns,
                'string_columns': string_columns,
                'date_columns': date_columns,
                'all_columns': schema['column_name'].tolist()
            }
            
            logger.info(f"数据摘要: {summary}")
            return summary
            
        except Exception as e:
            logger.error(f"获取数据摘要失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.client:
                self.client.close()
            if self.engine:
                self.engine.dispose()
            logger.info("ClickHouse数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class ClickHouseKPIAnalyzer:
    """基于ClickHouse的KPI分析器"""
    
    def __init__(self, connector: ClickHouseConnector):
        """
        初始化ClickHouse KPI分析器
        
        Args:
            connector: ClickHouse连接器
        """
        self.connector = connector
    
    def analyze_department_performance(self, 
                                     table_name: str,
                                     department_name: str,
                                     metric_columns: List[str],
                                     time_column: str = 'quarter') -> Dict[str, Any]:
        """
        分析部门绩效
        
        Args:
            table_name: 表名
            department_name: 部门名称
            metric_columns: 指标列名列表
            time_column: 时间列名
            
        Returns:
            部门绩效分析结果
        """
        try:
            # 获取部门数据
            dept_data = self.connector.get_department_kpi_data(
                table_name=table_name,
                department_name=department_name,
                time_column=time_column,
                metric_columns=metric_columns
            )
            
            if dept_data.empty:
                return {'error': f'未找到部门 {department_name} 的数据'}
            
            # 计算基本统计信息
            results = {
                'department_name': department_name,
                'data_points': len(dept_data),
                'time_range': {
                    'start': dept_data[time_column].min(),
                    'end': dept_data[time_column].max()
                },
                'metrics_analysis': {}
            }
            
            # 分析每个指标
            for metric in metric_columns:
                if metric in dept_data.columns:
                    metric_data = dept_data[metric].dropna()
                    if len(metric_data) > 0:
                        results['metrics_analysis'][metric] = {
                            'mean': float(metric_data.mean()),
                            'std': float(metric_data.std()),
                            'min': float(metric_data.min()),
                            'max': float(metric_data.max()),
                            'trend': self._calculate_trend(metric_data),
                            'anomalies': self._detect_anomalies(metric_data)
                        }
            
            return results
            
        except Exception as e:
            logger.error(f"分析部门绩效失败: {e}")
            return {'error': str(e)}
    
    def analyze_metric_correlations(self, 
                                  table_name: str,
                                  metric_columns: List[str],
                                  time_column: str = 'quarter') -> Dict[str, Any]:
        """
        分析指标相关性
        
        Args:
            table_name: 表名
            metric_columns: 指标列名列表
            time_column: 时间列名
            
        Returns:
            相关性分析结果
        """
        try:
            # 获取相关性数据
            corr_data = self.connector.get_correlation_data(
                table_name=table_name,
                metric_columns=metric_columns,
                time_column=time_column
            )
            
            if corr_data.empty:
                return {'error': '未找到有效数据'}
            
            # 计算相关性矩阵
            metric_data = corr_data[metric_columns].dropna()
            correlation_matrix = metric_data.corr()
            
            # 找出强相关性
            strong_correlations = []
            for i in range(len(correlation_matrix.columns)):
                for j in range(i+1, len(correlation_matrix.columns)):
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # 强相关性阈值
                        strong_correlations.append({
                            'metric1': correlation_matrix.columns[i],
                            'metric2': correlation_matrix.columns[j],
                            'correlation': float(corr_value)
                        })
            
            return {
                'correlation_matrix': correlation_matrix.to_dict(),
                'strong_correlations': strong_correlations,
                'data_points': len(metric_data)
            }
            
        except Exception as e:
            logger.error(f"分析指标相关性失败: {e}")
            return {'error': str(e)}
    
    def _calculate_trend(self, data: pd.Series) -> str:
        """计算趋势"""
        if len(data) < 2:
            return 'insufficient_data'
        
        # 简单线性回归
        x = np.arange(len(data))
        y = data.values
        
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.05:
            return 'increasing'
        elif slope < -0.05:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_anomalies(self, data: pd.Series, threshold: float = 2.0) -> List[int]:
        """检测异常值"""
        if len(data) < 3:
            return []
        
        mean = data.mean()
        std = data.std()
        
        if std == 0:
            return []
        
        z_scores = np.abs((data - mean) / std)
        anomalies = z_scores > threshold
        
        return data[anomalies].index.tolist()
