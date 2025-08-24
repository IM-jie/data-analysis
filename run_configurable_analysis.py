#!/usr/bin/env python3
"""
一键式可配置项目数据Apriori分析执行脚本
简化的入口脚本，支持快速执行项目数据分析和报告生成
"""

import sys
import os
from pathlib import Path
import pandas as pd
import argparse
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from analysis.configurable_project_analyzer import ConfigurableProjectAnalyzer
    print("✅ 可配置项目分析器加载成功")
except ImportError as e:
    print(f"❌ 分析器导入失败: {e}")
    print("请确保项目结构正确，并安装了必要的依赖库")
    sys.exit(1)


def print_banner():
    """打印程序横幅"""
    print("=" * 80)
    print("   可配置项目数据Apriori分析器")
    print("   支持自定义字段配置的关联规则挖掘和数据标签分类")
    print("=" * 80)


def create_sample_data():
    """创建示例数据"""
    print("📊 创建示例数据...")
    
    import numpy as np
    np.random.seed(42)
    n_projects = 100
    
    project_types = ['Web_App', 'Mobile_App', 'API_Service', 'Desktop_App']
    project_levels = ['P0', 'P1', 'P2']
    product_lines = ['E_Commerce', 'Financial_Service', 'Social_Media']
    organizations = ['QA_Team_A', 'QA_Team_B', 'Outsource_Team_C']
    
    data = []
    for i in range(n_projects):
        project_type = np.random.choice(project_types)
        project_level = np.random.choice(project_levels)
        product_line = np.random.choice(product_lines)
        organization = np.random.choice(organizations)
        
        # 基础指标计算
        level_multiplier = {'P0': 2.0, 'P1': 1.5, 'P2': 1.0}[project_level]
        base_cases = int(np.random.normal(80 * level_multiplier, 20))
        executed_cases = max(20, base_cases)
        automation_rate = np.random.uniform(0.3, 0.8)
        automated_cases = int(executed_cases * automation_rate)
        related_bugs = max(1, int(executed_cases * np.random.uniform(0.02, 0.08)))
        effort_hours = max(10, int(executed_cases * np.random.uniform(0.4, 0.8)))
        
        data.append({
            'project_name': f'Project_{product_line}_{project_type}_{i+1:03d}',
            'project_id': f'PRJ-{i+1:04d}',
            'project_type': project_type,
            'project_level': project_level,
            'product_line': product_line,
            'product_type': np.random.choice(['Frontend', 'Backend', 'Full_Stack']),
            'test_owner': f'Tester_{np.random.randint(1, 11):02d}',
            'test_owner_org': organization,
            'executed_cases': executed_cases,
            'automated_cases': automated_cases,
            'related_bugs': related_bugs,
            'effort_hours': effort_hours
        })
    
    df = pd.DataFrame(data)
    output_file = 'sample_configurable_project_data.xlsx'
    df.to_excel(output_file, index=False)
    print(f"✅ 示例数据已生成: {output_file}")
    return df, output_file


