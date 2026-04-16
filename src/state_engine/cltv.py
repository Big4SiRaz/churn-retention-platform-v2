# src/state_engine/cltv.py

import numpy as np
import pandas as pd

def compute_cltv(df, expected_extension_days):

    rate = df["total_amount_paid"] / df["tenure_days"].clip(lower=1)

    df["cltv"] = rate * (
        df["remaining_days"]
        + (1 - df["churn_probability"]) * expected_extension_days
    )

    cltv_log = np.log1p(df["cltv"])
    df["cltv_normalized"] = (cltv_log - cltv_log.min()) / (cltv_log.max() - cltv_log.min() + 1e-9)

    return df
