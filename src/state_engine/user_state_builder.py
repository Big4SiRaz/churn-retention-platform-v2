# src/state_engine/user_state_builder.py

def build_user_state_df(df):
    """
    Final assembly of user state DataFrame.
    """

    required_columns = [
        "msno",
        "risk_segment",
        "churn_probability",
        "cltv",
        "priority_score",
        "engagement",
        "engagement_normalized",
        "volatility",
        "volatility_normalized",
        "recoverability",
        "payment_status",
        "urgency",
        "status"
    ]

    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    user_state_df = df[required_columns].copy()

    user_state_df = user_state_df.rename(columns={
        "risk_segment": "risk_level"
    })

    return user_state_df
