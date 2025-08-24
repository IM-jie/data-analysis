#!/usr/bin/env python3
"""
ClickHouse KPI数据分析使用示例
演示如何使用ClickHouse数据库进行指标分析和数据挖掘
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.clickhouse_connector import ClickHouseConnector, ClickHouseKPIAnalyzer
from kpi_clickhouse_analyzer import KPIClickHouseAnalyzer
from loguru import logger


def example_1_connect_clickhouse():
    """示例1: 连接ClickHouse数据库"""
    print("=" * 60)
    print("示例1: 连接ClickHouse数据库")
    print("=" * 60)
    
    try:
        # 连接ClickHouse数据库
        connector = ClickHouseConnector(
            host='localhost',
            port=18123,
            username='default',
            password='Dxt456789',
            database='default'
        )
        
        # 测试连接
        if connector.test_connection():
            print("✓ ClickHouse数据库连接成功")
            
            # 获取数据库列表
            databases = connector.get_databases()
            print(f"可用数据库: {databases}")
            
            # 获取表列表
            tables = connector.get_tables()
            print(f"可用表: {tables}")
            
            connector.close()
            return True
        else:
            print("✗ ClickHouse数据库连接失败")
            return False
            
    except Exception as e:
        print(f"✗ 连接ClickHouse失败: {e}")
        print("请确保ClickHouse服务正在运行，或者修改连接配置")
        return False


def example_2_create_sample_data():
    """示例2: 创建示例数据（如果ClickHouse可用）"""
    print("\n" + "=" * 60)
    print("示例2: 创建示例数据")
    print("=" * 60)
    
    try:
        connector = ClickHouseConnector()
        
        # 创建示例表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS kpi_data (
            id UInt32,
            department_name String,
            quarter String,
            project_count UInt32,
            employee_count UInt32,
            test_case_count UInt32,
            automated_test_count UInt32,
            code_coverage Float32,
            bug_fix_rate Float32,
            delivery_rate Float32,
            customer_satisfaction Float32,
            created_at DateTime
        ) ENGINE = MergeTree()
        ORDER BY (department_name, quarter)
        """
        
        connector.client.command(create_table_sql)
        print("✓ 示例表创建成功")
        
        # 插入示例数据
        sample_data = []
        departments = ['技术部', '产品部', '运营部', '市场部', '销售部']
        quarters = ['2025Q1', '2025Q2', '2025Q3']
        
        id_counter = 1
        for dept in departments:
            for quarter in quarters:
                row = {
                    'id': id_counter,
                    'department_name': dept,
                    'quarter': quarter,
                    'project_count': np.random.randint(5, 20),
                    'employee_count': np.random.randint(20, 100),
                    'test_case_count': np.random.randint(500, 2000),
                    'automated_test_count': np.random.randint(200, 1000),
                    'code_coverage': np.random.uniform(0.6, 0.9),
                    'bug_fix_rate': np.random.uniform(0.7, 0.95),
                    'delivery_rate': np.random.uniform(0.8, 0.98),
                    'customer_satisfaction': np.random.uniform(3.5, 4.5)
                }
                sample_data.append(row)
                id_counter += 1
        
        # 批量插入数据
        insert_sql = """
        INSERT INTO kpi_data (
            id, department_name, quarter, project_count, employee_count,
            test_case_count, automated_test_count, code_coverage,
            bug_fix_rate, delivery_rate, customer_satisfaction
        ) VALUES
        """
        
        values = []
        for row in sample_data:
            values.append(f"({row['id']}, '{row['department_name']}', '{row['quarter']}', "
                         f"{row['project_count']}, {row['employee_count']}, "
                         f"{row['test_case_count']}, {row['automated_test_count']}, "
                         f"{row['code_coverage']:.3f}, {row['bug_fix_rate']:.3f}, "
                         f"{row['delivery_rate']:.3f}, {row['customer_satisfaction']:.3f})")
        
        insert_sql += ", ".join(values)
        connector.client.command(insert_sql)
        
        print(f"✓ 成功插入 {len(sample_data)} 条示例数据")
        
        # 验证数据
        result = connector.client.query("SELECT COUNT(*) FROM kpi_data")
        count = result.result_rows[0][0]
        print(f"✓ 表中总共有 {count} 条数据")
        
        connector.close()
        return True
        
    except Exception as e:
        print(f"✗ 创建示例数据失败: {e}")
        print("这可能是正常的，如果ClickHouse服务未运行")
        return False


