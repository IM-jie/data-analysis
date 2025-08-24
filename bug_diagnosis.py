#!/usr/bin/env python3
"""
简单的bug诊断脚本
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_basic_imports():
    """测试基础导入"""
    try:
        import pandas as pd
        import numpy as np
        from sklearn.ensemble import IsolationForest
        print("✓ 基础包导入成功")
        return True
    except Exception as e:
        print(f"✗ 基础包导入失败: {e}")
        return False

def test_excel_reader():
    """测试Excel读取器"""
    try:
        from utils.excel_reader import ExcelKPIReader, create_sample_excel
        
        # 创建测试文件
        test_file = create_sample_excel("test_debug.xlsx")
        print(f"✓ 测试文件创建: {test_file}")
        
        # 读取数据
        reader = ExcelKPIReader(test_file)
        data = reader.read_excel()
        column_info = reader.detect_columns()
        
        print(f"✓ 数据读取成功: {data.shape}")
        print(f"✓ 检测列: 部门={column_info['department_column']}, 指标数={len(column_info['metric_columns'])}")
        
        return data, column_info
        
    except Exception as e:
        print(f"✗ Excel读取器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_anomaly_detector():
    """测试异常检测器"""
    try:
        from analysis.kpi_anomaly_detector import KPIComprehensiveAnalyzer
        
        data, column_info = test_excel_reader()
        if data is None:
            return False
        
        analyzer = KPIComprehensiveAnalyzer()
        print("✓ 分析器初始化成功")
        
        # 只测试异常检测部分，跳过趋势分析
        print("尝试进行异常检测...")
        
        # 直接调用异常检测方法
        anomalies, anomaly_details = analyzer._detect_all_anomalies(
            data, 
            column_info['metric_columns'][:2],  # 只测试前2个指标
            column_info['department_column'],
            None  # 明确传递None
        )
        
        print(f"✓ 异常检测成功: {len(anomalies)} 个指标")
        print(f"✓ 异常详情: {len(anomaly_details)} 条记录")
        
        return True
        
    except Exception as e:
        print(f"✗ 异常检测器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("KPI系统Bug诊断")
    print("=" * 50)
    
    if not test_basic_imports():
        return
    
    if not test_anomaly_detector():
        return
    
    print("\n✓ 所有测试通过!")

if __name__ == "__main__":
    main()