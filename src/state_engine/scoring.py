# src/state_engine/scoring.py

import numpy as np


def robust_minmax_scale(series, lower_q=0.01, upper_q=0.99):
    """
    Scales data to [0,1] while preserving distribution shape
    and avoiding outliers.
    """

    lower = series.quantile(lower_q)
    upper = series.quantile(upper_q)

    scaled = (series - lower) / (upper - lower)

    return scaled.clip(0, 1)


# Sigmoid explicitly not required now - so following function not useful.
def sigmoid_transform(x, k=5, center=0.5):
    """
    x: input in [0,1]
    k: steepness (higher = sharper curve)
    center: midpoint shift
    """
    return 1 / (1 + np.exp(-k * (x - center)))


# Normalization function explicitly not required now - so following function not useful.
def normalize_column(series):
    """
    Min-Max normalization with safety for constant columns.
    Output range: [0, 1]

    -----> Not using due to outliers and skewness in engagement & volatility. Instead, we'll use a more robust approach in the future (e.g., quantile-based normalization or log transformation).
    
    min_val = series.min()
    max_val = series.max()

    # Avoid division by zero
    if max_val == min_val:
        return np.ones(len(series)) * 0.5

    return (series - min_val) / (max_val - min_val)
    """
    series = np.log1p(series)
    return series.rank(pct=True)



def compute_normalized_engagement(df):
    """
    Normalize engagement signal.
    Assumes engagement is already numeric or ordinal.
    

    # Step 1: log transform (handle skew)
    df["engagement_log"] = np.log1p(df["engagement"])

    # Step 2: percentile normalization
    df["engagement_pct"] = df["engagement_log"].rank(pct=True)

    # Step 3: sigmoid shaping (push more values upward)
    df["engagement_normalized"] = sigmoid_transform(
        df["engagement_pct"],
        k=5,          # steepness
        center=0.4    # shift left → more high values
    )   

    # Not Useful now
    # df["engagement_normalized"] = normalize_column(df["engagement_numeric"])
    """

    df["engagement_normalized"] = robust_minmax_scale(df["engagement"])

    return df


def compute_normalized_volatility(df):
    """
    Normalize volatility signal.
    
    
    # Step 1: log transform
    df["volatility_log"] = np.log1p(df["volatility"])

    # Step 2: percentile
    df["volatility_pct"] = df["volatility_log"].rank(pct=True)

    # Step 3: sigmoid shaping (push values downward)
    df["volatility_normalized"] = sigmoid_transform(
        df["volatility_pct"],
        k=5,
        center=0.6    # shift right → more low values
    )

    # Not Useful now
    # df["volatility_normalized"] = normalize_column(df["volatility_numeric"])
    """

    df["volatility_normalized"] = robust_minmax_scale(df["volatility"])

    return df


def compute_recoverability(df):
    """
    Recoverability based on normalized signals
    """
    # To account for cases where engagement & volatility might be zero, we can add a small constant to ensure non-zero values.
    engagement_adj = df["engagement_normalized"].where(
        df["engagement_normalized"] != 0, 0.0005
    )

    volatility_adj = df["volatility_normalized"].where(
        df["volatility_normalized"] != 0, 0.9995
    )

    df["recoverability"] = engagement_adj * (1 - volatility_adj)

    return df


def compute_priority(df, alpha=0.7, beta=1.5, delta=1.3):
    """
    beta → churn importance
    delta → urgency importance
    alpha → CLTV influence
    """

    df = df.copy()
    df['priority_score'] = (
        (df['churn_probability'] ** beta) *
        (df['urgency'] ** delta) *
        (1 + alpha * df['cltv_normalized'])
    )


    return df

def assign_priority_buckets(df):
    df = df.copy()

    df['priority_percentile'] = df['priority_score'].rank(pct=True)

    conditions = [
        df['priority_percentile'] >= 0.9,
        df['priority_percentile'] >= 0.7,
    ]

    choices = ['P0', 'P1']
    df['priority_bucket'] = np.select(conditions, choices, default='P2')

    return df