def example_3_basic_analysis():
    """示例3: 基础分析"""
    print("\n" + "=" * 60)
    print("示例3: 基础分析")
    print("=" * 60)
    
    try:
        # 使用ClickHouse分析器
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 获取表信息
        table_info = analyzer.get_table_info('kpi_data')
        if 'error' in table_info:
            print(f"✗ 获取表信息失败: {table_info['error']}")
            return False
        
        print("表信息:")
        print(f"  表名: {table_info['table_name']}")
        print(f"  总行数: {table_info['summary']['total_rows']}")
        print(f"  总列数: {table_info['summary']['total_columns']}")
        print(f"  数值列: {table_info['summary']['numeric_columns']}")
        
        # 分析整个表
        results = analyzer.analyze_table(
            table_name='kpi_data',
            department_column='department_name',
            time_column='quarter'
        )
        
        if 'error' in results:
            print(f"✗ 分析失败: {results['error']}")
            return False
        
        print("\n分析结果:")
        print(f"  数据形状: {results['data_shape']}")
        print(f"  报告路径: {results['report_path']}")
        
        # 显示关联关系摘要
        association_results = results.get('association_results', {})
        summary = association_results.get('summary', {})
        print(f"  强相关性关系: {summary.get('total_strong_correlations', 0)}")
        print(f"  强互信息关系: {summary.get('total_strong_mi_relationships', 0)}")
        print(f"  因果关系链: {summary.get('total_causal_chains', 0)}")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 基础分析失败: {e}")
        return False


def example_4_department_analysis():
    """示例4: 部门分析"""
    print("\n" + "=" * 60)
    print("示例4: 部门分析")
    print("=" * 60)
    
    try:
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 分析技术部
        results = analyzer.analyze_department(
            table_name='kpi_data',
            department_name='技术部',
            time_column='quarter'
        )
        
        if 'error' in results:
            print(f"✗ 部门分析失败: {results['error']}")
            return False
        
        print("技术部分析结果:")
        print(f"  数据点数量: {results['data_points']}")
        print(f"  时间范围: {results['time_range']['start']} - {results['time_range']['end']}")
        
        # 显示指标分析
        metrics_analysis = results.get('metrics_analysis', {})
        print(f"  分析指标数量: {len(metrics_analysis)}")
        
        for metric, analysis in metrics_analysis.items():
            print(f"\n  {metric}:")
            print(f"    平均值: {analysis['mean']:.3f}")
            print(f"    标准差: {analysis['std']:.3f}")
            print(f"    趋势: {analysis['trend']}")
            print(f"    异常点数量: {len(analysis['anomalies'])}")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 部门分析失败: {e}")
        return False


def example_5_correlation_analysis():
    """示例5: 相关性分析"""
    print("\n" + "=" * 60)
    print("示例5: 相关性分析")
    print("=" * 60)
    
    try:
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 分析指标相关性
        metric_columns = ['project_count', 'employee_count', 'test_case_count', 
                         'automated_test_count', 'code_coverage', 'bug_fix_rate']
        
        results = analyzer.analyze_correlations(
            table_name='kpi_data',
            metric_columns=metric_columns,
            time_column='quarter'
        )
        
        if 'error' in results:
            print(f"✗ 相关性分析失败: {results['error']}")
            return False
        
        print("相关性分析结果:")
        print(f"  数据点数量: {results['data_points']}")
        
        # 显示强相关性
        strong_correlations = results.get('strong_correlations', [])
        print(f"  强相关性关系数量: {len(strong_correlations)}")
        
        for i, corr in enumerate(strong_correlations[:5], 1):
            print(f"  {i}. {corr['metric1']} <-> {corr['metric2']}: {corr['correlation']:.3f}")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 相关性分析失败: {e}")
        return False


def example_6_association_mining():
    """示例6: 关联关系挖掘"""
    print("\n" + "=" * 60)
    print("示例6: 关联关系挖掘")
    print("=" * 60)
    
    try:
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 进行关联关系挖掘
        metric_columns = ['project_count', 'employee_count', 'test_case_count', 
                         'automated_test_count', 'code_coverage', 'bug_fix_rate']
        
        results = analyzer.analyze_associations(
            table_name='kpi_data',
            metric_columns=metric_columns,
            time_column='quarter',
            department_column='department_name'
        )
        
        if 'error' in results:
            print(f"✗ 关联关系挖掘失败: {results['error']}")
            return False
        
        print("关联关系挖掘结果:")
        print(f"  数据形状: {results['data_shape']}")
        
        # 显示关联关系摘要
        association_results = results.get('association_results', {})
        summary = association_results.get('summary', {})
        print(f"  强相关性关系: {summary.get('total_strong_correlations', 0)}")
        print(f"  强互信息关系: {summary.get('total_strong_mi_relationships', 0)}")
        print(f"  因果关系链: {summary.get('total_causal_chains', 0)}")
        
        # 显示关键洞察
        insights = summary.get('key_insights', [])
        if insights:
            print("\n关键洞察:")
            for i, insight in enumerate(insights[:3], 1):
                print(f"  {i}. {insight}")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 关联关系挖掘失败: {e}")
        return False


