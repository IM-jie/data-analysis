#!/usr/bin/env python3
"""
项目数据挖掘简化测试脚本
专门用于测试项目数据的关联规则挖掘功能
包含PDF报告生成功能
"""

import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# 导入PDF报告生成器
try:
    from visualization.pdf_report_generator import ProjectMiningPDFReporter
    PDF_AVAILABLE = True
except ImportError as e:
    print(f"PDF生成模块导入失败: {e}")
    PDF_AVAILABLE = False

# 导入HTML报告生成器
try:
    from visualization.html_report_generator import ProjectMiningHTMLReporter
    HTML_AVAILABLE = True
except ImportError as e:
    print(f"HTML生成模块导入失败: {e}")
    HTML_AVAILABLE = False

def create_test_project_data():
    """创建测试用的项目数据"""
    print("创建测试项目数据...")
    
    # 设置随机种子确保结果可重现
    np.random.seed(42)
    n_projects = 100
    
    # 项目基础信息
    project_types = ['Web应用', '移动应用', 'API服务', '桌面应用', '大数据平台']
    project_levels = ['P0', 'P1', 'P2', 'P3']
    product_lines = ['电商平台', '金融服务', '社交媒体', '企业服务', '游戏娱乐']
    product_types = ['前端', '后端', '数据库', '中间件', '算法']
    test_owners = [f'测试员{i:02d}' for i in range(1, 11)]
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
        level_multiplier = {'P0': 2.5, 'P1': 2.0, 'P2': 1.5, 'P3': 1.0}[project_level]
        auto_rate_base = 0.7 if project_type in ['Web应用', 'API服务'] else 0.4
        
        executed_cases = max(10, int(np.random.normal(100 * level_multiplier, 30)))
        automation_rate = max(0.1, min(0.9, np.random.normal(auto_rate_base, 0.2)))
        automated_cases = int(executed_cases * automation_rate)
        
        bug_rate_base = 0.05 if project_level == 'P0' else 0.08
        related_bugs = int(np.random.poisson(executed_cases * bug_rate_base))
        
        complexity_factor = 1.5 if project_type in ['大数据平台', '企业服务'] else 1.0
        effort_hours = max(10, int(np.random.normal(executed_cases * 0.5 * complexity_factor, 20)))
        
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
    
    # 保存数据
    output_file = 'test_project_data.xlsx'
    df.to_excel(output_file, index=False)
    print(f"测试数据已保存到: {output_file}")
    
    return df

def analyze_basic_statistics(data: pd.DataFrame):
    """分析基础统计信息"""
    print("\n=== 基础统计分析 ===")
    print(f"总项目数: {len(data)}")
    print(f"数据列: {list(data.columns)}")
    
    # 分类字段统计
    categorical_fields = ['项目类型', '项目级别', '产品线', '产品类型', '测试负责人所属组织架构']
    print("\n分类字段分布:")
    for field in categorical_fields:
        if field in data.columns:
            print(f"\n{field}:")
            counts = data[field].value_counts()
            for value, count in counts.head(5).items():
                print(f"  {value}: {count} ({count/len(data):.1%})")
    
    # 数值字段统计
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    print("\n数值字段统计:")
    for field in numerical_fields:
        if field in data.columns:
            print(f"\n{field}:")
            print(f"  平均值: {data[field].mean():.1f}")
            print(f"  中位数: {data[field].median():.1f}")
            print(f"  标准差: {data[field].std():.1f}")
            print(f"  最小值: {data[field].min()}")
            print(f"  最大值: {data[field].max()}")

