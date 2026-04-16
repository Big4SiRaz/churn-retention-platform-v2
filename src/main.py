# src/main.py

import pandas as pd

pd.set_option('display.float_format', '{:.8f}'.format)

from src.data_processing.feature_builder import enrich_features
from src.state_engine.cltv import compute_cltv
from src.state_engine.urgency import compute_urgency
from src.state_engine.scoring import (
    compute_normalized_engagement,
    compute_normalized_volatility,
    compute_recoverability,
    compute_priority,
    assign_priority_buckets,
)
from src.state_engine.user_state_builder import build_user_state_df, enrich_users_with_latent_traits



def main():

    # =========================
    # LOAD DATA
    # =========================
    df = pd.read_csv("data/processed/membersTransactionsUserAggregated.csv")

    # =========================
    # FILTER VALID USERS EARLY
    # =========================
    valid_mask = (df["remaining_days"] > 0) & (df["remaining_days"] != 999)

    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    EXPECTED_EXTENSION = 60

    # =========================
    # VALID USERS PIPELINE
    # =========================
    if not valid_df.empty:

        valid_df = enrich_features(valid_df)

        valid_df = compute_cltv(valid_df, EXPECTED_EXTENSION)
        valid_df = compute_urgency(valid_df)

        # 🔥 NEW NORMALIZATION FLOW
        valid_df = compute_normalized_engagement(valid_df)
        valid_df = compute_normalized_volatility(valid_df)

        valid_df = compute_recoverability(valid_df)
        valid_df = compute_priority(valid_df)
        valid_df = assign_priority_buckets(valid_df)

        valid_df["status"] = "active"

    # =========================
    # INVALID USERS
    # =========================
    if not invalid_df.empty:

        invalid_df["cltv"] = 0
        invalid_df["cltv_normalized"] = 0
        invalid_df["urgency"] = 0
        invalid_df["priority_score"] = 0
        invalid_df["engagement_normalized"] = 0
        invalid_df["engagement"] = 0
        invalid_df["volatility_normalized"] = 0
        invalid_df["volatility"] = 0
        invalid_df["priority_bucket"] = "NA"
        invalid_df["recoverability"] = 0
        invalid_df["status"] = "inactive"

    # =========================
    # MERGE BACK
    # =========================
    final_df = pd.concat([valid_df, invalid_df], axis=0)

    # =========================
    # FINAL USER STATE
    # =========================
    user_state_df = build_user_state_df(final_df)
    user_state_df = enrich_users_with_latent_traits(user_state_df)

    # print(user_state_df.columns)


    # Save Output 
    user_state_df.to_csv("data/processed/user_state_output.csv", index=False, float_format='%.8f')
    

    # print(user_state_df.head())


if __name__ == "__main__":
    main()
