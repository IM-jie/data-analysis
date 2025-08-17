#!/usr/bin/env python3
"""
KPI Excel数据分析使用示例
演示如何使用KPI分析系统进行数据分析
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.excel_reader import ExcelKPIReader, create_sample_excel
from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
from visualization.kpi_report_generator import KPIReportGenerator
from kpi_excel_analyzer import KPIExcelAnalyzer
from loguru import logger


def example_1_basic_analysis():
    """示例1: 基础分析流程"""
    print("=" * 50)
    print("示例1: 基础分析流程")
    print("=" * 50)
    
    # 1. 创建示例Excel文件
    print("1. 创建示例Excel文件...")
    sample_file = create_sample_excel("example_kpi_data.xlsx")
    print(f"   示例文件已创建: {sample_file}")
    
    # 2. 初始化分析器
    print("\n2. 初始化分析器...")
    analyzer = KPIExcelAnalyzer()
    
    # 3. 进行完整分析
    print("\n3. 进行完整分析...")
    results = analyzer.analyze_excel_file(sample_file)
    
    # 4. 打印结果摘要
    print("\n4. 分析结果摘要:")
    print(f"   - 报告文件: {results['report_path']}")
    print(f"   - 部门数量: {results['summary_stats']['total_departments']}")
    print(f"   - 指标数量: {results['summary_stats']['total_metrics']}")
    
    # 5. 获取异常检测摘要
    anomaly_summary = analyzer.get_anomaly_summary(results['analysis_results'])
    print(f"   - 异常指标数量: {anomaly_summary['total_metrics_with_anomalies']}")
    print(f"   - 总异常数量: {anomaly_summary['total_anomalies']}")
    
    # 6. 获取趋势分析摘要
    trend_summary = analyzer.get_trend_summary(results['analysis_results'])
    print(f"   - 上升趋势指标: {len(trend_summary['increasing_trends'])}")
    print(f"   - 下降趋势指标: {len(trend_summary['decreasing_trends'])}")
    print(f"   - 稳定趋势指标: {len(trend_summary['stable_trends'])}")
    
    return results


def example_2_specific_metric_analysis():
    """示例2: 特定指标分析"""
    print("\n" + "=" * 50)
    print("示例2: 特定指标分析")
    print("=" * 50)
    
    # 使用示例文件
    sample_file = "example_kpi_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 初始化分析器
    analyzer = KPIExcelAnalyzer()
    
    # 分析特定指标
    print("分析指标: 在编人数")
    results = analyzer.analyze_specific_metric(sample_file, "在编人数")
    
    # 打印分析结果
    analysis_results = results['analysis_results']
    anomalies = analysis_results.get('anomalies', {})
    trends = analysis_results.get('trends', {})
    
    print(f"\n指标 '{results['metric_name']}' 分析结果:")
    
    # 异常检测结果
    if 'value' in anomalies:
        for method, result in anomalies['value'].items():
            if result.get('anomalies'):
                count = sum(result['anomalies'])
                print(f"  - {method}方法检测到 {count} 个异常")
    
    # 趋势分析结果
    if 'value' in trends:
        trend_result = trends['value']
        print(f"  - 趋势斜率: {trend_result.get('trend_slope', 0):.3f}")
        print(f"  - 波动性: {trend_result.get('volatility', 0):.3f}")
        print(f"  - 变化点数量: {len(trend_result.get('change_points', []))}")


def example_3_specific_department_analysis():
    """示例3: 特定部门分析"""
    print("\n" + "=" * 50)
    print("示例3: 特定部门分析")
    print("=" * 50)
    
    # 使用示例文件
    sample_file = "example_kpi_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 初始化分析器
    analyzer = KPIExcelAnalyzer()
    
    # 分析特定部门
    print("分析部门: 技术部")
    results = analyzer.analyze_specific_department(sample_file, "技术部")
    
    # 打印分析结果
    analysis_results = results['analysis_results']
    summary = analysis_results.get('summary', {})
    recommendations = analysis_results.get('recommendations', [])
    
    print(f"\n部门 '{results['department_name']}' 分析结果:")
    print(f"  - 指标数量: {summary.get('total_metrics', 0)}")
    print(f"  - 建议数量: {len(recommendations)}")
    
    if recommendations:
        print("  - 主要建议:")
        for i, rec in enumerate(recommendations[:3], 1):  # 只显示前3条建议
            print(f"    {i}. {rec}")


def example_4_manual_analysis():
    """示例4: 手动分析流程"""
    print("\n" + "=" * 50)
    print("示例4: 手动分析流程")
    print("=" * 50)
    
    # 1. 读取Excel文件
    print("1. 读取Excel文件...")
    sample_file = "example_kpi_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    reader = ExcelKPIReader(sample_file)
    data = reader.read_excel()
    
    # 2. 检测列类型
    print("\n2. 检测列类型...")
    column_info = reader.detect_columns()
    print(f"   部门列: {column_info['department_column']}")
    print(f"   季度列: {column_info['quarter_columns']}")
    print(f"   指标列数量: {len(column_info['metric_columns'])}")
    
    # 3. 验证数据质量
    print("\n3. 验证数据质量...")
    validation_issues = reader.validate_data()
    if validation_issues:
        for issue_type, issues in validation_issues.items():
            if issues:
                print(f"   {issue_type}: {len(issues)}个问题")
    else:
        print("   数据质量良好")
    
    # 4. 获取数据摘要
    print("\n4. 获取数据摘要...")
    summary_stats = reader.get_summary_stats()
    print(f"   总部门数: {summary_stats['total_departments']}")
    print(f"   总指标数: {summary_stats['total_metrics']}")
    
    # 5. 进行异常检测
    print("\n5. 进行异常检测...")
    analyzer = KPIComprehensiveAnalyzer()
    analysis_results = analyzer.analyze_kpi_data(
        data=data,
        department_column=column_info['department_column'],
        metric_columns=column_info['metric_columns'],
        time_columns=column_info['quarter_columns']
    )
    
    # 6. 生成报告
    print("\n6. 生成报告...")
    report_generator = KPIReportGenerator()
    report_path = report_generator.generate_comprehensive_report(
        data=data,
        analysis_results=analysis_results,
        report_title="手动分析示例报告"
    )
    print(f"   报告已生成: {report_path}")
    
    # 7. 导出结果到Excel
    print("\n7. 导出结果到Excel...")
    excel_path = "manual_analysis_results.xlsx"
    with open(excel_path, 'w') as f:  # 创建空文件，实际导出在analyzer中
        pass
    
    print(f"   结果已导出: {excel_path}")


def example_5_advanced_features():
    """示例5: 高级功能演示"""
    print("\n" + "=" * 50)
    print("示例5: 高级功能演示")
    print("=" * 50)
    
    # 使用示例文件
    sample_file = "example_kpi_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 初始化分析器
    analyzer = KPIExcelAnalyzer()
    
    # 1. 数据重塑
    print("1. 数据重塑演示...")
    reader = ExcelKPIReader(sample_file)
    reader.read_excel()
    reshaped_data = reader.reshape_data()
    print(f"   原始数据形状: {reader.data.shape}")
    print(f"   重塑后数据形状: {reshaped_data.shape}")
    
    # 2. 多种异常检测方法对比
    print("\n2. 多种异常检测方法对比...")
    from analysis.kpi_anomaly_detector import KPIAnomalyDetector
    
    anomaly_detector = KPIAnomalyDetector()
    methods = ['isolation_forest', 'iqr', 'zscore', 'lof']
    
    # 选择一个指标进行演示
    metric_data = reader.get_metric_data("在编人数")
    metric_values = metric_data[['在编人数']].dropna()
    
    for method in methods:
        try:
            result = anomaly_detector.detect_anomalies(metric_values, method=method)
            if result.get('anomalies'):
                count = sum(result['anomalies'])
                print(f"   {method}: {count}个异常")
        except Exception as e:
            print(f"   {method}: 检测失败 - {e}")
    
    # 3. 趋势分析
    print("\n3. 趋势分析演示...")
    from analysis.kpi_anomaly_detector import KPITrendAnalyzer
    
    trend_analyzer = KPITrendAnalyzer()
    
    # 创建时间序列数据
    trend_data = []
    for i, row in metric_data.iterrows():
        for quarter in reader.quarter_columns:
            if pd.notna(row[quarter]):
                trend_data.append({
                    'time': quarter,
                    'value': row[quarter]
                })
    
    if trend_data:
        trend_df = pd.DataFrame(trend_data)
        trend_result = trend_analyzer.analyze_trend(trend_df)
        
        print(f"   趋势斜率: {trend_result['trend_slope']:.3f}")
        print(f"   波动性: {trend_result['volatility']:.3f}")
        print(f"   变化点数量: {len(trend_result['change_points'])}")
        print(f"   季节性: {'是' if trend_result['seasonality']['has_seasonality'] else '否'}")


def main():
    """主函数"""
    print("KPI Excel数据分析系统使用示例")
    print("本示例将演示如何使用KPI分析系统进行数据分析")
    
    try:
        # 运行所有示例
        results = example_1_basic_analysis()
        example_2_specific_metric_analysis()
        example_3_specific_department_analysis()
        example_4_manual_analysis()
        example_5_advanced_features()
        
        print("\n" + "=" * 50)
        print("所有示例运行完成！")
        print("=" * 50)
        print("\n生成的文件:")
        print("- example_kpi_data.xlsx (示例数据)")
        print("- reports/kpi_report_*.html (分析报告)")
        print("- manual_analysis_results.xlsx (手动分析结果)")
        
        print("\n使用建议:")
        print("1. 查看生成的HTML报告了解详细分析结果")
        print("2. 根据实际需求调整配置参数")
        print("3. 可以针对特定指标或部门进行深入分析")
        print("4. 建议定期运行分析以监控KPI趋势")
        
    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        print(f"\n错误: {e}")
        print("请检查依赖包是否正确安装")


if __name__ == "__main__":
    main()
