#!/usr/bin/env python3
"""
项目数据挖掘测试报告生成脚本
根据test_project_mining生成PDF格式的测试报告

使用方法:
    python run_project_mining_report.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    """主函数：运行项目数据挖掘并生成PDF报告"""
    print("=" * 60)
    print("项目数据挖掘测试报告生成器")
    print("=" * 60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # 导入并运行test_project_mining模块
        import test_project_mining
        
        # 调用main函数执行分析和报告生成
        test_project_mining.main()
        
        print()
        print("=" * 60)
        print("✅ 报告生成完成！")
        print()
        print("生成的文件：")
        
        # 列出生成的文件
        if os.path.exists('test_project_data.xlsx'):
            print("  📊 测试数据: test_project_data.xlsx")
            
        # 查找最新的PDF报告
        reports_dir = Path('reports')
        if reports_dir.exists():
            pdf_files = list(reports_dir.glob('project_mining_report_*.pdf'))
            html_files = list(reports_dir.glob('project_mining_report_*.html'))
            
            if pdf_files:
                latest_pdf = max(pdf_files, key=lambda p: p.stat().st_mtime)
                print(f"  📄 PDF报告: {latest_pdf}")
                
            if html_files:
                latest_html = max(html_files, key=lambda p: p.stat().st_mtime)
                print(f"  🌐 HTML报告: {latest_html}")
        
        print()
        print("🎉 测试报告生成成功！")
        print("=" * 60)
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖库已正确安装:")
        print("  pip install reportlab matplotlib seaborn pandas numpy scipy")
        
    except Exception as e:
        print(f"❌ 运行错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()