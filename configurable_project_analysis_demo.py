#!/usr/bin/env python3
"""
可配置项目数据Apriori分析示例
演示如何使用可配置分析器进行项目数据关联规则挖掘和标签分类
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from analysis.configurable_project_analyzer import ConfigurableProjectAnalyzer
    ANALYZER_AVAILABLE = True
    print("✅ 可配置项目分析器加载成功")
except ImportError as e:
    print(f"❌ 分析器导入失败: {e}")
    ANALYZER_AVAILABLE = False


def create_sample_english_data():
    """创建英文字段的示例项目数据"""
    print("创建示例项目数据（英文字段）...")
    
    np.random.seed(42)
    n_projects = 150
    
    # 英文字段数据
    project_types = ['Web_App', 'Mobile_App', 'API_Service', 'Desktop_App', 'Data_Platform']
    project_levels = ['P0', 'P1', 'P2', 'P3']
    product_lines = ['E_Commerce', 'Financial_Service', 'Social_Media', 'Enterprise_Service']
    product_types = ['Frontend', 'Backend', 'Full_Stack']
    organizations = ['QA_Team_A', 'QA_Team_B', 'QA_Team_C', 'Outsource_Team_D']
    test_owners = [f'Tester_{i:02d}' for i in range(1, 16)]
    
    data = []
    
    for i in range(n_projects):
        project_type = np.random.choice(project_types)
        project_level = np.random.choice(project_levels)
        product_line = np.random.choice(product_lines)
        product_type = np.random.choice(product_types)
        organization = np.random.choice(organizations)
        test_owner = np.random.choice(test_owners)
        
        # 创建一些关联规律
        
        # 规律1: Web_App + P0 -> QA_Team_A (80%概率)
        if project_type == 'Web_App' and project_level == 'P0':
            if np.random.random() < 0.2:
                organization = np.random.choice(['QA_Team_B', 'QA_Team_C'])
            else:
                organization = 'QA_Team_A'
        
        # 规律2: Financial_Service -> P0 (75%概率)
        if product_line == 'Financial_Service':
            if np.random.random() < 0.25:
                project_level = np.random.choice(['P1', 'P2'])
            else:
                project_level = 'P0'
        
        # 规律3: Mobile_App -> Frontend (70%概率)
        if project_type == 'Mobile_App':
            if np.random.random() < 0.3:
                product_type = np.random.choice(['Backend', 'Full_Stack'])
            else:
                product_type = 'Frontend'
        
        # 基础指标计算
        level_multiplier = {'P0': 2.5, 'P1': 2.0, 'P2': 1.5, 'P3': 1.0}[project_level]
        type_multiplier = {
            'Web_App': 1.2, 'Mobile_App': 1.0, 'API_Service': 0.8, 
            'Desktop_App': 1.1, 'Data_Platform': 1.5
        }[project_type]
        
        base_cases = int(np.random.normal(100 * level_multiplier * type_multiplier, 30))
        executed_cases = max(20, base_cases)
        
        automation_rate = np.random.uniform(0.3, 0.8)
        if project_type in ['API_Service', 'Web_App']:
            automation_rate = np.random.uniform(0.5, 0.9)  # 更高的自动化率
        
        automated_cases = int(executed_cases * automation_rate)
        related_bugs = max(1, int(executed_cases * np.random.uniform(0.02, 0.08)))
        effort_hours = max(20, int(executed_cases * np.random.uniform(0.3, 0.7)))
        
        data.append({
            'project_name': f'Project_{product_line}_{project_type}_{i+1:03d}',
            'project_id': f'PRJ-{i+1:04d}',
            'project_type': project_type,
            'project_level': project_level,
            'product_line': product_line,
            'product_type': product_type,
            'test_owner': test_owner,
            'test_owner_org': organization,
            'executed_cases': executed_cases,
            'automated_cases': automated_cases,
            'related_bugs': related_bugs,
            'effort_hours': effort_hours
        })
    
    df = pd.DataFrame(data)
    
    # 保存数据
    output_file = 'sample_project_data_english.xlsx'
    df.to_excel(output_file, index=False)
    print(f"示例数据已保存到: {output_file}")
    
    return df


def demonstrate_configurable_analysis():
    """演示可配置分析功能"""
    print("\n" + "=" * 80)
    print("可配置项目数据Apriori分析演示")
    print("=" * 80)
    
    if not ANALYZER_AVAILABLE:
        print("分析器不可用，请检查依赖")
        return
    
    # 1. 创建配置模板
    print("\n1. 创建配置模板...")
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)
    
    # 初始化分析器（使用默认配置）
    analyzer = ConfigurableProjectAnalyzer()
    
    # 创建配置模板
    config_file = analyzer.create_config_template()
    print(f"   配置模板已创建: {config_file}")
    
    # 2. 显示字段配置信息
    print("\n2. 字段配置信息:")
    field_info = analyzer.get_field_info()
    print(f"   维度字段（中文）: {field_info['dimension_fields_chinese']}")
    print(f"   指标字段（中文）: {field_info['metric_fields_chinese']}")
    print(f"   字段映射数量: {len(field_info['field_mapping'])}")
    
    # 3. 创建示例数据
    print("\n3. 创建示例数据...")
    project_data = create_sample_english_data()
    print(f"   数据形状: {project_data.shape}")
    print(f"   数据列: {list(project_data.columns)}")
    
    # 4. 验证数据
    print("\n4. 验证数据格式...")
    is_valid, errors = analyzer.validate_data(project_data)
    if is_valid:
        print("   ✅ 数据验证通过")
    else:
        print(f"   ❌ 数据验证失败: {errors}")
        return
    
    # 5. 执行分析
    print("\n5. 执行可配置Apriori分析...")
    
    start_time = datetime.now()
    analysis_results = analyzer.analyze_project_data(project_data)
    end_time = datetime.now()
    
    analysis_duration = (end_time - start_time).total_seconds()
    print(f"   分析耗时: {analysis_duration:.2f}秒")
    
    # 6. 显示分析摘要
    print("\n6. 分析结果摘要:")
    summary = analysis_results['summary']
    
    if 'association_rules' in summary:
        rule_summary = summary['association_rules']
        print(f"   关联规则总数: {rule_summary['total_rules']}")
        print(f"   高置信度规则: {rule_summary['high_confidence_rules']}")
        print(f"   强关联关系: {rule_summary['strong_associations']}")
    
    if 'correlations' in summary:
        corr_summary = summary['correlations']
        print(f"   强相关性数量: {corr_summary['strong_correlations']}")
        if corr_summary['correlation_details']:
            print("   前3个强相关性:")
            for i, corr in enumerate(corr_summary['correlation_details'][:3], 1):
                print(f"     {i}. {corr['field1']} ↔ {corr['field2']}: {corr['correlation']:.3f}")
    
    if 'labeling' in summary:
        label_summary = summary['labeling']
        print(f"   数据标签分类:")
        for category, count in label_summary['category_distribution'].items():
            print(f"     {category}: {count}项")
        print(f"   违反规则项目: {label_summary['violation_count']}项 ({label_summary['violation_rate']:.1%})")
    
    # 7. 显示关联规则详情
    print("\n7. 关联规则详情（前5个）:")
    mining_results = analysis_results['mining_results']
    association_rules = mining_results.get('categorical_associations', {}).get('association_rules', [])
    
    for i, rule in enumerate(association_rules[:5], 1):
        antecedents = ' & '.join(rule.get('antecedents', []))
        consequents = ' & '.join(rule.get('consequents', []))
        confidence = rule.get('confidence', 0)
        support = rule.get('support', 0)
        lift = rule.get('lift', 1)
        
        print(f"   规则{i}: {antecedents} => {consequents}")
        print(f"          置信度: {confidence:.3f}, 支持度: {support:.3f}, 提升度: {lift:.3f}")
    
    # 8. 显示违反规则的项目
    print("\n8. 违反规则的项目示例（前3个）:")
    labeled_data = analysis_results['labeled_data']
    if labeled_data is not None:
        violation_data = labeled_data[labeled_data['rule_violations'] != '']
        
        if len(violation_data) > 0:
            sample_violations = violation_data.head(3)
            for idx, row in sample_violations.iterrows():
                print(f"   项目: {row.get('项目名称', 'N/A')}")
                print(f"   特征: {row.get('项目类型', 'N/A')}, {row.get('项目级别', 'N/A')}")
                print(f"   违反规则: {row.get('rule_violations', 'N/A')}")
                print(f"   异常评分: {row.get('anomaly_score', 0):.3f}")
                print()
        else:
            print("   未发现违反规则的项目")
    
    # 9. 生成报告
    print("\n9. 生成分析报告...")
    try:
        generated_files = analyzer.generate_reports(analysis_results)
        
        if generated_files:
            print("   ✅ 报告生成成功:")
            for report_type, file_path in generated_files.items():
                print(f"     {report_type.upper()}报告: {file_path}")
        else:
            print("   ⚠️ 报告生成失败或跳过")
    except Exception as e:
        print(f"   ❌ 报告生成出错: {e}")
    
    return analysis_results


def demonstrate_custom_configuration():
    """演示自定义配置功能"""
    print("\n" + "=" * 80)
    print("自定义配置演示")
    print("=" * 80)
    
    # 自定义配置
    custom_config = {
        "field_mapping": {
            "proj_name": "项目名称",
            "proj_id": "项目编号",
            "proj_type": "项目类型",
            "proj_level": "项目级别",
            "prod_line": "产品线",
            "test_cases": "测试用例数",
            "auto_cases": "自动化用例数",
            "bug_count": "缺陷数量",
            "work_hours": "工作小时"
        },
        "dimension_fields": [
            "proj_type", "proj_level", "prod_line"
        ],
        "metric_fields": [
            "test_cases", "auto_cases", "bug_count", "work_hours"
        ],
        "analysis_parameters": {
            "min_support": 0.03,
            "min_confidence": 0.7,
            "min_lift": 1.5,
            "correlation_threshold": 0.7
        },
        "reporting": {
            "output_format": ["html"],  # 只生成HTML报告
            "output_directory": "custom_reports",
            "include_charts": True,
            "include_tables": True
        }
    }
    
    print("1. 使用自定义配置初始化分析器...")
    try:
        custom_analyzer = ConfigurableProjectAnalyzer(config_dict=custom_config)
        print("   ✅ 自定义配置加载成功")
        
        # 显示配置信息
        field_info = custom_analyzer.get_field_info()
        print(f"   自定义维度字段: {field_info['dimension_fields']}")
        print(f"   自定义指标字段: {field_info['metric_fields']}")
        
        # 导出配置
        config_export_file = "config/custom_config_export.yaml"
        custom_analyzer.export_configuration(config_export_file)
        print(f"   配置已导出到: {config_export_file}")
        
    except Exception as e:
        print(f"   ❌ 自定义配置加载失败: {e}")


def main():
    """主函数"""
    print("可配置项目数据Apriori分析演示")
    print("=" * 60)
    
    try:
        # 基本演示
        analysis_results = demonstrate_configurable_analysis()
        
        # 自定义配置演示
        demonstrate_custom_configuration()
        
        print("\n" + "=" * 60)
        print("演示完成！")
        print("\n功能特性:")
        print("✅ 支持自定义维度字段和指标字段配置")
        print("✅ 支持英文字段名到中文显示名的映射")
        print("✅ 支持可配置的Apriori算法参数")
        print("✅ 支持数据验证和格式检查")
        print("✅ 支持关联规则挖掘和数据标签分类")
        print("✅ 支持多格式报告生成（PDF/HTML）")
        print("✅ 支持配置模板生成和导出")
        
        if 'analysis_results' in locals():
            print("\n分析亮点:")
            summary = analysis_results.get('summary', {})
            if 'association_rules' in summary:
                print(f"🔍 发现了 {summary['association_rules']['total_rules']} 个关联规则")
            if 'labeling' in summary:
                print(f"🏷️ 标签分类违反率: {summary['labeling']['violation_rate']:.1%}")
            print("📊 生成了完整的可视化分析报告")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()