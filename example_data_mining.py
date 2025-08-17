#!/usr/bin/env python3
"""
KPI数据挖掘功能使用示例
演示如何使用关联关系挖掘和基于关联关系的异常检测
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.excel_reader import ExcelKPIReader, create_sample_excel
from analysis.kpi_association_miner import KPIAssociationMiner, KPIAssociationAnomalyDetector
from kpi_excel_analyzer import KPIExcelAnalyzer
from loguru import logger


def example_1_basic_association_mining():
    """示例1: 基础关联关系挖掘"""
    print("=" * 60)
    print("示例1: 基础关联关系挖掘")
    print("=" * 60)
    
    # 1. 创建示例数据
    print("1. 创建示例数据...")
    sample_file = create_sample_excel("mining_sample_data.xlsx")
    print(f"   示例文件已创建: {sample_file}")
    
    # 2. 初始化关联关系挖掘器
    print("\n2. 初始化关联关系挖掘器...")
    miner = KPIAssociationMiner()
    
    # 3. 读取数据
    print("\n3. 读取数据...")
    reader = ExcelKPIReader(sample_file)
    data = reader.read_excel()
    column_info = reader.detect_columns()
    
    print(f"   数据形状: {data.shape}")
    print(f"   指标数量: {len(column_info['metric_columns'])}")
    print(f"   指标列表: {column_info['metric_columns']}")
    
    # 4. 进行关联关系挖掘
    print("\n4. 进行关联关系挖掘...")
    association_results = miner.discover_associations(
        data=data,
        metric_columns=column_info['metric_columns']
    )
    
    # 5. 分析结果
    print("\n5. 分析结果:")
    
    # 相关性分析
    correlations = association_results.get('correlations', {})
    strong_corrs = correlations.get('strong_correlations', [])
    print(f"   强相关性关系数量: {len(strong_corrs)}")
    
    if strong_corrs:
        print("   前3个强相关性关系:")
        for i, corr in enumerate(strong_corrs[:3], 1):
            print(f"     {i}. {corr['pair']} ({corr['method']}: {corr['correlation']:.3f})")
    
    # 互信息分析
    mutual_info = association_results.get('mutual_info', {})
    strong_mi = mutual_info.get('strong_relationships', [])
    print(f"   强互信息关系数量: {len(strong_mi)}")
    
    if strong_mi:
        print("   前3个强互信息关系:")
        for i, mi in enumerate(strong_mi[:3], 1):
            print(f"     {i}. {mi['source']} -> {mi['target']} (MI: {mi['mi_score']:.3f})")
    
    # 因果关系分析
    causality = association_results.get('causal_relationships', {})
    causal_chains = causality.get('causal_chains', [])
    print(f"   因果关系链数量: {len(causal_chains)}")
    
    if causal_chains:
        print("   前3个因果关系链:")
        for i, chain in enumerate(causal_chains[:3], 1):
            print(f"     {i}. {chain['source']} -> {chain['target']} "
                  f"(滞后{chain['lag']}期, 相关性: {chain['correlation']:.3f})")
    
    # 关联规则
    association_rules = association_results.get('association_rules', {})
    strong_rules = association_rules.get('strong_rules', [])
    print(f"   强关联规则数量: {len(strong_rules)}")
    
    return association_results


def example_2_causal_relationship_analysis():
    """示例2: 因果关系分析"""
    print("\n" + "=" * 60)
    print("示例2: 因果关系分析")
    print("=" * 60)
    
    # 使用示例文件
    sample_file = "mining_sample_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 读取数据
    reader = ExcelKPIReader(sample_file)
    data = reader.read_excel()
    column_info = reader.detect_columns()
    
    # 进行因果关系分析
    miner = KPIAssociationMiner()
    causality_results = miner._analyze_causality(data, column_info['metric_columns'])
    
    print("因果关系分析结果:")
    
    # 分析滞后相关性
    lag_correlations = causality_results.get('lag_correlations', {})
    print(f"滞后相关性关系数量: {len(lag_correlations)}")
    
    for pair, lag_corrs in lag_correlations.items():
        if lag_corrs:
            # 找到最强的滞后相关性
            best_lag = max(lag_corrs, key=lambda x: abs(x['correlation']))
            if abs(best_lag['correlation']) > 0.5:
                print(f"  {pair}: 最强滞后相关性在滞后{best_lag['lag']}期 "
                      f"(相关性: {best_lag['correlation']:.3f}, p值: {best_lag['p_value']:.3f})")
    
    # 分析因果图
    causal_graph = causality_results.get('causal_graph')
    if causal_graph and len(causal_graph.edges()) > 0:
        print(f"\n因果图分析:")
        print(f"  节点数量: {causal_graph.number_of_nodes()}")
        print(f"  边数量: {causal_graph.number_of_edges()}")
        
        # 找到最强的因果关系
        strongest_edge = max(causal_graph.edges(data=True), 
                           key=lambda x: abs(x[2].get('correlation', 0)))
        print(f"  最强因果关系: {strongest_edge[0]} -> {strongest_edge[1]} "
              f"(相关性: {strongest_edge[2].get('correlation', 0):.3f})")


def example_3_association_anomaly_detection():
    """示例3: 基于关联关系的异常检测"""
    print("\n" + "=" * 60)
    print("示例3: 基于关联关系的异常检测")
    print("=" * 60)
    
    # 使用示例文件
    sample_file = "mining_sample_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 读取数据
    reader = ExcelKPIReader(sample_file)
    data = reader.read_excel()
    column_info = reader.detect_columns()
    
    # 初始化关联关系挖掘器和异常检测器
    miner = KPIAssociationMiner()
    detector = KPIAssociationAnomalyDetector(miner)
    
    # 构建基线
    print("1. 构建关联关系基线...")
    baseline_results = detector.build_baseline(data, column_info['metric_columns'])
    
    detection_rules = baseline_results.get('detection_rules', [])
    print(f"   构建了 {len(detection_rules)} 个检测规则")
    
    # 显示检测规则
    print("\n2. 检测规则详情:")
    for i, rule in enumerate(detection_rules[:5], 1):  # 只显示前5个
        if rule['type'] == 'correlation':
            print(f"   {i}. 相关性规则: {rule['source']} <-> {rule['target']} "
                  f"(预期相关性: {rule['expected_correlation']:.3f})")
        elif rule['type'] == 'causality':
            print(f"   {i}. 因果关系规则: {rule['source']} -> {rule['target']} "
                  f"(滞后{rule['lag']}期, 预期相关性: {rule['expected_correlation']:.3f})")
    
    # 创建异常数据（模拟项目增加但执行用例数减少的情况）
    print("\n3. 创建异常数据...")
    anomaly_data = data.copy()
    
    # 模拟异常：项目数量增加，但执行用例数减少
    if '项目数量' in anomaly_data.columns and '执行用例数' in anomaly_data.columns:
        # 增加项目数量
        anomaly_data['项目数量'] = anomaly_data['项目数量'] * 1.5
        # 减少执行用例数（异常情况）
        anomaly_data['执行用例数'] = anomaly_data['执行用例数'] * 0.7
        
        print("   模拟异常: 项目数量增加50%，执行用例数减少30%")
    
    # 检测异常
    print("\n4. 检测关联关系异常...")
    anomalies = detector.detect_association_anomalies(
        anomaly_data, column_info['metric_columns']
    )
    
    # 分析异常结果
    print("\n5. 异常检测结果:")
    summary = anomalies.get('summary', {})
    print(f"   总异常数量: {summary.get('total_anomalies', 0)}")
    print(f"   相关性异常: {summary.get('correlation_anomalies', 0)}")
    print(f"   因果关系异常: {summary.get('causality_anomalies', 0)}")
    print(f"   高严重性异常: {summary.get('high_severity', 0)}")
    
    # 生成洞察
    print("\n6. 异常洞察:")
    insights = detector.generate_anomaly_insights(anomalies)
    for i, insight in enumerate(insights[:3], 1):  # 只显示前3个
        print(f"   {i}. {insight}")


def example_4_comprehensive_data_mining():
    """示例4: 综合数据挖掘分析"""
    print("\n" + "=" * 60)
    print("示例4: 综合数据挖掘分析")
    print("=" * 60)
    
    # 使用主分析器进行综合数据挖掘
    analyzer = KPIExcelAnalyzer()
    
    # 使用示例文件
    sample_file = "mining_sample_data.xlsx"
    if not os.path.exists(sample_file):
        print("请先运行示例1创建示例文件")
        return
    
    # 进行关联关系分析
    print("进行综合关联关系分析...")
    results = analyzer.analyze_associations(sample_file)
    
    # 分析结果
    association_results = results['association_results']
    baseline_results = results['baseline_results']
    insights = results['insights']
    
    print("\n=== 综合数据挖掘结果 ===")
    
    # 关联关系摘要
    summary = association_results.get('summary', {})
    print(f"强相关性关系: {summary.get('total_strong_correlations', 0)}")
    print(f"强互信息关系: {summary.get('total_strong_mi_relationships', 0)}")
    print(f"强关联规则: {summary.get('total_strong_rules', 0)}")
    print(f"因果关系链: {summary.get('total_causal_chains', 0)}")
    
    # 检测规则
    detection_rules = baseline_results.get('detection_rules', [])
    print(f"检测规则数量: {len(detection_rules)}")
    
    # 关键洞察
    print(f"\n关键洞察数量: {len(insights)}")
    if insights:
        print("前5个关键洞察:")
        for i, insight in enumerate(insights[:5], 1):
            print(f"  {i}. {insight}")
    
    # 业务价值分析
    print(f"\n=== 业务价值分析 ===")
    
    # 识别关键指标关系
    strong_corrs = association_results.get('correlations', {}).get('strong_correlations', [])
    if strong_corrs:
        print("关键指标关系:")
        for corr in strong_corrs[:3]:
            metric1, metric2 = corr['pair'].split('__')
            print(f"  - {metric1} 与 {metric2} 强相关 "
                  f"({corr['method']}: {corr['correlation']:.3f})")
    
    # 识别因果关系
    causal_chains = association_results.get('causal_relationships', {}).get('causal_chains', [])
    if causal_chains:
        print("\n关键因果关系:")
        for chain in causal_chains[:3]:
            print(f"  - {chain['source']} 影响 {chain['target']} "
                  f"(滞后{chain['lag']}期, 相关性: {chain['correlation']:.3f})")
    
    return results


def example_5_real_world_scenarios():
    """示例5: 真实场景模拟"""
    print("\n" + "=" * 60)
    print("示例5: 真实场景模拟")
    print("=" * 60)
    
    # 创建更真实的KPI数据
    print("1. 创建真实场景数据...")
    
    # 模拟真实的部门KPI数据
    departments = ['技术部', '产品部', '运营部', '市场部', '销售部']
    metrics = ['项目数量', '在编人数', '执行用例数', '自动化执行用例数', 
               '代码覆盖率', 'bug修复率', '项目交付率', '客户满意度']
    
    # 创建基础数据
    data = []
    for dept in departments:
        row = {'部门名称': dept}
        
        # 为每个指标生成基础值
        for metric in metrics:
            if '项目' in metric:
                base_value = np.random.randint(5, 20)
            elif '人数' in metric:
                base_value = np.random.randint(20, 100)
            elif '用例' in metric:
                base_value = np.random.randint(500, 2000)
            elif '率' in metric:
                base_value = np.random.uniform(0.7, 0.95)
            elif '满意度' in metric:
                base_value = np.random.uniform(3.5, 4.5)
            else:
                base_value = np.random.uniform(50, 200)
            
            row[metric] = round(base_value, 2)
        
        data.append(row)
    
    # 添加时间序列数据
    quarters = ['2025Q1', '2025Q2', '2025Q3']
    for quarter in quarters:
        for dept in departments:
            row = {'部门名称': dept}
            
            for metric in metrics:
                # 添加一些趋势和相关性
                base_value = data[departments.index(dept)][metric]
                
                if '项目' in metric:
                    # 项目数量随时间增长
                    trend = 1.0 + (quarters.index(quarter) * 0.1)
                    value = base_value * trend + np.random.normal(0, 0.1 * base_value)
                elif '用例' in metric:
                    # 执行用例数与项目数量相关
                    project_value = data[departments.index(dept)]['项目数量']
                    correlation = 0.8  # 强相关性
                    value = base_value * (1 + correlation * (project_value / 10 - 1)) + np.random.normal(0, 0.05 * base_value)
                elif '率' in metric:
                    # 比率相对稳定
                    value = base_value + np.random.normal(0, 0.02)
                else:
                    # 其他指标
                    value = base_value + np.random.normal(0, 0.1 * base_value)
                
                row[f"{quarter}_{metric}"] = max(0, round(value, 2))
            
            data.append(row)
    
    # 保存到Excel
    real_data_file = "real_scenario_data.xlsx"
    df = pd.DataFrame(data)
    df.to_excel(real_data_file, index=False)
    print(f"   真实场景数据已创建: {real_data_file}")
    
    # 2. 进行关联关系挖掘
    print("\n2. 进行关联关系挖掘...")
    analyzer = KPIExcelAnalyzer()
    results = analyzer.analyze_associations(real_data_file)
    
    # 3. 分析业务洞察
    print("\n3. 业务洞察分析:")
    association_results = results['association_results']
    
    # 分析项目与用例的关系
    correlations = association_results.get('correlations', {})
    strong_corrs = correlations.get('strong_correlations', [])
    
    project_case_corrs = [corr for corr in strong_corrs 
                         if '项目' in corr['pair'] and '用例' in corr['pair']]
    
    if project_case_corrs:
        print("项目与用例关系分析:")
        for corr in project_case_corrs:
            print(f"  - {corr['pair']}: {corr['correlation']:.3f} ({corr['method']})")
    
    # 分析因果关系
    causality = association_results.get('causal_relationships', {})
    causal_chains = causality.get('causal_chains', [])
    
    project_causal = [chain for chain in causal_chains 
                     if '项目' in chain['source'] or '项目' in chain['target']]
    
    if project_causal:
        print("\n项目相关因果关系:")
        for chain in project_causal:
            print(f"  - {chain['source']} -> {chain['target']} "
                  f"(滞后{chain['lag']}期, 相关性: {chain['correlation']:.3f})")
    
    # 4. 模拟异常场景
    print("\n4. 模拟异常场景...")
    
    # 创建异常数据：项目增加但用例减少
    anomaly_data = df.copy()
    for i, row in anomaly_data.iterrows():
        if '项目数量' in row and pd.notna(row['项目数量']):
            # 项目数量增加
            anomaly_data.at[i, '项目数量'] = row['项目数量'] * 1.3
        if '执行用例数' in row and pd.notna(row['执行用例数']):
            # 执行用例数减少（异常）
            anomaly_data.at[i, '执行用例数'] = row['执行用例数'] * 0.6
    
    # 保存异常数据
    anomaly_file = "anomaly_scenario_data.xlsx"
    anomaly_data.to_excel(anomaly_file, index=False)
    print(f"   异常场景数据已创建: {anomaly_file}")
    
    # 5. 检测异常
    print("\n5. 检测异常...")
    miner = KPIAssociationMiner()
    detector = KPIAssociationAnomalyDetector(miner)
    
    # 使用原始数据构建基线
    baseline = detector.build_baseline(df, metrics)
    
    # 使用异常数据检测异常
    anomalies = detector.detect_association_anomalies(anomaly_data, metrics)
    
    # 分析异常结果
    print("\n6. 异常检测结果:")
    summary = anomalies.get('summary', {})
    print(f"   检测到 {summary.get('total_anomalies', 0)} 个关联关系异常")
    print(f"   其中 {summary.get('high_severity', 0)} 个高严重性异常")
    
    # 生成洞察
    insights = detector.generate_anomaly_insights(anomalies)
    if insights:
        print("\n异常洞察:")
        for i, insight in enumerate(insights[:3], 1):
            print(f"  {i}. {insight}")
    
    return results


def main():
    """主函数"""
    print("KPI数据挖掘功能使用示例")
    print("本示例将演示如何使用关联关系挖掘和基于关联关系的异常检测")
    
    try:
        # 运行所有示例
        example_1_basic_association_mining()
        example_2_causal_relationship_analysis()
        example_3_association_anomaly_detection()
        example_4_comprehensive_data_mining()
        example_5_real_world_scenarios()
        
        print("\n" + "=" * 60)
        print("所有数据挖掘示例运行完成！")
        print("=" * 60)
        
        print("\n生成的文件:")
        print("- mining_sample_data.xlsx (基础示例数据)")
        print("- real_scenario_data.xlsx (真实场景数据)")
        print("- anomaly_scenario_data.xlsx (异常场景数据)")
        
        print("\n数据挖掘功能特点:")
        print("1. 自动发现指标间的相关性、互信息和因果关系")
        print("2. 构建关联关系基线，用于异常检测")
        print("3. 基于关联关系变化检测异常情况")
        print("4. 支持复杂的业务场景分析")
        print("5. 提供详细的业务洞察和建议")
        
        print("\n使用建议:")
        print("1. 使用 --associations 参数进行专门的关联关系分析")
        print("2. 结合业务背景理解关联关系结果")
        print("3. 定期更新关联关系基线")
        print("4. 关注高严重性的关联关系异常")
        
    except Exception as e:
        logger.error(f"数据挖掘示例运行失败: {e}")
        print(f"\n错误: {e}")
        print("请检查依赖包是否正确安装")


if __name__ == "__main__":
    main()
