#!/usr/bin/env python3
"""
项目数据挖掘使用示例
演示如何使用ProjectClickHouseAnalyzer从ClickHouse数据库中挖掘项目测试数据的关联规则
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import argparse
from typing import Dict, List, Optional

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from analysis.project_clickhouse_analyzer import ProjectClickHouseAnalyzer
    from analysis.project_data_miner import ProjectDataMiner
    from utils.clickhouse_connector import ClickHouseConnector
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"分析模块导入失败: {e}")
    ANALYSIS_AVAILABLE = False
from loguru import logger


def create_sample_project_data():
    """创建示例项目数据用于演示"""
    logger.info("创建示例项目数据...")
    
    # 模拟项目数据
    np.random.seed(42)
    n_projects = 200
    
    # 项目基础信息
    project_types = ['Web应用', '移动应用', 'API服务', '桌面应用', '大数据平台']
    project_levels = ['P0', 'P1', 'P2', 'P3']
    product_lines = ['电商平台', '金融服务', '社交媒体', '企业服务', '游戏娱乐']
    product_types = ['前端', '后端', '数据库', '中间件', '算法']
    test_owners = [f'测试员{i:02d}' for i in range(1, 21)]
    organizations = ['质量部门A', '质量部门B', '质量部门C', '外包团队D', '外包团队E']
    
    data = []
    for i in range(n_projects):
        project_type = np.random.choice(project_types)
        project_level = np.random.choice(project_levels)
        product_line = np.random.choice(product_lines)
        product_type = np.random.choice(product_types)
        test_owner = np.random.choice(test_owners)
        organization = np.random.choice(organizations)
        
        # 基于项目类型和级别生成相关的指标
        # P0项目通常执行用例数更多，工时更多
        level_multiplier = {'P0': 2.5, 'P1': 2.0, 'P2': 1.5, 'P3': 1.0}[project_level]
        
        # Web应用和移动应用通常自动化率更高
        auto_rate_base = 0.7 if project_type in ['Web应用', 'API服务'] else 0.4
        
        # 生成执行用例数（基于项目级别和类型）
        executed_cases = int(np.random.normal(100 * level_multiplier, 30))
        executed_cases = max(10, executed_cases)
        
        # 生成自动化用例数
        automation_rate = max(0.1, min(0.9, np.random.normal(auto_rate_base, 0.2)))
        automated_cases = int(executed_cases * automation_rate)
        
        # 生成关联缺陷数（高级别项目缺陷相对较少）
        bug_rate_base = 0.05 if project_level == 'P0' else 0.08
        related_bugs = int(np.random.poisson(executed_cases * bug_rate_base))
        
        # 生成投入工时（基于执行用例数和项目复杂度）
        complexity_factor = 1.5 if project_type in ['大数据平台', '企业服务'] else 1.0
        effort_hours = int(np.random.normal(executed_cases * 0.5 * complexity_factor, 20))
        effort_hours = max(10, effort_hours)
        
        data.append({
            '项目名称': f'项目_{product_line}_{project_type}_{i+1:03d}',
            '项目编号': f'PRJ-{i+1:04d}',
            '项目类型': project_type,
            '项目级别': project_level,
            '产品线': product_line,
            '产品类型': product_type,
            '测试负责人': test_owner,
            '测试负责人所属组织架构': organization,
            '执行用例数': executed_cases,
            '自动化执行用例数': automated_cases,
            '关联缺陷': related_bugs,
            '投入工时': effort_hours
        })
    
    df = pd.DataFrame(data)
    
    # 保存为Excel文件
    output_file = 'sample_project_data.xlsx'
    df.to_excel(output_file, index=False)
    logger.info(f"示例项目数据已保存到: {output_file}")
    
    return df


def example_1_analyze_excel_project_data():
    """示例1: 分析Excel中的项目数据"""
    print("=" * 80)
    print("示例1: 分析Excel中的项目数据")
    print("=" * 80)
    
    # 创建示例数据
    project_data = create_sample_project_data()
    
    if not ANALYSIS_AVAILABLE:
        logger.error("分析模块不可用，请检查依赖")
        return {}
    
    # 使用ProjectDataMiner直接分析数据
    print("\n1. 初始化项目数据挖掘器...")
    config = {
        'min_support': 0.1,
        'min_confidence': 0.5,
        'min_lift': 1.2,
        'correlation_threshold': 0.6
    }
    
    miner = ProjectDataMiner(config)
    
    # 进行关联规则挖掘
    print("\n2. 执行项目数据关联规则挖掘...")
    results = miner.discover_project_associations(project_data)
    
    # 显示分析结果
    print("\n3. 分析结果概览:")
    data_overview = results.get('data_overview', {})
    print(f"   总项目数: {data_overview.get('total_projects', 0)}")
    
    # 分类关联
    categorical_associations = results.get('categorical_associations', {})
    strong_associations = categorical_associations.get('strong_associations', [])
    print(f"   强分类关联数量: {len(strong_associations)}")
    
    if strong_associations:
        print("   前3个强分类关联:")
        for i, assoc in enumerate(strong_associations[:3], 1):
            print(f"     {i}. {assoc['field1']} <-> {assoc['field2']} "
                  f"(Cramer's V: {assoc['cramers_v']:.3f})")
    
    # 数值相关性
    numerical_correlations = results.get('numerical_correlations', {})
    strong_correlations = numerical_correlations.get('strong_correlations', [])
    print(f"   强数值相关性数量: {len(strong_correlations)}")
    
    if strong_correlations:
        print("   前3个强数值相关性:")
        for i, corr in enumerate(strong_correlations[:3], 1):
            print(f"     {i}. {corr['field1']} <-> {corr['field2']} "
                  f"(相关系数: {corr['correlation']:.3f})")
    
    # 交叉类型关联
    cross_associations = results.get('cross_type_associations', {})
    significant_diffs = cross_associations.get('significant_differences', [])
    print(f"   显著交叉关联数量: {len(significant_diffs)}")
    
    if significant_diffs:
        print("   前3个显著交叉关联:")
        for i, diff in enumerate(significant_diffs[:3], 1):
            print(f"     {i}. {diff['categorical_field']} 对 {diff['numerical_field']} "
                  f"有显著影响 (p值: {diff['p_value']:.3f})")
    
    # 关键洞察
    summary = results.get('summary', {})
    key_findings = summary.get('key_findings', [])
    if key_findings:
        print("\n4. 关键发现:")
        for i, finding in enumerate(key_findings[:5], 1):
            print(f"   {i}. {finding}")
    
    return results


def example_2_analyze_clickhouse_project_data():
    """示例2: 分析ClickHouse中的项目数据（模拟）"""
    print("\n" + "=" * 80)
    print("示例2: 分析ClickHouse中的项目数据（配置示例）")
    print("=" * 80)
    
    # 显示如何配置ClickHouse分析器
    print("1. ClickHouse配置示例:")
    config_example = {
        'clickhouse': {
            'host': 'localhost',
            'port': 18123,
            'username': 'default',
            'password': 'your_password',
            'database': 'project_db',
            'secure': False
        },
        'data_mining': {
            'min_support': 0.1,
            'min_confidence': 0.5,
            'min_lift': 1.2,
            'correlation_threshold': 0.6
        }
    }
    
    print("   配置文件内容:")
    import yaml
    print(yaml.dump(config_example, default_flow_style=False, allow_unicode=True))
    
    print("\n2. 使用示例代码:")
    example_code = '''
# 初始化分析器
from analysis.project_clickhouse_analyzer import ProjectClickHouseAnalyzer

analyzer = ProjectClickHouseAnalyzer(config_path='config/clickhouse_config.yaml')

# 分析项目数据表
results = analyzer.analyze_project_table(
    table_name='project_test_data',
    custom_field_mapping={
        'project_name': 'prj_name',
        'executed_cases': 'test_cases_executed'
    },
    where_condition="created_date >= '2024-01-01'",
    limit=1000
)

# 按组织分析性能
org_analysis = analyzer.analyze_project_performance_by_organization(
    table_name='project_test_data'
)

# 分析产品线效率
efficiency_analysis = analyzer.analyze_product_line_efficiency(
    table_name='project_test_data'
)

# 发现质量模式
quality_patterns = analyzer.discover_quality_patterns(
    table_name='project_test_data',
    quality_threshold=0.1  # 10%缺陷率阈值
)
'''
    print(example_code)
    
    # 如果实际可以连接ClickHouse，执行真实分析
    try:
        print("\n3. 尝试连接ClickHouse（如果可用）...")
        analyzer = ProjectClickHouseAnalyzer()
        # 注意：这里会尝试连接，如果连接失败会抛出异常
        print("   ClickHouse连接成功！可以使用上述代码进行实际分析。")
    except Exception as e:
        print(f"   ClickHouse连接失败: {e}")
        print("   请确保ClickHouse服务正在运行，并且配置正确。")


def example_3_quality_pattern_analysis():
    """示例3: 质量模式分析"""
    print("\n" + "=" * 80)
    print("示例3: 深度质量模式分析")
    print("=" * 80)
    
    # 使用示例1的数据
    project_data = pd.read_excel('sample_project_data.xlsx')
    
    print("1. 质量指标计算...")
    
    # 计算质量相关指标
    project_data['自动化率'] = project_data['自动化执行用例数'] / project_data['执行用例数']
    project_data['缺陷密度'] = project_data['关联缺陷'] / project_data['执行用例数']
    project_data['测试效率'] = project_data['执行用例数'] / project_data['投入工时']
    
    print(f"   平均自动化率: {project_data['自动化率'].mean():.2%}")
    print(f"   平均缺陷密度: {project_data['缺陷密度'].mean():.3f}")
    print(f"   平均测试效率: {project_data['测试效率'].mean():.1f} 用例/小时")
    
    print("\n2. 按项目级别分析质量...")
    quality_by_level = project_data.groupby('项目级别').agg({
        '自动化率': 'mean',
        '缺陷密度': 'mean',
        '测试效率': 'mean',
        '项目名称': 'count'
    }).round(3)
    quality_by_level.columns = ['平均自动化率', '平均缺陷密度', '平均测试效率', '项目数量']
    print(quality_by_level)
    
    print("\n3. 按产品线分析质量...")
    quality_by_product = project_data.groupby('产品线').agg({
        '自动化率': 'mean',
        '缺陷密度': 'mean',
        '测试效率': 'mean',
        '项目名称': 'count'
    }).round(3)
    quality_by_product.columns = ['平均自动化率', '平均缺陷密度', '平均测试效率', '项目数量']
    print(quality_by_product)
    
    print("\n4. 高质量项目特征识别...")
    # 定义高质量项目：自动化率>60%，缺陷密度<5%，测试效率>2用例/小时
    high_quality_mask = (
        (project_data['自动化率'] > 0.6) & 
        (project_data['缺陷密度'] < 0.05) & 
        (project_data['测试效率'] > 2.0)
    )
    
    high_quality_projects = project_data[high_quality_mask]
    print(f"   高质量项目数量: {len(high_quality_projects)} ({len(high_quality_projects)/len(project_data):.1%})")
    
    if len(high_quality_projects) > 0:
        print("   高质量项目特征分布:")
        for col in ['项目类型', '项目级别', '产品线', '测试负责人所属组织架构']:
            print(f"     {col}:")
            dist = high_quality_projects[col].value_counts(normalize=True).head(3)
            for value, ratio in dist.items():
                print(f"       {str(value)}: {ratio:.1%}")
    
    print("\n5. 改进建议生成...")
    
    # 找出需要改进的领域
    low_automation = project_data[project_data['自动化率'] < 0.4]
    high_defects = project_data[project_data['缺陷密度'] > 0.1]
    low_efficiency = project_data[project_data['测试效率'] < 1.5]
    
    print("   改进重点:")
    if len(low_automation) > 0:
        print(f"   - 提升自动化率: {len(low_automation)} 个项目自动化率低于40%")
    if len(high_defects) > 0:
        print(f"   - 降低缺陷率: {len(high_defects)} 个项目缺陷密度高于10%")
    if len(low_efficiency) > 0:
        print(f"   - 提升测试效率: {len(low_efficiency)} 个项目测试效率低于1.5用例/小时")


def example_4_organization_performance_ranking():
    """示例4: 组织绩效排名分析"""
    print("\n" + "=" * 80)
    print("示例4: 组织绩效排名分析")
    print("=" * 80)
    
    # 使用示例数据
    project_data = pd.read_excel('sample_project_data.xlsx')
    
    # 计算关键指标
    project_data['自动化率'] = project_data['自动化执行用例数'] / project_data['执行用例数']
    project_data['缺陷密度'] = project_data['关联缺陷'] / project_data['执行用例数']
    project_data['测试效率'] = project_data['执行用例数'] / project_data['投入工时']
    
    print("1. 组织绩效综合分析...")
    
    # 按组织架构分组分析
    org_performance = project_data.groupby('测试负责人所属组织架构').agg({
        '项目名称': 'count',
        '执行用例数': ['sum', 'mean'],
        '自动化率': 'mean',
        '缺陷密度': 'mean',
        '测试效率': 'mean',
        '投入工时': 'sum'
    }).round(3)
    
    # 简化列名
    org_performance.columns = [
        '项目数量', '总执行用例数', '平均执行用例数', 
        '平均自动化率', '平均缺陷密度', '平均测试效率', '总投入工时'
    ]
    
    print("   各组织绩效指标:")
    print(org_performance)
    
    print("\n2. 组织排名...")
    
    # 计算综合绩效得分（自动化率权重0.3，缺陷密度权重-0.4，测试效率权重0.3）
    org_performance['综合得分'] = (
        org_performance['平均自动化率'] * 0.3 +
        (1 - org_performance['平均缺陷密度']) * 0.4 +  # 缺陷密度越低越好
        (org_performance['平均测试效率'] / org_performance['平均测试效率'].max()) * 0.3
    ).round(3)
    
    # 按综合得分排序
    try:
        org_ranking = org_performance.sort_values('综合得分', ascending=False)
    except Exception as e:
        logger.warning(f"排序失败: {e}")
        org_ranking = org_performance
    
    print("   组织排名（按综合绩效得分）:")
    for i, (org, row) in enumerate(org_ranking.iterrows(), 1):
        print(f"     {i}. {org}")
        print(f"        综合得分: {row['综合得分']:.3f}")
        print(f"        项目数量: {row['项目数量']}")
        print(f"        平均自动化率: {row['平均自动化率']:.1%}")
        print(f"        平均缺陷密度: {row['平均缺陷密度']:.3f}")
        print(f"        平均测试效率: {row['平均测试效率']:.1f} 用例/小时")
        print()
    
    print("3. 改进建议...")
    
    # 为排名较低的组织生成建议
    bottom_orgs = org_ranking.tail(2)
    for org, row in bottom_orgs.iterrows():
        print(f"   {org} 改进建议:")
        if row['平均自动化率'] < 0.5:
            print("     - 重点提升测试自动化率")
        if row['平均缺陷密度'] > 0.06:
            print("     - 加强质量控制，降低缺陷率")
        if row['平均测试效率'] < 2.0:
            print("     - 优化测试流程，提升执行效率")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='项目数据挖掘使用示例')
    parser.add_argument('--example', type=int, choices=[1, 2, 3, 4, 5], 
                       help='选择要运行的示例 (1-5)')
    parser.add_argument('--all', action='store_true', 
                       help='运行所有示例')
    
    args = parser.parse_args()
    
    if args.all or args.example == 1:
        example_1_analyze_excel_project_data()
    
    if args.all or args.example == 2:
        example_2_analyze_clickhouse_project_data()
    
    if args.all or args.example == 3:
        example_3_quality_pattern_analysis()
    
    if args.all or args.example == 4:
        example_4_organization_performance_ranking()
    
    if not args.all and not args.example:
        print("项目数据挖掘使用示例")
        print("=" * 50)
        print("使用方法:")
        print("  python example_project_mining.py --example 1  # 运行示例1")
        print("  python example_project_mining.py --all        # 运行所有示例")
        print()
        print("可用示例:")
        print("  1. 分析Excel中的项目数据")
        print("  2. 分析ClickHouse中的项目数据（配置示例）")
        print("  3. 深度质量模式分析")
        print("  4. 组织绩效排名分析")
        print()
        print("自动运行示例1...")
        example_1_analyze_excel_project_data()


if __name__ == "__main__":
    main()