#!/usr/bin/env python3
"""
数据分析项目使用示例
演示如何使用项目进行KPI指标分析
"""

import sys
import os
from datetime import datetime, timedelta

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.main import DataAnalysisPipeline
from src.utils.logger import setup_logger, get_logger


def main():
    """主函数 - 演示项目使用"""
    
    # 设置日志
    setup_logger()
    logger = get_logger("example_usage")
    
    print("=== 数据分析项目使用示例 ===\n")
    
    try:
        # 创建分析流水线
        print("1. 创建数据分析流水线...")
        pipeline = DataAnalysisPipeline()
        print("✓ 流水线创建成功\n")
        
        # 获取可用的KPI指标
        print("2. 获取可用的KPI指标...")
        available_kpis = pipeline.calculator.get_available_kpis()
        print(f"可用的KPI指标: {available_kpis}\n")
        
        # 运行分析（使用示例数据，因为可能没有真实的数据库连接）
        print("3. 运行分析示例...")
        print("注意: 由于没有真实的数据库连接，这里演示的是分析流程")
        print("实际使用时，请确保配置了正确的数据库连接信息\n")
        
        # 演示配置
        print("4. 配置说明:")
        print("   - 数据库配置: config/database.yaml")
        print("   - KPI配置: config/kpi_config.yaml")
        print("   - SQL文件: sql/ 目录")
        print("   - 分析结果: reports/ 目录\n")
        
        # 演示命令行使用
        print("5. 命令行使用示例:")
        print("   python -m src.main --kpi user_retention_rate --analysis distribution,trend,anomaly")
        print("   python -m src.main --kpi conversion_rate daily_active_users --start-date 2024-01-01 --end-date 2024-01-31")
        print("   python -m src.main --kpi average_order_value --output-dir custom_reports\n")
        
        # 演示Python API使用
        print("6. Python API使用示例:")
        print("""
from src.main import DataAnalysisPipeline

# 创建流水线
pipeline = DataAnalysisPipeline()

# 运行分析
results = pipeline.run_analysis(
    kpi_names=['user_retention_rate', 'conversion_rate'],
    analysis_types=['distribution', 'trend', 'anomaly'],
    params={'start_date': '2024-01-01', 'end_date': '2024-01-31'}
)

# 保存结果
output_path = pipeline.save_results(results, 'reports')

# 清理资源
pipeline.close()
        """)
        
        # 演示Jupyter笔记本使用
        print("7. Jupyter笔记本使用:")
        print("   运行 notebooks/kpi_analysis_example.py 查看完整示例\n")
        
        # 演示测试
        print("8. 运行测试:")
        print("   python -m pytest tests/")
        print("   python tests/test_basic.py\n")
        
        # 清理资源
        pipeline.close()
        print("✓ 示例演示完成")
        
    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        print(f"错误: {e}")
        print("\n请检查:")
        print("1. 是否安装了所有依赖: pip install -r requirements.txt")
        print("2. 数据库配置是否正确")
        print("3. 项目路径是否正确")


if __name__ == "__main__":
    main()
