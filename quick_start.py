#!/usr/bin/env python3
"""
KPI分析系统快速启动脚本
帮助用户快速上手和使用KPI分析系统
"""

import sys
import os
from pathlib import Path
import subprocess

def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🎯 KPI Excel数据分析系统 - 快速启动")
    print("=" * 60)
    print("本系统支持从Excel读取KPI数据，进行异常检测和趋势分析")
    print("=" * 60)

def check_environment():
    """检查环境"""
    print("🔍 检查运行环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8+")
        return False
    
    print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ 运行在虚拟环境中")
    else:
        print("⚠️  建议使用虚拟环境")
    
    return True

def install_dependencies():
    """安装依赖包"""
    print("\n📦 安装依赖包...")
    
    try:
        # 检查requirements.txt是否存在
        if not Path("requirements.txt").exists():
            print("❌ requirements.txt文件不存在")
            return False
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 依赖包安装成功")
            return True
        else:
            print(f"❌ 依赖包安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装过程出错: {e}")
        return False

def run_tests():
    """运行测试"""
    print("\n🧪 运行系统测试...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_kpi_system.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 系统测试通过")
            return True
        else:
            print(f"❌ 系统测试失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程出错: {e}")
        return False

def create_sample_data():
    """创建示例数据"""
    print("\n📊 创建示例数据...")
    
    try:
        # 添加src目录到Python路径
        sys.path.insert(0, str(Path(__file__).parent / 'src'))
        
        from utils.excel_reader import create_sample_excel
        
        sample_file = create_sample_excel("sample_kpi_data.xlsx")
        print(f"✅ 示例数据已创建: {sample_file}")
        return True
        
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        return False

def run_example():
    """运行示例分析"""
    print("\n🚀 运行示例分析...")
    
    try:
        result = subprocess.run([
            sys.executable, "example_kpi_analysis.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 示例分析完成")
            return True
        else:
            print(f"❌ 示例分析失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 示例运行出错: {e}")
        return False

def show_usage():
    """显示使用说明"""
    print("\n" + "=" * 60)
    print("📖 使用说明")
    print("=" * 60)
    
    print("\n1. 基础使用:")
    print("   python src/kpi_excel_analyzer.py your_kpi_data.xlsx")
    
    print("\n2. 分析特定指标:")
    print("   python src/kpi_excel_analyzer.py your_kpi_data.xlsx --metric '在编人数'")
    
    print("\n3. 分析特定部门:")
    print("   python src/kpi_excel_analyzer.py your_kpi_data.xlsx --department '技术部'")
    
    print("\n4. 导出结果到Excel:")
    print("   python src/kpi_excel_analyzer.py your_kpi_data.xlsx --export-excel results.xlsx")
    
    print("\n5. 编程接口使用:")
    print("   python -c \"from src.kpi_excel_analyzer import KPIExcelAnalyzer; analyzer = KPIExcelAnalyzer(); results = analyzer.analyze_excel_file('your_kpi_data.xlsx')\"")
    
    print("\n📁 输出文件:")
    print("   - reports/kpi_report_*.html (分析报告)")
    print("   - results.xlsx (分析结果)")
    
    print("\n📚 更多信息:")
    print("   - 查看 README_KPI_Analysis.md 获取详细文档")
    print("   - 运行 python example_kpi_analysis.py 查看完整示例")

def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 60)
    print("🎮 交互模式")
    print("=" * 60)
    
    while True:
        print("\n请选择操作:")
        print("1. 创建示例数据")
        print("2. 运行示例分析")
        print("3. 分析Excel文件")
        print("4. 查看使用说明")
        print("5. 退出")
        
        choice = input("\n请输入选择 (1-5): ").strip()
        
        if choice == "1":
            create_sample_data()
        elif choice == "2":
            run_example()
        elif choice == "3":
            file_path = input("请输入Excel文件路径: ").strip()
            if file_path and Path(file_path).exists():
                try:
                    sys.path.insert(0, str(Path(__file__).parent / 'src'))
                    from kpi_excel_analyzer import KPIExcelAnalyzer
                    
                    analyzer = KPIExcelAnalyzer()
                    results = analyzer.analyze_excel_file(file_path)
                    print(f"✅ 分析完成，报告路径: {results['report_path']}")
                except Exception as e:
                    print(f"❌ 分析失败: {e}")
            else:
                print("❌ 文件不存在")
        elif choice == "4":
            show_usage()
        elif choice == "5":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入")

def main():
    """主函数"""
    print_banner()
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请解决上述问题后重试")
        return
    
    # 检查是否已安装依赖
    try:
        import pandas
        import numpy
        import sklearn
        print("✅ 依赖包已安装")
    except ImportError:
        print("⚠️  依赖包未安装，正在安装...")
        if not install_dependencies():
            print("\n❌ 依赖包安装失败，请手动运行: pip install -r requirements.txt")
            return
    
    # 运行测试
    if not run_tests():
        print("\n⚠️  系统测试失败，但可以继续使用")
    
    # 创建示例数据
    if not create_sample_data():
        print("\n⚠️  示例数据创建失败")
    
    # 询问是否运行示例
    choice = input("\n是否运行示例分析？(y/n): ").strip().lower()
    if choice in ['y', 'yes', '是']:
        run_example()
    
    # 显示使用说明
    show_usage()
    
    # 询问是否进入交互模式
    choice = input("\n是否进入交互模式？(y/n): ").strip().lower()
    if choice in ['y', 'yes', '是']:
        interactive_mode()
    
    print("\n🎉 快速启动完成！")
    print("现在您可以开始使用KPI分析系统了。")

if __name__ == "__main__":
    main()
