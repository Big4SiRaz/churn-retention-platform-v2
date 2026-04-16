# src/state_engine/scoring.py

import numpy as np


def normalize_column(series):
    """
    Min-Max normalization with safety for constant columns.
    Output range: [0, 1]
    """
    min_val = series.min()
    max_val = series.max()

    # Avoid division by zero
    if max_val == min_val:
        return np.ones(len(series)) * 0.5

    return (series - min_val) / (max_val - min_val)


def compute_normalized_engagement(df):
    """
    Normalize engagement signal.
    Assumes engagement is already numeric or ordinal.
    """

    # If engagement is categorical → map first
    if df["engagement"].dtype == "object":
        engagement_map = {
            "Very Low": 1,
            "Low": 2,
            "Medium": 3,
            "High": 4,
            "Very High": 5
        }
        df["engagement_numeric"] = df["engagement"].map(engagement_map).fillna(3)
    else:
        df["engagement_numeric"] = df["engagement"]

    df["engagement_normalized"] = normalize_column(df["engagement_numeric"])

    return df


def compute_normalized_volatility(df):
    """
    Normalize volatility signal.
    """

    if df["volatility"].dtype == "object":
        volatility_map = {
            "Ultra Low": 1,
            "Low": 2,
            "Medium": 3,
            "High": 4,
            "Very High": 5
        }
        df["volatility_numeric"] = df["volatility"].map(volatility_map).fillna(3)
    else:
        df["volatility_numeric"] = df["volatility"]

    df["volatility_normalized"] = normalize_column(df["volatility_numeric"])

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