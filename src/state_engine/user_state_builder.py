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


def enrich_users_with_latent_traits(df):

    trait_rows = []

    users = df.to_dict(orient="records")

    traits = [
        latent_generator.generate_all_traits(user)
        for user in users
]

    traits_df = pd.DataFrame(traits)

    return pd.concat([df.reset_index(drop=True), traits_df], axis=1)



def apply_channel_preference(df):

    results = [
    latent_generator.generate_channel_preference(row)
    for row in df.to_dict(orient="records")
    ]

    df["channel_probs"] = [x["channel_probs"] for x in results]
    df["channel_ev"] = [x["channel_ev"] for x in results]
    df["ranked_channels"] = [x["ranked_channels"] for x in results]
    df["best_channel"] = [x["best_channel"] for x in results]

    return df

