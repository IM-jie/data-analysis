"""
KPI关联关系挖掘器
支持发现指标间的关联关系和基于关联关系的异常检测
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import networkx as nx
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import warnings
from loguru import logger


class KPIAssociationMiner:
    """KPI关联关系挖掘器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化关联关系挖掘器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.associations = {}
        self.correlation_matrix = None
        self.causal_graph = None
        self.scaler = StandardScaler()
        
    def discover_associations(self, data: pd.DataFrame, 
                             metric_columns: List[str],
                             methods: List[str] = None) -> Dict[str, Any]:
        """
        发现指标间的关联关系
        
        Args:
            data: 输入数据
            metric_columns: 指标列名列表
            methods: 关联分析方法列表
            
        Returns:
            关联关系分析结果
        """
        if methods is None:
            methods = ['correlation', 'mutual_info', 'association_rules', 'causality']
        
        results = {
            'correlations': {},
            'mutual_info': {},
            'association_rules': {},
            'causal_relationships': {},
            'summary': {}
        }
        
        # 1. 相关性分析
        if 'correlation' in methods:
            results['correlations'] = self._analyze_correlations(data, metric_columns)
        
        # 2. 互信息分析
        if 'mutual_info' in methods:
            results['mutual_info'] = self._analyze_mutual_information(data, metric_columns)
        
        # 3. 关联规则挖掘
        if 'association_rules' in methods:
            results['association_rules'] = self._mine_association_rules(data, metric_columns)
        
        # 4. 因果关系分析
        if 'causality' in methods:
            results['causal_relationships'] = self._analyze_causality(data, metric_columns)
        
        # 5. 生成摘要
        results['summary'] = self._generate_association_summary(results)
        
        self.associations = results
        return results
    
    def _analyze_correlations(self, data: pd.DataFrame, 
                             metric_columns: List[str]) -> Dict[str, Any]:
        """分析指标间的相关性"""
        correlations = {
            'pearson': {},
            'spearman': {},
            'kendall': {},
            'matrix': None,
            'strong_correlations': []
        }
        
        # 计算相关性矩阵
        metric_data = data[metric_columns].dropna()
        if len(metric_data) < 2:
            return correlations
        
        # 计算各种相关系数
        for i, metric1 in enumerate(metric_columns):
            for j, metric2 in enumerate(metric_columns):
                if i < j:  # 避免重复计算
                    # 获取有效数据
                    valid_data = metric_data[[metric1, metric2]].dropna()
                    if len(valid_data) < 3:
                        continue
                    
                    # Pearson相关系数
                    try:
                        pearson_corr, pearson_p = pearsonr(valid_data[metric1], valid_data[metric2])
                        correlations['pearson'][f"{metric1}__{metric2}"] = {
                            'correlation': pearson_corr,
                            'p_value': pearson_p,
                            'significant': pearson_p < 0.05
                        }
                    except:
                        pass
                    
                    # Spearman相关系数
                    try:
                        spearman_corr, spearman_p = spearmanr(valid_data[metric1], valid_data[metric2])
                        correlations['spearman'][f"{metric1}__{metric2}"] = {
                            'correlation': spearman_corr,
                            'p_value': spearman_p,
                            'significant': spearman_p < 0.05
                        }
                    except:
                        pass
                    
                    # Kendall相关系数
                    try:
                        kendall_corr, kendall_p = kendalltau(valid_data[metric1], valid_data[metric2])
                        correlations['kendall'][f"{metric1}__{metric2}"] = {
                            'correlation': kendall_corr,
                            'p_value': kendall_p,
                            'significant': kendall_p < 0.05
                        }
                    except:
                        pass
        
        # 生成相关性矩阵
        correlations['matrix'] = metric_data.corr()
        
        # 识别强相关性
        threshold = self.config.get('correlation_threshold', 0.7)
        for method in ['pearson', 'spearman', 'kendall']:
            for pair, result in correlations[method].items():
                if abs(result['correlation']) >= threshold and result['significant']:
                    correlations['strong_correlations'].append({
                        'pair': pair,
                        'method': method,
                        'correlation': result['correlation'],
                        'p_value': result['p_value']
                    })
        
        return correlations
    
    def _analyze_mutual_information(self, data: pd.DataFrame, 
                                   metric_columns: List[str]) -> Dict[str, Any]:
        """分析指标间的互信息"""
        mutual_info = {
            'matrix': None,
            'strong_relationships': [],
            'feature_importance': {}
        }
        
        metric_data = data[metric_columns].dropna()
        if len(metric_data) < 2:
            return mutual_info
        
        # 标准化数据
        scaler = StandardScaler()
        scaled_data = pd.DataFrame(
            scaler.fit_transform(metric_data),
            columns=metric_columns,
            index=metric_data.index
        )
        
        # 计算互信息矩阵
        mi_matrix = np.zeros((len(metric_columns), len(metric_columns)))
        
        for i, metric1 in enumerate(metric_columns):
            for j, metric2 in enumerate(metric_columns):
                if i != j:
                    try:
                        # 使用互信息回归
                        mi_score = mutual_info_regression(
                            scaled_data[[metric1]], 
                            scaled_data[metric2],
                            random_state=42
                        )[0]
                        mi_matrix[i, j] = mi_score
                    except:
                        mi_matrix[i, j] = 0
        
        mutual_info['matrix'] = pd.DataFrame(
            mi_matrix,
            index=metric_columns,
            columns=metric_columns
        )
        
        # 识别强互信息关系
        threshold = self.config.get('mi_threshold', 0.3)
        for i, metric1 in enumerate(metric_columns):
            for j, metric2 in enumerate(metric_columns):
                if i < j and mi_matrix[i, j] >= threshold:
                    mutual_info['strong_relationships'].append({
                        'source': metric1,
                        'target': metric2,
                        'mi_score': mi_matrix[i, j]
                    })
        
        return mutual_info
    
    def _mine_association_rules(self, data: pd.DataFrame, 
                               metric_columns: List[str]) -> Dict[str, Any]:
        """挖掘关联规则"""
        association_rules_result = {
            'frequent_itemsets': None,
            'rules': None,
            'strong_rules': []
        }
        
        try:
            # 将连续数据离散化
            discretized_data = self._discretize_metrics(data, metric_columns)
            
            # 转换为事务格式
            transactions = []
            for _, row in discretized_data.iterrows():
                transaction = []
                for col in metric_columns:
                    if pd.notna(row[col]):
                        transaction.append(f"{col}_{row[col]}")
                if transaction:
                    transactions.append(transaction)
            
            if len(transactions) < 2:
                return association_rules_result
            
            # 使用Apriori算法挖掘频繁项集
            te = TransactionEncoder()
            te_ary = te.fit(transactions).transform(transactions)
            df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
            
            # 挖掘频繁项集
            min_support = self.config.get('min_support', 0.1)
            frequent_itemsets = apriori(df_encoded, min_support=min_support, use_colnames=True)
            association_rules_result['frequent_itemsets'] = frequent_itemsets
            
            # 生成关联规则
            if len(frequent_itemsets) > 0:
                min_confidence = self.config.get('min_confidence', 0.5)
                rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
                association_rules_result['rules'] = rules
                
                # 识别强关联规则
                min_lift = self.config.get('min_lift', 1.2)
                strong_rules = rules[rules['lift'] >= min_lift]
                association_rules_result['strong_rules'] = strong_rules.to_dict('records')
        
        except Exception as e:
            logger.warning(f"关联规则挖掘失败: {e}")
        
        return association_rules_result
    
    def _discretize_metrics(self, data: pd.DataFrame, 
                           metric_columns: List[str]) -> pd.DataFrame:
        """将连续指标离散化"""
        discretized_data = data.copy()
        
        for metric in metric_columns:
            if metric in data.columns:
                metric_data = data[metric].dropna()
                if len(metric_data) > 0:
                    # 使用分位数进行离散化
                    try:
                        quantiles = metric_data.quantile([0.25, 0.5, 0.75])
                        discretized_data[metric] = pd.cut(
                            data[metric],
                            bins=[-np.inf] + list(quantiles) + [np.inf],
                            labels=['low', 'medium_low', 'medium_high', 'high'],
                            include_lowest=True
                        )
                    except:
                        # 如果分位数方法失败，使用等宽分箱
                        try:
                            discretized_data[metric] = pd.qcut(
                                data[metric],
                                q=4,
                                labels=['low', 'medium_low', 'medium_high', 'high'],
                                duplicates='drop'
                            )
                        except:
                            pass
        
        return discretized_data
    
    def _analyze_causality(self, data: pd.DataFrame, 
                          metric_columns: List[str]) -> Dict[str, Any]:
        """分析因果关系"""
        causality = {
            'lag_correlations': {},
            'causal_graph': None,
            'causal_chains': []
        }
        
        metric_data = data[metric_columns].dropna()
        if len(metric_data) < 10:
            return causality
        
        # 分析滞后相关性
        max_lag = min(5, len(metric_data) // 2)
        for i, metric1 in enumerate(metric_columns):
            for j, metric2 in enumerate(metric_columns):
                if i != j:
                    lag_corrs = []
                    for lag in range(1, max_lag + 1):
                        try:
                            # 计算滞后相关性
                            series1 = metric_data[metric1].iloc[lag:]
                            series2 = metric_data[metric2].iloc[:-lag]
                            
                            if len(series1) > 0 and len(series2) > 0:
                                corr, p_value = pearsonr(series1, series2)
                                lag_corrs.append({
                                    'lag': lag,
                                    'correlation': corr,
                                    'p_value': p_value,
                                    'significant': p_value < 0.05
                                })
                        except:
                            pass
                    
                    if lag_corrs:
                        causality['lag_correlations'][f"{metric1}__{metric2}"] = lag_corrs
                        
                        # 识别最强的滞后相关性
                        significant_lags = [lag for lag in lag_corrs if lag['significant']]
                        if significant_lags:
                            best_lag = max(significant_lags, key=lambda x: abs(x['correlation']))
                            if abs(best_lag['correlation']) > 0.5:
                                causality['causal_chains'].append({
                                    'source': metric1,
                                    'target': metric2,
                                    'lag': best_lag['lag'],
                                    'correlation': best_lag['correlation'],
                                    'p_value': best_lag['p_value']
                                })
        
        # 构建因果图
        causality['causal_graph'] = self._build_causal_graph(causality['causal_chains'])
        
        return causality
    
    def _build_causal_graph(self, causal_chains: List[Dict]) -> nx.DiGraph:
        """构建因果图"""
        G = nx.DiGraph()
        
        for chain in causal_chains:
            source = chain['source']
            target = chain['target']
            weight = abs(chain['correlation'])
            
            G.add_edge(source, target, 
                      weight=weight,
                      correlation=chain['correlation'],
                      lag=chain['lag'],
                      p_value=chain['p_value'])
        
        return G
    
    def _generate_association_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成关联关系摘要"""
        summary = {
            'total_strong_correlations': len(results.get('correlations', {}).get('strong_correlations', [])),
            'total_strong_mi_relationships': len(results.get('mutual_info', {}).get('strong_relationships', [])),
            'total_strong_rules': len(results.get('association_rules', {}).get('strong_rules', [])),
            'total_causal_chains': len(results.get('causal_relationships', {}).get('causal_chains', [])),
            'key_insights': []
        }
        
        # 生成关键洞察
        insights = []
        
        # 相关性洞察
        strong_corrs = results.get('correlations', {}).get('strong_correlations', [])
        if strong_corrs:
            top_corr = max(strong_corrs, key=lambda x: abs(x['correlation']))
            insights.append(f"最强相关性: {top_corr['pair']} ({top_corr['method']}: {top_corr['correlation']:.3f})")
        
        # 互信息洞察
        strong_mi = results.get('mutual_info', {}).get('strong_relationships', [])
        if strong_mi:
            top_mi = max(strong_mi, key=lambda x: x['mi_score'])
            insights.append(f"最强互信息关系: {top_mi['source']} -> {top_mi['target']} (MI: {top_mi['mi_score']:.3f})")
        
        # 因果关系洞察
        causal_chains = results.get('causal_relationships', {}).get('causal_chains', [])
        if causal_chains:
            top_causal = max(causal_chains, key=lambda x: abs(x['correlation']))
            insights.append(f"最强因果关系: {top_causal['source']} -> {top_causal['target']} (滞后{top_causal['lag']}期, 相关性: {top_causal['correlation']:.3f})")
        
        summary['key_insights'] = insights
        
        return summary


class KPIAssociationAnomalyDetector:
    """基于关联关系的KPI异常检测器"""
    
    def __init__(self, association_miner: KPIAssociationMiner):
        """
        初始化基于关联关系的异常检测器
        
        Args:
            association_miner: 关联关系挖掘器
        """
        self.association_miner = association_miner
        self.baseline_associations = None
        self.detection_rules = []
        
    def build_baseline(self, data: pd.DataFrame, 
                      metric_columns: List[str]) -> Dict[str, Any]:
        """
        构建关联关系基线
        
        Args:
            data: 历史数据
            metric_columns: 指标列名列表
            
        Returns:
            基线关联关系
        """
        logger.info("构建关联关系基线...")
        
        # 发现历史关联关系
        baseline = self.association_miner.discover_associations(data, metric_columns)
        
        # 提取关键关联规则
        detection_rules = []
        
        # 1. 强相关性规则
        strong_corrs = baseline.get('correlations', {}).get('strong_correlations', [])
        for corr in strong_corrs:
            if abs(corr['correlation']) > 0.8:  # 非常强的相关性
                metric1, metric2 = corr['pair'].split('__')
                detection_rules.append({
                    'type': 'correlation',
                    'source': metric1,
                    'target': metric2,
                    'expected_correlation': corr['correlation'],
                    'threshold': 0.1,  # 允许的偏差
                    'method': corr['method']
                })
        
        # 2. 因果关系规则
        causal_chains = baseline.get('causal_relationships', {}).get('causal_chains', [])
        for chain in causal_chains:
            if abs(chain['correlation']) > 0.6:  # 强因果关系
                detection_rules.append({
                    'type': 'causality',
                    'source': chain['source'],
                    'target': chain['target'],
                    'expected_correlation': chain['correlation'],
                    'lag': chain['lag'],
                    'threshold': 0.15,
                    'p_value': chain['p_value']
                })
        
        self.baseline_associations = baseline
        self.detection_rules = detection_rules
        
        logger.info(f"构建了 {len(detection_rules)} 个检测规则")
        
        return {
            'baseline': baseline,
            'detection_rules': detection_rules
        }
    
    def detect_association_anomalies(self, current_data: pd.DataFrame,
                                   metric_columns: List[str]) -> Dict[str, Any]:
        """
        检测基于关联关系的异常
        
        Args:
            current_data: 当前数据
            metric_columns: 指标列名列表
            
        Returns:
            异常检测结果
        """
        if self.baseline_associations is None:
            raise ValueError("请先构建基线关联关系")
        
        logger.info("检测关联关系异常...")
        
        anomalies = {
            'correlation_anomalies': [],
            'causality_anomalies': [],
            'summary': {}
        }
        
        # 1. 检测相关性异常
        current_correlations = self.association_miner._analyze_correlations(
            current_data, metric_columns
        )
        
        for rule in self.detection_rules:
            if rule['type'] == 'correlation':
                source = rule['source']
                target = rule['target']
                expected_corr = rule['expected_correlation']
                threshold = rule['threshold']
                
                # 检查当前相关性
                current_corr_key = f"{source}__{target}"
                if current_corr_key in current_correlations['pearson']:
                    current_corr = current_correlations['pearson'][current_corr_key]['correlation']
                    deviation = abs(current_corr - expected_corr)
                    
                    if deviation > threshold:
                        anomalies['correlation_anomalies'].append({
                            'rule': rule,
                            'current_correlation': current_corr,
                            'expected_correlation': expected_corr,
                            'deviation': deviation,
                            'severity': 'high' if deviation > threshold * 2 else 'medium'
                        })
        
        # 2. 检测因果关系异常
        current_causality = self.association_miner._analyze_causality(
            current_data, metric_columns
        )
        
        for rule in self.detection_rules:
            if rule['type'] == 'causality':
                source = rule['source']
                target = rule['target']
                expected_corr = rule['expected_correlation']
                lag = rule['lag']
                threshold = rule['threshold']
                
                # 检查当前因果关系
                current_corr_key = f"{source}__{target}"
                if current_corr_key in current_causality['lag_correlations']:
                    lag_corrs = current_causality['lag_correlations'][current_corr_key]
                    current_lag_corr = None
                    
                    for lag_corr in lag_corrs:
                        if lag_corr['lag'] == lag:
                            current_lag_corr = lag_corr['correlation']
                            break
                    
                    if current_lag_corr is not None:
                        deviation = abs(current_lag_corr - expected_corr)
                        
                        if deviation > threshold:
                            anomalies['causality_anomalies'].append({
                                'rule': rule,
                                'current_correlation': current_lag_corr,
                                'expected_correlation': expected_corr,
                                'deviation': deviation,
                                'severity': 'high' if deviation > threshold * 2 else 'medium'
                            })
        
        # 生成摘要
        total_anomalies = (len(anomalies['correlation_anomalies']) + 
                          len(anomalies['causality_anomalies']))
        
        anomalies['summary'] = {
            'total_anomalies': total_anomalies,
            'correlation_anomalies': len(anomalies['correlation_anomalies']),
            'causality_anomalies': len(anomalies['causality_anomalies']),
            'high_severity': sum(1 for a in anomalies['correlation_anomalies'] + 
                                anomalies['causality_anomalies'] 
                                if a.get('severity') == 'high')
        }
        
        logger.info(f"检测到 {total_anomalies} 个关联关系异常")
        
        return anomalies
    
    def generate_anomaly_insights(self, anomalies: Dict[str, Any]) -> List[str]:
        """
        生成异常洞察
        
        Args:
            anomalies: 异常检测结果
            
        Returns:
            洞察列表
        """
        insights = []
        
        # 相关性异常洞察
        for anomaly in anomalies['correlation_anomalies']:
            rule = anomaly['rule']
            source = rule['source']
            target = rule['target']
            deviation = anomaly['deviation']
            
            if anomaly['current_correlation'] > anomaly['expected_correlation']:
                insights.append(f"指标 '{source}' 和 '{target}' 的相关性异常增强 "
                              f"(当前: {anomaly['current_correlation']:.3f}, "
                              f"预期: {anomaly['expected_correlation']:.3f}, "
                              f"偏差: {deviation:.3f})")
            else:
                insights.append(f"指标 '{source}' 和 '{target}' 的相关性异常减弱 "
                              f"(当前: {anomaly['current_correlation']:.3f}, "
                              f"预期: {anomaly['expected_correlation']:.3f}, "
                              f"偏差: {deviation:.3f})")
        
        # 因果关系异常洞察
        for anomaly in anomalies['causality_anomalies']:
            rule = anomaly['rule']
            source = rule['source']
            target = rule['target']
            lag = rule['lag']
            deviation = anomaly['deviation']
            
            if anomaly['current_correlation'] > anomaly['expected_correlation']:
                insights.append(f"指标 '{source}' 对 '{target}' 的因果影响异常增强 "
                              f"(滞后{lag}期, 当前: {anomaly['current_correlation']:.3f}, "
                              f"预期: {anomaly['expected_correlation']:.3f})")
            else:
                insights.append(f"指标 '{source}' 对 '{target}' 的因果影响异常减弱 "
                              f"(滞后{lag}期, 当前: {anomaly['current_correlation']:.3f}, "
                              f"预期: {anomaly['expected_correlation']:.3f})")
        
        return insights
