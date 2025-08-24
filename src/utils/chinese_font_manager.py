"""
中文字体设置工具
用于确保PDF报告和图表中的中文字符正确显示
"""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ChineseFontManager:
    """中文字体管理器"""
    
    def __init__(self):
        """初始化字体管理器"""
        self.pdf_font = None
        self.matplotlib_font = None
        self.setup_fonts()
    
    def setup_fonts(self):
        """设置中文字体"""
        self._setup_pdf_font()
        self._setup_matplotlib_font()
    
    def _setup_pdf_font(self):
        """设置PDF中文字体"""
        try:
            # macOS系统字体路径
            font_paths_macos = [
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/Hiragino Sans GB.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                '/Library/Fonts/Arial Unicode MS.ttf',
            ]
            
            # Windows系统字体路径
            font_paths_windows = [
                'C:\\Windows\\Fonts\\msyh.ttc',
                'C:\\Windows\\Fonts\\simsun.ttc',
                'C:\\Windows\\Fonts\\simhei.ttf',
            ]
            
            # Linux系统字体路径
            font_paths_linux = [
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/usr/share/fonts/truetype/arphic/uming.ttc',
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
            ]
            
            all_font_paths = font_paths_macos + font_paths_windows + font_paths_linux
            
            for font_path in all_font_paths:
                if os.path.exists(font_path):
                    try:
                        font_name = self._get_font_name(font_path)
                        pdfmetrics.registerFont(TTFont(font_name, font_path))
                        self.pdf_font = font_name
                        print(f"✅ PDF中文字体加载成功: {font_name}")
                        break
                    except Exception as e:
                        print(f"⚠️ 字体加载失败 {font_path}: {e}")
                        continue
            
            if not self.pdf_font:
                self.pdf_font = 'Helvetica'
                print("⚠️ 未找到中文字体，PDF将使用默认字体")
                
        except Exception as e:
            print(f"❌ PDF字体设置失败: {e}")
            self.pdf_font = 'Helvetica'
    
    def _setup_matplotlib_font(self):
        """设置matplotlib中文字体"""
        try:
            # 查找系统中可用的中文字体
            font_families = []
            
            # 通过字体名称查找
            chinese_font_names = [
                'PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'SimHei', 
                'SimSun', 'Microsoft YaHei', 'WenQuanYi Micro Hei'
            ]
            
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            
            for font_name in chinese_font_names:
                if font_name in available_fonts:
                    font_families.append(font_name)
            
            if font_families:
                self.matplotlib_font = font_families[0]
                plt.rcParams['font.sans-serif'] = font_families + ['DejaVu Sans']
                print(f"✅ matplotlib中文字体设置成功: {self.matplotlib_font}")
            else:
                # 备用方案：直接设置字体名称
                backup_fonts = ['PingFang SC', 'SimHei', 'DejaVu Sans']
                plt.rcParams['font.sans-serif'] = backup_fonts
                self.matplotlib_font = backup_fonts[0]
                print(f"⚠️ 使用备用字体设置: {backup_fonts}")
            
            # 设置负号正常显示
            plt.rcParams['axes.unicode_minus'] = False
            
        except Exception as e:
            print(f"❌ matplotlib字体设置失败: {e}")
            self.matplotlib_font = 'DejaVu Sans'
    
    def _get_font_name(self, font_path):
        """根据字体路径生成字体名称"""
        font_file = os.path.basename(font_path)
        
        name_mapping = {
            'PingFang.ttc': 'PingFangSC',
            'Hiragino Sans GB.ttc': 'HiraginoSansGB',
            'STHeiti Light.ttc': 'STHeiti',
            'Arial Unicode MS.ttf': 'ArialUnicodeMS',
            'msyh.ttc': 'MicrosoftYaHei',
            'simsun.ttc': 'SimSun',
            'simhei.ttf': 'SimHei',
            'wqy-microhei.ttc': 'WenQuanYiMicroHei',
            'uming.ttc': 'ARPLUMing'
        }
        
        return name_mapping.get(font_file, 'ChineseFont')
    
    def get_pdf_font(self):
        """获取PDF字体名称"""
        return self.pdf_font
    
    def get_matplotlib_font(self):
        """获取matplotlib字体名称"""
        return self.matplotlib_font
    
    def test_fonts(self):
        """测试字体设置"""
        print("\n=== 字体设置测试 ===")
        print(f"PDF字体: {self.pdf_font}")
        print(f"matplotlib字体: {self.matplotlib_font}")
        
        # 测试matplotlib字体
        try:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.text(0.5, 0.5, '中文字体测试 Chinese Font Test', 
                   ha='center', va='center', fontsize=14)
            ax.set_title('字体测试图表')
            plt.tight_layout()
            plt.savefig('font_test.png', dpi=150, bbox_inches='tight')
            plt.close()
            print("✅ matplotlib中文字体测试成功，已生成 font_test.png")
        except Exception as e:
            print(f"❌ matplotlib字体测试失败: {e}")

# 全局字体管理器实例
_font_manager = None

def get_font_manager():
    """获取全局字体管理器实例"""
    global _font_manager
    if _font_manager is None:
        _font_manager = ChineseFontManager()
    return _font_manager

def setup_chinese_fonts():
    """设置中文字体（便捷函数）"""
    return get_font_manager()

if __name__ == "__main__":
    # 测试字体设置
    font_manager = ChineseFontManager()
    font_manager.test_fonts()