import numpy as np
import pandas as pd
from scipy.stats import zscore
from outliers import smirnov_grubbs as grubbs

class Mine:
    def __init__(self, data:pd.Series):
        self.data = data
    def get_mean(self) -> float:
        return round(self.data.mean(), 2)
    def get_std(self) -> float:
        return round(self.data.std(), 2)
    def get_median(self) -> float:
        return round(self.data.median(), 2)
    def get_iqr(self) -> float:
        return round(self.data.quantile(0.75) - self.data.quantile(0.25), 2)
    def apply_iqr_rule(self, k:float = 1.5) -> pd.Series:
        q1 = self.data.quantile(0.25)
        q3 = self.data.quantile(0.75)
        return (self.data < q1-k*self.get_iqr()) | (self.data > q3+k*self.get_iqr())
    def apply_zscore(self, threshold:float = 3, ddof:int = 1) -> pd.Series:
        return np.abs(zscore(self.data, ddof=ddof)) > threshold
    def apply_ma_distance(self, window:int = 7, distance_bound:float = 0.3) -> pd.Series:
        MIN_PERIODS = 1
        moving_avg = self.data.shift(1).rolling(window=window, min_periods=MIN_PERIODS).mean()
        moving_avg_denominator = moving_avg.replace(0, np.nan)
        distance = np.abs((self.data - moving_avg)) / moving_avg_denominator
        return (distance > distance_bound).fillna(False)
    def apply_grubbs(self, alpha:float = 0.05) -> pd.Series:
        if len(self.data) < 3:
            return pd.Series(False, index=self.data.index)
        inliers = grubbs.test(self.data, alpha=alpha)
        return ~self.data.isin(inliers)