"""
数据分析项目主程序
"""
import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import yaml

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.connection import ClickHouseConnector
from src.kpi.calculator import KPICalculator
from src.analysis.analyzer import DataAnalyzer
from src.visualization.charts import ChartGenerator
from src.utils.logger import setup_logger, get_logger


class DataAnalysisPipeline:
    """数据分析流水线"""
    
    def __init__(self, config_path: str = "config/kpi_config.yaml"):
        """
        初始化数据分析流水线
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.logger = get_logger("DataAnalysisPipeline")
        
        # 初始化组件
        self.connector = None
        self.calculator = None
        self.analyzer = None
        self.chart_generator = None
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化组件
        self._initialize_components()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            raise
    
    def _initialize_components(self):
        """初始化各个组件"""
        try:
            # 初始化数据库连接
            self.connector = ClickHouseConnector()
            
            # 初始化KPI计算器
            self.calculator = KPICalculator(self.connector, self.config_path)
            
            # 初始化数据分析器
            analysis_config = self.config.get('analysis_config', {})
            self.analyzer = DataAnalyzer(analysis_config)
            
            # 初始化图表生成器
            self.chart_generator = ChartGenerator()
            
            self.logger.info("所有组件初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化组件失败: {e}")
            raise
    
    def run_analysis(self, kpi_names: List[str], analysis_types: List[str] = None, 
                    params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        运行完整的数据分析流程
        
        Args:
            kpi_names: KPI指标名称列表
            analysis_types: 分析类型列表 ('distribution', 'trend', 'anomaly')
            params: 查询参数
            
        Returns:
            分析结果字典
        """
        try:
            if analysis_types is None:
                analysis_types = ['distribution', 'trend', 'anomaly']
            
            if params is None:
                params = {}
            
            self.logger.info(f"开始分析KPI指标: {kpi_names}")
            
            results = {
                'kpi_data': {},
                'analysis_results': {},
                'charts': {},
                'summary': {}
            }
            
            # 1. 计算KPI指标
            for kpi_name in kpi_names:
                try:
                    kpi_data = self.calculator.calculate_kpi(kpi_name, params)
                    results['kpi_data'][kpi_name] = kpi_data
                    
                    # 获取KPI摘要
                    summary = self.calculator.get_kpi_summary(kpi_data, kpi_name)
                    results['summary'][kpi_name] = summary
                    
                    self.logger.info(f"成功计算KPI: {kpi_name}, 数据行数: {len(kpi_data)}")
                    
                except Exception as e:
                    self.logger.error(f"计算KPI失败: {kpi_name}, 错误: {e}")
                    continue
            
            # 2. 执行数据分析
            for kpi_name, kpi_data in results['kpi_data'].items():
                analysis_results = {}
                
                # 分布分析
                if 'distribution' in analysis_types:
                    try:
                        distribution_result = self.analyzer.analyze_distribution(kpi_data)
                        analysis_results['distribution'] = distribution_result
                        self.logger.info(f"完成分布分析: {kpi_name}")
                    except Exception as e:
                        self.logger.error(f"分布分析失败: {kpi_name}, 错误: {e}")
                
                # 趋势分析
                if 'trend' in analysis_types:
                    try:
                        trend_result = self.analyzer.analyze_trend(kpi_data)
                        analysis_results['trend'] = trend_result
                        self.logger.info(f"完成趋势分析: {kpi_name}")
                    except Exception as e:
                        self.logger.error(f"趋势分析失败: {kpi_name}, 错误: {e}")
                
                # 异常检测
                if 'anomaly' in analysis_types:
                    try:
                        anomaly_method = self.config.get('analysis_config', {}).get('anomaly', {}).get('method', 'isolation_forest')
                        anomaly_result = self.analyzer.detect_anomalies(kpi_data, method=anomaly_method)
                        analysis_results['anomaly'] = anomaly_result
                        self.logger.info(f"完成异常检测: {kpi_name}")
                    except Exception as e:
                        self.logger.error(f"异常检测失败: {kpi_name}, 错误: {e}")
                
                results['analysis_results'][kpi_name] = analysis_results
            
            # 3. 生成图表
            for kpi_name, kpi_data in results['kpi_data'].items():
                charts = {}
                analysis_results = results['analysis_results'].get(kpi_name, {})
                
                # 分布图表
                if 'distribution' in analysis_results:
                    try:
                        distribution_chart = self.chart_generator.create_distribution_chart(
                            kpi_data, 
                            target_column=None,
                            analysis_result=analysis_results['distribution']
                        )
                        charts['distribution'] = distribution_chart
                    except Exception as e:
                        self.logger.error(f"生成分布图表失败: {kpi_name}, 错误: {e}")
                
                # 趋势图表
                if 'trend' in analysis_results:
                    try:
                        trend_chart = self.chart_generator.create_trend_chart(
                            kpi_data,
                            date_column=None,
                            value_column=None,
                            analysis_result=analysis_results['trend']
                        )
                        charts['trend'] = trend_chart
                    except Exception as e:
                        self.logger.error(f"生成趋势图表失败: {kpi_name}, 错误: {e}")
                
                # 异常检测图表
                if 'anomaly' in analysis_results:
                    try:
                        anomaly_chart = self.chart_generator.create_anomaly_chart(
                            kpi_data,
                            target_column=None,
                            analysis_result=analysis_results['anomaly']
                        )
                        charts['anomaly'] = anomaly_chart
                    except Exception as e:
                        self.logger.error(f"生成异常检测图表失败: {kpi_name}, 错误: {e}")
                
                results['charts'][kpi_name] = charts
            
            self.logger.info("数据分析流程完成")
            return results
            
        except Exception as e:
            self.logger.error(f"运行分析流程失败: {e}")
            raise
    
    def save_results(self, results: Dict[str, Any], output_dir: str = "reports"):
        """
        保存分析结果
        
        Args:
            results: 分析结果
            output_dir: 输出目录
        """
        try:
            # 创建输出目录
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(output_dir, f"analysis_report_{timestamp}")
            os.makedirs(output_path, exist_ok=True)
            
            # 保存图表
            charts_dir = os.path.join(output_path, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            for kpi_name, charts in results['charts'].items():
                kpi_charts_dir = os.path.join(charts_dir, kpi_name)
                os.makedirs(kpi_charts_dir, exist_ok=True)
                
                for chart_type, chart in charts.items():
                    chart_file = os.path.join(kpi_charts_dir, f"{chart_type}.html")
                    self.chart_generator.save_chart(chart, chart_file, 'html')
            
            # 保存数据
            data_dir = os.path.join(output_path, "data")
            os.makedirs(data_dir, exist_ok=True)
            
            for kpi_name, kpi_data in results['kpi_data'].items():
                data_file = os.path.join(data_dir, f"{kpi_name}.csv")
                kpi_data.to_csv(data_file, index=False)
            
            # 保存分析结果
            import json
            analysis_file = os.path.join(output_path, "analysis_results.json")
            with open(analysis_file, 'w', encoding='utf-8') as f:
                # 处理不可序列化的对象
                serializable_results = self._make_serializable(results)
                json.dump(serializable_results, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"分析结果已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            raise
    
    def _make_serializable(self, obj):
        """将对象转换为可序列化的格式"""
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif hasattr(obj, '__dict__'):
            return str(obj)
        else:
            return obj
    
    def close(self):
        """关闭资源"""
        if self.connector:
            self.connector.close()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="KPI指标数据分析工具")
    parser.add_argument("--kpi", nargs="+", required=True, help="KPI指标名称列表")
    parser.add_argument("--analysis", nargs="+", default=["distribution", "trend", "anomaly"], 
                       help="分析类型列表")
    parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--output-dir", default="reports", help="输出目录")
    parser.add_argument("--config", default="config/kpi_config.yaml", help="配置文件路径")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    parser.add_argument("--log-file", help="日志文件路径")
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logger(args.log_level, args.log_file)
    logger = get_logger("main")
    
    try:
        # 构建查询参数
        params = {}
        if args.start_date:
            params['start_date'] = args.start_date
        if args.end_date:
            params['end_date'] = args.end_date
        
        # 创建分析流水线
        pipeline = DataAnalysisPipeline(args.config)
        
        # 运行分析
        results = pipeline.run_analysis(args.kpi, args.analysis, params)
        
        # 保存结果
        output_path = pipeline.save_results(results, args.output_dir)
        
        logger.info(f"分析完成，结果保存在: {output_path}")
        
        # 打印摘要
        print("\n=== 分析摘要 ===")
        for kpi_name, summary in results['summary'].items():
            print(f"\nKPI: {kpi_name}")
            print(f"  描述: {summary.get('description', 'N/A')}")
            print(f"  单位: {summary.get('unit', 'N/A')}")
            print(f"  数据行数: {summary.get('total_records', 0):,}")
            
            # 打印统计信息
            stats = summary.get('statistics', {})
            if stats:
                for col, col_stats in stats.items():
                    print(f"  {col}:")
                    print(f"    均值: {col_stats.get('mean', 0):.2f}")
                    print(f"    标准差: {col_stats.get('std', 0):.2f}")
                    print(f"    范围: [{col_stats.get('min', 0):.2f}, {col_stats.get('max', 0):.2f}]")
        
        pipeline.close()
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