def analyze_correlations(data: pd.DataFrame) -> Dict[str, Any]:
    """分析数值字段间的相关性"""
    print("\n=== 相关性分析 ===")
    
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    available_fields = [field for field in numerical_fields if field in data.columns]
    
    results = {'correlation_matrix': None, 'strong_correlations': []}
    
    if len(available_fields) < 2:
        print("可用数值字段不足，跳过相关性分析")
        return results
    
    # 计算相关性矩阵
    corr_matrix = data[available_fields].corr()
    results['correlation_matrix'] = corr_matrix
    print("\n相关性矩阵:")
    print(corr_matrix.round(3))
    
    # 识别强相关性
    print("\n强相关性关系 (|r| > 0.6):")
    strong_correlations = []
    for i, field1 in enumerate(available_fields):
        for j, field2 in enumerate(available_fields):
            if i < j:
                corr_value = corr_matrix.loc[field1, field2]
                if abs(corr_value) > 0.6:
                    direction = "正相关" if corr_value > 0 else "负相关"
                    print(f"  {field1} <-> {field2}: {corr_value:.3f} ({direction})")
                    strong_correlations.append({
                        'field1': field1,
                        'field2': field2,
                        'correlation': corr_value
                    })
    
    results['strong_correlations'] = strong_correlations
    return results

def analyze_categorical_associations(data: pd.DataFrame) -> Dict[str, Any]:
    """分析分类字段间的关联性"""
    print("\n=== 分类关联分析 ===")
    
    from scipy.stats import chi2_contingency
    
    categorical_fields = ['项目类型', '项目级别', '产品线', '产品类型', '测试负责人所属组织架构']
    available_fields = [field for field in categorical_fields if field in data.columns]
    
    results = {'categorical_associations': []}
    
    if len(available_fields) < 2:
        print("可用分类字段不足，跳过关联分析")
        return results
    
    print("\n分类字段间关联性分析（卡方检验）:")
    associations = []
    for i, field1 in enumerate(available_fields):
        for j, field2 in enumerate(available_fields):
            if i < j:
                try:
                    # 创建交叉表
                    crosstab = pd.crosstab(data[field1], data[field2])
                    
                    # 卡方检验
                    chi2, p_value, dof, expected = chi2_contingency(crosstab)
                    
                    # Cramer's V
                    n = crosstab.sum().sum()
                    cramers_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
                    
                    significance = "显著" if p_value < 0.05 else "不显著"
                    strength = "强" if cramers_v > 0.3 else "中等" if cramers_v > 0.1 else "弱"
                    
                    print(f"  {field1} <-> {field2}:")
                    print(f"    Cramer's V: {cramers_v:.3f} ({strength}关联)")
                    print(f"    p值: {p_value:.3f} ({significance})")
                    
                    associations.append({
                        'field1': field1,
                        'field2': field2,
                        'cramers_v': cramers_v,
                        'p_value': p_value,
                        'strength': strength,
                        'significance': significance
                    })
                    
                except Exception as e:
                    print(f"  {field1} <-> {field2}: 分析失败 ({e})")
    
    results['categorical_associations'] = associations
    return results

def analyze_cross_type_relationships(data: pd.DataFrame):
    """分析分类字段与数值字段间的关系"""
    print("\n=== 交叉类型关系分析 ===")
    
    from scipy.stats import f_oneway
    
    categorical_fields = ['项目类型', '项目级别', '产品线', '测试负责人所属组织架构']
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    
    for cat_field in categorical_fields:
        if cat_field not in data.columns:
            continue
            
        print(f"\n按{cat_field}分组的数值字段分析:")
        
        for num_field in numerical_fields:
            if num_field not in data.columns:
                continue
                
            try:
                # 按分类字段分组
                groups = [group[num_field].dropna() for name, group in data.groupby(cat_field) 
                         if len(group[num_field].dropna()) >= 3]
                
                if len(groups) >= 2:
                    # 方差分析
                    f_stat, p_value = f_oneway(*groups)
                    significance = "显著差异" if p_value < 0.05 else "无显著差异"
                    
                    print(f"  {num_field}: F={f_stat:.2f}, p={p_value:.3f} ({significance})")
                    
                    # 显示各组的平均值
                    if p_value < 0.05:
                        group_means = data.groupby(cat_field)[num_field].mean().sort_values(ascending=False)
                        print(f"    各组平均值:")
                        for group_name, mean_value in group_means.head(3).items():
                            print(f"      {group_name}: {mean_value:.1f}")
                            
            except Exception as e:
                print(f"  {num_field}: 分析失败 ({e})")

