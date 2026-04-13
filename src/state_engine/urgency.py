# src/state_engine/urgency.py

import numpy as np


def compute_urgency(df):

    df["urgency"] = np.exp(-df["remaining_days"] / 30)

    df.loc[df["is_auto_renew"] == 1, "urgency"] *= 0.5

    return df
