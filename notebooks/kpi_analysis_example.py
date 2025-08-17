# KPI指标数据分析示例
# 本脚本演示如何使用数据分析项目进行KPI指标的分析

import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append('..')

# 导入项目模块
from src.database.connection import ClickHouseConnector
from src.kpi.calculator import KPICalculator
from src.analysis.analyzer import DataAnalyzer
from src.visualization.charts import ChartGenerator
from src.utils.logger import setup_logger, get_logger

def generate_sample_data(n_days=30):
    """生成示例KPI数据"""
    dates = pd.date_range(start=datetime.now() - timedelta(days=n_days), 
                          end=datetime.now(), freq='D')
    
    # 用户留存率数据
    np.random.seed(42)
    retention_data = pd.DataFrame({
        'date': dates,
        'retention_rate': np.random.normal(0.25, 0.05, len(dates)) + 0.1 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7),
        'new_users': np.random.poisson(1000, len(dates)),
        'retained_users': np.random.poisson(250, len(dates))
    })
    retention_data['retention_rate'] = retention_data['retention_rate'].clip(0, 1)
    
    # 转化率数据
    conversion_data = pd.DataFrame({
        'date': dates,
        'conversion_rate': np.random.normal(0.05, 0.01, len(dates)) + 0.02 * np.sin(np.arange(len(dates)) * 2 * np.pi / 14),
        'visitors': np.random.poisson(5000, len(dates)),
        'conversions': np.random.poisson(250, len(dates))
    })
    conversion_data['conversion_rate'] = conversion_data['conversion_rate'].clip(0, 0.2)
    
    # 日活跃用户数据
    dau_data = pd.DataFrame({
        'date': dates,
        'active_users': np.random.poisson(15000, len(dates)) + 2000 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7),
        'new_users': np.random.poisson(500, len(dates)),
        'returning_users': np.random.poisson(14500, len(dates))
    })
    
    # 平均订单金额数据
    aov_data = pd.DataFrame({
        'date': dates,
        'avg_order_value': np.random.normal(150, 20, len(dates)) + 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / 30),
        'total_orders': np.random.poisson(200, len(dates)),
        'total_revenue': np.random.poisson(30000, len(dates))
    })
    aov_data['avg_order_value'] = aov_data['avg_order_value'].clip(50, 300)
    
    return {
        'user_retention_rate': retention_data,
        'conversion_rate': conversion_data,
        'daily_active_users': dau_data,
        'average_order_value': aov_data
    }

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    logger = get_logger("example")
    
    print("=== KPI指标数据分析示例 ===\n")
    
    # 1. 初始化组件
    print("1. 初始化组件...")
    
    # 初始化数据库连接（如果数据库可用）
    try:
        connector = ClickHouseConnector()
        logger.info("数据库连接成功")
        calculator = KPICalculator(connector)
    except Exception as e:
        logger.warning(f"数据库连接失败: {e}")
        connector = None
        calculator = None
    
    # 初始化其他组件
    analyzer = DataAnalyzer()
    chart_generator = ChartGenerator()
    
    print("✓ 组件初始化完成\n")
    
    # 2. 生成示例数据
    print("2. 生成示例数据...")
    sample_data = generate_sample_data(60)
    print("生成的示例数据:")
    for kpi_name, data in sample_data.items():
        print(f"  {kpi_name}: {len(data)} 行数据")
    print()
    
    # 3. 分析用户留存率数据
    print("3. 分析用户留存率数据...")
    kpi_name = 'user_retention_rate'
    data = sample_data[kpi_name]
    
    # 分布分析
    distribution_result = analyzer.analyze_distribution(data, 'retention_rate')
    print(f"分布分析结果:")
    print(f"  分布类型: {distribution_result['distribution_type']}")
    print(f"  均值: {distribution_result['basic_stats']['mean']:.3f}")
    print(f"  标准差: {distribution_result['basic_stats']['std']:.3f}")
    print(f"  异常值数量: {distribution_result['outliers']['count']}")
    
    # 趋势分析
    trend_result = analyzer.analyze_trend(data, 'date', 'retention_rate')
    print(f"趋势分析结果:")
    print(f"  趋势方向: {trend_result['trend_direction']}")
    print(f"  数据点数: {trend_result['data_points']}")
    print(f"  增长率: {trend_result['growth_rates']}")
    
    # 异常检测
    anomaly_result = analyzer.detect_anomalies(data, 'retention_rate', 'isolation_forest')
    print(f"异常检测结果:")
    print(f"  异常点数量: {anomaly_result['anomaly_stats']['anomaly_count']}")
    print(f"  异常比例: {anomaly_result['anomaly_stats']['anomaly_percentage']:.2f}%")
    print()
    
    # 4. 批量分析所有KPI
    print("4. 批量分析所有KPI指标...")
    all_results = {}
    
    for kpi_name, data in sample_data.items():
        print(f"分析 {kpi_name}...")
        
        # 选择主要指标列
        if 'retention_rate' in data.columns:
            target_col = 'retention_rate'
        elif 'conversion_rate' in data.columns:
            target_col = 'conversion_rate'
        elif 'active_users' in data.columns:
            target_col = 'active_users'
        elif 'avg_order_value' in data.columns:
            target_col = 'avg_order_value'
        else:
            continue
        
        # 执行分析
        try:
            distribution = analyzer.analyze_distribution(data, target_col)
            trend = analyzer.analyze_trend(data, 'date', target_col)
            anomaly = analyzer.detect_anomalies(data, target_col)
            
            all_results[kpi_name] = {
                'distribution': distribution,
                'trend': trend,
                'anomaly': anomaly
            }
            
            print(f"  ✓ 完成分析")
            
        except Exception as e:
            print(f"  ✗ 分析失败: {e}")
    
    print(f"总共分析了 {len(all_results)} 个KPI指标\n")
    
    # 5. 保存分析结果
    print("5. 保存分析结果...")
    import json
    
    # 创建输出目录
    output_dir = f"../reports/example_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存数据
    for kpi_name, data in sample_data.items():
        data.to_csv(f"{output_dir}/{kpi_name}.csv", index=False)
    
    # 保存分析结果
    with open(f"{output_dir}/analysis_results.json", 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    
    # 保存图表
    charts_dir = f"{output_dir}/charts"
    os.makedirs(charts_dir, exist_ok=True)
    
    for kpi_name, results in all_results.items():
        kpi_charts_dir = f"{charts_dir}/{kpi_name}"
        os.makedirs(kpi_charts_dir, exist_ok=True)
        
        # 保存分布图表
        dist_chart = chart_generator.create_distribution_chart(
            sample_data[kpi_name], 
            target_column=None, 
            analysis_result=results['distribution']
        )
        chart_generator.save_chart(dist_chart, f"{kpi_charts_dir}/distribution.html")
        
        # 保存趋势图表
        trend_chart = chart_generator.create_trend_chart(
            sample_data[kpi_name], 
            date_column=None, 
            value_column=None, 
            analysis_result=results['trend']
        )
        chart_generator.save_chart(trend_chart, f"{kpi_charts_dir}/trend.html")
        
        # 保存异常检测图表
        anomaly_chart = chart_generator.create_anomaly_chart(
            sample_data[kpi_name], 
            target_column=None, 
            analysis_result=results['anomaly']
        )
        chart_generator.save_chart(anomaly_chart, f"{kpi_charts_dir}/anomaly.html")
    
    print(f"分析结果已保存到: {output_dir}")
    
    # 6. 清理资源
    if connector:
        connector.close()
        print("数据库连接已关闭")
    
    print("\n分析完成！")

if __name__ == "__main__":
    main()
