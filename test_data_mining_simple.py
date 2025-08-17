#!/usr/bin/env python3
"""
简化的KPI数据挖掘功能测试
只测试核心的关联关系挖掘功能
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.excel_reader import ExcelKPIReader, create_sample_excel
from analysis.kpi_association_miner import KPIAssociationMiner
from loguru import logger


def test_basic_association_mining():
    """测试基础关联关系挖掘"""
    print("=" * 60)
    print("测试基础关联关系挖掘")
    print("=" * 60)
    
    # 1. 创建简单的示例数据
    print("1. 创建简单示例数据...")
    
    # 创建更简单的数据
    data = {
        '部门名称': ['技术部', '产品部', '运营部'],
        '项目数量': [10, 8, 5],
        '在编人数': [50, 30, 20],
        '执行用例数': [1000, 800, 500],
        '自动化执行用例数': [600, 400, 200],
        '代码覆盖率': [0.85, 0.75, 0.65],
        'bug修复率': [0.90, 0.85, 0.80]
    }
    
    df = pd.DataFrame(data)
    simple_file = "simple_test_data.xlsx"
    df.to_excel(simple_file, index=False)
    print(f"   简单示例文件已创建: {simple_file}")
    
    # 2. 初始化关联关系挖掘器
    print("\n2. 初始化关联关系挖掘器...")
    miner = KPIAssociationMiner()
    
    # 3. 定义指标列
    metric_columns = ['项目数量', '在编人数', '执行用例数', '自动化执行用例数', '代码覆盖率', 'bug修复率']
    
    print(f"   指标列: {metric_columns}")
    
    # 4. 进行关联关系挖掘（只测试相关性分析）
    print("\n3. 进行相关性分析...")
    try:
        correlation_results = miner._analyze_correlations(df, metric_columns)
        
        print("   相关性分析结果:")
        strong_corrs = correlation_results.get('strong_correlations', [])
        print(f"   强相关性关系数量: {len(strong_corrs)}")
        
        if strong_corrs:
            print("   强相关性关系:")
            for i, corr in enumerate(strong_corrs[:3], 1):
                print(f"     {i}. {corr['pair']} ({corr['method']}: {corr['correlation']:.3f})")
        else:
            print("   未发现强相关性关系")
        
        # 显示相关性矩阵
        corr_matrix = correlation_results.get('matrix')
        if corr_matrix is not None:
            print(f"\n   相关性矩阵形状: {corr_matrix.shape}")
            print("   相关性矩阵:")
            print(corr_matrix.round(3))
        
        return True
        
    except Exception as e:
        print(f"   相关性分析失败: {e}")
        return False


def test_mutual_information():
    """测试互信息分析"""
    print("\n" + "=" * 60)
    print("测试互信息分析")
    print("=" * 60)
    
    # 使用简单数据
    simple_file = "simple_test_data.xlsx"
    if not os.path.exists(simple_file):
        print("请先运行基础测试创建数据文件")
        return False
    
    try:
        # 读取数据
        df = pd.read_excel(simple_file)
        metric_columns = ['项目数量', '在编人数', '执行用例数', '自动化执行用例数', '代码覆盖率', 'bug修复率']
        
        # 初始化挖掘器
        miner = KPIAssociationMiner()
        
        print("进行互信息分析...")
        mi_results = miner._analyze_mutual_information(df, metric_columns)
        
        print("互信息分析结果:")
        strong_mi = mi_results.get('strong_relationships', [])
        print(f"强互信息关系数量: {len(strong_mi)}")
        
        if strong_mi:
            print("强互信息关系:")
            for i, mi in enumerate(strong_mi[:3], 1):
                print(f"  {i}. {mi['source']} -> {mi['target']} (MI: {mi['mi_score']:.3f})")
        else:
            print("未发现强互信息关系")
        
        # 显示互信息矩阵
        mi_matrix = mi_results.get('matrix')
        if mi_matrix is not None:
            print(f"\n互信息矩阵形状: {mi_matrix.shape}")
            print("互信息矩阵:")
            print(mi_matrix.round(3))
        
        return True
        
    except Exception as e:
        print(f"互信息分析失败: {e}")
        return False


def test_causality_analysis():
    """测试因果关系分析"""
    print("\n" + "=" * 60)
    print("测试因果关系分析")
    print("=" * 60)
    
    # 创建时间序列数据
    print("1. 创建时间序列数据...")
    
    # 创建多个时间点的数据
    time_data = []
    departments = ['技术部', '产品部', '运营部']
    
    for quarter in ['Q1', 'Q2', 'Q3']:
        for dept in departments:
            row = {
                '部门名称': dept,
                'quarter': quarter,
                '项目数量': np.random.randint(5, 15),
                '在编人数': np.random.randint(20, 60),
                '执行用例数': np.random.randint(500, 1200),
                '自动化执行用例数': np.random.randint(200, 800),
                '代码覆盖率': np.random.uniform(0.6, 0.9),
                'bug修复率': np.random.uniform(0.7, 0.95)
            }
            time_data.append(row)
    
    df_time = pd.DataFrame(time_data)
    time_file = "time_series_test_data.xlsx"
    df_time.to_excel(time_file, index=False)
    print(f"   时间序列数据已创建: {time_file}")
    
    try:
        # 初始化挖掘器
        miner = KPIAssociationMiner()
        metric_columns = ['项目数量', '在编人数', '执行用例数', '自动化执行用例数', '代码覆盖率', 'bug修复率']
        
        print("\n2. 进行因果关系分析...")
        causality_results = miner._analyze_causality(df_time, metric_columns)
        
        print("因果关系分析结果:")
        lag_correlations = causality_results.get('lag_correlations', {})
        print(f"滞后相关性关系数量: {len(lag_correlations)}")
        
        if lag_correlations:
            print("滞后相关性关系:")
            for pair, lag_corrs in list(lag_correlations.items())[:3]:
                if lag_corrs:
                    best_lag = max(lag_corrs, key=lambda x: abs(x['correlation']))
                    print(f"  {pair}: 最强滞后相关性在滞后{best_lag['lag']}期 "
                          f"(相关性: {best_lag['correlation']:.3f})")
        
        causal_chains = causality_results.get('causal_chains', [])
        print(f"因果关系链数量: {len(causal_chains)}")
        
        if causal_chains:
            print("因果关系链:")
            for i, chain in enumerate(causal_chains[:3], 1):
                print(f"  {i}. {chain['source']} -> {chain['target']} "
                      f"(滞后{chain['lag']}期, 相关性: {chain['correlation']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"因果关系分析失败: {e}")
        return False


def test_association_anomaly_detection():
    """测试基于关联关系的异常检测"""
    print("\n" + "=" * 60)
    print("测试基于关联关系的异常检测")
    print("=" * 60)
    
    try:
        from analysis.kpi_association_miner import KPIAssociationAnomalyDetector
        
        # 使用简单数据
        simple_file = "simple_test_data.xlsx"
        if not os.path.exists(simple_file):
            print("请先运行基础测试创建数据文件")
            return False
        
        # 读取数据
        df = pd.read_excel(simple_file)
        metric_columns = ['项目数量', '在编人数', '执行用例数', '自动化执行用例数', '代码覆盖率', 'bug修复率']
        
        # 初始化挖掘器和检测器
        miner = KPIAssociationMiner()
        detector = KPIAssociationAnomalyDetector(miner)
        
        print("1. 构建关联关系基线...")
        baseline_results = detector.build_baseline(df, metric_columns)
        
        detection_rules = baseline_results.get('detection_rules', [])
        print(f"   构建了 {len(detection_rules)} 个检测规则")
        
        if detection_rules:
            print("   检测规则:")
            for i, rule in enumerate(detection_rules[:3], 1):
                if rule['type'] == 'correlation':
                    print(f"     {i}. 相关性规则: {rule['source']} <-> {rule['target']} "
                          f"(预期相关性: {rule['expected_correlation']:.3f})")
        
        # 创建异常数据
        print("\n2. 创建异常数据...")
        anomaly_data = df.copy()
        
        # 模拟异常：项目数量增加，但执行用例数减少
        if '项目数量' in anomaly_data.columns and '执行用例数' in anomaly_data.columns:
            anomaly_data['项目数量'] = anomaly_data['项目数量'] * 1.5
            anomaly_data['执行用例数'] = anomaly_data['执行用例数'] * 0.7
            print("   模拟异常: 项目数量增加50%，执行用例数减少30%")
        
        # 检测异常
        print("\n3. 检测关联关系异常...")
        anomalies = detector.detect_association_anomalies(anomaly_data, metric_columns)
        
        # 分析异常结果
        print("\n4. 异常检测结果:")
        summary = anomalies.get('summary', {})
        print(f"   总异常数量: {summary.get('total_anomalies', 0)}")
        print(f"   相关性异常: {summary.get('correlation_anomalies', 0)}")
        print(f"   因果关系异常: {summary.get('causality_anomalies', 0)}")
        print(f"   高严重性异常: {summary.get('high_severity', 0)}")
        
        # 生成洞察
        print("\n5. 异常洞察:")
        insights = detector.generate_anomaly_insights(anomalies)
        for i, insight in enumerate(insights[:3], 1):
            print(f"   {i}. {insight}")
        
        return True
        
    except Exception as e:
        print(f"异常检测测试失败: {e}")
        return False


def main():
    """主函数"""
    print("简化的KPI数据挖掘功能测试")
    print("本测试将验证核心的数据挖掘功能")
    
    results = []
    
    try:
        # 运行各个测试
        results.append(("基础关联关系挖掘", test_basic_association_mining()))
        results.append(("互信息分析", test_mutual_information()))
        results.append(("因果关系分析", test_causality_analysis()))
        results.append(("异常检测", test_association_anomaly_detection()))
        
        # 显示测试结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for test_name, success in results:
            status = "✓ 通过" if success else "✗ 失败"
            print(f"{test_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n总体结果: {passed}/{total} 个测试通过")
        
        if passed == total:
            print("\n🎉 所有数据挖掘功能测试通过！")
            print("\n数据挖掘功能特点:")
            print("1. ✓ 相关性分析 - 发现指标间的线性关系")
            print("2. ✓ 互信息分析 - 发现指标间的非线性关系")
            print("3. ✓ 因果关系分析 - 发现指标间的时序关系")
            print("4. ✓ 异常检测 - 基于关联关系变化检测异常")
            print("5. ✓ 业务洞察 - 生成可理解的业务建议")
            
            print("\n使用建议:")
            print("- 使用 --associations 参数进行专门的关联关系分析")
            print("- 结合业务背景理解关联关系结果")
            print("- 关注高严重性的关联关系异常")
            print("- 定期更新关联关系基线")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败，请检查相关功能")
        
        # 清理测试文件
        test_files = ["simple_test_data.xlsx", "time_series_test_data.xlsx"]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"已清理测试文件: {file}")
        
    except Exception as e:
        logger.error(f"数据挖掘测试失败: {e}")
        print(f"\n错误: {e}")
        print("请检查依赖包是否正确安装")


if __name__ == "__main__":
    main()
