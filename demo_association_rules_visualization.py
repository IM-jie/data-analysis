#!/usr/bin/env python3
"""
关联规则可视化演示脚本
展示如何使用Apriori算法进行关联规则挖掘并可视化规则关系
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
    print("✅ 可配置项目分析器加载成功")
except ImportError as e:
    print(f"❌ 分析器导入失败: {e}")
    sys.exit(1)


def create_sample_data_with_patterns():
    """创建包含明显关联模式的示例数据"""
    print("📊 创建包含关联模式的示例数据...")
    
    np.random.seed(42)
    n_projects = 150
    
    project_types = ['Web_App', 'Mobile_App', 'API_Service', 'Desktop_App']
    project_levels = ['P0', 'P1', 'P2']
    product_lines = ['E_Commerce', 'Financial_Service', 'Social_Media']
    organizations = ['QA_Team_A', 'QA_Team_B', 'QA_Team_C', 'Outsource_Team_D']
    product_types = ['Frontend', 'Backend', 'Full_Stack']
    
    data = []
    
    for i in range(n_projects):
        # 创建明显的关联规律
        
        # 规律1: Financial_Service + P0 -> QA_Team_A (85%概率)
        if np.random.random() < 0.3:  # 30%是金融服务
            product_line = 'Financial_Service'
            project_level = 'P0' if np.random.random() < 0.8 else np.random.choice(['P1', 'P2'])
            organization = 'QA_Team_A' if np.random.random() < 0.85 else np.random.choice(['QA_Team_B', 'QA_Team_C'])
            project_type = np.random.choice(project_types)
            product_type = np.random.choice(product_types)
        
        # 规律2: Web_App + Frontend -> Social_Media (80%概率)
        elif np.random.random() < 0.35:  # 35%是Web应用
            project_type = 'Web_App'
            product_type = 'Frontend' if np.random.random() < 0.7 else np.random.choice(['Backend', 'Full_Stack'])
            if product_type == 'Frontend':
                product_line = 'Social_Media' if np.random.random() < 0.8 else np.random.choice(product_lines)
            else:
                product_line = np.random.choice(product_lines)
            project_level = np.random.choice(project_levels)
            organization = np.random.choice(organizations)
        
        # 规律3: Outsource_Team_D -> Mobile_App (80%概率)
        elif np.random.random() < 0.25:  # 25%是外包团队
            organization = 'Outsource_Team_D'
            project_type = 'Mobile_App' if np.random.random() < 0.8 else np.random.choice(project_types)
            project_level = np.random.choice(project_levels)
            product_line = np.random.choice(product_lines)
            product_type = np.random.choice(product_types)
        
        else:
            # 随机数据
            project_type = np.random.choice(project_types)
            project_level = np.random.choice(project_levels)
            product_line = np.random.choice(product_lines)
            organization = np.random.choice(organizations)
            product_type = np.random.choice(product_types)
        
        # 基础指标计算
        level_multiplier = {'P0': 2.0, 'P1': 1.5, 'P2': 1.0}[project_level]
        executed_cases = max(20, int(np.random.normal(100 * level_multiplier, 30)))
        automation_rate = np.random.uniform(0.3, 0.8)
        automated_cases = int(executed_cases * automation_rate)
        related_bugs = max(1, int(executed_cases * np.random.uniform(0.02, 0.08)))
        effort_hours = max(10, int(executed_cases * np.random.uniform(0.3, 0.7)))
        
        data.append({
            'project_name': f'Project_{product_line}_{project_type}_{i+1:03d}',
            'project_id': f'PRJ-{i+1:04d}',
            'project_type': project_type,
            'project_level': project_level,
            'product_line': product_line,
            'product_type': product_type,
            'test_owner': f'Tester_{np.random.randint(1, 16):02d}',
            'test_owner_org': organization,
            'executed_cases': executed_cases,
            'automated_cases': automated_cases,
            'related_bugs': related_bugs,
            'effort_hours': effort_hours
        })
    
    df = pd.DataFrame(data)
    output_file = 'association_rules_demo_data.xlsx'
    df.to_excel(output_file, index=False)
    print(f"✅ 示例数据已生成: {output_file}")
    
    return df


def run_association_rules_visualization_demo():
    """运行关联规则可视化演示"""
    print("\n" + "=" * 80)
    print("关联规则可视化演示")
    print("=" * 80)
    
    # 1. 创建示例数据
    project_data = create_sample_data_with_patterns()
    
    print(f"\n📊 数据概览:")
    print(f"   总项目数: {len(project_data)}")
    print(f"   项目类型分布: {dict(project_data['project_type'].value_counts())}")
    print(f"   产品线分布: {dict(project_data['product_line'].value_counts())}")
    print(f"   组织分布: {dict(project_data['test_owner_org'].value_counts())}")
    
    # 2. 初始化分析器（使用较低阈值以发现更多规则）
    config = {
        'min_support': 0.05,     # 较低的支持度
        'min_confidence': 0.6,   # 中等置信度
        'min_lift': 1.1,         # 较低的提升度
        'correlation_threshold': 0.5
    }
    
    print(f"\n🔧 分析器配置: {config}")
    analyzer = ConfigurableProjectAnalyzer(config_dict={'analysis_parameters': config})
    
    # 3. 执行分析
    print("\n🚀 执行关联规则分析...")
    start_time = datetime.now()
    
    analysis_results = analyzer.analyze_project_data(project_data)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"✅ 分析完成，耗时: {duration:.2f}秒")
    
    # 4. 查看发现的关联规则
    mining_results = analysis_results.get('mining_results', {})
    categorical_associations = mining_results.get('categorical_associations', {})
    association_rules = categorical_associations.get('association_rules', [])
    
    print(f"\n📋 发现的关联规则: {len(association_rules)}个")
    
    if association_rules:
        print("\n🔍 关联规则详情（前10个）:")
        for i, rule in enumerate(association_rules[:10], 1):
            antecedents = ' & '.join(rule.get('antecedents', []))
            consequents = ' & '.join(rule.get('consequents', []))
            confidence = rule.get('confidence', 0)
            support = rule.get('support', 0)
            lift = rule.get('lift', 1)
            
            print(f"   {i:2d}. {antecedents} => {consequents}")
            print(f"       置信度: {confidence:.3f} | 支持度: {support:.3f} | 提升度: {lift:.3f}")
    
    # 5. 生成可视化图表
    print("\n🎨 生成关联规则可视化图表...")
    
    visualization_files = {}  # 初始化变量
    
    try:
        visualization_files = analyzer.generate_association_rules_visualizations(
            analysis_results, 
            format="both"  # 生成matplotlib和plotly两种格式
        )
        
        if visualization_files:
            print(f"✅ 可视化完成！生成了 {len(visualization_files)} 个文件:")
            for chart_type, file_path in visualization_files.items():
                print(f"   📊 {chart_type}: {file_path}")
        else:
            print("⚠️ 没有生成可视化图表")
            
    except Exception as e:
        print(f"❌ 可视化生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 6. 显示分析建议
    print("\n💡 分析建议:")
    print("   1. 查看网络图了解字段间的关联关系")
    print("   2. 使用气泡图筛选高质量规则（高置信度+高提升度）")
    print("   3. 通过热力图识别最强的关联模式")
    print("   4. 关注违反规则的异常项目进行进一步分析")
    
    return analysis_results, visualization_files


def main():
    """主函数"""
    try:
        print("🎯 关联规则可视化演示")
        print("=" * 40)
        
        # 运行演示
        results, viz_files = run_association_rules_visualization_demo()
        
        print("\n" + "=" * 80)
        print("演示完成！")
        print("\n🎉 主要成果:")
        print("   ✅ 成功挖掘项目数据中的关联规则")
        print("   ✅ 生成了多种类型的可视化图表")
        print("   ✅ 提供了规则关系的直观展示")
        print("   ✅ 支持交互式和静态两种可视化格式")
        
        if viz_files:
            print("\n📁 生成的可视化文件:")
            for chart_type, file_path in viz_files.items():
                if 'interactive' in chart_type or chart_type.endswith('.html'):
                    print(f"   🌐 {chart_type}: 可在浏览器中打开查看交互效果")
                elif chart_type.endswith('.png'):
                    print(f"   🖼️ {chart_type}: 静态图片文件")
                else:
                    print(f"   📄 {chart_type}: {file_path}")
        
        print("\n🔍 可视化图表说明:")
        print("   • 网络图: 展示规则间的关系网络，节点大小表示重要性")
        print("   • 气泡图: 三维展示支持度、置信度和提升度")
        print("   • 热力图: 矩阵形式展示字段间的关联强度")
        print("   • 交互式图表: 支持鼠标悬停查看详细信息")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()