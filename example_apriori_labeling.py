#!/usr/bin/env python3
"""
基于Apriori关联规则的数据标签分类示例
演示如何使用关联规则对项目数据进行标签分类，特别是识别符合前置条件但不符合后置条件的异常数据
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from analysis.project_data_miner import ProjectDataMiner
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    print(f"分析模块导入失败: {e}")
    ANALYSIS_AVAILABLE = False


def create_enhanced_project_data():
    """创建包含更明显规律的项目数据"""
    print("创建增强的项目数据...")
    
    np.random.seed(42)
    n_projects = 150
    
    project_types = ['Web应用', '移动应用', 'API服务', '桌面应用', '大数据平台']
    project_levels = ['P0', 'P1', 'P2', 'P3']
    product_lines = ['电商平台', '金融服务', '社交媒体', '企业服务', '游戏娱乐']
    organizations = ['质量部门A', '质量部门B', '质量部门C', '外包团队D', '外包团队E']
    
    data = []
    
    for i in range(n_projects):
        project_type = np.random.choice(project_types)
        project_level = np.random.choice(project_levels)
        product_line = np.random.choice(product_lines)
        organization = np.random.choice(organizations)
        
        # 创建一些明确的关联规律
        
        # 规律1: Web应用 + P0级别 -> 高自动化率 (80%概率)
        if project_type == 'Web应用' and project_level == 'P0':
            if np.random.random() < 0.8:  # 80%概率遵循规律
                automation_rate = np.random.uniform(0.7, 0.9)
            else:  # 20%概率异常（不遵循规律）
                automation_rate = np.random.uniform(0.2, 0.5)
        else:
            automation_rate = np.random.uniform(0.3, 0.7)
        
        # 规律2: 金融服务 + 质量部门A -> 低缺陷率 (75%概率)
        if product_line == '金融服务' and organization == '质量部门A':
            if np.random.random() < 0.75:  # 75%概率遵循规律
                bug_rate = np.random.uniform(0.02, 0.05)
            else:  # 25%概率异常
                bug_rate = np.random.uniform(0.08, 0.15)
        else:
            bug_rate = np.random.uniform(0.05, 0.12)
        
        # 规律3: P0级别 + API服务 -> 高投入工时 (70%概率)
        if project_level == 'P0' and project_type == 'API服务':
            if np.random.random() < 0.7:  # 70%概率遵循规律
                effort_multiplier = np.random.uniform(1.5, 2.0)
            else:  # 30%概率异常
                effort_multiplier = np.random.uniform(0.8, 1.2)
        else:
            effort_multiplier = np.random.uniform(0.8, 1.5)
        
        # 基础指标计算
        level_multiplier = {'P0': 2.5, 'P1': 2.0, 'P2': 1.5, 'P3': 1.0}[project_level]
        
        executed_cases = max(20, int(np.random.normal(100 * level_multiplier, 30)))
        automated_cases = int(executed_cases * automation_rate)
        related_bugs = max(1, int(executed_cases * bug_rate))
        effort_hours = max(20, int(executed_cases * 0.5 * effort_multiplier))
        
        data.append({
            '项目名称': f'项目_{product_line}_{project_type}_{i+1:03d}',
            '项目编号': f'PRJ-{i+1:04d}',
            '项目类型': project_type,
            '项目级别': project_level,
            '产品线': product_line,
            '产品类型': np.random.choice(['前端', '后端', '数据库', '中间件']),
            '测试负责人': f'测试员{np.random.randint(1, 16):02d}',
            '测试负责人所属组织架构': organization,
            '执行用例数': executed_cases,
            '自动化执行用例数': automated_cases,
            '关联缺陷': related_bugs,
            '投入工时': effort_hours
        })
    
    df = pd.DataFrame(data)
    
    # 计算衍生指标用于验证
    df['自动化率'] = df['自动化执行用例数'] / df['执行用例数']
    df['缺陷密度'] = df['关联缺陷'] / df['执行用例数']
    df['测试效率'] = df['执行用例数'] / df['投入工时']
    
    # 保存数据
    output_file = 'enhanced_project_data.xlsx'
    df.to_excel(output_file, index=False)
    print(f"增强的测试数据已保存到: {output_file}")
    
    return df


def demonstrate_apriori_labeling():
    """演示Apriori规则标签分类"""
    print("\n" + "=" * 80)
    print("演示Apriori关联规则的数据标签分类")
    print("=" * 80)
    
    if not ANALYSIS_AVAILABLE:
        print("分析模块不可用，请检查依赖")
        return
    
    # 创建测试数据
    project_data = create_enhanced_project_data()
    
    # 初始化挖掘器
    config = {
        'min_support': 0.05,     # 降低支持度阈值以发现更多规则
        'min_confidence': 0.6,   # 中等置信度
        'min_lift': 1.2,
        'correlation_threshold': 0.6
    }
    
    print(f"\n1. 初始化项目数据挖掘器...")
    print(f"   配置: {config}")
    
    miner = ProjectDataMiner(config)
    
    # 执行关联规则挖掘
    print(f"\n2. 执行关联规则挖掘...")
    results = miner.discover_project_associations(project_data.drop(['自动化率', '缺陷密度', '测试效率'], axis=1))
    
    # 查看发现的关联规则
    association_rules = results.get('categorical_associations', {}).get('association_rules', [])
    print(f"\n3. 发现的关联规则数量: {len(association_rules)}")
    
    if association_rules:
        print("\n   前5个关联规则:")
        for i, rule in enumerate(association_rules[:5], 1):
            antecedents = ' & '.join(rule.get('antecedents', []))
            consequents = ' & '.join(rule.get('consequents', []))
            confidence = rule.get('confidence', 0)
            support = rule.get('support', 0)
            lift = rule.get('lift', 1)
            
            print(f"     {i}. {antecedents} => {consequents}")
            print(f"        置信度: {confidence:.3f}, 支持度: {support:.3f}, 提升度: {lift:.3f}")
    
    # 查看标签分类结果
    labeled_data = results.get('labeled_data')
    if labeled_data is not None:
        print(f"\n4. 数据标签分类结果:")
        
        # 统计各类别数量
        category_counts = labeled_data['data_category'].value_counts()
        print(f"   数据分类统计:")
        for category, count in category_counts.items():
            print(f"     {category}: {count} 项 ({count/len(labeled_data):.1%})")
        
        # 显示异常数据示例
        anomaly_data = labeled_data[labeled_data['data_category'].str.contains('异常', na=False)]
        if len(anomaly_data) > 0:
            print(f"\n5. 异常数据示例 (前5项):")
            anomaly_sample = anomaly_data[['项目名称', '项目类型', '项目级别', '产品线', 
                                         'rule_violations', 'anomaly_score', 'data_category']].head(5)
            
            for idx, row in anomaly_sample.iterrows():
                print(f"\n     项目: {row['项目名称']}")
                print(f"     类型: {row['项目类型']}, 级别: {row['项目级别']}, 产品线: {row['产品线']}")
                print(f"     违反规则: {row['rule_violations'][:100]}...")  # 截取前100字符
                print(f"     异常评分: {row['anomaly_score']:.3f}")
                print(f"     分类: {row['data_category']}")
        
        # 规则遵循报告
        rule_compliance_report = results.get('rule_compliance_report', {})
        if rule_compliance_report and 'rule_details' in rule_compliance_report:
            print(f"\n6. 规则遵循情况:")
            rule_details = rule_compliance_report['rule_details']
            
            for rule_stat in rule_details[:3]:  # 显示前3个规则的统计
                print(f"\n     {rule_stat['rule_name']}:")
                print(f"     前置条件: {rule_stat['antecedents']}")
                print(f"     后置条件: {rule_stat['consequents']}")
                print(f"     期望置信度: {rule_stat['expected_confidence']:.3f}")
                print(f"     实际置信度: {rule_stat['actual_confidence']:.3f}")
                print(f"     违反数量: {rule_stat['violation_count']}/{rule_stat['antecedent_count']}")
                print(f"     违反率: {rule_stat['violation_rate']:.1%}")
        
        # 异常模式分析
        anomaly_patterns = results.get('anomaly_patterns', {})
        if anomaly_patterns and 'common_violation_patterns' in anomaly_patterns:
            print(f"\n7. 常见违反模式:")
            violation_patterns = anomaly_patterns['common_violation_patterns']
            
            for pattern in violation_patterns[:3]:  # 显示前3个常见模式
                print(f"     模式: {pattern['pattern'][:80]}...")  # 截取前80字符
                print(f"     出现次数: {pattern['count']}")
                print(f"     出现率: {pattern['rate']:.1%}")
                print()
        
        return labeled_data, results
    
    else:
        print("   未能进行数据标签分类")
        return None, results


def analyze_specific_violations(labeled_data: pd.DataFrame):
    """分析具体的违反情况"""
    print("\n" + "=" * 80)
    print("具体违反情况分析")
    print("=" * 80)
    
    if labeled_data is None:
        print("没有标签数据可供分析")
        return
    
    # 使用标准化后的列名
    project_type_col = 'project_type' if 'project_type' in labeled_data.columns else '项目类型'
    project_level_col = 'project_level' if 'project_level' in labeled_data.columns else '项目级别'
    project_name_col = 'project_name' if 'project_name' in labeled_data.columns else '项目名称'
    test_owner_org_col = 'test_owner_org' if 'test_owner_org' in labeled_data.columns else '测试负责人所属组织架构'
    
    # 分析每种项目类型的违反情况
    print("\n1. 按项目类型分析违反情况:")
    if project_type_col in labeled_data.columns:
        type_violation_stats = labeled_data.groupby(project_type_col).agg({
            'rule_violations': lambda x: sum(1 for v in x if v),
            'anomaly_score': 'mean',
            project_name_col: 'count'
        }).round(3)
        type_violation_stats.columns = ['违反规则项目数', '平均异常评分', '总项目数']
        type_violation_stats['违反率'] = (type_violation_stats['违反规则项目数'] / 
                                      type_violation_stats['总项目数']).round(3)
        
        print(type_violation_stats)
    else:
        print("   未找到项目类型字段")
    
    # 分析每种项目级别的违反情况
    print("\n2. 按项目级别分析违反情况:")
    if project_level_col in labeled_data.columns:
        level_violation_stats = labeled_data.groupby(project_level_col).agg({
            'rule_violations': lambda x: sum(1 for v in x if v),
            'anomaly_score': 'mean',
            project_name_col: 'count'
        }).round(3)
        level_violation_stats.columns = ['违反规则项目数', '平均异常评分', '总项目数']
        level_violation_stats['违反率'] = (level_violation_stats['违反规则项目数'] / 
                                       level_violation_stats['总项目数']).round(3)
        
        print(level_violation_stats)
    else:
        print("   未找到项目级别字段")
    
    # 分析高风险项目特征
    high_risk_projects = labeled_data[labeled_data['anomaly_score'] > 1.0]
    if len(high_risk_projects) > 0:
        print(f"\n3. 高风险项目特征分析 ({len(high_risk_projects)} 个项目):")
        
        if project_type_col in high_risk_projects.columns:
            print("\n   项目类型分布:")
            type_dist = high_risk_projects[project_type_col].value_counts(normalize=True)
            for ptype, ratio in type_dist.items():
                print(f"     {ptype}: {ratio:.1%}")
        
        if project_level_col in high_risk_projects.columns:
            print("\n   项目级别分布:")
            level_dist = high_risk_projects[project_level_col].value_counts(normalize=True)
            for level, ratio in level_dist.items():
                print(f"     {level}: {ratio:.1%}")
        
        if test_owner_org_col in high_risk_projects.columns:
            print("\n   组织架构分布:")
            org_dist = high_risk_projects[test_owner_org_col].value_counts(normalize=True)
            for org, ratio in org_dist.items():
                print(f"     {org}: {ratio:.1%}")
    else:
        print("\n3. 未发现高风险项目")


def generate_improvement_recommendations(labeled_data: pd.DataFrame, results: Dict):
    """基于违反规则的分析生成改进建议"""
    print("\n" + "=" * 80)
    print("改进建议生成")
    print("=" * 80)
    
    if labeled_data is None:
        print("没有数据可供分析")
        return
    
    recommendations = []
    
    # 使用标准化后的列名
    project_name_col = 'project_name' if 'project_name' in labeled_data.columns else '项目名称'
    
    # 基于违反率生成建议
    violation_data = labeled_data[labeled_data['rule_violations'] != '']
    
    if len(violation_data) > 0:
        violation_rate = len(violation_data) / len(labeled_data)
        print(f"总体违反率: {violation_rate:.1%}")
        
        if violation_rate > 0.2:
            recommendations.append("整体违反率偏高，建议系统性审查测试流程和质量控制标准")
        
        # 分析最常违反的规则
        rule_compliance_report = results.get('rule_compliance_report', {})
        if 'summary' in rule_compliance_report:
            high_violation_rules = rule_compliance_report['summary'].get('high_violation_rules', [])
            
            for rule in high_violation_rules:
                antecedents = rule['antecedents']
                consequents = rule['consequents']
                violation_rate = rule['violation_rate']
                
                recommendations.append(
                    f"针对'{antecedents}'项目，需要重点关注'{consequents}'指标，"
                    f"当前违反率为{violation_rate:.1%}"
                )
        
        # 基于异常模式生成建议
        anomaly_patterns = results.get('anomaly_patterns', {})
        if 'anomaly_distribution' in anomaly_patterns:
            for field, distribution in anomaly_patterns['anomaly_distribution'].items():
                if distribution:
                    top_anomaly = max(distribution.items(), key=lambda x: x[1])
                    recommendations.append(
                        f"{field}中'{top_anomaly[0]}'的异常率最高({top_anomaly[1]:.1%})，需要重点关注"
                    )
    
    print("\n改进建议:")
    for i, rec in enumerate(recommendations[:8], 1):  # 最多显示8条建议
        print(f"  {i}. {rec}")
    
    if not recommendations:
        print("  当前数据质量良好，未发现明显的改进点")


def main():
    """主函数"""
    print("基于Apriori关联规则的数据标签分类演示")
    print("=" * 60)
    
    try:
        # 执行演示
        labeled_data, results = demonstrate_apriori_labeling()
        
        if labeled_data is not None:
            # 分析具体违反情况
            analyze_specific_violations(labeled_data)
            
            # 生成改进建议
            generate_improvement_recommendations(labeled_data, results)
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("\n说明:")
        print("- 'rule_violations': 记录了违反的具体规则")
        print("- 'anomaly_flags': 标识了符合前置但不符合后置条件的情况")
        print("- 'anomaly_score': 异常评分，越高表示越异常")
        print("- 'data_category': 数据分类（规则符合/低中高风险异常/未匹配规则）")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()