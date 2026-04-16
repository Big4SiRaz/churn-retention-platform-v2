# src/state_engine/user_state_builder.py

import pandas as pd

from src.simulation.latent_traits import LatentTraitGenerator
from src.config.config_loader import load_config

config = load_config()
latent_generator = LatentTraitGenerator(config)

def build_user_state_df(df):
    """
    Final assembly of user state DataFrame.
    """

    required_columns = [
        "msno",
        "risk_segment",
        "churn_probability",
        "cltv",
        "cltv_normalized",
        "priority_score",
        "priority_bucket",
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


def enrich_users_with_latent_traits(users_df):
    """
    Adds latent behavioral traits to user dataframe
    """

    trait_rows = []

    for _, row in users_df.iterrows():
        user_dict = row.to_dict()

        traits = latent_generator.generate_all_traits(user_dict)

        trait_rows.append(traits)

    traits_df = pd.DataFrame(trait_rows)

    # Combine with original data
    enriched_df = pd.concat(
        [users_df.reset_index(drop=True), traits_df],
        axis=1
    )

    return enriched_df

