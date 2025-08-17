#!/usr/bin/env python3
"""
KPI分析系统测试脚本
测试各个功能模块是否正常工作
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_excel_reader():
    """测试Excel读取器"""
    print("测试Excel读取器...")
    
    try:
        from utils.excel_reader import ExcelKPIReader, create_sample_excel
        
        # 创建测试数据
        test_file = create_sample_excel("test_kpi_data.xlsx")
        print(f"✓ 测试文件创建成功: {test_file}")
        
        # 读取数据
        reader = ExcelKPIReader(test_file)
        data = reader.read_excel()
        print(f"✓ 数据读取成功，形状: {data.shape}")
        
        # 检测列类型
        column_info = reader.detect_columns()
        print(f"✓ 列检测成功: {column_info}")
        
        # 验证数据质量
        validation_issues = reader.validate_data()
        print(f"✓ 数据验证完成: {validation_issues}")
        
        # 获取摘要统计
        summary_stats = reader.get_summary_stats()
        print(f"✓ 摘要统计完成: 部门数={summary_stats['total_departments']}, 指标数={summary_stats['total_metrics']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Excel读取器测试失败: {e}")
        return False

def test_anomaly_detector():
    """测试异常检测器"""
    print("\n测试异常检测器...")
    
    try:
        from analysis.kpi_anomaly_detector import KPIAnomalyDetector
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'value': [1, 2, 3, 100, 4, 5, 6, 7, 8, 9, 10]  # 包含异常值100
        })
        
        detector = KPIAnomalyDetector()
        
        # 测试不同方法
        methods = ['isolation_forest', 'iqr', 'zscore']
        for method in methods:
            result = detector.detect_anomalies(test_data, method=method)
            anomaly_count = sum(result.get('anomalies', []))
            print(f"✓ {method}方法检测到 {anomaly_count} 个异常")
        
        return True
        
    except Exception as e:
        print(f"✗ 异常检测器测试失败: {e}")
        return False

def test_trend_analyzer():
    """测试趋势分析器"""
    print("\n测试趋势分析器...")
    
    try:
        from analysis.kpi_anomaly_detector import KPITrendAnalyzer
        
        # 创建测试时间序列数据
        test_data = pd.DataFrame({
            'time': ['2025Q1', '2025Q2', '2025Q3', '2025Q4'],
            'value': [10, 15, 20, 25]  # 上升趋势
        })
        
        analyzer = KPITrendAnalyzer()
        result = analyzer.analyze_trend(test_data)
        
        print(f"✓ 趋势斜率: {result['trend_slope']:.3f}")
        print(f"✓ 波动性: {result['volatility']:.3f}")
        print(f"✓ 变化点数量: {len(result['change_points'])}")
        
        return True
        
    except Exception as e:
        print(f"✗ 趋势分析器测试失败: {e}")
        return False

def test_comprehensive_analyzer():
    """测试综合分析器"""
    print("\n测试综合分析器...")
    
    try:
        from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
        
        # 创建测试数据
        test_data = pd.DataFrame({
            '部门名称': ['技术部', '产品部', '运营部'],
            '在编人数': [50, 30, 25],
            '执行用例数': [1000, 500, 300],
            '2025Q1_在编人数': [45, 28, 23],
            '2025Q2_在编人数': [52, 32, 27]
        })
        
        analyzer = KPIComprehensiveAnalyzer()
        results = analyzer.analyze_kpi_data(
            data=test_data,
            department_column='部门名称',
            metric_columns=['在编人数', '执行用例数'],
            time_columns=['2025Q1_在编人数', '2025Q2_在编人数']
        )
        
        print(f"✓ 综合分析完成")
        print(f"  - 异常检测结果: {len(results['anomalies'])} 个指标")
        print(f"  - 趋势分析结果: {len(results['trends'])} 个指标")
        print(f"  - 建议数量: {len(results['recommendations'])} 条")
        
        return True
        
    except Exception as e:
        print(f"✗ 综合分析器测试失败: {e}")
        return False

def test_report_generator():
    """测试报告生成器"""
    print("\n测试报告生成器...")
    
    try:
        from visualization.kpi_report_generator import KPIReportGenerator
        
        # 创建测试数据
        test_data = pd.DataFrame({
            '部门名称': ['技术部', '产品部'],
            '在编人数': [50, 30],
            '执行用例数': [1000, 500]
        })
        
        # 创建测试分析结果
        test_results = {
            'summary': {
                'total_departments': 2,
                'total_metrics': 2,
                'departments': ['技术部', '产品部'],
                'metrics': ['在编人数', '执行用例数']
            },
            'anomalies': {
                '在编人数': {
                    'iqr': {'anomalies': [False, False], 'method': 'iqr'}
                }
            },
            'trends': {
                '在编人数': {
                    'trend_slope': 0.1,
                    'volatility': 0.05,
                    'change_points': [],
                    'seasonality': {'has_seasonality': False}
                }
            },
            'recommendations': ['建议关注在编人数变化趋势']
        }
        
        generator = KPIReportGenerator()
        
        # 测试简化版报告
        simple_report = generator.generate_simple_report(test_data, test_results)
        print(f"✓ 简化版报告生成成功: {simple_report}")
        
        # 测试完整版报告
        full_report = generator.generate_comprehensive_report(
            test_data, test_results, "测试报告"
        )
        print(f"✓ 完整版报告生成成功: {full_report}")
        
        return True
        
    except Exception as e:
        print(f"✗ 报告生成器测试失败: {e}")
        return False

def test_main_analyzer():
    """测试主分析器"""
    print("\n测试主分析器...")
    
    try:
        from kpi_excel_analyzer import KPIExcelAnalyzer
        
        # 创建测试文件
        from utils.excel_reader import create_sample_excel
        test_file = create_sample_excel("test_main_analysis.xlsx")
        
        # 初始化分析器
        analyzer = KPIExcelAnalyzer()
        
        # 进行完整分析
        results = analyzer.analyze_excel_file(test_file)
        
        print(f"✓ 主分析器测试成功")
        print(f"  - 报告路径: {results['report_path']}")
        print(f"  - 部门数量: {results['summary_stats']['total_departments']}")
        print(f"  - 指标数量: {results['summary_stats']['total_metrics']}")
        
        # 测试特定指标分析
        metric_results = analyzer.analyze_specific_metric(test_file, "在编人数")
        print(f"  - 特定指标分析成功: {metric_results['metric_name']}")
        
        # 测试特定部门分析
        dept_results = analyzer.analyze_specific_department(test_file, "技术部")
        print(f"  - 特定部门分析成功: {dept_results['department_name']}")
        
        return True
        
    except Exception as e:
        print(f"✗ 主分析器测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖包"""
    print("测试依赖包...")
    
    required_packages = [
        'pandas', 'numpy', 'scikit-learn', 'plotly', 
        'matplotlib', 'seaborn', 'openpyxl', 'jinja2', 'loguru'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少的依赖包: {missing_packages}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def cleanup_test_files():
    """清理测试文件"""
    test_files = [
        "test_kpi_data.xlsx",
        "test_main_analysis.xlsx",
        "reports/simple_kpi_report_*.html",
        "reports/kpi_report_*.html"
    ]
    
    for pattern in test_files:
        for file_path in Path('.').glob(pattern):
            try:
                file_path.unlink()
                print(f"清理测试文件: {file_path}")
            except:
                pass

def main():
    """主测试函数"""
    print("=" * 60)
    print("KPI分析系统功能测试")
    print("=" * 60)
    
    # 测试结果统计
    test_results = []
    
    # 1. 测试依赖包
    test_results.append(("依赖包检查", test_dependencies()))
    
    # 2. 测试各个模块
    test_results.append(("Excel读取器", test_excel_reader()))
    test_results.append(("异常检测器", test_anomaly_detector()))
    test_results.append(("趋势分析器", test_trend_analyzer()))
    test_results.append(("综合分析器", test_comprehensive_analyzer()))
    test_results.append(("报告生成器", test_report_generator()))
    test_results.append(("主分析器", test_main_analyzer()))
    
    # 3. 输出测试结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统功能正常。")
        print("\n下一步:")
        print("1. 运行 python example_kpi_analysis.py 查看完整示例")
        print("2. 准备您的KPI数据文件")
        print("3. 使用 python src/kpi_excel_analyzer.py your_data.xlsx 进行分析")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关模块。")
    
    # 4. 清理测试文件
    print("\n清理测试文件...")
    cleanup_test_files()
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
