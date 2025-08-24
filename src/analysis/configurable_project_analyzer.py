#!/usr/bin/env python3
"""
可配置的Apriori项目数据分析器
支持自定义维度字段、指标字段、中英文字段映射的项目数据关联规则挖掘
"""

import pandas as pd
import numpy as np
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime
import json
from loguru import logger

try:
    from .project_data_miner import ProjectDataMiner
except ImportError:
    try:
        from project_data_miner import ProjectDataMiner
    except ImportError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from project_data_miner import ProjectDataMiner

try:
    from ..visualization.pdf_report_generator import ProjectMiningPDFReporter
    from ..visualization.html_report_generator import ProjectMiningHTMLReporter
    from ..visualization.association_rules_visualizer import AssociationRulesVisualizer
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from visualization.pdf_report_generator import ProjectMiningPDFReporter
        from visualization.html_report_generator import ProjectMiningHTMLReporter
        from visualization.association_rules_visualizer import AssociationRulesVisualizer
    except ImportError as e:
        logger.warning(f"报告生成器导入失败: {e}")
        ProjectMiningPDFReporter = None
        ProjectMiningHTMLReporter = None
        AssociationRulesVisualizer = None

DEPENDENCIES_AVAILABLE = ProjectDataMiner is not None


class ConfigurableProjectAnalyzer:
    """可配置的项目数据Apriori分析器"""
    
    def __init__(self, config_file: Optional[str] = None, config_dict: Optional[Dict] = None):
        """
        初始化可配置项目分析器
        
        Args:
            config_file: 配置文件路径 (YAML格式)
            config_dict: 配置字典 (如果提供，将覆盖config_file)
        """
        self.config = self._load_config(config_file, config_dict)
        self.field_mapping = self.config.get('field_mapping', {})
        self.dimension_fields = self.config.get('dimension_fields', [])
        self.metric_fields = self.config.get('metric_fields', [])
        self.analysis_config = self.config.get('analysis_parameters', {})
        
        # 初始化项目数据挖掘器
        if DEPENDENCIES_AVAILABLE and ProjectDataMiner is not None:
            self.miner = ProjectDataMiner(self.analysis_config)
        else:
            raise ImportError("缺少必要的依赖模块，请检查项目结构")
        
        logger.info("可配置项目分析器初始化完成")
    
    def _load_config(self, config_file: Optional[str], config_dict: Optional[Dict]) -> Dict:
        """加载配置"""
        if config_dict:
            return config_dict
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # 返回默认配置
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            "field_mapping": {
                "project_name": "项目名称",
                "project_id": "项目编号", 
                "project_type": "项目类型",
                "project_level": "项目级别",
                "product_line": "产品线",
                "product_type": "产品类型",
                "test_owner": "测试负责人",
                "test_owner_org": "测试负责人所属组织架构",
                "executed_cases": "执行用例数",
                "automated_cases": "自动化执行用例数",
                "related_bugs": "关联缺陷",
                "effort_hours": "投入工时"
            },
            "dimension_fields": [
                "project_type", "project_level", "product_line", 
                "product_type", "test_owner", "test_owner_org"
            ],
            "metric_fields": [
                "executed_cases", "automated_cases", "related_bugs", "effort_hours"
            ],
            "analysis_parameters": {
                "min_support": 0.05,
                "min_confidence": 0.6,
                "min_lift": 1.2,
                "correlation_threshold": 0.6
            },
            "reporting": {
                "output_format": ["pdf", "html"],
                "output_directory": "reports",
                "include_charts": True,
                "include_tables": True
            }
        }
    
    def create_config_template(self, output_file: str = "config/project_analysis_config.yaml"):
        """创建配置模板文件"""
        template_config = {
            "# 字段映射配置 (英文字段名 -> 中文显示名)": None,
            "field_mapping": {
                "project_name": "项目名称",
                "project_id": "项目编号",
                "project_type": "项目类型", 
                "project_level": "项目级别",
                "product_line": "产品线",
                "product_type": "产品类型",
                "test_owner": "测试负责人",
                "test_owner_org": "测试负责人所属组织架构",
                "executed_cases": "执行用例数",
                "automated_cases": "自动化执行用例数",
                "related_bugs": "关联缺陷",
                "effort_hours": "投入工时"
            },
            
            "# 维度字段配置 (用于关联规则挖掘的分类字段)": None,
            "dimension_fields": [
                "project_type",
                "project_level", 
                "product_line",
                "product_type",
                "test_owner",
                "test_owner_org"
            ],
            
            "# 指标字段配置 (用于数值分析的字段)": None,
            "metric_fields": [
                "executed_cases",
                "automated_cases", 
                "related_bugs",
                "effort_hours"
            ],
            
            "# Apriori算法参数配置": None,
            "analysis_parameters": {
                "min_support": 0.05,      # 最小支持度：规则在数据中出现的最小频率
                "min_confidence": 0.6,    # 最小置信度：规则的可信程度
                "min_lift": 1.2,         # 最小提升度：规则的有效性指标
                "correlation_threshold": 0.6  # 相关性分析阈值
            },
            
            "# 报告生成配置": None,
            "reporting": {
                "output_format": ["pdf", "html"],  # 支持的输出格式
                "output_directory": "reports",     # 报告输出目录
                "include_charts": True,            # 是否包含图表
                "include_tables": True             # 是否包含统计表格
            }
        }
        
        # 确保输出目录存在
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入YAML文件（移除注释键）
        clean_config = {k: v for k, v in template_config.items() if not k.startswith('#')}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(clean_config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"配置模板已创建: {output_file}")
        return output_file
    
    def validate_data(self, data: pd.DataFrame) -> Tuple[bool, List[str]]:
        """验证数据格式和字段"""
        errors = []
        
        # 检查必需的维度字段
        missing_dimensions = []
        for field in self.dimension_fields:
            if field not in data.columns:
                missing_dimensions.append(field)
        
        if missing_dimensions:
            errors.append(f"缺少维度字段: {missing_dimensions}")
        
        # 检查必需的指标字段
        missing_metrics = []
        for field in self.metric_fields:
            if field not in data.columns:
                missing_metrics.append(field)
        
        if missing_metrics:
            errors.append(f"缺少指标字段: {missing_metrics}")
        
        # 检查数据量
        if len(data) < 10:
            errors.append("数据量不足，至少需要10条记录进行有效分析")
        
        # 检查字段类型
        for field in self.dimension_fields:
            if field in data.columns and data[field].dtype not in ['object', 'category']:
                logger.warning(f"维度字段 {field} 应该是分类类型，当前类型: {data[field].dtype}")
        
        for field in self.metric_fields:
            if field in data.columns and not pd.api.types.is_numeric_dtype(data[field]):
                errors.append(f"指标字段 {field} 应该是数值类型，当前类型: {data[field].dtype}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def translate_data_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """将英文字段名翻译为中文字段名"""
        translation_map = {}
        
        for english_name, chinese_name in self.field_mapping.items():
            if english_name in data.columns:
                translation_map[english_name] = chinese_name
        
        translated_data = data.rename(columns=translation_map)
        
        logger.info(f"字段翻译完成，翻译了 {len(translation_map)} 个字段")
        return translated_data
    
    def analyze_project_data(self, data: pd.DataFrame, 
                           translate_columns: bool = True) -> Dict[str, Any]:
        """
        分析项目数据
        
        Args:
            data: 项目数据DataFrame
            translate_columns: 是否将字段名翻译为中文
            
        Returns:
            分析结果字典
        """
        logger.info("开始可配置项目数据分析...")
        
        # 验证数据
        is_valid, errors = self.validate_data(data)
        if not is_valid:
            raise ValueError(f"数据验证失败: {errors}")
        
        # 翻译字段名
        if translate_columns:
            analysis_data = self.translate_data_columns(data)
        else:
            analysis_data = data.copy()
        
        # 记录分析信息
        analysis_info = {
            "analysis_time": datetime.now().isoformat(),
            "total_records": len(analysis_data),
            "dimension_fields": [self.field_mapping.get(f, f) for f in self.dimension_fields],
            "metric_fields": [self.field_mapping.get(f, f) for f in self.metric_fields],
            "configuration": self.analysis_config
        }
        
        # 执行关联规则挖掘
        logger.info("执行Apriori关联规则挖掘...")
        mining_results = self.miner.discover_project_associations(analysis_data)
        
        # 基于关联规则进行数据标签分类
        logger.info("基于关联规则进行数据标签分类...")
        # 提取关联规则列表
        association_rules = mining_results.get('categorical_associations', {}).get('association_rules', [])
        if association_rules:
            labeled_data = self.miner.label_data_by_association_rules(
                analysis_data, association_rules
            )
        else:
            logger.warning("未发现关联规则，跳过标签分类")
            labeled_data = analysis_data.copy()
            # 添加默认标签列
            labeled_data['rule_labels'] = ''
            labeled_data['rule_violations'] = ''
            labeled_data['rule_compliance_score'] = 0.0
            labeled_data['anomaly_flags'] = ''
            labeled_data['anomaly_score'] = 0.0
            labeled_data['data_category'] = '未匹配规则'
        
        # 汇总分析结果
        results = {
            "analysis_info": analysis_info,
            "mining_results": mining_results,
            "labeled_data": labeled_data,
            "summary": self._create_analysis_summary(mining_results, labeled_data)
        }
        
        logger.info("项目数据分析完成")
        return results
    
    def _create_analysis_summary(self, mining_results: Dict, labeled_data: pd.DataFrame) -> Dict:
        """创建分析摘要"""
        summary = {}
        
        # 关联规则摘要
        categorical_associations = mining_results.get('categorical_associations', {})
        association_rules = categorical_associations.get('association_rules', [])
        
        summary['association_rules'] = {
            "total_rules": len(association_rules),
            "high_confidence_rules": len([r for r in association_rules if r.get('confidence', 0) > 0.8]),
            "strong_associations": len(categorical_associations.get('strong_associations', []))
        }
        
        # 数值相关性摘要
        numerical_correlations = mining_results.get('numerical_correlations', {})
        strong_correlations = numerical_correlations.get('strong_correlations', [])
        
        summary['correlations'] = {
            "strong_correlations": len(strong_correlations),
            "correlation_details": strong_correlations[:5]  # 前5个强相关性
        }
        
        # 标签分类摘要
        if labeled_data is not None and 'data_category' in labeled_data.columns:
            category_counts = labeled_data['data_category'].value_counts().to_dict()
            violation_count = len(labeled_data[labeled_data['rule_violations'] != ''])
            
            summary['labeling'] = {
                "category_distribution": category_counts,
                "violation_count": violation_count,
                "violation_rate": violation_count / len(labeled_data) if len(labeled_data) > 0 else 0
            }
        
        return summary
    
    def generate_reports(self, analysis_results: Dict[str, Any], 
                        output_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        生成分析报告
        
        Args:
            analysis_results: 分析结果
            output_prefix: 输出文件前缀
            
        Returns:
            生成的报告文件路径字典
        """
        if not (DEPENDENCIES_AVAILABLE and ProjectMiningPDFReporter and ProjectMiningHTMLReporter):
            logger.error("报告生成器不可用")
            return {}
        
        logger.info("开始生成分析报告...")
        
        # 确保输出目录存在
        output_dir = Path(self.config['reporting']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not output_prefix:
            output_prefix = "configurable_project_analysis"
        
        # 转换数据格式
        report_data = self._convert_results_for_reporting(analysis_results)
        
        generated_files = {}
        output_formats = self.config['reporting'].get('output_format', ['pdf'])
        
        # 生成PDF报告
        if 'pdf' in output_formats:
            try:
                pdf_reporter = ProjectMiningPDFReporter()
                pdf_path = output_dir / f"{output_prefix}_{timestamp}.pdf"
                pdf_file = pdf_reporter.generate_project_mining_report(
                    report_data, str(pdf_path)
                )
                generated_files['pdf'] = pdf_file
                logger.info(f"PDF报告已生成: {pdf_file}")
            except Exception as e:
                logger.error(f"PDF报告生成失败: {e}")
        
        # 生成HTML报告
        if 'html' in output_formats:
            try:
                html_reporter = ProjectMiningHTMLReporter()
                html_path = output_dir / f"{output_prefix}_{timestamp}.html"
                html_file = html_reporter.generate_project_mining_html_report(
                    report_data, str(html_path)
                )
                generated_files['html'] = html_file
                logger.info(f"HTML报告已生成: {html_file}")
            except Exception as e:
                logger.error(f"HTML报告生成失败: {e}")
        
        return generated_files
    
    def _convert_results_for_reporting(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """转换分析结果为报告格式"""
        mining_results = analysis_results['mining_results']
        labeled_data = analysis_results['labeled_data']
        analysis_info = analysis_results['analysis_info']
        
        # 构建报告数据
        report_data = {
            'total_projects': analysis_info['total_records'],
            'analysis_configuration': analysis_info['configuration'],
            'categorical_distributions': self._extract_categorical_distributions(labeled_data),
            'numerical_statistics': self._extract_numerical_statistics(labeled_data),
            'correlation_matrix': self._extract_correlation_matrix(mining_results),
            'strong_correlations': mining_results.get('numerical_correlations', {}).get('strong_correlations', []),
            'quality_metrics': self._calculate_quality_metrics(labeled_data),
            'key_findings': self._generate_key_findings(analysis_results),
            'conclusions': self._generate_conclusions(analysis_results),
            'recommendations': self._generate_recommendations(analysis_results),
            'labeled_data': labeled_data,
            'analysis_results': mining_results
        }
        
        return report_data
    
    def _extract_categorical_distributions(self, data: pd.DataFrame) -> Dict[str, Dict]:
        """提取分类字段分布"""
        distributions = {}
        
        # 获取中文字段名对应的分类字段
        chinese_dimension_fields = [self.field_mapping.get(f, f) for f in self.dimension_fields]
        
        for field in chinese_dimension_fields:
            if field in data.columns:
                distributions[field] = dict(data[field].value_counts())
        
        return distributions
    
    def _extract_numerical_statistics(self, data: pd.DataFrame) -> Dict[str, Dict]:
        """提取数值字段统计"""
        statistics = {}
        
        # 获取中文字段名对应的指标字段
        chinese_metric_fields = [self.field_mapping.get(f, f) for f in self.metric_fields]
        
        for field in chinese_metric_fields:
            if field in data.columns and pd.api.types.is_numeric_dtype(data[field]):
                statistics[field] = {
                    'mean': float(data[field].mean()),
                    'median': float(data[field].median()),
                    'std': float(data[field].std()),
                    'min': int(data[field].min()),
                    'max': int(data[field].max())
                }
        
        return statistics
    
    def _extract_correlation_matrix(self, mining_results: Dict) -> Optional[pd.DataFrame]:
        """提取相关性矩阵"""
        numerical_correlations = mining_results.get('numerical_correlations', {})
        return numerical_correlations.get('correlation_matrix')
    
    def _calculate_quality_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """计算质量指标"""
        metrics = {}
        
        # 获取中文字段名
        executed_cases_field = self.field_mapping.get('executed_cases', 'executed_cases')
        automated_cases_field = self.field_mapping.get('automated_cases', 'automated_cases')
        related_bugs_field = self.field_mapping.get('related_bugs', 'related_bugs')
        effort_hours_field = self.field_mapping.get('effort_hours', 'effort_hours')
        
        if all(field in data.columns for field in [executed_cases_field, automated_cases_field, related_bugs_field, effort_hours_field]):
            # 计算自动化率
            automation_rates = data[automated_cases_field] / data[executed_cases_field]
            metrics['avg_automation_rate'] = automation_rates.mean()
            
            # 计算缺陷密度
            defect_densities = data[related_bugs_field] / data[executed_cases_field]
            metrics['avg_defect_density'] = defect_densities.mean()
            
            # 计算测试效率
            test_efficiencies = data[executed_cases_field] / data[effort_hours_field]
            metrics['avg_test_efficiency'] = test_efficiencies.mean()
            
            # 高质量项目统计
            metrics['high_automation_projects'] = len(automation_rates[automation_rates > 0.7])
            metrics['low_defect_projects'] = len(defect_densities[defect_densities < 0.05])
            metrics['high_efficiency_projects'] = len(test_efficiencies[test_efficiencies > 2.0])
        
        return metrics
    
    def _generate_key_findings(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成关键发现"""
        findings = []
        
        analysis_info = analysis_results['analysis_info']
        summary = analysis_results['summary']
        
        findings.append(f"共分析了{analysis_info['total_records']}个项目的数据")
        
        if 'association_rules' in summary:
            rule_count = summary['association_rules']['total_rules']
            findings.append(f"发现了{rule_count}个关联规则")
        
        if 'labeling' in summary:
            violation_rate = summary['labeling']['violation_rate']
            findings.append(f"违反规则的项目占比为{violation_rate:.1%}")
        
        findings.append("基于可配置字段进行了全面的模式识别和异常检测")
        findings.append("为项目质量管理和风险控制提供了数据支持")
        
        return findings
    
    def _generate_conclusions(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成结论"""
        conclusions = [
            "可配置的Apriori分析成功识别了项目数据中的关联模式",
            "基于用户定义的维度和指标字段发现了有价值的业务规则",
            "标签分类功能有效地识别了异常和违反规则的项目",
            "分析结果为项目管理决策提供了量化的数据支持"
        ]
        return conclusions
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = [
            "建立基于发现的关联规则的项目监控体系",
            "针对违反规则的项目制定专门的管理策略",
            "定期更新分析配置以适应业务变化",
            "扩展维度和指标字段以获得更全面的洞察",
            "建立自动化的项目风险预警机制"
        ]
        return recommendations
    
    def export_configuration(self, output_file: str):
        """导出当前配置"""
        with open(output_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"配置已导出到: {output_file}")
    
    def generate_association_rules_visualizations(self, 
                                                 analysis_results: Dict[str, Any],
                                                 output_dir: Optional[str] = None,
                                                 format: str = "both") -> Dict[str, str]:
        """
        生成关联规则的可视化图表
        
        Args:
            analysis_results: 分析结果
            output_dir: 输出目录
            format: 输出格式 ('matplotlib', 'plotly', 'both')
            
        Returns:
            生成的图表文件路径字典
        """
        if not AssociationRulesVisualizer:
            logger.error("关联规则可视化器不可用")
            return {}
        
        logger.info("开始生成关联规则可视化图表...")
        
        # 提取关联规则
        mining_results = analysis_results.get('mining_results', {})
        categorical_associations = mining_results.get('categorical_associations', {})
        association_rules = categorical_associations.get('association_rules', [])
        
        if not association_rules:
            logger.warning("没有关联规则可供可视化")
            return {}
        
        # 设置输出目录
        if not output_dir:
            reporting_config = self.config.get('reporting', {})
            output_directory = reporting_config.get('output_directory', 'reports')
            output_dir = Path(output_directory) / "visualizations"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建可视化器
        visualizer = AssociationRulesVisualizer()
        
        # 生成可视化图表
        generated_files = visualizer.visualize_association_rules(
            association_rules, str(output_dir), format
        )
        
        # 生成可视化总结
        if generated_files:
            summary = visualizer.generate_visualization_summary(association_rules, generated_files)
            summary_file = output_dir / "visualization_summary.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            generated_files['summary'] = str(summary_file)
            
            logger.info(f"关联规则可视化完成，生成了 {len(generated_files)} 个文件")
        
        return generated_files
    
    def get_field_info(self) -> Dict[str, Any]:
        """获取字段配置信息"""
        return {
            "field_mapping": self.field_mapping,
            "dimension_fields": self.dimension_fields,
            "metric_fields": self.metric_fields,
            "dimension_fields_chinese": [self.field_mapping.get(f, f) for f in self.dimension_fields],
            "metric_fields_chinese": [self.field_mapping.get(f, f) for f in self.metric_fields]
        }