def analyze_quality_efficiency_patterns(data: pd.DataFrame):
    """分析质量效率模式"""
    print("\n=== 质量效率模式分析 ===")
    
    # 计算衍生指标
    if '执行用例数' in data.columns and '自动化执行用例数' in data.columns:
        data['自动化率'] = data['自动化执行用例数'] / data['执行用例数']
        print("✓ 计算自动化率")
    
    if '关联缺陷' in data.columns and '执行用例数' in data.columns:
        data['缺陷密度'] = data['关联缺陷'] / data['执行用例数']
        print("✓ 计算缺陷密度")
    
    if '执行用例数' in data.columns and '投入工时' in data.columns:
        data['测试效率'] = data['执行用例数'] / data['投入工时']
        print("✓ 计算测试效率")
    
    # 质量效率统计
    if '自动化率' in data.columns:
        print(f"\n自动化率统计:")
        print(f"  平均自动化率: {data['自动化率'].mean():.1%}")
        print(f"  中位数自动化率: {data['自动化率'].median():.1%}")
        
        high_auto = data[data['自动化率'] > 0.7]
        print(f"  高自动化率项目 (>70%): {len(high_auto)} 个 ({len(high_auto)/len(data):.1%})")
    
    if '缺陷密度' in data.columns:
        print(f"\n缺陷密度统计:")
        print(f"  平均缺陷密度: {data['缺陷密度'].mean():.3f}")
        print(f"  中位数缺陷密度: {data['缺陷密度'].median():.3f}")
        
        low_defect = data[data['缺陷密度'] < 0.05]
        print(f"  低缺陷密度项目 (<5%): {len(low_defect)} 个 ({len(low_defect)/len(data):.1%})")
    
    if '测试效率' in data.columns:
        print(f"\n测试效率统计:")
        print(f"  平均测试效率: {data['测试效率'].mean():.1f} 用例/小时")
        print(f"  中位数测试效率: {data['测试效率'].median():.1f} 用例/小时")
        
        high_eff = data[data['测试效率'] > 2.0]
        print(f"  高效率项目 (>2用例/小时): {len(high_eff)} 个 ({len(high_eff)/len(data):.1%})")

def analyze_organization_performance(data: pd.DataFrame):
    """分析组织绩效"""
    print("\n=== 组织绩效分析 ===")
    
    org_field = '测试负责人所属组织架构'
    if org_field not in data.columns:
        print("未找到组织架构字段")
        return
    
    # 按组织统计项目数量
    org_counts = data[org_field].value_counts()
    print(f"\n各组织项目数量:")
    for org, count in org_counts.items():
        print(f"  {org}: {count} 个项目")
    
    # 按组织统计平均指标
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    available_fields = [field for field in numerical_fields if field in data.columns]
    
    if available_fields:
        print(f"\n各组织平均指标:")
        org_stats = data.groupby(org_field)[available_fields].mean().round(1)
        print(org_stats)
    
    # 计算组织综合得分
    if all(field in data.columns for field in ['执行用例数', '自动化执行用例数', '关联缺陷']):
        # 计算自动化率和缺陷密度
        data['自动化率'] = data['自动化执行用例数'] / data['执行用例数']
        data['缺陷密度'] = data['关联缺陷'] / data['执行用例数']
        
        org_performance = data.groupby(org_field).agg({
            '自动化率': 'mean',
            '缺陷密度': 'mean',
            '执行用例数': 'mean'
        }).round(3)
        
        # 计算综合得分 (自动化率权重0.4，缺陷密度权重-0.4，执行用例数权重0.2)
        org_performance['综合得分'] = (
            org_performance['自动化率'] * 0.4 +
            (1 - org_performance['缺陷密度']) * 0.4 +
            (org_performance['执行用例数'] / org_performance['执行用例数'].max()) * 0.2
        ).round(3)
        
        print(f"\n组织绩效排名:")
        org_ranking = org_performance.sort_values('综合得分', ascending=False)
        for i, (org, row) in enumerate(org_ranking.iterrows(), 1):
            print(f"  {i}. {org}")
            print(f"     综合得分: {row['综合得分']:.3f}")
            print(f"     平均自动化率: {row['自动化率']:.1%}")
            print(f"     平均缺陷密度: {row['缺陷密度']:.3f}")