def run_analysis(data_file=None, config_file=None, output_prefix=None):
    """执行完整的分析流程"""
    
    print_banner()
    
    # 1. 准备数据
    if data_file and Path(data_file).exists():
        print(f"📂 读取数据文件: {data_file}")
        try:
            if data_file.endswith('.xlsx'):
                data = pd.read_excel(data_file)
            elif data_file.endswith('.csv'):
                data = pd.read_csv(data_file)
            else:
                raise ValueError("仅支持Excel(.xlsx)和CSV(.csv)文件")
        except Exception as e:
            print(f"❌ 数据文件读取失败: {e}")
            return None
    else:
        print("📊 未指定数据文件，将创建示例数据...")
        data, _ = create_sample_data()
    
    print(f"📋 数据概览: {data.shape[0]}行 × {data.shape[1]}列")
    print(f"📄 数据字段: {list(data.columns)}")
    
    # 2. 初始化分析器
    print("\n🔧 初始化分析器...")
    try:
        if config_file and Path(config_file).exists():
            print(f"📝 使用配置文件: {config_file}")
            analyzer = ConfigurableProjectAnalyzer(config_file=config_file)
        else:
            print("📋 使用默认配置")
            analyzer = ConfigurableProjectAnalyzer()
            
            # 创建配置模板（如果不存在）
            config_template = "config/project_analysis_config.yaml"
            if not Path(config_template).exists():
                print("📝 创建配置模板...")
                analyzer.create_config_template(config_template)
                print(f"✅ 配置模板已创建: {config_template}")
    
    except Exception as e:
        print(f"❌ 分析器初始化失败: {e}")
        return None
    
    # 3. 验证数据
    print("\n🔍 验证数据格式...")
    is_valid, errors = analyzer.validate_data(data)
    if not is_valid:
        print(f"❌ 数据验证失败:")
        for error in errors:
            print(f"   • {error}")
        return None
    print("✅ 数据验证通过")
    
    # 4. 执行分析
    print("\n🚀 开始执行Apriori关联规则分析...")
    start_time = datetime.now()
    
    try:
        results = analyzer.analyze_project_data(data)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"✅ 分析完成，耗时: {duration:.2f}秒")
    except Exception as e:
        print(f"❌ 分析执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    # 5. 显示分析摘要
    print("\n📊 分析结果摘要:")
    summary = results.get('summary', {})
    
    if 'association_rules' in summary:
        rule_summary = summary['association_rules']
        print(f"   🔗 关联规则总数: {rule_summary['total_rules']}")
        print(f"   📈 高置信度规则: {rule_summary['high_confidence_rules']}")
        print(f"   🔥 强关联关系: {rule_summary['strong_associations']}")
    
    if 'correlations' in summary:
        corr_summary = summary['correlations']
        print(f"   📊 强相关性数量: {corr_summary['strong_correlations']}")
    
    if 'labeling' in summary:
        label_summary = summary['labeling']
        print(f"   🏷️ 数据分类统计:")
        for category, count in label_summary['category_distribution'].items():
            print(f"      • {category}: {count}项")
        print(f"   ⚠️ 违反规则项目: {label_summary['violation_count']}项 ({label_summary['violation_rate']:.1%})")
    
    # 6. 生成报告
    print("\n📄 生成分析报告...")
    try:
        report_files = analyzer.generate_reports(results, output_prefix)
        
        if report_files:
            print("✅ 报告生成成功:")
            for report_type, file_path in report_files.items():
                print(f"   📋 {report_type.upper()}报告: {file_path}")
        else:
            print("⚠️ 报告生成失败或跳过")
    
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
    
    # 7. 显示关键发现
    if 'key_findings' in results:
        print("\n💡 关键发现:")
        for i, finding in enumerate(results['key_findings'][:5], 1):
            print(f"   {i}. {finding}")
    
    print("\n🎉 分析完成！")
    return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="可配置项目数据Apriori分析器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 使用示例数据和默认配置
  python run_configurable_analysis.py
  
  # 使用自定义数据文件
  python run_configurable_analysis.py --data my_project_data.xlsx
  
  # 使用自定义配置文件
  python run_configurable_analysis.py --config my_config.yaml
  
  # 指定输出文件前缀
  python run_configurable_analysis.py --output my_analysis
        """
    )
    
    parser.add_argument(
        '--data', '-d',
        type=str,
        help='输入数据文件路径 (支持.xlsx和.csv格式)'
    )
    
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='配置文件路径 (YAML格式)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='输出文件前缀'
    )
    
    parser.add_argument(
        '--create-sample',
        action='store_true',
        help='仅创建示例数据文件'
    )
    
    parser.add_argument(
        '--create-config',
        action='store_true',
        help='仅创建配置模板文件'
    )
    
    args = parser.parse_args()
    
    # 仅创建示例数据
    if args.create_sample:
        print_banner()
        create_sample_data()
        return
    
    # 仅创建配置模板
    if args.create_config:
        print_banner()
        analyzer = ConfigurableProjectAnalyzer()
        config_file = analyzer.create_config_template()
        print(f"✅ 配置模板已创建: {config_file}")
        return
    
    # 执行完整分析
    try:
        results = run_analysis(
            data_file=args.data,
            config_file=args.config,
            output_prefix=args.output
        )
        
        if results:
            print("\n🚀 分析成功完成！主要功能:")
            print("  ✅ 自定义字段配置和中英文映射")
            print("  ✅ Apriori关联规则挖掘")
            print("  ✅ 数据标签分类和异常检测")
            print("  ✅ 多格式报告生成(PDF/HTML)")
            print("  ✅ 可视化图表和统计分析")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()