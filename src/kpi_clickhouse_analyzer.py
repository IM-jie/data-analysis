"""
集成了ClickHouse数据库功能的KPI分析器
支持从ClickHouse数据库读取数据进行指标分析和数据挖掘
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
import argparse
import yaml
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.clickhouse_connector import ClickHouseConnector, ClickHouseKPIAnalyzer
from analysis.kpi_association_miner import KPIAssociationMiner, KPIAssociationAnomalyDetector
from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
from visualization.kpi_report_generator import KPIReportGenerator


class KPIClickHouseAnalyzer:
    """集成了ClickHouse数据库功能的KPI分析器"""
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 clickhouse_config: Optional[Dict] = None):
        """
        初始化ClickHouse KPI分析器
        
        Args:
            config_path: 配置文件路径
            clickhouse_config: ClickHouse连接配置
        """
        self.config = self._load_config(config_path)
        self.clickhouse_config = clickhouse_config or self.config.get('clickhouse', {})
        
        # 初始化组件
        self.connector = None
        self.kpi_analyzer = None
        self.association_miner = KPIAssociationMiner(self.config)
        self.association_detector = KPIAssociationAnomalyDetector(self.association_miner)
        self.comprehensive_analyzer = KPIComprehensiveAnalyzer(self.config)
        self.report_generator = KPIReportGenerator()
        
        # 连接ClickHouse数据库
        self._connect_clickhouse()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {config_path}")
                return config
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        # 使用默认配置
        logger.info("使用默认配置")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'clickhouse': {
                'host': 'localhost',
                'port': 18123,
                'username': 'default',
                'password': 'Dxt456789',
                'database': 'default',
                'secure': False
            },
            'analysis': {
                'correlation_threshold': 0.7,
                'anomaly_threshold': 2.0,
                'trend_threshold': 0.05
            },
            'data_mining': {
                'min_support': 0.1,
                'min_confidence': 0.5,
                'min_lift': 1.2,
                'mi_threshold': 0.3
            }
        }
    
    def _connect_clickhouse(self):
        """连接ClickHouse数据库"""
        try:
            self.connector = ClickHouseConnector(**self.clickhouse_config)
            self.kpi_analyzer = ClickHouseKPIAnalyzer(self.connector)
            
            # 测试连接
            if self.connector.test_connection():
                logger.info("ClickHouse数据库连接成功")
            else:
                logger.error("ClickHouse数据库连接失败")
                raise Exception("无法连接到ClickHouse数据库")
                
        except Exception as e:
            logger.error(f"连接ClickHouse数据库失败: {e}")
            raise
    
    def analyze_table(self, 
                     table_name: str,
                     metric_columns: Optional[List[str]] = None,
                     department_column: str = 'department_name',
                     time_column: str = 'quarter') -> Dict[str, Any]:
        """
        分析ClickHouse表中的KPI数据
        
        Args:
            table_name: 表名
            metric_columns: 指标列名列表
            department_column: 部门列名
            time_column: 时间列名
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析表: {table_name}")
            
            # 获取数据摘要
            data_summary = self.connector.get_data_summary(table_name)
            
            # 如果没有指定指标列，使用数值列
            if not metric_columns:
                metric_columns = data_summary.get('numeric_columns', [])
            
            # 获取KPI数据
            kpi_data = self.connector.get_kpi_data(
                table_name=table_name,
                department_column=department_column,
                time_column=time_column,
                metric_columns=metric_columns
            )
            
            if kpi_data.empty:
                return {'error': '未找到有效数据'}
            
            # 进行综合分析
            analysis_results = self.comprehensive_analyzer.analyze_kpi_data(
                data=kpi_data,
                department_column=department_column,
                metric_columns=metric_columns,
                time_columns=[time_column]
            )
            
            # 进行关联关系挖掘
            logger.info("开始关联关系挖掘...")
            association_results = self.association_miner.discover_associations(
                data=kpi_data,
                metric_columns=metric_columns
            )
            
            # 构建关联关系基线
            logger.info("构建关联关系基线...")
            baseline_results = self.association_detector.build_baseline(
                data=kpi_data,
                metric_columns=metric_columns
            )
            
            # 生成报告
            report_path = self.report_generator.generate_comprehensive_report(
                data=kpi_data,
                analysis_results=analysis_results,
                report_title=f"ClickHouse KPI数据分析报告 - {table_name}"
            )
            
            return {
                'table_name': table_name,
                'data_summary': data_summary,
                'analysis_results': analysis_results,
                'association_results': association_results,
                'baseline_results': baseline_results,
                'report_path': report_path,
                'data_shape': kpi_data.shape
            }
            
        except Exception as e:
            logger.error(f"分析表 {table_name} 失败: {e}")
            return {'error': str(e)}
    
    def analyze_department(self, 
                          table_name: str,
                          department_name: str,
                          metric_columns: Optional[List[str]] = None,
                          time_column: str = 'quarter') -> Dict[str, Any]:
        """
        分析特定部门的KPI数据
        
        Args:
            table_name: 表名
            department_name: 部门名称
            metric_columns: 指标列名列表
            time_column: 时间列名
            
        Returns:
            部门分析结果
        """
        try:
            logger.info(f"开始分析部门: {department_name}")
            
            # 使用ClickHouse KPI分析器
            results = self.kpi_analyzer.analyze_department_performance(
                table_name=table_name,
                department_name=department_name,
                metric_columns=metric_columns or [],
                time_column=time_column
            )
            
            if 'error' in results:
                return results
            
            # 获取部门趋势数据
            trend_data = {}
            for metric in results['metrics_analysis'].keys():
                trend_df = self.connector.get_metric_trend_data(
                    table_name=table_name,
                    metric_name=metric,
                    time_column=time_column,
                    group_by_department=False
                )
                trend_data[metric] = trend_df
            
            results['trend_data'] = trend_data
            
            return results
            
        except Exception as e:
            logger.error(f"分析部门 {department_name} 失败: {e}")
            return {'error': str(e)}
    
    def analyze_correlations(self, 
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
            logger.info(f"开始分析指标相关性: {metric_columns}")
            
            # 使用ClickHouse KPI分析器
            results = self.kpi_analyzer.analyze_metric_correlations(
                table_name=table_name,
                metric_columns=metric_columns,
                time_column=time_column
            )
            
            return results
            
        except Exception as e:
            logger.error(f"分析指标相关性失败: {e}")
            return {'error': str(e)}
    
    def analyze_associations(self, 
                           table_name: str,
                           metric_columns: List[str],
                           time_column: str = 'quarter',
                           department_column: str = 'department_name') -> Dict[str, Any]:
        """
        进行关联关系挖掘
        
        Args:
            table_name: 表名
            metric_columns: 指标列名列表
            time_column: 时间列名
            department_column: 部门列名
            
        Returns:
            关联关系挖掘结果
        """
        try:
            logger.info(f"开始关联关系挖掘: {metric_columns}")
            
            # 获取关联关系数据
            association_data = self.connector.get_association_data(
                table_name=table_name,
                metric_columns=metric_columns,
                time_column=time_column,
                department_column=department_column
            )
            
            if association_data.empty:
                return {'error': '未找到有效数据'}
            
            # 进行关联关系挖掘
            association_results = self.association_miner.discover_associations(
                data=association_data,
                metric_columns=metric_columns
            )
            
            # 构建基线
            baseline_results = self.association_detector.build_baseline(
                data=association_data,
                metric_columns=metric_columns
            )
            
            return {
                'association_results': association_results,
                'baseline_results': baseline_results,
                'data_shape': association_data.shape
            }
            
        except Exception as e:
            logger.error(f"关联关系挖掘失败: {e}")
            return {'error': str(e)}
    
    def detect_anomalies(self, 
                        table_name: str,
                        metric_name: str,
                        time_column: str = 'quarter',
                        anomaly_threshold: float = 2.0) -> Dict[str, Any]:
        """
        检测异常数据
        
        Args:
            table_name: 表名
            metric_name: 指标名称
            time_column: 时间列名
            anomaly_threshold: 异常阈值
            
        Returns:
            异常检测结果
        """
        try:
            logger.info(f"开始检测异常: {metric_name}")
            
            # 获取异常数据
            anomaly_data = self.connector.get_anomaly_data(
                table_name=table_name,
                metric_name=metric_name,
                time_column=time_column,
                anomaly_threshold=anomaly_threshold
            )
            
            return {
                'metric_name': metric_name,
                'anomaly_count': len(anomaly_data),
                'anomaly_data': anomaly_data.to_dict('records'),
                'threshold': anomaly_threshold
            }
            
        except Exception as e:
            logger.error(f"检测异常失败: {e}")
            return {'error': str(e)}
    
    def get_available_tables(self) -> List[str]:
        """获取可用的表列表"""
        try:
            return self.connector.get_tables()
        except Exception as e:
            logger.error(f"获取表列表失败: {e}")
            return []
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """获取表信息"""
        try:
            schema = self.connector.get_table_schema(table_name)
            summary = self.connector.get_data_summary(table_name)
            
            return {
                'table_name': table_name,
                'schema': schema.to_dict('records'),
                'summary': summary
            }
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return {'error': str(e)}
    
    def export_to_excel(self, 
                       table_name: str,
                       output_file: str,
                       metric_columns: Optional[List[str]] = None,
                       limit: Optional[int] = None) -> str:
        """
        导出数据到Excel文件
        
        Args:
            table_name: 表名
            output_file: 输出文件路径
            metric_columns: 指标列名列表
            limit: 限制行数
            
        Returns:
            输出文件路径
        """
        try:
            logger.info(f"开始导出数据到Excel: {output_file}")
            
            # 获取数据
            data = self.connector.get_kpi_data(
                table_name=table_name,
                metric_columns=metric_columns,
                limit=limit
            )
            
            # 导出到Excel
            data.to_excel(output_file, index=False)
            
            logger.info(f"数据导出成功: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"导出数据失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connector:
            self.connector.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ClickHouse KPI数据分析工具')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--table', help='要分析的表名')
    parser.add_argument('--department', help='要分析的部门名')
    parser.add_argument('--metrics', nargs='+', help='要分析的指标列名')
    parser.add_argument('--time-column', default='quarter', help='时间列名')
    parser.add_argument('--department-column', default='department_name', help='部门列名')
    parser.add_argument('--action', choices=['analyze', 'correlations', 'associations', 'anomalies', 'export', 'list-tables'], 
                       default='analyze', help='执行的操作')
    parser.add_argument('--output', help='输出文件路径')
    parser.add_argument('--limit', type=int, help='限制数据行数')
    
    args = parser.parse_args()
    
    try:
        # 初始化分析器
        analyzer = KPIClickHouseAnalyzer(args.config)
        
        if args.action == 'list-tables':
            # 列出可用表
            tables = analyzer.get_available_tables()
            print("可用表列表:")
            for table in tables:
                print(f"  - {table}")
        
        elif args.action == 'analyze':
            if not args.table:
                parser.error("分析操作需要指定表名")
            
            if args.department:
                # 分析特定部门
                results = analyzer.analyze_department(
                    table_name=args.table,
                    department_name=args.department,
                    metric_columns=args.metrics,
                    time_column=args.time_column
                )
            else:
                # 分析整个表
                results = analyzer.analyze_table(
                    table_name=args.table,
                    metric_columns=args.metrics,
                    department_column=args.department_column,
                    time_column=args.time_column
                )
            
            print("分析结果:")
            print(f"  表名: {args.table}")
            if 'error' not in results:
                print(f"  数据形状: {results.get('data_shape', 'N/A')}")
                print(f"  报告路径: {results.get('report_path', 'N/A')}")
            else:
                print(f"  错误: {results['error']}")
        
        elif args.action == 'correlations':
            if not args.table or not args.metrics:
                parser.error("相关性分析需要指定表名和指标列")
            
            results = analyzer.analyze_correlations(
                table_name=args.table,
                metric_columns=args.metrics,
                time_column=args.time_column
            )
            
            print("相关性分析结果:")
            if 'error' not in results:
                strong_corrs = results.get('strong_correlations', [])
                print(f"  强相关性关系数量: {len(strong_corrs)}")
                for corr in strong_corrs[:5]:  # 显示前5个
                    print(f"    {corr['metric1']} <-> {corr['metric2']}: {corr['correlation']:.3f}")
            else:
                print(f"  错误: {results['error']}")
        
        elif args.action == 'associations':
            if not args.table or not args.metrics:
                parser.error("关联关系分析需要指定表名和指标列")
            
            results = analyzer.analyze_associations(
                table_name=args.table,
                metric_columns=args.metrics,
                time_column=args.time_column,
                department_column=args.department_column
            )
            
            print("关联关系分析结果:")
            if 'error' not in results:
                association_results = results.get('association_results', {})
                summary = association_results.get('summary', {})
                print(f"  强相关性关系: {summary.get('total_strong_correlations', 0)}")
                print(f"  强互信息关系: {summary.get('total_strong_mi_relationships', 0)}")
                print(f"  因果关系链: {summary.get('total_causal_chains', 0)}")
            else:
                print(f"  错误: {results['error']}")
        
        elif args.action == 'anomalies':
            if not args.table or not args.metrics:
                parser.error("异常检测需要指定表名和指标列")
            
            for metric in args.metrics:
                results = analyzer.detect_anomalies(
                    table_name=args.table,
                    metric_name=metric,
                    time_column=args.time_column
                )
                
                print(f"异常检测结果 - {metric}:")
                if 'error' not in results:
                    print(f"  异常数量: {results.get('anomaly_count', 0)}")
                else:
                    print(f"  错误: {results['error']}")
        
        elif args.action == 'export':
            if not args.table or not args.output:
                parser.error("导出操作需要指定表名和输出文件路径")
            
            output_file = analyzer.export_to_excel(
                table_name=args.table,
                output_file=args.output,
                metric_columns=args.metrics,
                limit=args.limit
            )
            
            print(f"数据导出成功: {output_file}")
        
        # 关闭连接
        analyzer.close()
        
    except Exception as e:
        logger.error(f"执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