def generate_insights_and_recommendations(data: pd.DataFrame):
    """生成洞察和建议"""
    print("\n=== 关键洞察与建议 ===")
    
    insights = []
    recommendations = []
    
    # 数据质量洞察
    insights.append(f"共分析了 {len(data)} 个项目的数据")
    
    # 自动化洞察
    if '执行用例数' in data.columns and '自动化执行用例数' in data.columns:
        data['自动化率'] = data['自动化执行用例数'] / data['执行用例数']
        avg_auto_rate = data['自动化率'].mean()
        insights.append(f"平均自动化率为 {avg_auto_rate:.1%}")
        
        if avg_auto_rate < 0.5:
            recommendations.append("建议重点提升测试自动化率，目标达到50%以上")
    
    # 缺陷洞察
    if '关联缺陷' in data.columns and '执行用例数' in data.columns:
        data['缺陷密度'] = data['关联缺陷'] / data['执行用例数']
        avg_defect_rate = data['缺陷密度'].mean()
        insights.append(f"平均缺陷密度为 {avg_defect_rate:.1%}")
        
        if avg_defect_rate > 0.08:
            recommendations.append("建议加强质量控制，降低缺陷密度至8%以下")
    
    # 效率洞察
    if '执行用例数' in data.columns and '投入工时' in data.columns:
        data['测试效率'] = data['执行用例数'] / data['投入工时']
        avg_efficiency = data['测试效率'].mean()
        insights.append(f"平均测试效率为 {avg_efficiency:.1f} 用例/小时")
        
        if avg_efficiency < 2.0:
            recommendations.append("建议优化测试流程，提升执行效率至2用例/小时以上")
    
    # 项目类型洞察
    if '项目类型' in data.columns:
        type_counts = data['项目类型'].value_counts()
        top_type = type_counts.index[0]
        insights.append(f"最常见的项目类型是 {top_type} ({type_counts.iloc[0]} 个项目)")
    
    # 输出洞察
    print("\n关键洞察:")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")
    
    # 输出建议
    print("\n改进建议:")
    for i, recommendation in enumerate(recommendations, 1):
        print(f"  {i}. {recommendation}")

def get_numerical_statistics(data: pd.DataFrame) -> Dict[str, Dict]:
    """获取数值字段统计信息"""
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    stats = {}
    
    for field in numerical_fields:
        if field in data.columns:
            stats[field] = {
                'mean': data[field].mean(),
                'median': data[field].median(),
                'std': data[field].std(),
                'min': data[field].min(),
                'max': data[field].max()
            }
    
    return stats

def collect_analysis_results(data: pd.DataFrame) -> Dict[str, any]:
    """收集所有分析结果"""
    results = {}
    
    # 收集相关性分析结果
    numerical_fields = ['执行用例数', '自动化执行用例数', '关联缺陷', '投入工时']
    available_fields = [field for field in numerical_fields if field in data.columns]
    
    if len(available_fields) >= 2:
        corr_matrix = data[available_fields].corr()
        results['correlation_matrix'] = corr_matrix
        
        strong_correlations = []
        for i, field1 in enumerate(available_fields):
            for j, field2 in enumerate(available_fields):
                if i < j:
                    corr_value = corr_matrix.loc[field1, field2]
                    if abs(corr_value) > 0.6:
                        strong_correlations.append({
                            'field1': field1,
                            'field2': field2,
                            'correlation': corr_value
                        })
        results['strong_correlations'] = strong_correlations
    
    # 收集质量指标
    quality_metrics = {}
    if '执行用例数' in data.columns and '自动化执行用例数' in data.columns:
        data['自动化率'] = data['自动化执行用例数'] / data['执行用例数']
        quality_metrics['avg_automation_rate'] = data['自动化率'].mean()
        quality_metrics['high_automation_projects'] = len(data[data['自动化率'] > 0.7])
    
    if '关联缺陷' in data.columns and '执行用例数' in data.columns:
        data['缺陷密度'] = data['关联缺陷'] / data['执行用例数']
        quality_metrics['avg_defect_density'] = data['缺陷密度'].mean()
        quality_metrics['low_defect_projects'] = len(data[data['缺陷密度'] < 0.05])
    
    if '执行用例数' in data.columns and '投入工时' in data.columns:
        data['测试效率'] = data['执行用例数'] / data['投入工时']
        quality_metrics['avg_test_efficiency'] = data['测试效率'].mean()
        quality_metrics['high_efficiency_projects'] = len(data[data['测试效率'] > 2.0])
    
    results['quality_metrics'] = quality_metrics
    
    return results


