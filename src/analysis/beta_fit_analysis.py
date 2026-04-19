import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import beta, kstest


# -------------------------
# LOAD DATA
# -------------------------
df = pd.read_csv("data/processed/user_state_output.csv")

# -------------------------
# FILTER ONLY VALID USERS
# -------------------------
df = df[df["status"] == "active"].copy()


# -------------------------
# EXPECTED DISTRIBUTIONS (FROM CONFIG)
# -------------------------
EXPECTED_PARAMS = {
    "price_sensitivity": (2, 5),
    "engagement_affinity": (5, 2)
}


# -------------------------
# ESTIMATE ALPHA, BETA
# -------------------------
def estimate_beta_params(data):

    data = data.dropna()

    mean = np.mean(data)
    var = np.var(data)

    if var == 0:
        return None, None

    alpha = mean * ((mean * (1 - mean) / var) - 1)
    beta_param = (1 - mean) * ((mean * (1 - mean) / var) - 1)

    return alpha, beta_param


# -------------------------
# KS TEST
# -------------------------
def perform_ks_test(data, alpha, beta_param):

    # Normalize to [0,1] just in case
    data = data[(data > 0) & (data < 1)]

    D, p_value = kstest(data, 'beta', args=(alpha, beta_param))

    return D, p_value


# -------------------------
# MAIN PLOT FUNCTION
# -------------------------
def plot_beta_fit(column_name):

    data = df[column_name].dropna()

    # Keep within (0,1)
    data = data[(data > 0) & (data < 1)]

    if len(data) == 0:
        print(f"Skipping {column_name} (no valid data)")
        return

    # -------------------------
    # Estimate parameters
    # -------------------------
    alpha, beta_param = estimate_beta_params(data)

    if alpha is None:
        print(f"Skipping {column_name} (zero variance)")
        return

    print(f"\n==============================")
    print(f"Column: {column_name}")

    print(f"Estimated Alpha: {alpha:.4f}")
    print(f"Estimated Beta : {beta_param:.4f}")

    # -------------------------
    # Compare with expected
    # -------------------------
    if column_name in EXPECTED_PARAMS:
        exp_alpha, exp_beta = EXPECTED_PARAMS[column_name]

        print(f"Expected Alpha: {exp_alpha}")
        print(f"Expected Beta : {exp_beta}")

        print(f"Alpha Diff: {alpha - exp_alpha:.4f}")
        print(f"Beta Diff : {beta_param - exp_beta:.4f}")

    # -------------------------
    # KS TEST
    # -------------------------
    D, p_value = perform_ks_test(data, alpha, beta_param)

    print(f"KS Statistic: {D:.4f}")
    print(f"P-value     : {p_value:.6f}")

    if p_value > 0.05:
        print("Fit Quality : GOOD (fail to reject)")
    else:
        print("Fit Quality : POOR (reject fit)")

    # -------------------------
    # PLOT
    # -------------------------
    plt.figure(figsize=(8, 5))

    plt.hist(data, bins=50, density=True, alpha=0.6, label="Actual Data")

    x = np.linspace(0, 1, 100)
    y = beta.pdf(x, alpha, beta_param)

    plt.plot(x, y, 'r-', linewidth=2, label="Fitted Beta")

    plt.title(f"Beta Fit: {column_name}")
    plt.legend()

    plt.show()


# -------------------------
# COLUMNS TO ANALYZE
# -------------------------
columns = [
    #"cltv_normalized",
    "volatility",
    "volatility_normalized",
    "engagement",
    "engagement_normalized"
    #"urgency",
    #"price_sensitivity",
    #"engagement_affinity"
]


# -------------------------
# RUN
# -------------------------
for col in columns:
    if col in df.columns:
        plot_beta_fit(col)
    else:
        print(f"{col} not found")



data = df["engagement"].dropna()

print("\n==== RAW ENGAGEMENT ANALYSIS ====")

print("\nBasic Stats:")
print(data.describe())

print("\nValue Counts (Top 10):")
print(data.value_counts().head(10))

print("\nZero Percentage:")
print((data == 0).mean())

print("\nUnique Values:")
print(data.nunique())

# Plot histogram
import matplotlib.pyplot as plt

plt.hist(data, bins=50)
plt.title("Raw Engagement Distribution")
plt.show()

# Log version
import numpy as np
log_data = np.log1p(data)

plt.hist(log_data, bins=50)
plt.title("Log(1 + Engagement)")
plt.show()