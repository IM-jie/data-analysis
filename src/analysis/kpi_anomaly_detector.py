"""
KPI异常检测分析器
支持多种异常检测算法和趋势分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from scipy import stats
from scipy.signal import savgol_filter
import warnings
from loguru import logger


class KPIAnomalyDetector:
    """KPI异常检测器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化异常检测器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.scaler = StandardScaler()
        self.models = {}
        
    def detect_anomalies(self, data: pd.DataFrame, method: str = 'isolation_forest', 
                        **kwargs) -> Dict[str, Any]:
        """
        检测异常值
        
        Args:
            data: 输入数据
            method: 异常检测方法
            **kwargs: 其他参数
            
        Returns:
            异常检测结果
        """
        if method == 'isolation_forest':
            return self._isolation_forest_detection(data, **kwargs)
        elif method == 'lof':
            return self._lof_detection(data, **kwargs)
        elif method == 'one_class_svm':
            return self._one_class_svm_detection(data, **kwargs)
        elif method == 'statistical':
            return self._statistical_detection(data, **kwargs)
        elif method == 'iqr':
            return self._iqr_detection(data, **kwargs)
        elif method == 'zscore':
            return self._zscore_detection(data, **kwargs)
        else:
            raise ValueError(f"不支持的异常检测方法: {method}")
    
    def _isolation_forest_detection(self, data: pd.DataFrame, 
                                   contamination: float = 0.1,
                                   random_state: int = 42) -> Dict[str, Any]:
        """Isolation Forest异常检测"""
        # 准备数据
        X = data.select_dtypes(include=[np.number]).fillna(0)
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'isolation_forest'}
        
        # 标准化数据
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        model.fit(X_scaled)
        
        # 预测异常
        predictions = model.predict(X_scaled)
        scores = model.score_samples(X_scaled)
        
        # 标记异常（-1为异常，1为正常）
        anomalies = predictions == -1
        
        return {
            'anomalies': anomalies.tolist(),
            'scores': scores.tolist(),
            'method': 'isolation_forest',
            'model': model
        }
    
    def _lof_detection(self, data: pd.DataFrame, 
                      contamination: float = 0.1,
                      n_neighbors: int = 20) -> Dict[str, Any]:
        """Local Outlier Factor异常检测"""
        X = data.select_dtypes(include=[np.number]).fillna(0)
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'lof'}
        
        X_scaled = self.scaler.fit_transform(X)
        
        model = LocalOutlierFactor(
            contamination=contamination,
            n_neighbors=n_neighbors
        )
        
        predictions = model.fit_predict(X_scaled)
        scores = model.negative_outlier_factor_
        
        anomalies = predictions == -1
        
        return {
            'anomalies': anomalies.tolist(),
            'scores': scores.tolist(),
            'method': 'lof',
            'model': model
        }
    
    def _one_class_svm_detection(self, data: pd.DataFrame,
                                nu: float = 0.1,
                                kernel: str = 'rbf') -> Dict[str, Any]:
        """One-Class SVM异常检测"""
        X = data.select_dtypes(include=[np.number]).fillna(0)
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'one_class_svm'}
        
        X_scaled = self.scaler.fit_transform(X)
        
        model = OneClassSVM(nu=nu, kernel=kernel)
        model.fit(X_scaled)
        
        predictions = model.predict(X_scaled)
        scores = model.score_samples(X_scaled)
        
        anomalies = predictions == -1
        
        return {
            'anomalies': anomalies.tolist(),
            'scores': scores.tolist(),
            'method': 'one_class_svm',
            'model': model
        }
    
    def _statistical_detection(self, data: pd.DataFrame,
                              threshold: float = 3.0) -> Dict[str, Any]:
        """统计方法异常检测（基于均值和标准差）"""
        X = data.select_dtypes(include=[np.number])
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'statistical'}
        
        anomalies = []
        scores = []
        
        for col in X.columns:
            col_data = X[col].dropna()
            if len(col_data) > 0:
                mean_val = col_data.mean()
                std_val = col_data.std()
                
                if std_val > 0:
                    z_scores = np.abs((col_data - mean_val) / std_val)
                    col_anomalies = z_scores > threshold
                    anomalies.extend(col_anomalies.tolist())
                    scores.extend(z_scores.tolist())
        
        return {
            'anomalies': anomalies,
            'scores': scores,
            'method': 'statistical'
        }
    
    def _iqr_detection(self, data: pd.DataFrame,
                      factor: float = 1.5) -> Dict[str, Any]:
        """IQR方法异常检测"""
        X = data.select_dtypes(include=[np.number])
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'iqr'}
        
        anomalies = []
        scores = []
        
        for col in X.columns:
            col_data = X[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - factor * IQR
                upper_bound = Q3 + factor * IQR
                
                col_anomalies = (col_data < lower_bound) | (col_data > upper_bound)
                anomalies.extend(col_anomalies.tolist())
                
                # 计算异常分数
                col_scores = np.where(col_anomalies, 
                                    np.abs(col_data - col_data.median()) / IQR,
                                    0)
                scores.extend(col_scores.tolist())
        
        return {
            'anomalies': anomalies,
            'scores': scores,
            'method': 'iqr'
        }
    
    def _zscore_detection(self, data: pd.DataFrame,
                         threshold: float = 3.0) -> Dict[str, Any]:
        """Z-score方法异常检测"""
        X = data.select_dtypes(include=[np.number])
        
        if X.empty:
            return {'anomalies': [], 'scores': [], 'method': 'zscore'}
        
        anomalies = []
        scores = []
        
        for col in X.columns:
            col_data = X[col].dropna()
            if len(col_data) > 0:
                z_scores = np.abs(stats.zscore(col_data))
                col_anomalies = z_scores > threshold
                anomalies.extend(col_anomalies.tolist())
                scores.extend(z_scores.tolist())
        
        return {
            'anomalies': anomalies,
            'scores': scores,
            'method': 'zscore'
        }


class KPITrendAnalyzer:
    """KPI趋势分析器"""
    
    def __init__(self):
        """初始化趋势分析器"""
        pass
    
    def analyze_trend(self, data: pd.DataFrame, 
                     time_column: str = 'quarter',
                     value_column: str = 'value',
                     window_size: int = 3) -> Dict[str, Any]:
        """
        分析时间序列趋势
        
        Args:
            data: 输入数据
            time_column: 时间列名
            value_column: 值列名
            window_size: 移动平均窗口大小
            
        Returns:
            趋势分析结果
        """
        # 确保数据按时间排序
        data_sorted = data.sort_values(time_column).copy()
        
        # 计算移动平均
        data_sorted['moving_average'] = data_sorted[value_column].rolling(
            window=window_size, min_periods=1
        ).mean()
        
        # 计算趋势斜率
        trend_slope = self._calculate_trend_slope(data_sorted, value_column)
        
        # 检测趋势变化点
        change_points = self._detect_change_points(data_sorted, value_column)
        
        # 计算季节性
        seasonality = self._detect_seasonality(data_sorted, value_column)
        
        # 计算波动性
        volatility = self._calculate_volatility(data_sorted, value_column)
        
        return {
            'trend_slope': trend_slope,
            'change_points': change_points,
            'seasonality': seasonality,
            'volatility': volatility,
            'moving_average': data_sorted['moving_average'].tolist(),
            'data': data_sorted
        }
    
    def _calculate_trend_slope(self, data: pd.DataFrame, 
                              value_column: str) -> float:
        """计算趋势斜率"""
        if len(data) < 2:
            return 0.0
        
        x = np.arange(len(data))
        y = data[value_column].values
        
        # 使用线性回归计算斜率
        slope, _, _, _, _ = stats.linregress(x, y)
        return slope
    
    def _detect_change_points(self, data: pd.DataFrame, 
                             value_column: str,
                             threshold: float = 0.1) -> List[int]:
        """检测趋势变化点"""
        values = data[value_column].values
        change_points = []
        
        for i in range(1, len(values) - 1):
            # 计算前后变化率
            prev_change = (values[i] - values[i-1]) / (values[i-1] + 1e-8)
            next_change = (values[i+1] - values[i]) / (values[i] + 1e-8)
            
            # 如果变化方向发生改变且幅度超过阈值
            if (prev_change * next_change < 0 and 
                abs(prev_change) > threshold and 
                abs(next_change) > threshold):
                change_points.append(i)
        
        return change_points
    
    def _detect_seasonality(self, data: pd.DataFrame, 
                           value_column: str) -> Dict[str, Any]:
        """检测季节性模式"""
        values = data[value_column].values
        
        if len(values) < 4:
            return {'has_seasonality': False, 'period': None, 'strength': 0.0}
        
        # 计算自相关
        autocorr = np.correlate(values, values, mode='full')
        autocorr = autocorr[len(autocorr)//2:]
        
        # 寻找周期性峰值
        peaks = []
        for i in range(1, len(autocorr) - 1):
            if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                peaks.append(i)
        
        if peaks:
            # 计算平均周期
            period = np.mean(peaks)
            strength = np.max(autocorr[peaks]) / autocorr[0]
            
            return {
                'has_seasonality': True,
                'period': period,
                'strength': strength,
                'peaks': peaks
            }
        else:
            return {'has_seasonality': False, 'period': None, 'strength': 0.0}
    
    def _calculate_volatility(self, data: pd.DataFrame, 
                             value_column: str) -> float:
        """计算波动性"""
        values = data[value_column].values
        return np.std(values)


class KPIComprehensiveAnalyzer:
    """KPI综合分析器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化综合分析器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.anomaly_detector = KPIAnomalyDetector(config)
        self.trend_analyzer = KPITrendAnalyzer()
    
    def analyze_kpi_data(self, data: pd.DataFrame,
                        department_column: str = '部门名称',
                        metric_columns: List[str] = None,
                        time_columns: List[str] = None) -> Dict[str, Any]:
        """
        综合分析KPI数据
        
        Args:
            data: KPI数据
            department_column: 部门列名
            metric_columns: 指标列名列表
            time_columns: 时间列名列表
            
        Returns:
            综合分析结果
        """
        results = {
            'summary': {},
            'anomalies': {},
            'trends': {},
            'recommendations': []
        }
        
        # 数据摘要
        results['summary'] = self._generate_summary(data, department_column, metric_columns)
        
        # 异常检测
        anomalies, anomaly_details = self._detect_all_anomalies(
            data, metric_columns, department_column, time_columns
        )
        results['anomalies'] = anomalies
        results['anomaly_details'] = anomaly_details
        
        # 趋势分析
        results['trends'] = self._analyze_all_trends(data, metric_columns, time_columns)
        
        # 生成建议
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _generate_summary(self, data: pd.DataFrame,
                         department_column: str,
                         metric_columns: List[str]) -> Dict[str, Any]:
        """生成数据摘要"""
        summary = {
            'total_departments': len(data),
            'total_metrics': len(metric_columns) if metric_columns else 0,
            'departments': data[department_column].unique().tolist(),
            'metrics': metric_columns or [],
            'data_quality': {}
        }
        
        # 数据质量评估
        for col in data.columns:
            if col != department_column:
                missing_pct = data[col].isna().sum() / len(data) * 100
                summary['data_quality'][col] = {
                    'missing_percentage': missing_pct,
                    'data_type': str(data[col].dtype)
                }
        
        return summary
    
    def _detect_all_anomalies(self, data: pd.DataFrame,
                             metric_columns: List[str],
                             department_column: Optional[str],
                             time_columns: Optional[List[str]]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """对所有指标进行异常检测，并返回明细"""
        anomalies: Dict[str, Any] = {}
        anomaly_details: List[Dict[str, Any]] = []

        for metric in metric_columns:
            if metric in data.columns:
                # 保留原索引，便于回溯到原行
                metric_series = data[metric]
                metric_data = metric_series.to_frame().dropna()

                if len(metric_data) > 0:
                    methods = ['isolation_forest', 'iqr', 'zscore']
                    metric_anomalies = {}

                    for method in methods:
                        try:
                            result = self.anomaly_detector.detect_anomalies(
                                metric_data, method=method
                            )
                            metric_anomalies[method] = result

                            # 生成明细
                            flags = result.get('anomalies', [])
                            scores = result.get('scores', [])
                            # 对齐索引
                            idx_list = list(metric_data.index)
                            for pos, is_anom in enumerate(flags):
                                if bool(is_anom):
                                    idx = idx_list[pos]
                                    row_no = int(idx) + 1 if isinstance(idx, (int, np.integer)) else None
                                    department = None
                                    if department_column and department_column in data.columns:
                                        try:
                                            department = data.at[idx, department_column]
                                        except Exception:
                                            department = None
                                    # 时间列（若存在），取第一个非空时间值组合展示
                                    time_value = None
                                    if time_columns:
                                        try:
                                            times = []
                                            for tcol in time_columns:
                                                if tcol in data.columns:
                                                    val = data.at[idx, tcol]
                                                    if pd.notna(val):
                                                        times.append(str(val))
                                            if times:
                                                time_value = ','.join(times[:3])  # 避免过长
                                        except Exception:
                                            time_value = None

                                    value = data.at[idx, metric] if metric in data.columns else None
                                    score = scores[pos] if pos < len(scores) else None
                                    detail = {
                                        'row': row_no,
                                        'index': idx,
                                        'department': department,
                                        'time': time_value,
                                        'metric': metric,
                                        'method': method,
                                        'value': float(value) if isinstance(value, (int, float, np.floating, np.integer)) and pd.notna(value) else value,
                                        'score': float(score) if isinstance(score, (int, float, np.floating, np.integer)) and score is not None else score
                                    }
                                    anomaly_details.append(detail)

                        except Exception as e:
                            logger.warning(f"异常检测失败 {metric} - {method}: {e}")

                    anomalies[metric] = metric_anomalies

        # 按严重程度排序（若有分数）
        def severity_key(d: Dict[str, Any]):
            sc = d.get('score')
            try:
                return -abs(float(sc)) if sc is not None else 0.0
            except Exception:
                return 0.0

        anomaly_details.sort(key=severity_key)

        return anomalies, anomaly_details
    
    def _analyze_all_trends(self, data: pd.DataFrame,
                           metric_columns: List[str],
                           time_columns: Optional[List[str]]) -> Dict[str, Any]:
        """分析所有指标的趋势"""
        trends = {}
        
        # 如果没有时间列，跳过趋势分析
        if not time_columns:
            logger.info("没有时间列，跳过趋势分析")
            return trends
        
        for metric in metric_columns:
            if metric in data.columns:
                # 创建时间序列数据
                trend_data = []
                for i, row in data.iterrows():
                    for time_col in time_columns:
                        if time_col in data.columns and pd.notna(row[time_col]):
                            trend_data.append({
                                'time': row[time_col],
                                'value': row[metric]
                            })
                
                if trend_data:
                    trend_df = pd.DataFrame(trend_data)
                    trend_df = trend_df.sort_values('time')
                    
                    try:
                        trend_result = self.trend_analyzer.analyze_trend(trend_df)
                        trends[metric] = trend_result
                    except Exception as e:
                        logger.warning(f"趋势分析失败 {metric}: {e}")
        
        return trends
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """基于分析结果生成建议"""
        recommendations = []
        
        # 基于异常检测的建议
        anomalies = results.get('anomalies', {})
        for metric, metric_anomalies in anomalies.items():
            for method, result in metric_anomalies.items():
                if result.get('anomalies'):
                    anomaly_count = sum(result['anomalies'])
                    if anomaly_count > 0:
                        recommendations.append(
                            f"指标 '{metric}' 检测到 {anomaly_count} 个异常值 "
                            f"(方法: {method})，建议进一步调查"
                        )
        
        # 基于趋势的建议
        trends = results.get('trends', {})
        for metric, trend_result in trends.items():
            slope = trend_result.get('trend_slope', 0)
            if abs(slope) > 0.1:  # 显著趋势
                direction = "上升" if slope > 0 else "下降"
                recommendations.append(
                    f"指标 '{metric}' 呈现显著{direction}趋势 "
                    f"(斜率: {slope:.3f})，建议关注"
                )
        
        # 基于数据质量的建议
        summary = results.get('summary', {})
        data_quality = summary.get('data_quality', {})
        for col, quality in data_quality.items():
            missing_pct = quality.get('missing_percentage', 0)
            if missing_pct > 20:  # 缺失值超过20%
                recommendations.append(
                    f"列 '{col}' 缺失值比例较高 ({missing_pct:.1f}%)，"
                    f"建议补充数据或调整数据收集流程"
                )
        
        return recommendations
