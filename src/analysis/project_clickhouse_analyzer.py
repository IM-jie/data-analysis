"""
项目数据ClickHouse分析器
专门用于从ClickHouse数据库中读取项目测试数据并进行关联规则挖掘
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import pandas as pd
import numpy as np
import yaml
from loguru import logger

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.clickhouse_connector import ClickHouseConnector
from analysis.project_data_miner import ProjectDataMiner
from visualization.kpi_report_generator import KPIReportGenerator


class ProjectClickHouseAnalyzer:
    """项目数据ClickHouse分析器"""
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 clickhouse_config: Optional[Dict] = None):
        """
        初始化项目数据ClickHouse分析器
        
        Args:
            config_path: 配置文件路径
            clickhouse_config: ClickHouse连接配置
        """
        self.config = self._load_config(config_path)
        self.clickhouse_config = clickhouse_config or self.config.get('clickhouse', {})
        
        # 初始化组件
        self.connector = None
        self.project_miner = ProjectDataMiner(self.config.get('data_mining', {}))
        self.report_generator = KPIReportGenerator()
        
        # 项目数据字段映射
        self.project_fields = {
            'project_name': ['项目名称', 'project_name', 'name'],
            'project_id': ['项目编号', 'project_id', 'id'],
            'project_type': ['项目类型', 'project_type', 'type'],
            'project_level': ['项目级别', 'project_level', 'level'],
            'product_line': ['产品线', 'product_line', 'line'],
            'product_type': ['产品类型', 'product_type'],
            'test_owner': ['测试负责人', 'test_owner', 'owner'],
            'test_owner_org': ['测试负责人所属组织架构', 'test_owner_org', 'organization'],
            'executed_cases': ['执行用例数', 'executed_cases', 'cases'],
            'automated_cases': ['自动化执行用例数', 'automated_cases', 'auto_cases'],
            'related_bugs': ['关联缺陷', 'related_bugs', 'bugs'],
            'effort_hours': ['投入工时', 'effort_hours', 'hours']
        }
        
        # 连接ClickHouse数据库
        try:
            self._connect_clickhouse()
        except Exception as e:
            logger.warning(f"ClickHouse连接失败: {e}")
            self.connector = None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"成功加载配置文件: {config_path}")
                return config
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
        
        # 使用默认配置
        logger.info("使用默认配置")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'clickhouse': {
                'host': 'localhost',
                'port': 18123,
                'username': 'default',
                'password': 'Dxt456789',
                'database': 'default',
                'secure': False
            },
            'data_mining': {
                'min_support': 0.1,
                'min_confidence': 0.5,
                'min_lift': 1.2,
                'correlation_threshold': 0.6
            }
        }
    
    def _connect_clickhouse(self):
        """连接ClickHouse数据库"""
        try:
            self.connector = ClickHouseConnector(**self.clickhouse_config)
            
            # 测试连接
            if self.connector.test_connection():
                logger.info("ClickHouse数据库连接成功")
            else:
                logger.error("ClickHouse数据库连接失败")
                raise Exception("无法连接到ClickHouse数据库")
                
        except Exception as e:
            logger.error(f"连接ClickHouse数据库失败: {e}")
            raise
    
    def analyze_project_table(self, 
                             table_name: str,
                             custom_field_mapping: Optional[Dict[str, str]] = None,
                             where_condition: Optional[str] = None,
                             limit: Optional[int] = None) -> Dict[str, Any]:
        """
        分析ClickHouse中的项目数据表
        
        Args:
            table_name: 项目数据表名
            custom_field_mapping: 自定义字段映射
            where_condition: WHERE条件
            limit: 限制返回行数
            
        Returns:
            分析结果
        """
        try:
            logger.info(f"开始分析项目数据表: {table_name}")
            
            # 获取表结构
            if self.connector is None:
                return {'error': 'ClickHouse连接未建立'}
                
            table_schema = self.connector.get_table_schema(table_name)
            logger.info(f"表 {table_name} 包含 {len(table_schema)} 个字段")
            
            # 自动识别项目数据字段
            detected_fields = self._detect_project_fields(table_schema)
            logger.info(f"识别到的项目字段: {detected_fields}")
            
            # 更新字段映射
            if custom_field_mapping:
                detected_fields.update(custom_field_mapping)
            
            # 构建查询
            select_columns = list(detected_fields.values())
            query = f"SELECT {', '.join(select_columns)} FROM {self.connector.database}.{table_name}"
            
            if where_condition:
                query += f" WHERE {where_condition}"
            
            if limit:
                query += f" LIMIT {limit}"
            
            # 执行查询获取数据
            logger.info(f"执行查询: {query}")
            project_data = self.connector.execute_query(query)
            
            if project_data.empty:
                return {'error': '未找到有效的项目数据'}
            
            logger.info(f"获取到 {len(project_data)} 条项目数据记录")
            
            # 重命名列为标准字段名
            reverse_mapping = {v: k for k, v in detected_fields.items()}
            project_data = project_data.rename(columns=reverse_mapping)
            
            # 进行项目数据关联规则挖掘
            logger.info("开始项目数据关联规则挖掘...")
            mining_results = self.project_miner.discover_project_associations(
                data=project_data,
                custom_fields=detected_fields
            )
            
            # 生成报告
            report_path = self._generate_project_report(
                table_name=table_name,
                project_data=project_data,
                mining_results=mining_results
            )
            
            return {
                'table_name': table_name,
                'data_shape': project_data.shape,
                'detected_fields': detected_fields,
                'mining_results': mining_results,
                'report_path': report_path,
                'summary': self._generate_analysis_summary(mining_results)
            }
            
        except Exception as e:
            logger.error(f"分析项目数据表 {table_name} 失败: {e}")
            return {'error': str(e)}
    
    def _detect_project_fields(self, table_schema: pd.DataFrame) -> Dict[str, str]:
        """自动检测项目数据字段"""
        detected_fields = {}
        
        if table_schema.empty:
            return detected_fields
        
        column_names = table_schema['column_name'].str.lower()
        
        for standard_field, possible_names in self.project_fields.items():
            for col_name in column_names:
                for possible_name in possible_names:
                    if possible_name.lower() in col_name or col_name in possible_name.lower():
                        # 找到原始列名
                        original_col_series = table_schema[
                            table_schema['column_name'].str.lower() == col_name
                        ]['column_name']
                        if len(original_col_series) > 0:
                            detected_fields[standard_field] = original_col_series.iloc[0]
                        break
                if standard_field in detected_fields:
                    break
        
        return detected_fields
    
    def analyze_project_performance_by_organization(self, 
                                                   table_name: str,
                                                   organization_field: Optional[str] = None) -> Dict[str, Any]:
        """
        按组织分析项目性能
        
        Args:
            table_name: 项目数据表名
            organization_field: 组织字段名（如果不指定，会自动检测）
            
        Returns:
            按组织的性能分析结果
        """
        try:
            # 获取项目数据
            analysis_result = self.analyze_project_table(table_name)
            
            if 'error' in analysis_result:
                return analysis_result
            
            mining_results = analysis_result['mining_results']
            org_performance = mining_results.get('organization_performance', {})
            
            # 提取组织性能洞察
            insights = {
                'organization_rankings': {},
                'performance_patterns': [],
                'recommendations': []
            }
            
            # 分析组织排名
            by_organization = org_performance.get('by_organization', {})
            if by_organization:
                insights['organization_rankings'] = self._rank_organizations(by_organization)
            
            # 生成组织性能模式
            insights['performance_patterns'] = self._identify_org_patterns(org_performance)
            
            # 生成改进建议
            insights['recommendations'] = self._generate_org_recommendations(org_performance)
            
            return {
                'table_name': table_name,
                'organization_insights': insights,
                'detailed_analysis': org_performance
            }
            
        except Exception as e:
            logger.error(f"按组织分析项目性能失败: {e}")
            return {'error': str(e)}
    
    def analyze_product_line_efficiency(self, 
                                       table_name: str,
                                       product_line_field: Optional[str] = None) -> Dict[str, Any]:
        """
        分析产品线效率
        
        Args:
            table_name: 项目数据表名
            product_line_field: 产品线字段名
            
        Returns:
            产品线效率分析结果
        """
        try:
            # 获取项目数据分析结果
            analysis_result = self.analyze_project_table(table_name)
            
            if 'error' in analysis_result:
                return analysis_result
            
            mining_results = analysis_result['mining_results']
            product_insights = mining_results.get('product_insights', {})
            
            # 分析产品线效率
            efficiency_analysis = {
                'product_line_rankings': {},
                'efficiency_patterns': [],
                'automation_insights': {},
                'recommendations': []
            }
            
            # 产品线效率排名
            by_product_line = product_insights.get('by_product_line', {})
            if by_product_line:
                efficiency_analysis['product_line_rankings'] = self._rank_product_lines(by_product_line)
            
            # 效率模式识别
            efficiency_analysis['efficiency_patterns'] = self._identify_efficiency_patterns(product_insights)
            
            # 自动化洞察
            efficiency_analysis['automation_insights'] = self._analyze_automation_by_product(product_insights)
            
            # 生成建议
            efficiency_analysis['recommendations'] = self._generate_product_recommendations(product_insights)
            
            return {
                'table_name': table_name,
                'efficiency_analysis': efficiency_analysis,
                'detailed_insights': product_insights
            }
            
        except Exception as e:
            logger.error(f"分析产品线效率失败: {e}")
            return {'error': str(e)}
    
    def discover_quality_patterns(self, 
                                 table_name: str,
                                 quality_threshold: float = 0.1) -> Dict[str, Any]:
        """
        发现质量模式
        
        Args:
            table_name: 项目数据表名
            quality_threshold: 质量阈值（缺陷率）
            
        Returns:
            质量模式分析结果
        """
        try:
            # 获取项目数据分析结果
            analysis_result = self.analyze_project_table(table_name)
            
            if 'error' in analysis_result:
                return analysis_result
            
            mining_results = analysis_result['mining_results']
            quality_efficiency = mining_results.get('quality_efficiency_analysis', {})
            
            # 质量模式分析
            quality_patterns = {
                'high_quality_patterns': [],
                'low_quality_patterns': [],
                'quality_drivers': [],
                'quality_risks': [],
                'improvement_opportunities': []
            }
            
            # 识别高质量模式
            quality_patterns['high_quality_patterns'] = self._identify_high_quality_patterns(
                quality_efficiency, quality_threshold
            )
            
            # 识别低质量模式
            quality_patterns['low_quality_patterns'] = self._identify_low_quality_patterns(
                quality_efficiency, quality_threshold
            )
            
            # 质量驱动因素
            quality_patterns['quality_drivers'] = self._identify_quality_drivers(mining_results)
            
            # 质量风险
            quality_patterns['quality_risks'] = self._identify_quality_risks(mining_results)
            
            # 改进机会
            quality_patterns['improvement_opportunities'] = self._identify_improvement_opportunities(
                mining_results
            )
            
            return {
                'table_name': table_name,
                'quality_patterns': quality_patterns,
                'quality_threshold': quality_threshold
            }
            
        except Exception as e:
            logger.error(f"发现质量模式失败: {e}")
            return {'error': str(e)}
    
    def _generate_project_report(self, 
                                table_name: str,
                                project_data: pd.DataFrame,
                                mining_results: Dict[str, Any]) -> str:
        """生成项目数据挖掘报告"""
        try:
            report_title = f"项目数据关联规则挖掘报告 - {table_name}"
            
            # 创建报告目录
            report_dir = Path("reports/project_mining")
            report_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成报告文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"project_mining_{table_name}_{timestamp}.html"
            report_path = report_dir / report_filename
            
            # 生成HTML报告内容
            html_content = self._create_project_report_html(
                table_name, project_data, mining_results
            )
            
            # 写入文件
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"项目数据挖掘报告已生成: {report_path}")
            return str(report_path)
            
        except Exception as e:
            logger.error(f"生成项目报告失败: {e}")
            return ""
    
    def _create_project_report_html(self, 
                                   table_name: str,
                                   project_data: pd.DataFrame,
                                   mining_results: Dict[str, Any]) -> str:
        """创建项目报告HTML内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>项目数据关联规则挖掘报告 - {table_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; }}
                .section {{ margin: 20px 0; }}
                .subsection {{ margin: 10px 0; padding-left: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .insight {{ background-color: #e7f3ff; padding: 10px; margin: 10px 0; }}
                .recommendation {{ background-color: #fff2e7; padding: 10px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>项目数据关联规则挖掘报告</h1>
                <p>数据源: {table_name}</p>
                <p>生成时间: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>项目数量: {len(project_data)}</p>
            </div>
            
            <div class="section">
                <h2>数据概览</h2>
                {self._format_data_overview_html(mining_results.get('data_overview', {}))}
            </div>
            
            <div class="section">
                <h2>关联规则发现</h2>
                {self._format_associations_html(mining_results.get('categorical_associations', {}))}
            </div>
            
            <div class="section">
                <h2>数值相关性分析</h2>
                {self._format_correlations_html(mining_results.get('numerical_correlations', {}))}
            </div>
            
            <div class="section">
                <h2>组织绩效分析</h2>
                {self._format_organization_html(mining_results.get('organization_performance', {}))}
            </div>
            
            <div class="section">
                <h2>产品洞察</h2>
                {self._format_product_insights_html(mining_results.get('product_insights', {}))}
            </div>
            
            <div class="section">
                <h2>关键发现与建议</h2>
                {self._format_summary_html(mining_results.get('summary', {}))}
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_analysis_summary(self, mining_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成分析摘要"""
        summary = {
            'total_projects': 0,
            'key_associations': [],
            'main_correlations': [],
            'top_insights': [],
            'recommendations': []
        }
        
        # 从挖掘结果中提取关键信息
        data_overview = mining_results.get('data_overview', {})
        summary['total_projects'] = data_overview.get('total_projects', 0)
        
        # 关键关联
        categorical_associations = mining_results.get('categorical_associations', {})
        strong_associations = categorical_associations.get('strong_associations', [])
        summary['key_associations'] = strong_associations[:5]  # 前5个
        
        # 主要相关性
        numerical_correlations = mining_results.get('numerical_correlations', {})
        strong_correlations = numerical_correlations.get('strong_correlations', [])
        summary['main_correlations'] = strong_correlations[:5]  # 前5个
        
        # 顶级洞察
        summary_data = mining_results.get('summary', {})
        summary['top_insights'] = summary_data.get('key_findings', [])
        summary['recommendations'] = summary_data.get('recommendations', [])
        
        return summary
    
    # 辅助方法
    def _rank_organizations(self, org_data: Dict) -> Dict:
        """组织排名"""
        # 实现组织排名逻辑
        return {}
    
    def _identify_org_patterns(self, org_performance: Dict) -> List[Dict]:
        """识别组织模式"""
        # 实现组织模式识别逻辑
        return []
    
    def _generate_org_recommendations(self, org_performance: Dict) -> List[str]:
        """生成组织改进建议"""
        # 实现建议生成逻辑
        return []
    
    def _rank_product_lines(self, product_data: Dict) -> Dict:
        """产品线排名"""
        return {}
    
    def _identify_efficiency_patterns(self, product_insights: Dict) -> List[Dict]:
        """识别效率模式"""
        return []
    
    def _analyze_automation_by_product(self, product_insights: Dict) -> Dict:
        """按产品分析自动化"""
        return {}
    
    def _generate_product_recommendations(self, product_insights: Dict) -> List[str]:
        """生成产品改进建议"""
        return []
    
    def _identify_high_quality_patterns(self, quality_efficiency: Dict, threshold: float) -> List[Dict]:
        """识别高质量模式"""
        return []
    
    def _identify_low_quality_patterns(self, quality_efficiency: Dict, threshold: float) -> List[Dict]:
        """识别低质量模式"""
        return []
    
    def _identify_quality_drivers(self, mining_results: Dict) -> List[Dict]:
        """识别质量驱动因素"""
        return []
    
    def _identify_quality_risks(self, mining_results: Dict) -> List[Dict]:
        """识别质量风险"""
        return []
    
    def _identify_improvement_opportunities(self, mining_results: Dict) -> List[Dict]:
        """识别改进机会"""
        return []
    
    def _format_data_overview_html(self, data_overview: Dict) -> str:
        """格式化数据概览HTML"""
        return "<p>数据概览信息</p>"
    
    def _format_associations_html(self, associations: Dict) -> str:
        """格式化关联规则HTML"""
        return "<p>关联规则信息</p>"
    
    def _format_correlations_html(self, correlations: Dict) -> str:
        """格式化相关性HTML"""
        return "<p>相关性分析信息</p>"
    
    def _format_organization_html(self, org_performance: Dict) -> str:
        """格式化组织绩效HTML"""
        return "<p>组织绩效信息</p>"
    
    def _format_product_insights_html(self, product_insights: Dict) -> str:
        """格式化产品洞察HTML"""
        return "<p>产品洞察信息</p>"
    
    def _format_summary_html(self, summary: Dict) -> str:
        """格式化摘要HTML"""
        return "<p>摘要信息</p>"