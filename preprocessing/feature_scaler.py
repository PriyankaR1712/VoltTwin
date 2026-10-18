
import numpy as np


class FeatureScaler:
    """Min-max scaler fitted on training data only."""

    def __init__(self):
        self.min_ = None
        self.max_ = None

    def fit(self, X):
        X = np.asarray(X, dtype=np.float32)

        if X.ndim != 2:
            raise ValueError("Expected a 2D array of shape (samples, features).")

        if X.shape[0] == 0:
            raise ValueError("Cannot fit the scaler on empty data.")

        if not np.isfinite(X).all():
            raise ValueError("Features contain NaN or infinite values.")

        self.min_ = X.min(axis=0)
        self.max_ = X.max(axis=0)
        return self

    def transform(self, X):
        if self.min_ is None or self.max_ is None:
            raise RuntimeError("Call fit() before transform().")

        X = np.asarray(X, dtype=np.float32)

        if X.ndim != 2 or X.shape[1] != len(self.min_):
            raise ValueError("Input feature count does not match the fitted scaler.")

        if not np.isfinite(X).all():
            raise ValueError("Features contain NaN or infinite values.")

        denominator = self.max_ - self.min_
        denominator = np.where(denominator == 0, 1.0, denominator)

        return (2.0 * (X - self.min_) / denominator - 1.0).astype(
            np.float32
        )

    def fit_transform(self, X):
        return self.fit(X).transform(X)