def main():
    print("项目数据挖掘简化测试")
    print("=" * 50)
    
    # 用于存储分析结果的字典
    analysis_results = {
        'total_projects': 0,
        'key_findings': [],
        'summary_metrics': {},
        'data_overview': {},
        'numerical_statistics': {},
        'correlation_matrix': None,
        'strong_correlations': [],
        'categorical_associations': [],
        'significant_differences': [],
        'quality_metrics': {},
        'organization_ranking': {},
        'categorical_distributions': {},
        'conclusions': [],
        'recommendations': []
    }
    
    try:
        # 创建测试数据
        project_data = create_test_project_data()
        analysis_results['total_projects'] = len(project_data)
        analysis_results['categorical_distributions'] = {
            '项目类型': project_data['项目类型'].value_counts().to_dict(),
            '项目级别': project_data['项目级别'].value_counts().to_dict(),
            '产品线': project_data['产品线'].value_counts().to_dict(),
            '测试负责人所属组织架构': project_data['测试负责人所属组织架构'].value_counts().to_dict()
        }
        
        # 执行各种分析并收集结果
        basic_stats_results = analyze_basic_statistics(project_data)
        analysis_results['numerical_statistics'] = get_numerical_statistics(project_data)
        
        correlation_results = analyze_correlations(project_data)
        analysis_results.update(correlation_results)
        
        categorical_results = analyze_categorical_associations(project_data)
        analysis_results.update(categorical_results)
        
        cross_results = analyze_cross_type_relationships(project_data)
        if cross_results:
            analysis_results.update(cross_results)
        
        quality_results = analyze_quality_efficiency_patterns(project_data)
        if quality_results:
            analysis_results.update(quality_results)
        
        org_results = analyze_organization_performance(project_data)
        if org_results:
            analysis_results.update(org_results)
        
        # 生成洞察和建议
        insights_results = generate_insights_and_recommendations(project_data)
        
        # 收集分析结果
        collected_results = collect_analysis_results(project_data)
        analysis_results.update(collected_results)
        
        print("\n" + "=" * 50)
        print("项目数据挖掘测试完成！")
        print("详细数据已保存到 test_project_data.xlsx")
        
        # 生成PDF报告
        if PDF_AVAILABLE:
            print("\n正在生成PDF报告...")
            try:
                reporter = ProjectMiningPDFReporter()
                pdf_path = reporter.generate_project_mining_report(analysis_results)
                print(f"PDF报告已生成: {pdf_path}")
                
                # 清理临时文件
                temp_files = ['temp_distribution_chart.png', 'temp_correlation_heatmap.png']
                for temp_file in temp_files:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        
            except Exception as e:
                print(f"PDF报告生成失败: {e}")
        else:
            print("\nPDF生成功能不可用，请安装 reportlab 库")
        
        # 生成HTML报告
        if HTML_AVAILABLE:
            print("\n正在生成HTML报告...")
            try:
                html_reporter = ProjectMiningHTMLReporter()
                html_path = html_reporter.generate_project_mining_html_report(analysis_results)
                print(f"HTML报告已生成: {html_path}")
                        
            except Exception as e:
                print(f"HTML报告生成失败: {e}")
        else:
            print("\nHTML生成功能不可用，请安装 plotly 库")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()