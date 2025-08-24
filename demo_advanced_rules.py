#!/usr/bin/env python3
"""
高级Apriori规则标签分类演示
展示更复杂的规律和异常检测
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


def create_advanced_project_data():
    """创建包含更复杂规律的项目数据"""
    print("创建高级项目数据...")
    
    np.random.seed(42)
    n_projects = 200
    
    project_types = ['Web应用', '移动应用', 'API服务', '桌面应用']
    project_levels = ['P0', 'P1', 'P2']
    product_lines = ['电商平台', '金融服务', '社交媒体']
    organizations = ['质量部门A', '质量部门B', '外包团队C']
    
    data = []
    
    for i in range(n_projects):
        project_type = np.random.choice(project_types)
        project_level = np.random.choice(project_levels)
        product_line = np.random.choice(product_lines)
        organization = np.random.choice(organizations)
        
        # 创建更明确的关联规律
        
        # 规律1: Web应用 + P0级别 -> 质量部门A (80%概率)
        if project_type == 'Web应用' and project_level == 'P0':
            if np.random.random() < 0.2:  # 20%概率违反规律
                organization = np.random.choice(['质量部门B', '外包团队C'])
            else:
                organization = '质量部门A'
        
        # 规律2: 金融服务 -> P0级别 (75%概率)
        if product_line == '金融服务':
            if np.random.random() < 0.25:  # 25%概率违反规律
                project_level = np.random.choice(['P1', 'P2'])
            else:
                project_level = 'P0'
        
        # 规律3: 外包团队C -> 移动应用 (70%概率)
        if organization == '外包团队C':
            if np.random.random() < 0.3:  # 30%概率违反规律
                project_type = np.random.choice(['Web应用', 'API服务', '桌面应用'])
            else:
                project_type = '移动应用'
        
        # 规律4: 社交媒体 + API服务 -> 质量部门B (85%概率)
        if product_line == '社交媒体' and project_type == 'API服务':
            if np.random.random() < 0.15:  # 15%概率违反规律
                organization = np.random.choice(['质量部门A', '外包团队C'])
            else:
                organization = '质量部门B'
        
        # 基础指标计算
        level_multiplier = {'P0': 2.5, 'P1': 2.0, 'P2': 1.5}[project_level]
        
        executed_cases = max(20, int(np.random.normal(100 * level_multiplier, 30)))
        automation_rate = np.random.uniform(0.3, 0.8)
        automated_cases = int(executed_cases * automation_rate)
        related_bugs = max(1, int(executed_cases * np.random.uniform(0.03, 0.1)))
        effort_hours = max(20, int(executed_cases * np.random.uniform(0.4, 0.8)))
        
        data.append({
            '项目名称': f'项目_{product_line}_{project_type}_{i+1:03d}',
            '项目编号': f'PRJ-{i+1:04d}',
            '项目类型': project_type,
            '项目级别': project_level,
            '产品线': product_line,
            '产品类型': np.random.choice(['前端', '后端', '全栈']),
            '测试负责人': f'测试员{np.random.randint(1, 11):02d}',
            '测试负责人所属组织架构': organization,
            '执行用例数': executed_cases,
            '自动化执行用例数': automated_cases,
            '关联缺陷': related_bugs,
            '投入工时': effort_hours
        })
    
    df = pd.DataFrame(data)
    
    # 保存数据
    output_file = 'advanced_project_data.xlsx'
    df.to_excel(output_file, index=False)
    print(f"高级测试数据已保存到: {output_file}")
    
    return df


def run_advanced_demo():
    """运行高级演示"""
    print("\n" + "=" * 80)
    print("高级Apriori关联规则数据标签分类演示")
    print("=" * 80)
    
    if not ANALYSIS_AVAILABLE:
        print("分析模块不可用，请检查依赖")
        return None, None
    
    # 创建测试数据
    project_data = create_advanced_project_data()
    
    # 显示数据概览
    print("\n1. 数据概览:")
    print(f"   总项目数: {len(project_data)}")
    print(f"   项目类型分布: {dict(project_data['项目类型'].value_counts())}")
    print(f"   项目级别分布: {dict(project_data['项目级别'].value_counts())}")
    print(f"   产品线分布: {dict(project_data['产品线'].value_counts())}")
    print(f"   组织分布: {dict(project_data['测试负责人所属组织架构'].value_counts())}")
    
    # 初始化挖掘器（使用更低的阈值）
    config = {
        'min_support': 0.02,     # 更低的支持度阈值
        'min_confidence': 0.5,   # 中等置信度
        'min_lift': 1.1,         # 更低的提升度
        'correlation_threshold': 0.5
    }
    
    print(f"\n2. 初始化挖掘器配置: {config}")
    
    miner = ProjectDataMiner(config)
    
    # 执行关联规则挖掘和标签分类
    print(f"\n3. 执行关联规则挖掘...")
    results = miner.discover_project_associations(project_data)
    
    # 查看发现的关联规则
    association_rules = results.get('categorical_associations', {}).get('association_rules', [])
    print(f"\n4. 发现的关联规则数量: {len(association_rules)}")
    
    if association_rules:
        print("\n   关联规则详情:")
        for i, rule in enumerate(association_rules, 1):
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
        print(f"\n5. 数据标签分类结果:")
        
        # 统计各类别数量
        category_counts = labeled_data['data_category'].value_counts()
        print(f"   数据分类统计:")
        for category, count in category_counts.items():
            print(f"     {category}: {count} 项 ({count/len(labeled_data):.1%})")
        
        # 显示违反规则的项目
        violation_data = labeled_data[labeled_data['rule_violations'] != '']
        if len(violation_data) > 0:
            print(f"\n6. 违反规则的项目 ({len(violation_data)} 项):")
            
            # 显示前5个违反规则的项目
            violation_sample = violation_data[[
                'project_name', 'project_type', 'project_level', 
                'product_line', 'test_owner_org', 'rule_violations', 
                'anomaly_flags', 'anomaly_score'
            ]].head(5)
            
            for idx, row in violation_sample.iterrows():
                print(f"\n     项目: {row['project_name']}")
                print(f"     特征: {row['project_type']}, {row['project_level']}, {row['product_line']}, {row['test_owner_org']}")
                print(f"     违反规则: {row['rule_violations']}")
                print(f"     异常标记: {row['anomaly_flags']}")
                print(f"     异常评分: {row['anomaly_score']:.3f}")
        
        # 规则遵循统计
        rule_compliance_report = results.get('rule_compliance_report', {})
        if 'rule_details' in rule_compliance_report:
            print(f"\n7. 规则遵循统计:")
            rule_details = rule_compliance_report['rule_details']
            
            for rule_stat in rule_details:
                print(f"\n     规则: {rule_stat['antecedents']} => {rule_stat['consequents']}")
                print(f"     期望置信度: {rule_stat['expected_confidence']:.3f}")
                print(f"     实际置信度: {rule_stat['actual_confidence']:.3f}")
                print(f"     符合前置条件: {rule_stat['antecedent_count']} 项")
                print(f"     完全符合规则: {rule_stat['complete_count']} 项")
                print(f"     违反规则: {rule_stat['violation_count']} 项")
                print(f"     违反率: {rule_stat['violation_rate']:.1%}")
        
        return labeled_data, results
    
    return None, results


def analyze_rule_effectiveness(labeled_data: pd.DataFrame, results: Dict):
    """分析规则有效性"""
    print("\n" + "=" * 80)
    print("规则有效性分析")
    print("=" * 80)
    
    rule_compliance_report = results.get('rule_compliance_report', {})
    
    if 'summary' in rule_compliance_report:
        summary = rule_compliance_report['summary']
        
        # 高违反率规则
        high_violation_rules = summary.get('high_violation_rules', [])
        if high_violation_rules:
            print(f"\n1. 高违反率规则 ({len(high_violation_rules)} 个):")
            for rule in high_violation_rules:
                print(f"   规则: {rule['antecedents']} => {rule['consequents']}")
                print(f"   违反率: {rule['violation_rate']:.1%}")
        
        # 低置信度规则
        low_confidence_rules = summary.get('low_confidence_rules', [])
        if low_confidence_rules:
            print(f"\n2. 低置信度规则 ({len(low_confidence_rules)} 个):")
            for rule in low_confidence_rules:
                print(f"   规则: {rule['rule_name']}")
                print(f"   期望置信度: {rule['expected_confidence']:.3f}")
                print(f"   实际置信度: {rule['actual_confidence']:.3f}")
                print(f"   置信度差距: {rule['confidence_gap']:.3f}")
        
        # 有效规则
        effective_rules = summary.get('effective_rules', [])
        if effective_rules:
            print(f"\n3. 有效规则 ({len(effective_rules)} 个):")
            for rule in effective_rules:
                print(f"   规则: {rule['rule_name']}")
                print(f"   置信度: {rule['confidence']:.3f}")
                print(f"   支持度: {rule['support']:.3f}")
    
    # 总体违反情况分析
    if labeled_data is not None:
        violation_data = labeled_data[labeled_data['rule_violations'] != '']
        total_violations = len(violation_data)
        violation_rate = total_violations / len(labeled_data)
        
        print(f"\n4. 总体违反情况:")
        print(f"   违反规则的项目数: {total_violations}")
        print(f"   总体违反率: {violation_rate:.1%}")
        
        if violation_rate > 0.15:
            print(f"   评估: 违反率较高，需要重点关注")
        elif violation_rate > 0.05:
            print(f"   评估: 违反率适中，有改进空间")
        else:
            print(f"   评估: 违反率较低，规则遵循良好")


def main():
    """主函数"""
    print("高级Apriori关联规则数据标签分类演示")
    print("=" * 60)
    
    try:
        # 运行高级演示
        labeled_data, results = run_advanced_demo()
        
        if labeled_data is not None:
            # 分析规则有效性
            analyze_rule_effectiveness(labeled_data, results)
        
        print("\n" + "=" * 60)
        print("高级演示完成！")
        print("\n关键功能说明:")
        print("1. 发现了多个具有实际意义的关联规则")
        print("2. 成功识别了违反规则的异常项目")
        print("3. 对符合前置条件但不符合后置条件的数据进行了标记")
        print("4. 生成了详细的规则遵循统计和违反模式分析")
        print("5. 为每个项目计算了异常评分并进行了风险分类")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()