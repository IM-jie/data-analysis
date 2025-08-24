"""
项目数据关联规则挖掘器
专门用于分析项目测试数据中的关联规则和模式
支持项目名称、项目编号、项目类型、项目级别、产品线、产品类型、测试负责人、
测试负责人所属组织架构、执行用例数、自动化执行用例数、关联缺陷、投入工时等字段的关联分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau, chi2_contingency
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import networkx as nx
try:
    from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
    from mlxtend.preprocessing import TransactionEncoder
    MLXTEND_AVAILABLE = True
except ImportError:
    logger.warning("mlxtend未安装，关联规则挖掘功能将受限")
    MLXTEND_AVAILABLE = False
import itertools
import warnings
from loguru import logger


class ProjectDataMiner:
    """项目数据关联规则挖掘器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化项目数据挖掘器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 默认字段映射
        self.field_mapping = {
            '项目名称': 'project_name',
            '项目编号': 'project_id', 
            '项目类型': 'project_type',
            '项目级别': 'project_level',
            '产品线': 'product_line',
            '产品类型': 'product_type',
            '测试负责人': 'test_owner',
            '测试负责人所属组织架构': 'test_owner_org',
            '执行用例数': 'executed_cases',
            '自动化执行用例数': 'automated_cases',
            '关联缺陷': 'related_bugs',
            '投入工时': 'effort_hours'
        }
        
        # 分类字段和数值字段
        self.categorical_fields = [
            'project_type', 'project_level', 'product_line', 
            'product_type', 'test_owner', 'test_owner_org'
        ]
        self.numerical_fields = [
            'executed_cases', 'automated_cases', 'related_bugs', 'effort_hours'
        ]
        
        self.analysis_results = {}
        
    def discover_project_associations(self, 
                                    data: pd.DataFrame,
                                    custom_fields: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        发现项目数据中的关联规则
        
        Args:
            data: 项目数据DataFrame
            custom_fields: 自定义字段映射
            
        Returns:
            关联规则挖掘结果
        """
        logger.info("开始项目数据关联规则挖掘...")
        
        # 更新字段映射
        if custom_fields:
            self.field_mapping.update(custom_fields)
        
        # 标准化列名
        data_normalized = self._normalize_columns(data)
        
        results = {
            'data_overview': self._analyze_data_overview(data_normalized),
            'categorical_associations': self._mine_categorical_associations(data_normalized),
            'numerical_correlations': self._analyze_numerical_correlations(data_normalized),
            'cross_type_associations': self._mine_cross_type_associations(data_normalized),
            'project_patterns': self._discover_project_patterns(data_normalized),
            'quality_efficiency_analysis': self._analyze_quality_efficiency(data_normalized),
            'organization_performance': self._analyze_organization_performance(data_normalized),
            'product_insights': self._analyze_product_insights(data_normalized),
            'summary': {}
        }
        
        # 生成综合洞察
        results['summary'] = self._generate_insights_summary(results)
        
        # 基于关联规则进行数据标签分类
        association_rules = results.get('categorical_associations', {}).get('association_rules', [])
        if association_rules:
            logger.info("开始基于关联规则进行数据标签分类...")
            labeled_data = self.label_data_by_association_rules(data_normalized, association_rules)
            results['labeled_data'] = labeled_data
            
            # 生成规则遵循报告
            results['rule_compliance_report'] = self.generate_rule_compliance_report()
            
            # 识别异常模式
            results['anomaly_patterns'] = self.identify_anomaly_patterns(labeled_data)
        
        self.analysis_results = results
        return results
    
    def _normalize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化列名"""
        data_copy = data.copy()
        
        # 尝试映射已知字段
        column_mapping = {}
        used_standard_names = set()  # 记录已使用的标准字段名
        
        for col in data_copy.columns:
            for chinese_name, english_name in self.field_mapping.items():
                # 检查是否已经映射过该标准字段名
                if english_name in used_standard_names:
                    continue
                    
                if chinese_name in col or col in chinese_name:
                    column_mapping[col] = english_name
                    used_standard_names.add(english_name)
                    break
        
        if column_mapping:
            data_copy = data_copy.rename(columns=column_mapping)
            logger.info(f"字段映射完成: {column_mapping}")
        
        return data_copy
    
    def _analyze_data_overview(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析数据概览"""
        overview = {
            'total_projects': len(data),
            'columns': list(data.columns),
            'data_types': data.dtypes.to_dict(),
            'missing_values': data.isnull().sum().to_dict(),
            'categorical_summary': {},
            'numerical_summary': {}
        }
        
        # 分析分类字段
        for field in self.categorical_fields:
            if field in data.columns:
                overview['categorical_summary'][field] = {
                    'unique_count': data[field].nunique(),
                    'top_values': data[field].value_counts().head(10).to_dict(),
                    'missing_rate': data[field].isnull().mean()
                }
        
        # 分析数值字段
        for field in self.numerical_fields:
            if field in data.columns:
                overview['numerical_summary'][field] = {
                    'mean': data[field].mean(),
                    'std': data[field].std(),
                    'min': data[field].min(),
                    'max': data[field].max(),
                    'median': data[field].median(),
                    'missing_rate': data[field].isnull().mean()
                }
        
        return overview
    
    def _mine_categorical_associations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """挖掘分类字段间的关联规则"""
        associations = {
            'chi_square_tests': {},
            'cramers_v': {},
            'association_rules': [],
            'strong_associations': []
        }
        
        categorical_cols = [col for col in self.categorical_fields if col in data.columns]
        
        if len(categorical_cols) < 2:
            return associations
        
        # 卡方检验和Cramer's V
        for i, col1 in enumerate(categorical_cols):
            for j, col2 in enumerate(categorical_cols):
                if i < j:
                    try:
                        # 创建交叉表
                        crosstab = pd.crosstab(data[col1].fillna('Missing'), 
                                             data[col2].fillna('Missing'))
                        
                        # 卡方检验
                        chi2_stat, p_value, dof, expected = chi2_contingency(crosstab)
                        chi2 = float(chi2_stat)
                        
                        # Cramer's V
                        n = crosstab.sum().sum()
                        cramers_v = np.sqrt(chi2 / (n * (min(crosstab.shape) - 1)))
                        
                        pair_key = f"{col1}__{col2}"
                        associations['chi_square_tests'][pair_key] = {
                            'chi2': chi2,
                            'p_value': float(p_value),
                            'significant': float(p_value) < 0.05
                        }
                        
                        associations['cramers_v'][pair_key] = {
                            'cramers_v': cramers_v,
                            'strength': self._interpret_cramers_v(cramers_v)
                        }
                        
                        # 如果关联性强，记录
                        if cramers_v > 0.3 and float(p_value) < 0.05:
                            associations['strong_associations'].append({
                                'field1': col1,
                                'field2': col2,
                                'cramers_v': cramers_v,
                                'p_value': p_value,
                                'interpretation': self._interpret_association(col1, col2, cramers_v)
                            })
                    
                    except Exception as e:
                        logger.warning(f"分析 {col1} 和 {col2} 的关联性失败: {e}")
        
        # 使用Apriori算法挖掘关联规则
        if MLXTEND_AVAILABLE:
            try:
                associations['association_rules'] = self._mine_apriori_rules(data, categorical_cols)
            except Exception as e:
                logger.warning(f"Apriori关联规则挖掘失败: {e}")
        else:
            logger.warning("由于mlxtend不可用，跳过Apriori关联规则挖掘")
        
        return associations
    
    def _analyze_numerical_correlations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析数值字段间的相关性"""
        correlations = {
            'correlation_matrix': None,
            'strong_correlations': [],
            'regression_insights': []
        }
        
        numerical_cols = [col for col in self.numerical_fields if col in data.columns]
        
        if len(numerical_cols) < 2:
            return correlations
        
        # 计算相关性矩阵
        numeric_data = data[numerical_cols].dropna()
        if len(numeric_data) < 3:
            return correlations
        
        correlations['correlation_matrix'] = numeric_data.corr()
        
        # 识别强相关性
        threshold = self.config.get('correlation_threshold', 0.6)
        for i, col1 in enumerate(numerical_cols):
            for j, col2 in enumerate(numerical_cols):
                if i < j:
                    try:
                        corr_coef = float(numeric_data[col1].corr(numeric_data[col2]))
                        if abs(corr_coef) >= threshold:
                            correlations['strong_correlations'].append({
                                'field1': col1,
                                'field2': col2,
                                'correlation': corr_coef,
                                'interpretation': self._interpret_numerical_correlation(col1, col2, corr_coef)
                            })
                    except Exception as e:
                        logger.warning(f"计算 {col1} 和 {col2} 相关性失败: {e}")
        
        return correlations
    
    def _mine_cross_type_associations(self, data: pd.DataFrame) -> Dict[str, Any]:
        """挖掘分类字段和数值字段间的关联"""
        cross_associations = {
            'anova_tests': {},
            'group_statistics': {},
            'significant_differences': []
        }
        
        categorical_cols = [col for col in self.categorical_fields if col in data.columns]
        numerical_cols = [col for col in self.numerical_fields if col in data.columns]
        
        for cat_col in categorical_cols:
            for num_col in numerical_cols:
                try:
                    # 按分类字段分组分析数值字段
                    groups = data.groupby(cat_col)[num_col].apply(list)
                    
                    # 过滤掉空组和过小的组
                    valid_groups = [group for group in groups if len(group) >= 3]
                    
                    if len(valid_groups) >= 2:
                        # 执行方差分析
                        f_stat, p_value = stats.f_oneway(*valid_groups)
                        
                        pair_key = f"{cat_col}__{num_col}"
                        cross_associations['anova_tests'][pair_key] = {
                            'f_statistic': f_stat,
                            'p_value': p_value,
                            'significant': p_value < 0.05
                        }
                        
                        # 计算组统计信息
                        group_stats = data.groupby(cat_col)[num_col].agg(['count', 'mean', 'std']).to_dict()
                        cross_associations['group_statistics'][pair_key] = group_stats
                        
                        # 如果差异显著，记录详细信息
                        if p_value < 0.05:
                            cross_associations['significant_differences'].append({
                                'categorical_field': cat_col,
                                'numerical_field': num_col,
                                'f_statistic': f_stat,
                                'p_value': p_value,
                                'interpretation': self._interpret_cross_association(cat_col, num_col, f_stat, p_value),
                                'group_means': data.groupby(cat_col)[num_col].mean().to_dict()
                            })
                
                except Exception as e:
                    logger.warning(f"分析 {cat_col} 和 {num_col} 的交叉关联失败: {e}")
        
        return cross_associations
    
    def _discover_project_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """发现项目模式"""
        patterns = {
            'high_performance_patterns': [],
            'low_performance_patterns': [],
            'automation_patterns': [],
            'efficiency_patterns': []
        }
        
        # 计算自动化率
        if 'executed_cases' in data.columns and 'automated_cases' in data.columns:
            data['automation_rate'] = data['automated_cases'] / (data['executed_cases'] + 0.001)
        
        # 计算效率指标（每工时执行用例数）
        if 'executed_cases' in data.columns and 'effort_hours' in data.columns:
            data['efficiency'] = data['executed_cases'] / (data['effort_hours'] + 0.001)
        
        # 计算质量指标（每用例缺陷数）
        if 'related_bugs' in data.columns and 'executed_cases' in data.columns:
            data['bug_rate'] = data['related_bugs'] / (data['executed_cases'] + 0.001)
        
        # 分析高性能模式
        patterns['high_performance_patterns'] = self._find_performance_patterns(data, 'high')
        
        # 分析低性能模式
        patterns['low_performance_patterns'] = self._find_performance_patterns(data, 'low')
        
        # 分析自动化模式
        if 'automation_rate' in data.columns:
            patterns['automation_patterns'] = self._find_automation_patterns(data)
        
        # 分析效率模式
        if 'efficiency' in data.columns:
            patterns['efficiency_patterns'] = self._find_efficiency_patterns(data)
        
        return patterns
    
    def _analyze_quality_efficiency(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析质量和效率的关系"""
        analysis = {
            'quality_metrics': {},
            'efficiency_metrics': {},
            'quality_efficiency_correlation': {},
            'insights': []
        }
        
        # 计算质量指标
        if 'related_bugs' in data.columns and 'executed_cases' in data.columns:
            data['defect_density'] = data['related_bugs'] / (data['executed_cases'] + 0.001)
            analysis['quality_metrics']['avg_defect_density'] = data['defect_density'].mean()
            analysis['quality_metrics']['std_defect_density'] = data['defect_density'].std()
        
        # 计算效率指标
        if 'executed_cases' in data.columns and 'effort_hours' in data.columns:
            data['test_efficiency'] = data['executed_cases'] / (data['effort_hours'] + 0.001)
            analysis['efficiency_metrics']['avg_test_efficiency'] = data['test_efficiency'].mean()
            analysis['efficiency_metrics']['std_test_efficiency'] = data['test_efficiency'].std()
        
        # 分析质量与效率的关系
        if 'defect_density' in data.columns and 'test_efficiency' in data.columns:
            corr = float(data['defect_density'].corr(data['test_efficiency']))
            analysis['quality_efficiency_correlation'] = {
                'correlation': corr,
                'interpretation': self._interpret_quality_efficiency_correlation(corr)
            }
        
        return analysis
    
    def _analyze_organization_performance(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析组织绩效"""
        org_analysis = {
            'by_organization': {},
            'by_test_owner': {},
            'organization_rankings': {}
        }
        
        # 按组织架构分析
        if 'test_owner_org' in data.columns:
            org_stats = self._calculate_organization_stats(data, 'test_owner_org')
            org_analysis['by_organization'] = org_stats
        
        # 按测试负责人分析
        if 'test_owner' in data.columns:
            owner_stats = self._calculate_organization_stats(data, 'test_owner')
            org_analysis['by_test_owner'] = owner_stats
        
        return org_analysis
    
    def _analyze_product_insights(self, data: pd.DataFrame) -> Dict[str, Any]:
        """分析产品洞察"""
        product_analysis = {
            'by_product_line': {},
            'by_product_type': {},
            'product_complexity': {},
            'product_recommendations': []
        }
        
        # 按产品线分析
        if 'product_line' in data.columns:
            product_analysis['by_product_line'] = self._analyze_by_dimension(data, 'product_line')
        
        # 按产品类型分析
        if 'product_type' in data.columns:
            product_analysis['by_product_type'] = self._analyze_by_dimension(data, 'product_type')
        
        return product_analysis
    
    def _mine_apriori_rules(self, data: pd.DataFrame, categorical_cols: List[str]) -> List[Dict]:
        """使用Apriori算法挖掘关联规则"""
        rules = []
        
        if not MLXTEND_AVAILABLE:
            return rules
        
        try:
            # 准备事务数据
            transactions = []
            for _, row in data.iterrows():
                transaction = []
                for col in categorical_cols:
                    if pd.notna(row[col]) and row[col] is not None:
                        transaction.append(f"{col}_{row[col]}")
                if transaction:
                    transactions.append(transaction)
            
            if not transactions:
                return rules
            
            # 转换为布尔矩阵
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
            
            # 挖掘频繁项集
            min_support = self.config.get('min_support', 0.1)
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
            
            if not frequent_itemsets.empty:
                # 生成关联规则
                min_confidence = self.config.get('min_confidence', 0.5)
                association_rules_df = association_rules(
                    frequent_itemsets, 
                    metric="confidence", 
                    min_threshold=min_confidence
                )
                
                # 转换为字典列表
                for _, rule in association_rules_df.iterrows():
                    rules.append({
                        'antecedents': list(rule['antecedents']),
                        'consequents': list(rule['consequents']),
                        'support': rule['support'],
                        'confidence': rule['confidence'],
                        'lift': rule['lift'],
                        'conviction': rule['conviction'] if 'conviction' in rule else None
                    })
        
        except Exception as e:
            logger.warning(f"Apriori规则挖掘失败: {e}")
        
        return rules
    
    def _generate_insights_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合洞察摘要"""
        summary = {
            'key_findings': [],
            'recommendations': [],
            'risk_alerts': [],
            'performance_insights': []
        }
        
        # 从各个分析结果中提取关键发现
        data_overview = results.get('data_overview', {})
        categorical_associations = results.get('categorical_associations', {})
        numerical_correlations = results.get('numerical_correlations', {})
        cross_type_associations = results.get('cross_type_associations', {})
        
        # 数据质量洞察
        total_projects = data_overview.get('total_projects', 0)
        summary['key_findings'].append(f"分析了 {total_projects} 个项目的数据")
        
        # 强关联发现
        strong_associations = categorical_associations.get('strong_associations', [])
        if strong_associations:
            summary['key_findings'].append(f"发现 {len(strong_associations)} 个强分类关联")
        
        strong_correlations = numerical_correlations.get('strong_correlations', [])
        if strong_correlations:
            summary['key_findings'].append(f"发现 {len(strong_correlations)} 个强数值相关性")
        
        # 生成建议
        summary['recommendations'] = self._generate_recommendations(results)
        
        return summary
    
    def label_data_by_association_rules(self, 
                                      data: pd.DataFrame,
                                      rules: List[Dict],
                                      min_confidence: float = 0.7) -> pd.DataFrame:
        """
        基于关联规则对数据进行标签分类
        
        Args:
            data: 原始数据
            rules: 关联规则列表
            min_confidence: 最小置信度阈值
            
        Returns:
            包含标签的数据DataFrame
        """
        logger.info("开始基于关联规则对数据进行标签分类...")
        
        # 复制数据
        labeled_data = data.copy()
        
        # 初始化标签列
        labeled_data['rule_labels'] = ''
        labeled_data['rule_violations'] = ''
        labeled_data['rule_compliance_score'] = 0.0
        labeled_data['anomaly_flags'] = ''
        
        # 过滤高置信度规则
        high_confidence_rules = [rule for rule in rules 
                               if rule.get('confidence', 0) >= min_confidence]
        
        logger.info(f"使用 {len(high_confidence_rules)} 个高置信度规则进行标签分类")
        
        rule_compliance_stats = []
        
        for rule_idx, rule in enumerate(high_confidence_rules):
            try:
                antecedents = rule.get('antecedents', [])
                consequents = rule.get('consequents', [])
                confidence = rule.get('confidence', 0)
                support = rule.get('support', 0)
                lift = rule.get('lift', 1)
                
                if not antecedents or not consequents:
                    continue
                
                # 检查每行数据是否符合规则
                rule_name = f"Rule_{rule_idx+1}"
                antecedent_matches = self._check_rule_conditions(labeled_data, antecedents)
                consequent_matches = self._check_rule_conditions(labeled_data, consequents)
                
                # 符合前置条件的数据
                antecedent_mask = antecedent_matches
                # 符合后置条件的数据
                consequent_mask = consequent_matches
                # 符合完整规则的数据（前置且后置都符合）
                complete_rule_mask = antecedent_mask & consequent_mask
                # 违反规则的数据（符合前置但不符合后置）
                violation_mask = antecedent_mask & (~consequent_mask)
                
                # 统计规则遵循情况
                antecedent_count = antecedent_mask.sum()
                complete_count = complete_rule_mask.sum()
                violation_count = violation_mask.sum()
                
                actual_confidence = complete_count / antecedent_count if antecedent_count > 0 else 0
                
                rule_stats = {
                    'rule_name': rule_name,
                    'antecedents': ' & '.join(antecedents),
                    'consequents': ' & '.join(consequents),
                    'expected_confidence': confidence,
                    'actual_confidence': actual_confidence,
                    'support': support,
                    'lift': lift,
                    'antecedent_count': antecedent_count,
                    'complete_count': complete_count,
                    'violation_count': violation_count,
                    'violation_rate': violation_count / antecedent_count if antecedent_count > 0 else 0
                }
                rule_compliance_stats.append(rule_stats)
                
                # 为符合完整规则的数据添加标签
                rule_label = f"{rule_name}(完全符合)"
                labeled_data.loc[complete_rule_mask, 'rule_labels'] += f"{rule_label}; "
                labeled_data.loc[complete_rule_mask, 'rule_compliance_score'] += confidence
                
                # 为违反规则的数据添加标签和异常标记
                violation_label = f"{rule_name}(违反规则)"
                labeled_data.loc[violation_mask, 'rule_violations'] += f"{violation_label}; "
                labeled_data.loc[violation_mask, 'anomaly_flags'] += f"前置符合但后置不符合({' & '.join(antecedents)} -> {' & '.join(consequents)}); "
                
                logger.info(f"{rule_name}: 前置条件匹配{antecedent_count}项, 完全符合{complete_count}项, 违反{violation_count}项")
                
            except Exception as e:
                logger.warning(f"处理规则 {rule_idx+1} 时出错: {e}")
                continue
        
        # 清理标签字符串
        labeled_data['rule_labels'] = labeled_data['rule_labels'].str.rstrip('; ')
        labeled_data['rule_violations'] = labeled_data['rule_violations'].str.rstrip('; ')
        labeled_data['anomaly_flags'] = labeled_data['anomaly_flags'].str.rstrip('; ')
        
        # 计算异常评分
        labeled_data['anomaly_score'] = self._calculate_anomaly_score(labeled_data)
        
        # 分类数据
        labeled_data['data_category'] = self._categorize_data(labeled_data)
        
        # 保存规则遵循统计
        self.rule_compliance_stats = rule_compliance_stats
        
        logger.info(f"数据标签分类完成，共处理 {len(labeled_data)} 条记录")
        
        return labeled_data
    
    def _check_rule_conditions(self, data: pd.DataFrame, conditions: List[str]) -> pd.Series:
        """
        检查数据是否符合规则条件
        
        Args:
            data: 数据
            conditions: 条件列表（格式如：['项目类型_Web应用', '项目级别_P0']）
            
        Returns:
            布尔Series，表示每行是否符合条件
        """
        if not conditions:
            return pd.Series([False] * len(data), index=data.index)
        
        # 初始化为全True
        result_mask = pd.Series([True] * len(data), index=data.index)
        
        for condition in conditions:
            try:
                # 解析条件（格式：字段名_值）
                if '_' in condition:
                    field_name, field_value = condition.rsplit('_', 1)
                    
                    # 检查字段是否存在
                    if field_name in data.columns:
                        # 检查字段值是否匹配
                        condition_mask = (data[field_name].astype(str) == field_value)
                        result_mask = result_mask & condition_mask
                    else:
                        # 字段不存在，该条件为False
                        result_mask = pd.Series([False] * len(data), index=data.index)
                        break
                else:
                    # 条件格式不正确
                    logger.warning(f"无法解析条件: {condition}")
                    result_mask = pd.Series([False] * len(data), index=data.index)
                    break
                    
            except Exception as e:
                logger.warning(f"检查条件 {condition} 时出错: {e}")
                result_mask = pd.Series([False] * len(data), index=data.index)
                break
        
        return result_mask
    
    def _calculate_anomaly_score(self, labeled_data: pd.DataFrame) -> pd.Series:
        """
        计算异常评分
        
        Args:
            labeled_data: 已标记的数据
            
        Returns:
            异常评分Series
        """
        anomaly_scores = pd.Series([0.0] * len(labeled_data), index=labeled_data.index)
        
        # 基于违反规则的数量和严重程度计算异常评分
        for idx, row in labeled_data.iterrows():
            score = 0.0
            
            # 违反规则的惩罚
            violations = row.get('rule_violations', '')
            if violations:
                violation_count = len([v for v in violations.split(';') if v.strip()])
                score += violation_count * 0.3
            
            # 异常标记的惩罚
            anomaly_flags = row.get('anomaly_flags', '')
            if anomaly_flags:
                flag_count = len([f for f in anomaly_flags.split(';') if f.strip()])
                score += flag_count * 0.5
            
            # 规则遵循度的奖励（负分）
            compliance_score = row.get('rule_compliance_score', 0)
            score -= compliance_score * 0.1
            
            anomaly_scores.iloc[anomaly_scores.index.get_loc(idx)] = max(0, score)
        
        return anomaly_scores
    
    def _categorize_data(self, labeled_data: pd.DataFrame) -> pd.Series:
        """
        基于标签对数据进行分类
        
        Args:
            labeled_data: 已标记的数据
            
        Returns:
            数据分类Series
        """
        categories = []
        
        for _, row in labeled_data.iterrows():
            violations = row.get('rule_violations', '')
            rule_labels = row.get('rule_labels', '')
            anomaly_score = row.get('anomaly_score', 0)
            
            if violations:
                if anomaly_score > 1.0:
                    category = "高风险异常"
                elif anomaly_score > 0.5:
                    category = "中风险异常"
                else:
                    category = "低风险异常"
            elif rule_labels:
                category = "规则符合"
            else:
                category = "未匹配规则"
            
            categories.append(category)
        
        return pd.Series(categories, index=labeled_data.index)
    
    def generate_rule_compliance_report(self) -> Dict[str, Any]:
        """
        生成规则遵循报告
        
        Returns:
            规则遵循报告
        """
        if not hasattr(self, 'rule_compliance_stats'):
            return {'error': '尚未执行规则标签分类'}
        
        report = {
            'total_rules': len(self.rule_compliance_stats),
            'rule_details': self.rule_compliance_stats,
            'summary': {
                'high_violation_rules': [],
                'low_confidence_rules': [],
                'effective_rules': []
            }
        }
        
        # 分析规则效果
        for rule_stat in self.rule_compliance_stats:
            rule_name = rule_stat['rule_name']
            violation_rate = rule_stat['violation_rate']
            actual_confidence = rule_stat['actual_confidence']
            expected_confidence = rule_stat['expected_confidence']
            
            # 高违反率规则
            if violation_rate > 0.3:
                report['summary']['high_violation_rules'].append({
                    'rule_name': rule_name,
                    'violation_rate': violation_rate,
                    'antecedents': rule_stat['antecedents'],
                    'consequents': rule_stat['consequents']
                })
            
            # 低置信度规则
            if actual_confidence < expected_confidence * 0.8:
                report['summary']['low_confidence_rules'].append({
                    'rule_name': rule_name,
                    'expected_confidence': expected_confidence,
                    'actual_confidence': actual_confidence,
                    'confidence_gap': expected_confidence - actual_confidence
                })
            
            # 有效规则
            if violation_rate < 0.1 and actual_confidence >= expected_confidence * 0.9:
                report['summary']['effective_rules'].append({
                    'rule_name': rule_name,
                    'confidence': actual_confidence,
                    'support': rule_stat['support']
                })
        
        return report
    
    def identify_anomaly_patterns(self, labeled_data: pd.DataFrame) -> Dict[str, Any]:
        """
        识别异常模式
        
        Args:
            labeled_data: 已标记的数据
            
        Returns:
            异常模式分析结果
        """
        logger.info("识别异常模式...")
        
        # 筛选异常数据
        anomaly_data = labeled_data[labeled_data['data_category'].str.contains('异常', na=False)]
        
        if len(anomaly_data) == 0:
            return {'message': '未发现异常数据'}
        
        patterns = {
            'anomaly_count': len(anomaly_data),
            'anomaly_rate': len(anomaly_data) / len(labeled_data),
            'anomaly_distribution': {},
            'common_violation_patterns': [],
            'high_risk_projects': [],
            'anomaly_by_category': {}
        }
        
        # 异常分布分析
        for col in self.categorical_fields:
            if col in anomaly_data.columns:
                dist = anomaly_data[col].value_counts(normalize=True).head(5)
                patterns['anomaly_distribution'][col] = dist.to_dict()
        
        # 常见违反模式
        violation_patterns = anomaly_data['rule_violations'].value_counts().head(10)
        patterns['common_violation_patterns'] = [
            {'pattern': pattern, 'count': count, 'rate': count/len(anomaly_data)}
            for pattern, count in violation_patterns.items() if pattern
        ]
        
        # 高风险项目
        high_risk = anomaly_data[anomaly_data['anomaly_score'] > 1.0].copy()
        if len(high_risk) > 0:
            patterns['high_risk_projects'] = high_risk[[
                '项目名称', '项目类型', '项目级别', '异常评分', 'rule_violations'
            ]].to_dict('records') if '项目名称' in high_risk.columns else []
        
        # 按分类统计异常
        category_stats = labeled_data['data_category'].value_counts()
        patterns['anomaly_by_category'] = category_stats.to_dict()
        
        return patterns
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 基于分析结果生成建议
        quality_efficiency = results.get('quality_efficiency_analysis', {})
        if quality_efficiency:
            recommendations.append("建议关注测试质量与效率的平衡")
        
        org_performance = results.get('organization_performance', {})
        if org_performance:
            recommendations.append("建议优化组织间的测试流程标准化")
        
        return recommendations
    
    # 辅助方法
    def _interpret_cramers_v(self, cramers_v: float) -> str:
        """解释Cramer's V值"""
        if cramers_v < 0.1:
            return "弱关联"
        elif cramers_v < 0.3:
            return "中等关联"
        elif cramers_v < 0.5:
            return "强关联"
        else:
            return "非常强关联"
    
    def _interpret_association(self, field1: str, field2: str, cramers_v: float) -> str:
        """解释字段间的关联"""
        strength = self._interpret_cramers_v(cramers_v)
        return f"{field1}与{field2}存在{strength}（Cramer's V = {cramers_v:.3f}）"
    
    def _interpret_numerical_correlation(self, field1: str, field2: str, correlation: float) -> str:
        """解释数值相关性"""
        if correlation > 0:
            direction = "正相关"
        else:
            direction = "负相关"
        
        strength = "强" if abs(correlation) > 0.7 else "中等"
        return f"{field1}与{field2}存在{strength}{direction}（r = {correlation:.3f}）"
    
    def _interpret_cross_association(self, cat_field: str, num_field: str, f_stat: float, p_value: float) -> str:
        """解释交叉关联"""
        return f"{cat_field}对{num_field}有显著影响（F = {f_stat:.3f}, p = {p_value:.3f}）"
    
    def _interpret_quality_efficiency_correlation(self, correlation: float) -> str:
        """解释质量效率相关性"""
        if correlation > 0.3:
            return "效率提高可能导致缺陷增加，需要平衡质量与效率"
        elif correlation < -0.3:
            return "效率提高伴随缺陷减少，说明流程优化有效"
        else:
            return "质量与效率之间关系不明显"
    
    def _find_performance_patterns(self, data: pd.DataFrame, performance_type: str) -> List[Dict]:
        """查找性能模式"""
        patterns = []
        # 这里可以根据具体需求实现性能模式识别逻辑
        return patterns
    
    def _find_automation_patterns(self, data: pd.DataFrame) -> List[Dict]:
        """查找自动化模式"""
        patterns = []
        # 实现自动化模式识别逻辑
        return patterns
    
    def _find_efficiency_patterns(self, data: pd.DataFrame) -> List[Dict]:
        """查找效率模式"""
        patterns = []
        # 实现效率模式识别逻辑
        return patterns
    
    def _calculate_organization_stats(self, data: pd.DataFrame, group_col: str) -> Dict:
        """计算组织统计信息"""
        stats = {}
        if group_col in data.columns:
            for col in self.numerical_fields:
                if col in data.columns:
                    stats[col] = data.groupby(group_col)[col].agg(['count', 'mean', 'std']).to_dict()
        return stats
    
    def _analyze_by_dimension(self, data: pd.DataFrame, dimension: str) -> Dict:
        """按维度分析"""
        analysis = {}
        if dimension in data.columns:
            for col in self.numerical_fields:
                if col in data.columns:
                    analysis[col] = data.groupby(dimension)[col].agg(['count', 'mean', 'std']).to_dict()
        return analysis