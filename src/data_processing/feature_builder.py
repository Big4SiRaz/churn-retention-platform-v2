import joblib

dist = joblib.load("src/config/distributions/distributions.pkl")
TIME_THRESH = dist["time_signal"]

def enrich_features(df):
    df["engagement"] = df.apply(compute_engagement, axis=1)
    df["volatility"] = df.apply(compute_volatility, axis=1)
    df["payment_status"] = df.apply(compute_payment_status, axis=1)

    return df


def compute_engagement(row):

    total_events = (
        row["recent_num_985"] +
        row["recent_num_100"] +
        row["recent_num_75"] +
        row["recent_num_50"] +
        row["recent_num_25"]
    )

    if total_events == 0:
        return 0

    completion_ratio = (
        row["recent_num_985"] +
        row["recent_num_100"] +
        row["recent_num_75"]
    ) / total_events

    # -------------------------------
    # CASE 1 — OLD rowS
    # -------------------------------
    if row["tenure_days"] >= 120:

        time_ratio = (
            row["recent_total_secs"] /
            max(1, (90 - row["remaining_days"]))
        ) / max(1, (row["mid_total_secs"] / 60))

        return 0.5 * completion_ratio + 0.5 * time_ratio

    # -------------------------------
    # CASE 2 — NEW rowS
    # -------------------------------
    else:

        raw_time = (
            row["recent_total_secs"] /
            max(1, (90 - row["remaining_days"]))
        )

        if raw_time == 0 :
            percentile_score = 0.0
        elif raw_time < TIME_THRESH[1]:
            percentile_score = 0.4
        elif raw_time < TIME_THRESH[2]:
            percentile_score = 0.6
        elif raw_time < TIME_THRESH[3]:
            percentile_score = 0.8
        else:
            percentile_score = 1.0

        return 0.8 * completion_ratio + 0.2 * percentile_score
    


def compute_volatility(row):

    total = (
        row["recent_num_985"] +
        row["recent_num_100"] +
        row["recent_num_75"] +
        row["recent_num_50"] +
        row["recent_num_25"]
    )

    if total == 0:
        return 0

    score = (
        0.2 * (row["recent_num_25"] / total) +
        0.2 * (row["recent_num_unq"] / total) +
        0.3 * (row["recent_num_25"] / max(1, (row["recent_num_985"] + row["recent_num_100"]))) +
        0.2 * (row["recent_num_unq"] / max(1, row["recent_num_100"])) +
        0.1 * ((row["recent_num_50"] + row["recent_num_75"]) / total)
    )

    return score


def compute_payment_status(row):
    if row["is_auto_renew"] == 0:
        if row["remaining_days"] > 10:
            return "Stable"
        elif row["remaining_days"] > 6 :
            return "Critical"
        else:
            return "At Risk"
        
    else:
        if row["remaining_days"] > 6:
            return "Stable"
        elif row["remaining_days"] > 3 :
            return "Critical"
        else:
            return "At Risk"