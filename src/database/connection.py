"""
ClickHouse数据库连接模块
"""
import yaml
import os
from typing import Dict, Any, Optional
from clickhouse_driver import Client
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from loguru import logger


class ClickHouseConnector:
    """ClickHouse数据库连接器"""
    
    def __init__(self, config_path: str = "config/database.yaml"):
        """
        初始化数据库连接器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.client = None
        self.engine = None
        self._connect()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载数据库配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('clickhouse', {})
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'host': 'localhost',
            'port': 9000,
            'database': 'analytics',
            'user': 'default',
            'password': '',
            'connect_timeout': 10,
            'send_receive_timeout': 30,
            'compression': True
        }
    
    def _connect(self):
        """建立数据库连接"""
        try:
            # 创建ClickHouse客户端连接
            self.client = Client(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password'],
                connect_timeout=self.config.get('connect_timeout', 10),
                send_receive_timeout=self.config.get('send_receive_timeout', 30),
                compression=self.config.get('compression', True)
            )
            
            # 创建SQLAlchemy引擎（用于pandas集成）
            connection_string = (
                f"clickhouse://{self.config['user']}:{self.config['password']}"
                f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
            )
            self.engine = create_engine(connection_string)
            
            logger.info(f"成功连接到ClickHouse数据库: {self.config['host']}:{self.config['port']}")
            
        except Exception as e:
            logger.error(f"连接ClickHouse数据库失败: {e}")
            raise
    
    def execute_query(self, sql: str, params: Optional[Dict] = None) -> Any:
        """
        执行SQL查询
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果
        """
        try:
            if params:
                result = self.client.execute(sql, params)
            else:
                result = self.client.execute(sql)
            
            logger.debug(f"执行SQL查询: {sql[:100]}...")
            return result
            
        except Exception as e:
            logger.error(f"执行SQL查询失败: {e}")
            logger.error(f"SQL: {sql}")
            raise
    
    def execute_query_pandas(self, sql: str, params: Optional[Dict] = None):
        """
        执行SQL查询并返回pandas DataFrame
        
        Args:
            sql: SQL查询语句
            params: 查询参数
            
        Returns:
            pandas DataFrame
        """
        try:
            import pandas as pd
            
            if params:
                # 替换SQL中的参数占位符
                for key, value in params.items():
                    sql = sql.replace(f":{key}", str(value))
            
            df = pd.read_sql(sql, self.engine)
            logger.debug(f"执行SQL查询并返回DataFrame，行数: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"执行SQL查询并返回DataFrame失败: {e}")
            logger.error(f"SQL: {sql}")
            raise
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        Returns:
            连接是否成功
        """
        try:
            result = self.execute_query("SELECT 1")
            return result[0][0] == 1
        except Exception as e:
            logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息
        
        Args:
            table_name: 表名
            
        Returns:
            表信息字典
        """
        try:
            sql = f"DESCRIBE {table_name}"
            result = self.execute_query(sql)
            
            columns = []
            for row in result:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'default': row[2],
                    'compression': row[3],
                    'ttl': row[4]
                })
            
            return {
                'table_name': table_name,
                'columns': columns
            }
            
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        try:
            if self.client:
                self.client.disconnect()
            if self.engine:
                self.engine.dispose()
            logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
