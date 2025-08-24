#!/usr/bin/env python3
"""
依赖模块检查脚本
检查requirements.txt中的所有模块是否可以正常导入
"""

import sys
import importlib
from typing import List, Tuple

def check_imports() -> List[Tuple[str, bool, str]]:
    """检查所有必需的模块导入"""
    
    # 今天新增功能使用的核心模块
    required_modules = [
        # 基础数据处理
        'pandas',
        'numpy', 
        'scipy',
        
        # 数据可视化
        'matplotlib',
        'seaborn',
        'plotly',
        
        # 机器学习和数据挖掘
        'sklearn',
        'mlxtend',
        'networkx',
        'statsmodels',
        
        # 文件处理
        'openpyxl',
        'xlrd',
        
        # 配置和日志
        'yaml',
        'loguru',
        
        # 数据库连接
        'clickhouse_connect',
        'sqlalchemy',
        
        # PDF报告生成
        'reportlab',
        
        # 字体处理
        'fonttools',
        
        # 其他工具
        'tqdm',
        'pathlib',
        'json',
        'datetime',
        'typing',
        'argparse'
    ]
    
    results = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            results.append((module, True, "✅ 导入成功"))
        except ImportError as e:
            results.append((module, False, f"❌ 导入失败: {e}"))
    
    return results

def main():
    """主函数"""
    print("=" * 60)
    print("依赖模块检查")
    print("=" * 60)
    
    results = check_imports()
    
    success_count = 0
    failed_modules = []
    
    for module, success, message in results:
        print(f"{module:20} {message}")
        if success:
            success_count += 1
        else:
            failed_modules.append(module)
    
    print("\n" + "=" * 60)
    print(f"检查结果: {success_count}/{len(results)} 个模块导入成功")
    
    if failed_modules:
        print(f"\n❌ 失败的模块: {', '.join(failed_modules)}")
        print("\n建议安装命令:")
        print("pip install -r requirements.txt")
    else:
        print("\n🎉 所有依赖模块检查通过！")
    
    print("\n今天新增的主要功能模块:")
    print("- 可配置项目数据Apriori分析器")
    print("- HTML饼图报告生成修复")
    print("- 一键式执行脚本")
    print("- YAML配置文件支持")
    print("- 中英文字段映射")

if __name__ == "__main__":
    main()