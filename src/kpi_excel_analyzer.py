"""
KPI Excel数据分析主程序
整合Excel读取、异常检测、趋势分析和报告生成功能
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from loguru import logger
import argparse
import sys

# 导入自定义模块
from utils.excel_reader import ExcelKPIReader, create_sample_excel
from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
from analysis.kpi_association_miner import KPIAssociationMiner, KPIAssociationAnomalyDetector
from visualization.kpi_report_generator import KPIReportGenerator


class KPIExcelAnalyzer:
    """KPI Excel数据分析器主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化KPI分析器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.excel_reader = None
        self.analyzer = KPIComprehensiveAnalyzer(self.config)
        self.association_miner = KPIAssociationMiner(self.config)
        self.association_detector = KPIAssociationAnomalyDetector(self.association_miner)
        self.report_generator = KPIReportGenerator()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"加载配置文件: {config_path}")
        else:
            config = self._get_default_config()
            logger.info("使用默认配置")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'analysis_config': {
                'distribution': {
                    'bins': 20,
                    'outlier_method': 'iqr'
                },
                'trend': {
                    'window_size': 3,
                    'seasonality': 4
                },
                'anomaly': {
                    'method': 'isolation_forest',
                    'contamination': 0.1,
                    'threshold': 0.95
                }
            },
            'report_config': {
                'output_format': ['html'],
                'charts': [
                    'distribution_histogram',
                    'trend_line',
                    'anomaly_scatter',
                    'correlation_matrix'
                ],
                'auto_generate': True
            }
        }
    
    def analyze_excel_file(self, 
                          excel_path: str,
                          sheet_name: Optional[str] = None,
                          output_dir: str = "reports") -> Dict[str, Any]:
        """
        分析Excel文件
        
        Args:
            excel_path: Excel文件路径
            sheet_name: 工作表名称
            output_dir: 输出目录
            
        Returns:
            分析结果字典
        """
        try:
            # 1. 读取Excel文件
            logger.info(f"开始分析Excel文件: {excel_path}")
            self.excel_reader = ExcelKPIReader(excel_path)
            data = self.excel_reader.read_excel(sheet_name)
            
            # 2. 检测列类型
            column_info = self.excel_reader.detect_columns()
            logger.info(f"检测到的列信息: {column_info}")
            
            # 3. 验证数据质量
            validation_issues = self.excel_reader.validate_data()
            if validation_issues:
                logger.warning(f"数据质量问题: {validation_issues}")
            
            # 4. 获取数据摘要
            summary_stats = self.excel_reader.get_summary_stats()
            logger.info(f"数据摘要: {summary_stats}")
            
            # 5. 进行综合分析
            analysis_results = self.analyzer.analyze_kpi_data(
                data=data,
                department_column=column_info['department_column'],
                metric_columns=column_info['metric_columns'],
                time_columns=column_info['quarter_columns']
            )
            
            # 6. 进行关联关系挖掘
            logger.info("开始关联关系挖掘...")
            association_results = self.association_miner.discover_associations(
                data=data,
                metric_columns=column_info['metric_columns']
            )
            
            # 7. 基于关联关系进行异常检测
            logger.info("基于关联关系进行异常检测...")
            association_anomalies = self.association_detector.build_baseline(
                data=data,
                metric_columns=column_info['metric_columns']
            )
            
            # 将关联关系分析结果合并到主分析结果中
            analysis_results['associations'] = association_results
            analysis_results['association_anomalies'] = association_anomalies
            
            # 8. 生成报告
            report_path = self.report_generator.generate_comprehensive_report(
                data=data,
                analysis_results=analysis_results,
                report_title=f"KPI数据分析报告 - {Path(excel_path).stem}"
            )
            
            # 9. 返回完整结果
            results = {
                'excel_path': excel_path,
                'column_info': column_info,
                'validation_issues': validation_issues,
                'summary_stats': summary_stats,
                'analysis_results': analysis_results,
                'association_results': association_results,
                'association_anomalies': association_anomalies,
                'report_path': report_path
            }
            
            logger.info(f"分析完成，报告已生成: {report_path}")
            return results
            
        except Exception as e:
            logger.error(f"分析过程中发生错误: {e}")
            raise
    
    def analyze_associations(self, excel_path: str,
                           sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        专门进行关联关系分析
        
        Args:
            excel_path: Excel文件路径
            sheet_name: 工作表名称
            
        Returns:
            关联关系分析结果
        """
        try:
            # 读取数据
            self.excel_reader = ExcelKPIReader(excel_path)
            data = self.excel_reader.read_excel(sheet_name)
            
            # 检测列类型
            column_info = self.excel_reader.detect_columns()
            
            # 进行关联关系挖掘
            logger.info("开始关联关系挖掘...")
            association_results = self.association_miner.discover_associations(
                data=data,
                metric_columns=column_info['metric_columns']
            )
            
            # 构建关联关系基线
            logger.info("构建关联关系基线...")
            baseline_results = self.association_detector.build_baseline(
                data=data,
                metric_columns=column_info['metric_columns']
            )
            
            # 生成关联关系洞察
            insights = self.association_detector.generate_anomaly_insights(
                baseline_results
            )
            
            return {
                'excel_path': excel_path,
                'column_info': column_info,
                'association_results': association_results,
                'baseline_results': baseline_results,
                'insights': insights
            }
            
        except Exception as e:
            logger.error(f"关联关系分析失败: {e}")
            raise
    
    def analyze_specific_metric(self, 
                               excel_path: str,
                               metric_name: str,
                               sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        分析特定指标
        
        Args:
            excel_path: Excel文件路径
            metric_name: 指标名称
            sheet_name: 工作表名称
            
        Returns:
            特定指标的分析结果
        """
        # 读取数据
        self.excel_reader = ExcelKPIReader(excel_path)
        data = self.excel_reader.read_excel(sheet_name)
        
        # 检测列类型
        column_info = self.excel_reader.detect_columns()
        
        # 获取特定指标数据
        metric_data = self.excel_reader.get_metric_data(metric_name)
        
        # 分析特定指标
        analysis_results = self.analyzer.analyze_kpi_data(
            data=metric_data,
            department_column=column_info['department_column'],
            metric_columns=['value'],
            time_columns=column_info['quarter_columns']
        )
        
        return {
            'metric_name': metric_name,
            'metric_data': metric_data,
            'analysis_results': analysis_results
        }
    
    def analyze_specific_department(self, 
                                   excel_path: str,
                                   department_name: str,
                                   sheet_name: Optional[str] = None) -> Dict[str, Any]:
        """
        分析特定部门
        
        Args:
            excel_path: Excel文件路径
            department_name: 部门名称
            sheet_name: 工作表名称
            
        Returns:
            特定部门的分析结果
        """
        # 读取数据
        self.excel_reader = ExcelKPIReader(excel_path)
        data = self.excel_reader.read_excel(sheet_name)
        
        # 检测列类型
        column_info = self.excel_reader.detect_columns()
        
        # 获取特定部门数据
        dept_data = self.excel_reader.get_department_data(department_name)
        
        # 分析特定部门
        analysis_results = self.analyzer.analyze_kpi_data(
            data=dept_data,
            department_column=column_info['department_column'],
            metric_columns=column_info['metric_columns'],
            time_columns=column_info['quarter_columns']
        )
        
        return {
            'department_name': department_name,
            'department_data': dept_data,
            'analysis_results': analysis_results
        }
    
    def get_anomaly_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取异常检测摘要
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            异常检测摘要
        """
        anomalies = analysis_results.get('anomalies', {})
        summary = {
            'total_metrics_with_anomalies': 0,
            'total_anomalies': 0,
            'anomaly_details': [],
            'high_risk_metrics': []
        }
        
        for metric, methods in anomalies.items():
            metric_anomaly_count = 0
            for method, result in methods.items():
                if result.get('anomalies'):
                    count = sum(result['anomalies'])
                    metric_anomaly_count += count
                    summary['total_anomalies'] += count
                    
                    if count > 0:
                        summary['anomaly_details'].append({
                            'metric': metric,
                            'method': method,
                            'count': count
                        })
            
            if metric_anomaly_count > 0:
                summary['total_metrics_with_anomalies'] += 1
                
                # 标记高风险指标（异常数量超过阈值）
                if metric_anomaly_count >= 3:  # 可配置的阈值
                    summary['high_risk_metrics'].append({
                        'metric': metric,
                        'anomaly_count': metric_anomaly_count
                    })
        
        return summary
    
    def get_trend_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取趋势分析摘要
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            趋势分析摘要
        """
        trends = analysis_results.get('trends', {})
        summary = {
            'total_metrics': len(trends),
            'increasing_trends': [],
            'decreasing_trends': [],
            'stable_trends': [],
            'high_volatility_metrics': []
        }
        
        for metric, trend_result in trends.items():
            slope = trend_result.get('trend_slope', 0)
            volatility = trend_result.get('volatility', 0)
            
            if abs(slope) < 0.01:  # 稳定趋势
                summary['stable_trends'].append({
                    'metric': metric,
                    'slope': slope
                })
            elif slope > 0:  # 上升趋势
                summary['increasing_trends'].append({
                    'metric': metric,
                    'slope': slope
                })
            else:  # 下降趋势
                summary['decreasing_trends'].append({
                    'metric': metric,
                    'slope': slope
                })
            
            # 标记高波动性指标
            if volatility > 0.5:  # 可配置的阈值
                summary['high_volatility_metrics'].append({
                    'metric': metric,
                    'volatility': volatility
                })
        
        return summary
    
    def export_results_to_excel(self, 
                               analysis_results: Dict[str, Any],
                               output_path: str) -> str:
        """
        将分析结果导出到Excel
        
        Args:
            analysis_results: 分析结果
            output_path: 输出文件路径
            
        Returns:
            输出文件路径
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 数据摘要
            summary = analysis_results.get('summary', {})
            summary_df = pd.DataFrame([summary])
            summary_df.to_excel(writer, sheet_name='数据摘要', index=False)
            
            # 2. 异常检测结果
            anomalies = analysis_results.get('anomalies', {})
            anomaly_data = []
            for metric, methods in anomalies.items():
                for method, result in methods.items():
                    if result.get('anomalies'):
                        count = sum(result['anomalies'])
                        if count > 0:
                            anomaly_data.append({
                                '指标': metric,
                                '检测方法': method,
                                '异常数量': count,
                                '异常比例': f"{count/len(result['anomalies'])*100:.2f}%"
                            })
            
            if anomaly_data:
                anomaly_df = pd.DataFrame(anomaly_data)
                anomaly_df.to_excel(writer, sheet_name='异常检测结果', index=False)
            
            # 3. 趋势分析结果
            trends = analysis_results.get('trends', {})
            trend_data = []
            for metric, trend_result in trends.items():
                trend_data.append({
                    '指标': metric,
                    '趋势斜率': trend_result.get('trend_slope', 0),
                    '波动性': trend_result.get('volatility', 0),
                    '变化点数量': len(trend_result.get('change_points', [])),
                    '季节性': '是' if trend_result.get('seasonality', {}).get('has_seasonality', False) else '否'
                })
            
            if trend_data:
                trend_df = pd.DataFrame(trend_data)
                trend_df.to_excel(writer, sheet_name='趋势分析结果', index=False)
            
            # 4. 建议
            recommendations = analysis_results.get('recommendations', [])
            if recommendations:
                rec_df = pd.DataFrame({'建议': recommendations})
                rec_df.to_excel(writer, sheet_name='分析建议', index=False)
        
        logger.info(f"分析结果已导出到: {output_path}")
        return output_path


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='KPI Excel数据分析工具')
    parser.add_argument('excel_file', nargs='?', help='Excel文件路径')
    parser.add_argument('--sheet', help='工作表名称')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--output-dir', default='reports', help='输出目录')
    parser.add_argument('--metric', help='分析特定指标')
    parser.add_argument('--department', help='分析特定部门')
    parser.add_argument('--export-excel', help='导出结果到Excel文件')
    parser.add_argument('--associations', action='store_true', help='进行关联关系分析')
    parser.add_argument('--create-sample', action='store_true', help='创建示例Excel文件')
    
    args = parser.parse_args()
    
    # 创建示例文件
    if args.create_sample:
        sample_path = create_sample_excel()
        print(f"示例Excel文件已创建: {sample_path}")
        return
    
    # 初始化分析器
    analyzer = KPIExcelAnalyzer(args.config)
    
    try:
        if args.metric:
            # 分析特定指标
            results = analyzer.analyze_specific_metric(
                args.excel_file, args.metric, args.sheet
            )
            print(f"指标 '{args.metric}' 分析完成")
            
        elif args.department:
            # 分析特定部门
            results = analyzer.analyze_specific_department(
                args.excel_file, args.department, args.sheet
            )
            print(f"部门 '{args.department}' 分析完成")
            
        elif args.associations:
            # 关联关系分析
            results = analyzer.analyze_associations(
                args.excel_file, args.sheet
            )
            print(f"关联关系分析完成")
            
            # 打印关联关系摘要
            association_results = results['association_results']
            summary = association_results.get('summary', {})
            print(f"\n=== 关联关系分析摘要 ===")
            print(f"强相关性关系: {summary.get('total_strong_correlations', 0)}")
            print(f"强互信息关系: {summary.get('total_strong_mi_relationships', 0)}")
            print(f"强关联规则: {summary.get('total_strong_rules', 0)}")
            print(f"因果关系链: {summary.get('total_causal_chains', 0)}")
            
            # 打印关键洞察
            insights = summary.get('key_insights', [])
            if insights:
                print(f"\n关键洞察:")
                for i, insight in enumerate(insights[:5], 1):  # 只显示前5个
                    print(f"  {i}. {insight}")
            
        else:
            # 完整分析
            results = analyzer.analyze_excel_file(
                args.excel_file, args.sheet, args.output_dir
            )
            print(f"完整分析完成，报告路径: {results['report_path']}")
        
        # 导出到Excel
        if args.export_excel:
            analyzer.export_results_to_excel(
                results['analysis_results'], args.export_excel
            )
            print(f"结果已导出到: {args.export_excel}")
        
        # 打印摘要
        if 'analysis_results' in results:
            anomaly_summary = analyzer.get_anomaly_summary(results['analysis_results'])
            trend_summary = analyzer.get_trend_summary(results['analysis_results'])
            
            print("\n=== 分析摘要 ===")
            print(f"发现异常的指标数量: {anomaly_summary['total_metrics_with_anomalies']}")
            print(f"总异常数量: {anomaly_summary['total_anomalies']}")
            print(f"上升趋势指标: {len(trend_summary['increasing_trends'])}")
            print(f"下降趋势指标: {len(trend_summary['decreasing_trends'])}")
            print(f"稳定趋势指标: {len(trend_summary['stable_trends'])}")
            
            if anomaly_summary['high_risk_metrics']:
                print("\n高风险指标:")
                for metric in anomaly_summary['high_risk_metrics']:
                    print(f"  - {metric['metric']}: {metric['anomaly_count']}个异常")
        
    except Exception as e:
        logger.error(f"分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
