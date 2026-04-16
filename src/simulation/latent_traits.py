import numpy as np
import random


class LatentTraitGenerator:
    def __init__(self, config):
        """
        config: dict containing distribution configs
        """
        self.config = config["latent_traits"]

    # -------------------------
    # Core Sampling Functions
    # -------------------------

    def _sample_beta(self, alpha, beta):
        return np.random.beta(alpha, beta)

    def _sample_categorical(self, values, probs):
        return random.choices(values, weights=probs, k=1)[0]

    # -------------------------
    # Trait Generators
    # -------------------------

    def generate_price_sensitivity(self, user):
        cfg = self.config["price_sensitivity"]
        base = self._sample_beta(cfg["params"]["alpha"], cfg["params"]["beta"])

        # Weak correlation: lower CLTV → higher price sensitivity
        if user.get("cltv", 0) < 0.4:
            base += 0.1

        return float(np.clip(base, 0, 1))

    def generate_engagement_affinity(self, user):
        cfg = self.config["engagement_affinity"]
        base = self._sample_beta(cfg["params"]["alpha"], cfg["params"]["beta"])

        # Weak correlation: high engagement → higher affinity
        if user.get("engagement", 0) > 0.6:
            base += 0.1

        return float(np.clip(base, 0, 1))

    def generate_channel_preference(self, user):
        cfg = self.config["channel_preference"]

        values = cfg["values"]
        probs = cfg["probs"].copy()

        # Weak conditional shift
        if user.get("engagement", 0) > 0.6:
            # Increase push likelihood slightly
            probs = [probs[0], probs[1] + 0.1, probs[2]]

        # Normalize probabilities
        total = sum(probs)
        probs = [p / total for p in probs]

        return self._sample_categorical(values, probs)

    # -------------------------
    # Public API
    # -------------------------

    def generate_all_traits(self, user):
        return {
            "price_sensitivity": self.generate_price_sensitivity(user),
            "engagement_affinity": self.generate_engagement_affinity(user),
            "channel_preference": self.generate_channel_preference(user),
        }