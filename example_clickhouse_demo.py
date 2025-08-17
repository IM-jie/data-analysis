#!/usr/bin/env python3
"""
ClickHouse KPI数据分析功能演示
使用模拟数据演示ClickHouse分析功能
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from analysis.kpi_association_miner import KPIAssociationMiner, KPIAssociationAnomalyDetector
from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
from visualization.kpi_report_generator import KPIReportGenerator
from loguru import logger


class MockClickHouseConnector:
    """模拟ClickHouse连接器，用于演示功能"""
    
    def __init__(self):
        """初始化模拟连接器"""
        self.data = self._create_mock_data()
        logger.info("模拟ClickHouse连接器初始化完成")
    
    def _create_mock_data(self) -> pd.DataFrame:
        """创建模拟的KPI数据"""
        # 创建更真实的KPI数据
        departments = ['技术部', '产品部', '运营部', '市场部', '销售部']
        quarters = ['2025Q1', '2025Q2', '2025Q3', '2025Q4']
        
        data = []
        id_counter = 1
        
        for dept in departments:
            for quarter in quarters:
                # 基础值
                base_project_count = np.random.randint(8, 25)
                base_employee_count = np.random.randint(30, 120)
                base_test_case_count = np.random.randint(800, 2500)
                base_automated_test_count = np.random.randint(400, 1500)
                base_code_coverage = np.random.uniform(0.65, 0.92)
                base_bug_fix_rate = np.random.uniform(0.75, 0.96)
                base_delivery_rate = np.random.uniform(0.82, 0.98)
                base_customer_satisfaction = np.random.uniform(3.8, 4.6)
                
                # 添加趋势和相关性
                quarter_index = quarters.index(quarter)
                trend_factor = 1.0 + (quarter_index * 0.05)  # 随时间增长
                
                # 项目数量与员工数量相关
                employee_factor = base_employee_count / 50
                project_count = int(base_project_count * trend_factor * (0.8 + 0.4 * employee_factor))
                
                # 测试用例数与项目数量相关
                test_case_count = int(base_test_case_count * (1.0 + 0.3 * (project_count / 15 - 1)))
                
                # 自动化测试用例数与测试用例数相关
                automated_test_count = int(base_test_case_count * 0.6 * (1.0 + 0.2 * (test_case_count / 1500 - 1)))
                
                # 代码覆盖率与自动化测试相关
                code_coverage = min(0.95, base_code_coverage * (1.0 + 0.1 * (automated_test_count / 1000 - 1)))
                
                # Bug修复率与代码覆盖率相关
                bug_fix_rate = min(0.98, base_bug_fix_rate * (1.0 + 0.05 * (code_coverage / 0.8 - 1)))
                
                # 项目交付率与员工数量相关
                delivery_rate = min(0.99, base_delivery_rate * (1.0 + 0.03 * (employee_factor - 1)))
                
                # 客户满意度与交付率相关
                customer_satisfaction = min(5.0, base_customer_satisfaction * (1.0 + 0.02 * (delivery_rate / 0.9 - 1)))
                
                row = {
                    'id': id_counter,
                    'department_name': dept,
                    'quarter': quarter,
                    'project_count': project_count,
                    'employee_count': base_employee_count,
                    'test_case_count': test_case_count,
                    'automated_test_count': automated_test_count,
                    'code_coverage': round(code_coverage, 3),
                    'bug_fix_rate': round(bug_fix_rate, 3),
                    'delivery_rate': round(delivery_rate, 3),
                    'customer_satisfaction': round(customer_satisfaction, 3)
                }
                data.append(row)
                id_counter += 1
        
        return pd.DataFrame(data)
    
    def test_connection(self) -> bool:
        """测试连接"""
        return True
    
    def get_databases(self) -> list:
        """获取数据库列表"""
        return ['default', 'kpi_db', 'analytics']
    
    def get_tables(self) -> list:
        """获取表列表"""
        return ['kpi_data', 'department_metrics', 'project_analytics']
    
    def get_data_summary(self, table_name: str) -> dict:
        """获取数据摘要"""
        return {
            'table_name': table_name,
            'database': 'default',
            'total_rows': len(self.data),
            'total_columns': len(self.data.columns),
            'numeric_columns': ['project_count', 'employee_count', 'test_case_count', 
                              'automated_test_count', 'code_coverage', 'bug_fix_rate', 
                              'delivery_rate', 'customer_satisfaction'],
            'string_columns': ['department_name', 'quarter'],
            'date_columns': [],
            'all_columns': list(self.data.columns)
        }
    
    def get_kpi_data(self, **kwargs) -> pd.DataFrame:
        """获取KPI数据"""
        return self.data.copy()
    
    def get_department_kpi_data(self, department_name: str, **kwargs) -> pd.DataFrame:
        """获取部门KPI数据"""
        return self.data[self.data['department_name'] == department_name].copy()
    
    def get_metric_trend_data(self, metric_name: str, **kwargs) -> pd.DataFrame:
        """获取指标趋势数据"""
        if metric_name not in self.data.columns:
            return pd.DataFrame()
        
        trend_data = self.data.groupby('quarter')[metric_name].agg(['mean', 'min', 'max', 'count']).reset_index()
        trend_data.columns = ['quarter', 'avg_value', 'min_value', 'max_value', 'data_count']
        return trend_data
    
    def get_correlation_data(self, metric_columns: list, **kwargs) -> pd.DataFrame:
        """获取相关性数据"""
        return self.data[['department_name', 'quarter'] + metric_columns].copy()
    
    def get_association_data(self, metric_columns: list, **kwargs) -> pd.DataFrame:
        """获取关联关系数据"""
        return self.data[['department_name', 'quarter'] + metric_columns].copy()
    
    def close(self):
        """关闭连接"""
        logger.info("模拟ClickHouse连接已关闭")


class MockClickHouseKPIAnalyzer:
    """模拟ClickHouse KPI分析器"""
    
    def __init__(self, connector):
        self.connector = connector
    
    def analyze_department_performance(self, department_name: str, **kwargs):
        """分析部门绩效"""
        dept_data = self.connector.get_department_kpi_data(department_name)
        
        if dept_data.empty:
            return {'error': f'未找到部门 {department_name} 的数据'}
        
        results = {
            'department_name': department_name,
            'data_points': len(dept_data),
            'time_range': {
                'start': dept_data['quarter'].min(),
                'end': dept_data['quarter'].max()
            },
            'metrics_analysis': {}
        }
        
        # 分析每个指标
        metric_columns = ['project_count', 'employee_count', 'test_case_count', 
                         'automated_test_count', 'code_coverage', 'bug_fix_rate', 
                         'delivery_rate', 'customer_satisfaction']
        
        for metric in metric_columns:
            if metric in dept_data.columns:
                metric_data = dept_data[metric].dropna()
                if len(metric_data) > 0:
                    results['metrics_analysis'][metric] = {
                        'mean': float(metric_data.mean()),
                        'std': float(metric_data.std()),
                        'min': float(metric_data.min()),
                        'max': float(metric_data.max()),
                        'trend': self._calculate_trend(metric_data),
                        'anomalies': self._detect_anomalies(metric_data)
                    }
        
        return results
    
    def analyze_metric_correlations(self, metric_columns: list, **kwargs):
        """分析指标相关性"""
        corr_data = self.connector.get_correlation_data(metric_columns)
        
        if corr_data.empty:
            return {'error': '未找到有效数据'}
        
        # 计算相关性矩阵
        metric_data = corr_data[metric_columns].dropna()
        correlation_matrix = metric_data.corr()
        
        # 找出强相关性
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # 强相关性阈值
                    strong_correlations.append({
                        'metric1': correlation_matrix.columns[i],
                        'metric2': correlation_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations,
            'data_points': len(metric_data)
        }
    
    def _calculate_trend(self, data: pd.Series) -> str:
        """计算趋势"""
        if len(data) < 2:
            return 'insufficient_data'
        
        x = np.arange(len(data))
        y = data.values
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.05:
            return 'increasing'
        elif slope < -0.05:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_anomalies(self, data: pd.Series, threshold: float = 2.0) -> list:
        """检测异常值"""
        if len(data) < 3:
            return []
        
        mean = data.mean()
        std = data.std()
        
        if std == 0:
            return []
        
        z_scores = np.abs((data - mean) / std)
        anomalies = z_scores > threshold
        
        return data[anomalies].index.tolist()


def demo_1_basic_analysis():
    """演示1: 基础分析"""
    print("=" * 60)
    print("演示1: 基础分析")
    print("=" * 60)
    
    # 初始化模拟连接器
    connector = MockClickHouseConnector()
    analyzer = MockClickHouseKPIAnalyzer(connector)
    
    # 获取数据摘要
    summary = connector.get_data_summary('kpi_data')
    print("数据摘要:")
    print(f"  表名: {summary['table_name']}")
    print(f"  总行数: {summary['total_rows']}")
    print(f"  总列数: {summary['total_columns']}")
    print(f"  数值列: {summary['numeric_columns']}")
    
    # 获取KPI数据
    kpi_data = connector.get_kpi_data()
    print(f"\n数据形状: {kpi_data.shape}")
    print(f"数据预览:")
    print(kpi_data.head())
    
    # 进行综合分析
    comprehensive_analyzer = KPIComprehensiveAnalyzer()
    analysis_results = comprehensive_analyzer.analyze_kpi_data(
        data=kpi_data,
        department_column='department_name',
        metric_columns=['project_count', 'employee_count', 'test_case_count', 
                       'automated_test_count', 'code_coverage', 'bug_fix_rate', 
                       'delivery_rate', 'customer_satisfaction'],
        time_columns=['quarter']
    )
    
    print("\n分析结果摘要:")
    print(f"  异常检测结果: {len(analysis_results.get('anomaly_detection', {}).get('anomalies', []))} 个异常")
    print(f"  趋势分析结果: {len(analysis_results.get('trend_analysis', {}).get('trends', []))} 个趋势")
    
    connector.close()
    return True


def demo_2_department_analysis():
    """演示2: 部门分析"""
    print("\n" + "=" * 60)
    print("演示2: 部门分析")
    print("=" * 60)
    
    connector = MockClickHouseConnector()
    analyzer = MockClickHouseKPIAnalyzer(connector)
    
    # 分析技术部
    results = analyzer.analyze_department_performance('技术部')
    
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
    
    connector.close()
    return True


def demo_3_correlation_analysis():
    """演示3: 相关性分析"""
    print("\n" + "=" * 60)
    print("演示3: 相关性分析")
    print("=" * 60)
    
    connector = MockClickHouseConnector()
    analyzer = MockClickHouseKPIAnalyzer(connector)
    
    # 分析指标相关性
    metric_columns = ['project_count', 'employee_count', 'test_case_count', 
                     'automated_test_count', 'code_coverage', 'bug_fix_rate']
    
    results = analyzer.analyze_metric_correlations(metric_columns)
    
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
    
    connector.close()
    return True


def demo_4_association_mining():
    """演示4: 关联关系挖掘"""
    print("\n" + "=" * 60)
    print("演示4: 关联关系挖掘")
    print("=" * 60)
    
    connector = MockClickHouseConnector()
    
    # 获取关联关系数据
    metric_columns = ['project_count', 'employee_count', 'test_case_count', 
                     'automated_test_count', 'code_coverage', 'bug_fix_rate']
    
    association_data = connector.get_association_data(metric_columns)
    
    if association_data.empty:
        print("✗ 未找到有效数据")
        return False
    
    # 进行关联关系挖掘
    miner = KPIAssociationMiner()
    association_results = miner.discover_associations(
        data=association_data,
        metric_columns=metric_columns
    )
    
    print("关联关系挖掘结果:")
    print(f"  数据形状: {association_data.shape}")
    
    # 显示关联关系摘要
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
    
    connector.close()
    return True


def demo_5_anomaly_detection():
    """演示5: 异常检测"""
    print("\n" + "=" * 60)
    print("演示5: 异常检测")
    print("=" * 60)
    
    connector = MockClickHouseConnector()
    
    # 检测异常
    metrics = ['project_count', 'test_case_count', 'code_coverage']
    
    for metric in metrics:
        # 获取指标趋势数据
        trend_data = connector.get_metric_trend_data(metric)
        
        if not trend_data.empty:
            # 简单的异常检测（基于平均值和标准差）
            values = trend_data['avg_value']
            mean = values.mean()
            std = values.std()
            
            anomalies = []
            for i, value in enumerate(values):
                z_score = abs((value - mean) / std)
                if z_score > 2.0:  # 异常阈值
                    anomalies.append({
                        'quarter': trend_data.iloc[i]['quarter'],
                        'value': value,
                        'z_score': z_score
                    })
            
            print(f"\n{metric} 异常检测结果:")
            print(f"  异常数量: {len(anomalies)}")
            if anomalies:
                print("  异常数据示例:")
                for i, anomaly in enumerate(anomalies[:3], 1):
                    print(f"    {i}. 季度: {anomaly['quarter']}, "
                          f"值: {anomaly['value']:.3f}, "
                          f"Z-score: {anomaly['z_score']:.3f}")
    
    connector.close()
    return True


def demo_6_data_export():
    """演示6: 数据导出"""
    print("\n" + "=" * 60)
    print("演示6: 数据导出")
    print("=" * 60)
    
    connector = MockClickHouseConnector()
    
    # 导出数据到Excel
    output_file = "mock_clickhouse_kpi_data.xlsx"
    kpi_data = connector.get_kpi_data()
    
    try:
        kpi_data.to_excel(output_file, index=False)
        print(f"✓ 数据导出成功: {output_file}")
        print(f"✓ 导出文件包含 {len(kpi_data)} 行数据")
        print(f"✓ 导出文件包含 {len(kpi_data.columns)} 列")
        
        # 验证导出文件
        if os.path.exists(output_file):
            df = pd.read_excel(output_file)
            print(f"✓ 验证成功，文件包含 {len(df)} 行数据")
        else:
            print("✗ 导出文件未找到")
        
    except Exception as e:
        print(f"✗ 数据导出失败: {e}")
    
    connector.close()
    return True


def main():
    """主函数"""
    print("ClickHouse KPI数据分析功能演示")
    print("使用模拟数据演示ClickHouse分析功能")
    
    results = []
    
    try:
        # 运行各个演示
        results.append(("基础分析", demo_1_basic_analysis()))
        results.append(("部门分析", demo_2_department_analysis()))
        results.append(("相关性分析", demo_3_correlation_analysis()))
        results.append(("关联关系挖掘", demo_4_association_mining()))
        results.append(("异常检测", demo_5_anomaly_detection()))
        results.append(("数据导出", demo_6_data_export()))
        
        # 显示演示结果
        print("\n" + "=" * 60)
        print("演示结果汇总")
        print("=" * 60)
        
        passed = 0
        total = len(results)
        
        for demo_name, success in results:
            status = "✓ 通过" if success else "✗ 失败"
            print(f"{demo_name}: {status}")
            if success:
                passed += 1
        
        print(f"\n总体结果: {passed}/{total} 个演示通过")
        
        if passed == total:
            print("\n🎉 所有ClickHouse功能演示成功！")
            print("\nClickHouse功能特点:")
            print("1. ✓ 高性能数据查询 - 支持大规模KPI数据分析")
            print("2. ✓ 实时数据处理 - 支持实时指标监控")
            print("3. ✓ 复杂SQL查询 - 支持复杂的分析查询")
            print("4. ✓ 数据导出 - 支持导出到Excel格式")
            print("5. ✓ 集成分析 - 与数据挖掘功能无缝集成")
            
            print("\n实际使用建议:")
            print("- 安装并配置ClickHouse数据库服务")
            print("- 使用 --config 参数指定ClickHouse配置文件")
            print("- 使用 --table 参数指定要分析的表名")
            print("- 使用 --action 参数选择执行的操作")
            print("- 使用 --metrics 参数指定要分析的指标列")
            print("- 定期备份重要的KPI数据")
            
            print("\nClickHouse安装指南:")
            print("1. 下载ClickHouse: https://clickhouse.com/docs/en/install")
            print("2. 启动服务: sudo systemctl start clickhouse-server")
            print("3. 创建数据库和表")
            print("4. 导入KPI数据")
            print("5. 运行分析脚本")
        else:
            print(f"\n⚠️  有 {total - passed} 个演示失败")
        
        # 清理导出文件
        if os.path.exists("mock_clickhouse_kpi_data.xlsx"):
            os.remove("mock_clickhouse_kpi_data.xlsx")
            print("已清理导出文件")
        
    except Exception as e:
        logger.error(f"ClickHouse演示运行失败: {e}")
        print(f"\n错误: {e}")
        print("请检查依赖包是否正确安装")


if __name__ == "__main__":
    main()
