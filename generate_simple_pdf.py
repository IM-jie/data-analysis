#!/usr/bin/env python3
"""
简化的PDF报告生成器
专注于解决中文字体显示问题，暂时去掉图表功能
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.colors import Color, HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def setup_chinese_font():
    """设置中文字体"""
    try:
        # 尝试加载STHeiti字体（在前面的测试中成功了）
        font_path = '/System/Library/Fonts/STHeiti Light.ttc'
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('STHeiti', font_path))
            print("✅ 成功加载STHeiti字体")
            return 'STHeiti'
        
        # 备用字体
        backup_fonts = [
            ('/System/Library/Fonts/PingFang.ttc', 'PingFangSC'),
            ('/System/Library/Fonts/Hiragino Sans GB.ttc', 'HiraginoSansGB'),
            ('C:\\Windows\\Fonts\\msyh.ttc', 'MicrosoftYaHei'),
            ('C:\\Windows\\Fonts\\simsun.ttc', 'SimSun'),
        ]
        
        for font_path, font_name in backup_fonts:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    print(f"✅ 成功加载备用字体: {font_name}")
                    return font_name
                except Exception as e:
                    print(f"⚠️ 字体加载失败 {font_name}: {e}")
                    continue
        
        print("⚠️ 使用默认字体")
        return 'Helvetica'
        
    except Exception as e:
        print(f"❌ 字体设置失败: {e}")
        return 'Helvetica'

def create_simple_pdf_report():
    """创建简化的PDF报告"""
    
    # 设置中文字体
    chinese_font = setup_chinese_font()
    
    # 创建输出目录
    output_dir = Path('reports')
    output_dir.mkdir(exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"simple_project_report_{timestamp}.pdf"
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 设置样式
    styles = getSampleStyleSheet()
    
    # 添加中文样式
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        parent=styles['Title'],
        fontName=chinese_font,
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseHeading1',
        parent=styles['Heading1'],
        fontName=chinese_font,
        fontSize=18,
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseHeading2',
        parent=styles['Heading2'],
        fontName=chinese_font,
        fontSize=14,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='ChineseBodyText',
        parent=styles['BodyText'],
        fontName=chinese_font,
        fontSize=10,
        spaceAfter=8
    ))
    
    # 构建报告内容
    story = []
    
    # 1. 封面页
    title = Paragraph("项目数据挖掘分析报告", styles['ChineseTitle'])
    story.append(title)
    story.append(Spacer(1, 50))
    
    # 基本信息表
    info_data = [
        ['项目数量', '100'],
        ['分析日期', datetime.now().strftime("%Y年%m月%d日")],
        ['报告版本', 'v1.0'],
        ['生成工具', '项目数据挖掘系统']
    ]
    
    info_table = Table(info_data, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f0f0f0')),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 100))
    
    # 报告说明
    description = "本报告基于项目测试数据进行深度分析，包含统计分析、相关性分析、关联性分析等多个维度，为项目管理和质量改进提供数据支持。"
    desc_para = Paragraph(description, styles['ChineseBodyText'])
    story.append(desc_para)
    
    story.append(PageBreak())
    
    # 2. 执行摘要
    story.append(Paragraph("执行摘要", styles['ChineseHeading1']))
    
    story.append(Paragraph("关键发现:", styles['ChineseHeading2']))
    
    key_findings = [
        "共分析了100个项目的测试数据，涵盖Web应用、移动应用、API服务等多种项目类型",
        "项目级别P0占比33%，是最重要的项目类型，需要重点关注",
        "金融服务产品线项目数量最多，占总项目的30%",
        "执行用例数与投入工时存在强正相关关系（相关系数0.814）",
        "不同项目类型的自动化率存在显著差异，需要针对性改进"
    ]
    
    for i, finding in enumerate(key_findings, 1):
        finding_text = f"{i}. {finding}"
        story.append(Paragraph(finding_text, styles['ChineseBodyText']))
    
    story.append(Paragraph("主要指标:", styles['ChineseHeading2']))
    
    metrics_lines = [
        "• 总项目数: 100个",
        "• 平均执行用例数: 181.2个",
        "• 平均自动化用例数: 89.8个",
        "• 平均关联缺陷: 12.4个",
        "• 平均投入工时: 104.7小时"
    ]
    
    for line in metrics_lines:
        story.append(Paragraph(line, styles['ChineseBodyText']))
    
    story.append(PageBreak())
    
    # 3. 统计分析
    story.append(Paragraph("统计分析", styles['ChineseHeading1']))
    
    story.append(Paragraph("项目分布统计", styles['ChineseHeading2']))
    
    # 项目类型分布表
    type_data = [
        ['项目类型', '数量', '占比'],
        ['大数据平台', '24', '24.0%'],
        ['桌面应用', '21', '21.0%'],
        ['Web应用', '20', '20.0%'],
        ['API服务', '18', '18.0%'],
        ['移动应用', '17', '17.0%']
    ]
    
    type_table = Table(type_data)
    type_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    story.append(type_table)
    story.append(Spacer(1, 20))
    
    # 数值统计表
    story.append(Paragraph("数值字段统计", styles['ChineseHeading2']))
    
    stats_data = [
        ['字段名', '平均值', '中位数', '标准差', '最小值', '最大值'],
        ['执行用例数', '181.2', '182.0', '69.1', '57', '307'],
        ['自动化执行用例数', '89.8', '73.0', '53.7', '10', '216'],
        ['关联缺陷', '12.4', '12.5', '5.0', '3', '28'],
        ['投入工时', '104.7', '103.0', '48.8', '14', '254']
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#f0f0f0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    
    story.append(stats_table)
    story.append(PageBreak())
    
    # 4. 相关性分析
    story.append(Paragraph("相关性分析", styles['ChineseHeading1']))
    
    story.append(Paragraph("强相关性关系", styles['ChineseHeading2']))
    
    correlations = [
        "执行用例数 ↔ 投入工时: 0.814 (强正相关)",
        "执行用例数 ↔ 自动化执行用例数: 0.545 (中等正相关)",
        "执行用例数 ↔ 关联缺陷: 0.432 (中等正相关)"
    ]
    
    for corr in correlations:
        corr_text = f"• {corr}"
        story.append(Paragraph(corr_text, styles['ChineseBodyText']))
    
    story.append(PageBreak())
    
    # 5. 质量效率分析
    story.append(Paragraph("质量效率分析", styles['ChineseHeading1']))
    
    story.append(Paragraph("质量效率指标", styles['ChineseHeading2']))
    
    quality_lines = [
        "• 平均自动化率: 49.5%",
        "• 平均缺陷密度: 0.068",
        "• 平均测试效率: 1.7 用例/小时",
        "• 高自动化率项目 (>70%): 18 个",
        "• 低缺陷密度项目 (<5%): 32 个",
        "• 高效率项目 (>2用例/小时): 35 个"
    ]
    
    for line in quality_lines:
        story.append(Paragraph(line, styles['ChineseBodyText']))
    
    story.append(PageBreak())
    
    # 6. 结论与建议
    story.append(Paragraph("结论与建议", styles['ChineseHeading1']))
    
    story.append(Paragraph("主要结论", styles['ChineseHeading2']))
    
    conclusions = [
        "项目数据分析显示了不同类型、级别项目的显著特征差异",
        "自动化率与项目类型存在明显关联，Web应用和API服务自动化程度更高",
        "项目级别对各项指标有显著影响，需要针对性管理",
        "组织间绩效存在差异，建议加强最佳实践分享"
    ]
    
    for i, conclusion in enumerate(conclusions, 1):
        conclusion_text = f"{i}. {conclusion}"
        story.append(Paragraph(conclusion_text, styles['ChineseBodyText']))
    
    story.append(Paragraph("改进建议", styles['ChineseHeading2']))
    
    recommendations = [
        "提升测试自动化率，特别是桌面应用和大数据平台项目",
        "加强P0级别项目的质量控制和资源投入",
        "优化组织间的测试流程标准化",
        "建立项目质量预警机制，及时识别高风险项目",
        "定期进行数据分析，持续优化测试管理策略"
    ]
    
    for i, recommendation in enumerate(recommendations, 1):
        rec_text = f"{i}. {recommendation}"
        story.append(Paragraph(rec_text, styles['ChineseBodyText']))
    
    # 构建PDF
    doc.build(story)
    
    print(f"✅ 简化PDF报告已生成: {output_path}")
    return str(output_path)

if __name__ == "__main__":
    create_simple_pdf_report()