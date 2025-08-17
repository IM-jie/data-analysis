"""
数据分析模块 - 核心分析器
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from loguru import logger


class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化数据分析器
        
        Args:
            config: 分析配置
        """
        self.config = config or {}
        self.scaler = StandardScaler()
    
    def analyze_distribution(self, df: pd.DataFrame, target_column: str = None) -> Dict[str, Any]:
        """
        分析数据分布情况
        
        Args:
            df: 数据DataFrame
            target_column: 目标列名，如果为None则自动选择第一个数值列
            
        Returns:
            分布分析结果
        """
        try:
            # 选择目标列
            if target_column is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) == 0:
                    raise ValueError("没有找到数值列")
                target_column = numeric_columns[0]
            
            data = df[target_column].dropna()
            
            # 基本统计信息
            stats_info = {
                'count': len(data),
                'mean': data.mean(),
                'std': data.std(),
                'min': data.min(),
                'max': data.max(),
                'median': data.median(),
                'q25': data.quantile(0.25),
                'q75': data.quantile(0.75),
                'skewness': data.skew(),
                'kurtosis': data.kurtosis()
            }
            
            # 分布类型检测
            distribution_type = self._detect_distribution(data)
            
            # 异常值检测
            outliers = self._detect_outliers_iqr(data)
            
            # 分位数信息
            percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
            percentile_values = {f'p{p}': data.quantile(p/100) for p in percentiles}
            
            result = {
                'target_column': target_column,
                'basic_stats': stats_info,
                'distribution_type': distribution_type,
                'outliers': {
                    'count': len(outliers),
                    'indices': outliers.index.tolist(),
                    'values': outliers.tolist()
                },
                'percentiles': percentile_values,
                'data_quality': {
                    'null_count': df[target_column].isnull().sum(),
                    'null_percentage': df[target_column].isnull().sum() / len(df) * 100,
                    'unique_count': df[target_column].nunique(),
                    'duplicate_count': df[target_column].duplicated().sum()
                }
            }
            
            logger.info(f"完成分布分析: {target_column}")
            return result
            
        except Exception as e:
            logger.error(f"分布分析失败: {e}")
            raise
    
    def analyze_trend(self, df: pd.DataFrame, date_column: str = None, value_column: str = None) -> Dict[str, Any]:
        """
        分析数据趋势
        
        Args:
            df: 数据DataFrame
            date_column: 日期列名
            value_column: 数值列名
            
        Returns:
            趋势分析结果
        """
        try:
            # 自动选择列
            if date_column is None:
                date_columns = df.select_dtypes(include=['datetime64']).columns
                if len(date_columns) == 0:
                    # 尝试转换字符串列为日期
                    for col in df.columns:
                        try:
                            df[col] = pd.to_datetime(df[col])
                            date_columns = [col]
                            break
                        except:
                            continue
                if len(date_columns) == 0:
                    raise ValueError("没有找到日期列")
                date_column = date_columns[0]
            
            if value_column is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) == 0:
                    raise ValueError("没有找到数值列")
                value_column = numeric_columns[0]
            
            # 确保数据按日期排序
            df_sorted = df.sort_values(date_column).copy()
            df_sorted = df_sorted[[date_column, value_column]].dropna()
            
            # 时间序列分解
            try:
                decomposition = seasonal_decompose(
                    df_sorted[value_column], 
                    period=min(30, len(df_sorted) // 4),  # 自适应周期
                    extrapolate_trend='freq'
                )
                
                trend = decomposition.trend
                seasonal = decomposition.seasonal
                residual = decomposition.resid
            except Exception as e:
                logger.warning(f"时间序列分解失败: {e}")
                trend = seasonal = residual = None
            
            # 趋势检测
            trend_direction = self._detect_trend_direction(df_sorted[value_column])
            
            # 移动平均
            window_sizes = [3, 7, 14, 30]
            moving_averages = {}
            for window in window_sizes:
                if len(df_sorted) >= window:
                    moving_averages[f'ma_{window}'] = df_sorted[value_column].rolling(window=window).mean().tolist()
            
            # 增长率计算
            growth_rates = self._calculate_growth_rates(df_sorted[value_column])
            
            # 季节性检测
            seasonality = self._detect_seasonality(df_sorted[value_column])
            
            result = {
                'date_column': date_column,
                'value_column': value_column,
                'trend_direction': trend_direction,
                'moving_averages': moving_averages,
                'growth_rates': growth_rates,
                'seasonality': seasonality,
                'decomposition': {
                    'trend': trend.tolist() if trend is not None else None,
                    'seasonal': seasonal.tolist() if seasonal is not None else None,
                    'residual': residual.tolist() if residual is not None else None
                },
                'data_points': len(df_sorted),
                'date_range': {
                    'start': df_sorted[date_column].min().isoformat(),
                    'end': df_sorted[date_column].max().isoformat(),
                    'total_days': (df_sorted[date_column].max() - df_sorted[date_column].min()).days
                }
            }
            
            logger.info(f"完成趋势分析: {value_column}")
            return result
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            raise
    
    def detect_anomalies(self, df: pd.DataFrame, target_column: str = None, method: str = 'isolation_forest') -> Dict[str, Any]:
        """
        异常检测
        
        Args:
            df: 数据DataFrame
            target_column: 目标列名
            method: 异常检测方法 ('isolation_forest', 'lof', 'zscore', 'iqr')
            
        Returns:
            异常检测结果
        """
        try:
            # 选择目标列
            if target_column is None:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                if len(numeric_columns) == 0:
                    raise ValueError("没有找到数值列")
                target_column = numeric_columns[0]
            
            data = df[target_column].dropna()
            
            if method == 'isolation_forest':
                anomalies = self._detect_anomalies_isolation_forest(data)
            elif method == 'lof':
                anomalies = self._detect_anomalies_lof(data)
            elif method == 'zscore':
                anomalies = self._detect_anomalies_zscore(data)
            elif method == 'iqr':
                anomalies = self._detect_anomalies_iqr(data)
            else:
                raise ValueError(f"不支持的异常检测方法: {method}")
            
            # 异常值统计
            anomaly_stats = {
                'total_points': len(data),
                'anomaly_count': len(anomalies),
                'anomaly_percentage': len(anomalies) / len(data) * 100,
                'normal_count': len(data) - len(anomalies)
            }
            
            # 异常值详细信息
            anomaly_details = []
            for idx in anomalies.index:
                anomaly_details.append({
                    'index': idx,
                    'value': data.loc[idx],
                    'timestamp': df.loc[idx].get('timestamp', None) if 'timestamp' in df.columns else None
                })
            
            result = {
                'target_column': target_column,
                'method': method,
                'anomaly_stats': anomaly_stats,
                'anomaly_indices': anomalies.index.tolist(),
                'anomaly_values': anomalies.tolist(),
                'anomaly_details': anomaly_details,
                'normal_data': data[~data.index.isin(anomalies.index)].tolist()
            }
            
            logger.info(f"完成异常检测: {target_column}, 方法: {method}, 异常点数量: {len(anomalies)}")
            return result
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            raise
    
    def _detect_distribution(self, data: pd.Series) -> str:
        """检测数据分布类型"""
        try:
            # 正态性检验
            _, p_value = stats.normaltest(data)
            
            if p_value > 0.05:
                return 'normal'
            elif data.skew() > 1:
                return 'right_skewed'
            elif data.skew() < -1:
                return 'left_skewed'
            else:
                return 'unknown'
        except:
            return 'unknown'
    
    def _detect_outliers_iqr(self, data: pd.Series) -> pd.Series:
        """使用IQR方法检测异常值"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return data[(data < lower_bound) | (data > upper_bound)]
    
    def _detect_trend_direction(self, data: pd.Series) -> str:
        """检测趋势方向"""
        if len(data) < 2:
            return 'insufficient_data'
        
        # 计算线性回归斜率
        x = np.arange(len(data))
        slope, _, _, _, _ = stats.linregress(x, data)
        
        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_growth_rates(self, data: pd.Series) -> Dict[str, float]:
        """计算增长率"""
        if len(data) < 2:
            return {}
        
        # 日增长率
        daily_growth = ((data.iloc[-1] - data.iloc[0]) / data.iloc[0]) * 100
        
        # 周增长率（如果有足够数据）
        weekly_growth = None
        if len(data) >= 7:
            weekly_growth = ((data.iloc[-1] - data.iloc[-7]) / data.iloc[-7]) * 100
        
        # 月增长率（如果有足够数据）
        monthly_growth = None
        if len(data) >= 30:
            monthly_growth = ((data.iloc[-1] - data.iloc[-30]) / data.iloc[-30]) * 100
        
        return {
            'daily_growth': daily_growth,
            'weekly_growth': weekly_growth,
            'monthly_growth': monthly_growth
        }
    
    def _detect_seasonality(self, data: pd.Series) -> Dict[str, Any]:
        """检测季节性"""
        if len(data) < 30:
            return {'has_seasonality': False, 'reason': 'insufficient_data'}
        
        try:
            # 使用自相关函数检测季节性
            acf = sm.tsa.acf(data.dropna(), nlags=min(30, len(data)//2))
            
            # 寻找峰值
            peaks = []
            for i in range(1, len(acf)-1):
                if acf[i] > acf[i-1] and acf[i] > acf[i+1] and acf[i] > 0.3:
                    peaks.append(i)
            
            if peaks:
                return {
                    'has_seasonality': True,
                    'seasonal_periods': peaks,
                    'strongest_period': peaks[np.argmax([acf[p] for p in peaks])]
                }
            else:
                return {'has_seasonality': False, 'reason': 'no_significant_peaks'}
                
        except Exception as e:
            return {'has_seasonality': False, 'reason': f'analysis_error: {str(e)}'}
    
    def _detect_anomalies_isolation_forest(self, data: pd.Series) -> pd.Series:
        """使用隔离森林检测异常值"""
        contamination = self.config.get('anomaly', {}).get('contamination', 0.1)
        
        # 重塑数据
        X = data.values.reshape(-1, 1)
        
        # 训练模型
        clf = IsolationForest(contamination=contamination, random_state=42)
        clf.fit(X)
        
        # 预测
        predictions = clf.predict(X)
        
        # 返回异常值（-1表示异常）
        return data[predictions == -1]
    
    def _detect_anomalies_lof(self, data: pd.Series) -> pd.Series:
        """使用局部异常因子检测异常值"""
        contamination = self.config.get('anomaly', {}).get('contamination', 0.1)
        
        # 重塑数据
        X = data.values.reshape(-1, 1)
        
        # 训练模型
        clf = LocalOutlierFactor(contamination=contamination)
        predictions = clf.fit_predict(X)
        
        # 返回异常值（-1表示异常）
        return data[predictions == -1]
    
    def _detect_anomalies_zscore(self, data: pd.Series) -> pd.Series:
        """使用Z-score检测异常值"""
        threshold = self.config.get('anomaly', {}).get('threshold', 3)
        
        z_scores = np.abs(stats.zscore(data))
        return data[z_scores > threshold]
    
    def _detect_anomalies_iqr(self, data: pd.Series) -> pd.Series:
        """使用IQR检测异常值"""
        return self._detect_outliers_iqr(data)
