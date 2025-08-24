"""
项目数据挖掘PDF报告生成器
生成基于test_project_mining分析结果的PDF格式报告
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# 导入中文字体管理器
try:
    import sys
    from pathlib import Path
    # 动态添加路径
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from utils.chinese_font_manager import get_font_manager
    FONT_MANAGER_AVAILABLE = True
    print("✅ 中文字体管理器加载成功")
except ImportError as e:
    FONT_MANAGER_AVAILABLE = False
    print(f"⚠️ 中文字体管理器不可用: {e}")

class ProjectMiningPDFReporter:
    """项目数据挖掘PDF报告生成器"""
    
    def __init__(self):
        """初始化PDF报告生成器"""
        self.setup_fonts()
        self.setup_styles()
        self.setup_matplotlib()
        
    def setup_fonts(self):
        """设置中文字体支持"""
        if FONT_MANAGER_AVAILABLE:
            # 使用专门的字体管理器
            font_manager = get_font_manager()
            self.chinese_font = font_manager.get_pdf_font()
            print(f"使用专门的中文字体管理器: {self.chinese_font}")
        else:
            # 备用字体设置
            self._setup_fallback_fonts()
    def _setup_fallback_fonts(self):
        """备用字体设置方法"""
        try:
            # 尝试注册中文字体
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/System/Library/Fonts/Hiragino Sans GB.ttc',  # macOS
                '/Library/Fonts/Arial Unicode MS.ttf',  # macOS
                '/System/Library/Fonts/STHeiti Light.ttc',  # macOS
                'C:\\Windows\\Fonts\\simsun.ttc',  # Windows
                'C:\\Windows\\Fonts\\msyh.ttc',  # Windows
                'C:\\Windows\\Fonts\\simhei.ttf',  # Windows
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            ]
            
            self.chinese_font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        # 使用不同的字体名称避免冲突
                        if 'PingFang' in font_path:
                            pdfmetrics.registerFont(TTFont('PingFangSC', font_path))
                            self.chinese_font = 'PingFangSC'
                        elif 'Hiragino' in font_path:
                            pdfmetrics.registerFont(TTFont('HiraginoSansGB', font_path))
                            self.chinese_font = 'HiraginoSansGB'
                        elif 'Arial Unicode' in font_path:
                            pdfmetrics.registerFont(TTFont('ArialUnicodeMS', font_path))
                            self.chinese_font = 'ArialUnicodeMS'
                        elif 'STHeiti' in font_path:
                            pdfmetrics.registerFont(TTFont('STHeiti', font_path))
                            self.chinese_font = 'STHeiti'
                        elif 'simsun' in font_path:
                            pdfmetrics.registerFont(TTFont('SimSun', font_path))
                            self.chinese_font = 'SimSun'
                        elif 'msyh' in font_path:
                            pdfmetrics.registerFont(TTFont('MicrosoftYaHei', font_path))
                            self.chinese_font = 'MicrosoftYaHei'
                        elif 'simhei' in font_path:
                            pdfmetrics.registerFont(TTFont('SimHei', font_path))
                            self.chinese_font = 'SimHei'
                        else:
                            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                            self.chinese_font = 'ChineseFont'
                        
                        print(f"成功加载中文字体: {self.chinese_font} ({font_path})")
                        break
                    except Exception as e:
                        print(f"字体加载失败 {font_path}: {e}")
                        continue
            
            if not self.chinese_font:
                # 使用默认字体
                self.chinese_font = 'Helvetica'
                print("警告: 未找到中文字体，将使用默认字体")
        
        except Exception as e:
            print(f"字体设置失败: {e}")
            self.chinese_font = 'Helvetica'
    
    def setup_styles(self):
        """设置文档样式"""
        self.styles = getSampleStyleSheet()
        
        # 添加中文样式
        self.styles.add(ParagraphStyle(
            name='ChineseTitle',
            parent=self.styles['Title'],
            fontName=self.chinese_font,
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseHeading1',
            parent=self.styles['Heading1'],
            fontName=self.chinese_font,
            fontSize=18,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseHeading2',
            parent=self.styles['Heading2'],
            fontName=self.chinese_font,
            fontSize=14,
            spaceAfter=15
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseNormal',
            parent=self.styles['Normal'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=10
        ))
        
        self.styles.add(ParagraphStyle(
            name='ChineseBodyText',
            parent=self.styles['BodyText'],
            fontName=self.chinese_font,
            fontSize=10,
            spaceAfter=8
        ))
    
    def setup_matplotlib(self):
        """设置matplotlib中文支持"""
        if FONT_MANAGER_AVAILABLE:
            # 使用专门的字体管理器
            font_manager = get_font_manager()
            matplotlib_font = font_manager.get_matplotlib_font()
            print(f"matplotlib使用中文字体: {matplotlib_font}")
        else:
            # 备用matplotlib设置
            self._setup_matplotlib_fallback()
        
        # 设置图表样式
        sns.set_style("whitegrid")
        plt.style.use('default')
    
    def _setup_matplotlib_fallback(self):
        """备用matplotlib设置"""
        # 设置matplotlib支持中文
        import matplotlib.font_manager as fm
        
        # 查找系统中可用的中文字体
        chinese_fonts = []
        font_list = fm.findSystemFonts()
        
        # 常见中文字体名称
        chinese_font_names = [
            'PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'SimHei', 'SimSun', 
            'Microsoft YaHei', 'WenQuanYi Micro Hei', 'AR PL UMing CN'
        ]
        
        # 查找可用的中文字体
        for font_path in font_list:
            try:
                font_prop = fm.FontProperties(fname=font_path)
                font_name = font_prop.get_name()
                if any(chinese_name in font_name for chinese_name in chinese_font_names):
                    chinese_fonts.append(font_name)
            except:
                continue
        
        # 设置中文字体优先级
        if chinese_fonts:
            plt.rcParams['font.sans-serif'] = chinese_fonts + ['DejaVu Sans']
            print(f"使用中文字体: {chinese_fonts[0]}")
        else:
            plt.rcParams['font.sans-serif'] = ['PingFang SC', 'SimHei', 'DejaVu Sans']
            print("未找到中文字体，使用默认设置")
        
        plt.rcParams['axes.unicode_minus'] = False
    
    def generate_project_mining_report(self, 
                                     analysis_results: Dict[str, Any],
                                     output_path: Optional[str] = None) -> str:
        """
        生成项目数据挖掘PDF报告
        
        Args:
            analysis_results: 分析结果字典
            output_path: 输出文件路径
            
        Returns:
            生成的PDF文件路径
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/project_mining_report_{timestamp}.pdf"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 构建报告内容
        story = []
        
        # 1. 封面页
        story.extend(self._create_cover_page(analysis_results))
        story.append(PageBreak())
        
        # 2. 执行摘要
        story.extend(self._create_executive_summary(analysis_results))
        story.append(PageBreak())
        
        # 3. 数据概览
        story.extend(self._create_data_overview(analysis_results))
        story.append(PageBreak())
        
        # 4. 统计分析
        story.extend(self._create_statistical_analysis(analysis_results))
        story.append(PageBreak())
        
        # 5. 相关性分析
        story.extend(self._create_correlation_analysis(analysis_results))
        story.append(PageBreak())
        
        # 6. 质量效率分析
        story.extend(self._create_quality_efficiency_analysis(analysis_results))
        story.append(PageBreak())
        
        # 7. 结论与建议
        story.extend(self._create_conclusions_recommendations(analysis_results))
        
        # 构建PDF
        doc.build(story)
        
        print(f"PDF报告已生成: {output_path}")
        return output_path
    
    def _create_cover_page(self, results: Dict[str, Any]) -> List:
        """创建封面页"""
        elements = []
        
        # 标题
        title = Paragraph("项目数据挖掘分析报告", self.styles['ChineseTitle'])
        elements.append(title)
        elements.append(Spacer(1, 50))
        
        # 基本信息
        project_count = results.get('total_projects', 0)
        
        info_data = [
            ['项目数量', str(project_count)],
            ['分析日期', datetime.now().strftime("%Y年%m月%d日")],
            ['报告版本', 'v1.0'],
            ['生成工具', '项目数据挖掘系统']
        ]
        
        info_table = Table(info_data, colWidths=[4*cm, 6*cm])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
        ]))
        
        elements.append(info_table)
        elements.append(Spacer(1, 100))
        
        # 报告说明
        description = "本报告基于项目测试数据进行深度分析，包含统计分析、相关性分析、关联性分析等多个维度，为项目管理和质量改进提供数据支持。"
        
        desc_para = Paragraph(description, self.styles['ChineseBodyText'])
        elements.append(desc_para)
        
        return elements
    
    def _create_executive_summary(self, results: Dict[str, Any]) -> List:
        """创建执行摘要"""
        elements = []
        
        # 标题
        elements.append(Paragraph("执行摘要", self.styles['ChineseHeading1']))
        
        # 关键发现
        key_findings = results.get('key_findings', [])
        if key_findings:
            elements.append(Paragraph("关键发现:", self.styles['ChineseHeading2']))
            
            for i, finding in enumerate(key_findings[:5], 1):
                finding_text = f"{i}. {finding}"
                elements.append(Paragraph(finding_text, self.styles['ChineseBodyText']))
        
        # 主要指标
        elements.append(Paragraph("主要指标:", self.styles['ChineseHeading2']))
        
        total_projects = results.get('total_projects', 0)
        quality_metrics = results.get('quality_metrics', {})
        
        metrics_lines = [
            f"• 总项目数: {total_projects}",
            f"• 平均自动化率: {quality_metrics.get('avg_automation_rate', 0):.1%}",
            f"• 平均缺陷密度: {quality_metrics.get('avg_defect_density', 0):.3f}",
            f"• 平均测试效率: {quality_metrics.get('avg_test_efficiency', 0):.1f} 用例/小时"
        ]
        
        for line in metrics_lines:
            elements.append(Paragraph(line, self.styles['ChineseBodyText']))
        
        return elements
    
    def _create_data_overview(self, results: Dict[str, Any]) -> List:
        """创建数据概览"""
        elements = []
        
        elements.append(Paragraph("数据概览", self.styles['ChineseHeading1']))
        
        # 项目分布图表
        if 'categorical_distributions' in results:
            chart_path = self._create_distribution_charts(results['categorical_distributions'])
            if chart_path:
                elements.append(Paragraph("项目分布情况", self.styles['ChineseHeading2']))
                img = RLImage(chart_path, width=16*cm, height=12*cm)
                elements.append(img)
                elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_statistical_analysis(self, results: Dict[str, Any]) -> List:
        """创建统计分析"""
        elements = []
        
        elements.append(Paragraph("统计分析", self.styles['ChineseHeading1']))
        
        # 数值字段统计表
        numerical_stats = results.get('numerical_statistics', {})
        if numerical_stats:
            elements.append(Paragraph("数值字段统计", self.styles['ChineseHeading2']))
            
            stats_data = [['字段名', '平均值', '中位数', '标准差', '最小值', '最大值']]
            
            for field, stats in numerical_stats.items():
                row = [
                    field,
                    f"{stats.get('mean', 0):.1f}",
                    f"{stats.get('median', 0):.1f}",
                    f"{stats.get('std', 0):.1f}",
                    str(stats.get('min', 0)),
                    str(stats.get('max', 0))
                ]
                stats_data.append(row)
            
            stats_table = Table(stats_data)
            stats_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.chinese_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_correlation_analysis(self, results: Dict[str, Any]) -> List:
        """创建相关性分析"""
        elements = []
        
        elements.append(Paragraph("相关性分析", self.styles['ChineseHeading1']))
        
        # 相关性热力图
        correlation_matrix = results.get('correlation_matrix')
        if correlation_matrix is not None:
            chart_path = self._create_correlation_heatmap(correlation_matrix)
            if chart_path:
                elements.append(Paragraph("相关性热力图", self.styles['ChineseHeading2']))
                img = RLImage(chart_path, width=14*cm, height=10*cm)
                elements.append(img)
                elements.append(Spacer(1, 20))
        
        # 强相关性列表
        strong_correlations = results.get('strong_correlations', [])
        if strong_correlations:
            elements.append(Paragraph("强相关性关系", self.styles['ChineseHeading2']))
            
            for corr in strong_correlations:
                direction = "正相关" if corr['correlation'] > 0 else "负相关"
                corr_text = f"• {corr['field1']} ↔ {corr['field2']}: {corr['correlation']:.3f} ({direction})"
                elements.append(Paragraph(corr_text, self.styles['ChineseBodyText']))
        
        return elements
    
    def _create_quality_efficiency_analysis(self, results: Dict[str, Any]) -> List:
        """创建质量效率分析"""
        elements = []
        
        elements.append(Paragraph("质量效率分析", self.styles['ChineseHeading1']))
        
        # 质量效率指标
        quality_metrics = results.get('quality_metrics', {})
        if quality_metrics:
            elements.append(Paragraph("质量效率指标", self.styles['ChineseHeading2']))
            
            metrics_lines = [
                f"• 平均自动化率: {quality_metrics.get('avg_automation_rate', 0):.1%}",
                f"• 平均缺陷密度: {quality_metrics.get('avg_defect_density', 0):.3f}",
                f"• 平均测试效率: {quality_metrics.get('avg_test_efficiency', 0):.1f} 用例/小时",
                f"• 高自动化率项目: {quality_metrics.get('high_automation_projects', 0)} 个",
                f"• 低缺陷密度项目: {quality_metrics.get('low_defect_projects', 0)} 个",
                f"• 高效率项目: {quality_metrics.get('high_efficiency_projects', 0)} 个"
            ]
            
            for line in metrics_lines:
                elements.append(Paragraph(line, self.styles['ChineseBodyText']))
        
        return elements
    
    def _create_conclusions_recommendations(self, results: Dict[str, Any]) -> List:
        """创建结论与建议"""
        elements = []
        
        elements.append(Paragraph("结论与建议", self.styles['ChineseHeading1']))
        
        # 主要结论
        elements.append(Paragraph("主要结论", self.styles['ChineseHeading2']))
        
        conclusions = results.get('conclusions', [])
        if conclusions:
            for i, conclusion in enumerate(conclusions, 1):
                conclusion_text = f"{i}. {conclusion}"
                elements.append(Paragraph(conclusion_text, self.styles['ChineseBodyText']))
        else:
            # 默认结论
            default_conclusions = [
                "项目数据分析显示了不同类型、级别项目的显著特征差异",
                "自动化率与项目类型存在明显关联，Web应用和API服务自动化程度更高",
                "项目级别对各项指标有显著影响，需要针对性管理",
                "组织间绩效存在差异，建议加强最佳实践分享"
            ]
            
            for i, conclusion in enumerate(default_conclusions, 1):
                conclusion_text = f"{i}. {conclusion}"
                elements.append(Paragraph(conclusion_text, self.styles['ChineseBodyText']))
        
        # 改进建议
        elements.append(Paragraph("改进建议", self.styles['ChineseHeading2']))
        
        recommendations = results.get('recommendations', [])
        if recommendations:
            for i, recommendation in enumerate(recommendations, 1):
                rec_text = f"{i}. {recommendation}"
                elements.append(Paragraph(rec_text, self.styles['ChineseBodyText']))
        else:
            # 默认建议
            default_recommendations = [
                "提升测试自动化率，特别是桌面应用和大数据平台项目",
                "加强P0级别项目的质量控制和资源投入",
                "优化组织间的测试流程标准化",
                "建立项目质量预警机制，及时识别高风险项目",
                "定期进行数据分析，持续优化测试管理策略"
            ]
            
            for i, recommendation in enumerate(default_recommendations, 1):
                rec_text = f"{i}. {recommendation}"
                elements.append(Paragraph(rec_text, self.styles['ChineseBodyText']))
        
        return elements
    
    def _create_distribution_charts(self, distributions: Dict[str, Any]) -> Optional[str]:
        """创建分布图表"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('项目分布情况', fontsize=16, fontweight='bold')
            
            chart_data = [
                ('项目类型', distributions.get('项目类型', {})),
                ('项目级别', distributions.get('项目级别', {})),
                ('产品线', distributions.get('产品线', {})),
                ('组织架构', distributions.get('测试负责人所属组织架构', {}))
            ]
            
            for i, (title, data) in enumerate(chart_data):
                if data:
                    row, col = i // 2, i % 2
                    ax = axes[row, col]
                    
                    labels = list(data.keys())
                    values = list(data.values())
                    
                    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                    ax.set_title(title)
            
            plt.tight_layout()
            
            # 保存图表
            chart_path = 'temp_distribution_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"创建分布图表失败: {e}")
            return None
    
    def _create_correlation_heatmap(self, correlation_matrix: pd.DataFrame) -> Optional[str]:
        """创建相关性热力图"""
        try:
            plt.figure(figsize=(10, 8))
            
            # 创建热力图
            sns.heatmap(
                correlation_matrix,
                annot=True,
                cmap='coolwarm',
                center=0,
                square=True,
                fmt='.3f'
            )
            
            plt.title('数值字段相关性热力图', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # 保存图表
            chart_path = 'temp_correlation_heatmap.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"创建相关性热力图失败: {e}")
            return None