def example_7_anomaly_detection():
    """示例7: 异常检测"""
    print("\n" + "=" * 60)
    print("示例7: 异常检测")
    print("=" * 60)
    
    try:
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 检测异常
        metrics = ['project_count', 'test_case_count', 'code_coverage']
        
        for metric in metrics:
            results = analyzer.detect_anomalies(
                table_name='kpi_data',
                metric_name=metric,
                time_column='quarter'
            )
            
            print(f"\n{metric} 异常检测结果:")
            if 'error' not in results:
                print(f"  异常数量: {results['anomaly_count']}")
                if results['anomaly_count'] > 0:
                    print("  异常数据示例:")
                    for i, anomaly in enumerate(results['anomaly_data'][:3], 1):
                        print(f"    {i}. 部门: {anomaly['department_name']}, "
                              f"季度: {anomaly['quarter']}, "
                              f"值: {anomaly[metric]:.3f}, "
                              f"Z-score: {anomaly['z_score']:.3f}")
            else:
                print(f"  错误: {results['error']}")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 异常检测失败: {e}")
        return False


def example_8_data_export():
    """示例8: 数据导出"""
    print("\n" + "=" * 60)
    print("示例8: 数据导出")
    print("=" * 60)
    
    try:
        analyzer = KPIClickHouseAnalyzer('config/clickhouse_config.yaml')
        
        # 导出数据到Excel
        output_file = "clickhouse_kpi_data.xlsx"
        
        exported_file = analyzer.export_to_excel(
            table_name='kpi_data',
            output_file=output_file,
            limit=100
        )
        
        print(f"✓ 数据导出成功: {exported_file}")
        
        # 验证导出文件
        if os.path.exists(output_file):
            df = pd.read_excel(output_file)
            print(f"✓ 导出文件包含 {len(df)} 行数据")
            print(f"✓ 导出文件包含 {len(df.columns)} 列")
        else:
            print("✗ 导出文件未找到")
        
        analyzer.close()
        return True
        
    except Exception as e:
        print(f"✗ 数据导出失败: {e}")
        return False


def main():
    """主函数"""
    print("ClickHouse KPI数据分析使用示例")
    print("本示例将演示如何使用ClickHouse数据库进行指标分析和数据挖掘")
    
    results = []
    
    try:
        # 运行各个示例
        results.append(("连接ClickHouse", example_1_connect_clickhouse()))
        
        # 只有在连接成功的情况下才运行其他示例
        if results[0][1]:
            results.append(("创建示例数据", example_2_create_sample_data()))
            results.append(("基础分析", example_3_basic_analysis()))
            results.append(("部门分析", example_4_department_analysis()))
            results.append(("相关性分析", example_5_correlation_analysis()))
            results.append(("关联关系挖掘", example_6_association_mining()))
            results.append(("异常检测", example_7_anomaly_detection()))
            results.append(("数据导出", example_8_data_export()))
        else:
            print("\n由于无法连接ClickHouse，跳过其他示例")
            print("请确保ClickHouse服务正在运行，或者修改连接配置")
        
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
            print("\n🎉 所有ClickHouse功能测试通过！")
            print("\nClickHouse功能特点:")
            print("1. ✓ 高性能数据查询 - 支持大规模KPI数据分析")
            print("2. ✓ 实时数据处理 - 支持实时指标监控")
            print("3. ✓ 复杂SQL查询 - 支持复杂的分析查询")
            print("4. ✓ 数据导出 - 支持导出到Excel格式")
            print("5. ✓ 集成分析 - 与数据挖掘功能无缝集成")
            
            print("\n使用建议:")
            print("- 使用 --config 参数指定ClickHouse配置文件")
            print("- 使用 --table 参数指定要分析的表名")
            print("- 使用 --action 参数选择执行的操作")
            print("- 使用 --metrics 参数指定要分析的指标列")
            print("- 定期备份重要的KPI数据")
        else:
            print(f"\n⚠️  有 {total - passed} 个测试失败")
            if not results[0][1]:
                print("主要原因是无法连接ClickHouse数据库")
                print("请检查:")
                print("1. ClickHouse服务是否正在运行")
                print("2. 连接配置是否正确")
                print("3. 网络连接是否正常")
        
        # 清理导出文件
        if os.path.exists("clickhouse_kpi_data.xlsx"):
            os.remove("clickhouse_kpi_data.xlsx")
            print("已清理导出文件")
        
    except Exception as e:
        logger.error(f"ClickHouse示例运行失败: {e}")
        print(f"\n错误: {e}")
        print("请检查依赖包是否正确安装")


if __name__ == "__main__":
    main()
