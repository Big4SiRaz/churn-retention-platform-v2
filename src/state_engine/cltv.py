# src/state_engine/cltv.py

def compute_cltv(df, expected_extension_days):

    rate = df["total_amount_paid"] / df["tenure_days"].clip(lower=1)

    df["cltv"] = rate * (
        df["remaining_days"]
        + (1 - df["churn_probability"]) * expected_extension_days
    )

    return df
