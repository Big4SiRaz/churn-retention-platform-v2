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
        # Eariler set as 0.4 but looking at beta distribution, it was too strong. Adjusting to 0.15 for a more subtle effect.
        if user.get("cltv_normalized", 0) < 0.15:
            base += 0.1
        elif user.get("cltv_normalized", 0) < 0.1:
            base += 0.03

        return float(np.clip(base, 0, 1))

    def generate_engagement_affinity(self, user):
        cfg = self.config["engagement_affinity"]
        base = self._sample_beta(cfg["params"]["alpha"], cfg["params"]["beta"])

        # Weak correlation: high engagement → higher affinity
        if user.get("engagement", 0) > 0.983333:
            base += 0.1
        elif user.get("engagement", 0) > 0.5:
            base += 0.05

        return float(np.clip(base, 0, 1))

    def generate_channel_preference(self, user):
            """
            Returns:
            - probabilities for each channel
            - expected value per channel
            - ranked channel preference
            """

            # -------------------------
            # STEP 1: BASE PROBABILITIES (can be modified per your diagram)
            # -------------------------
            email = 0.5
            push = 0.3
            call = 0.2

            engagement = user.get("engagement", 0) # Raw Enaggement due to better distribtuion Shape
            urgency = user.get("urgency", 0)
            volatility = user.get("volatility_normalized", 0)

            # -------------------------
            # STEP 2: APPLY RULES (ADJUST BASED ON YOUR DIAGRAM)
            # 👉 MODIFY THESE WEIGHTS AS PER YOUR DRAW.IO LOGIC
            # -------------------------

            # Engagement effect
            if engagement > 0.983333:
                push += 0.2
                email -= 0.1
                call -= 0.1

            # Urgency effect
            if urgency > 0.7:
                call += 0.25
                email -= 0.1
                push += 0.05
            else:
                email += 0.1
                call += 0.25
                push += 0.1

            # Volatility effect
            if volatility > 0.35:
                call -= 0.2  # avoid intrusive
                push -=0.1

            # -------------------------
            # STEP 3: SAFETY CLIP
            # -------------------------
            email = max(email, 0.05)
            push = max(push, 0.05)
            call = max(call, 0.05)

            # -------------------------
            # STEP 4: NORMALIZE
            # -------------------------
            total = email + push + call

            email_prob = email / total
            push_prob = push / total
            call_prob = call / total

            channel_probs = {
                "email": email_prob,
                "push": push_prob,
                "call": call_prob
            }

            # -------------------------
            # STEP 5: DEFINE CHANNEL IMPACT (UPLIFT)
            # 👉 These are business assumptions
            # -------------------------
            channel_impact = {
                "email": 0.05,
                "push": 0.15,
                "call": 0.25
            }

            # -------------------------
            # STEP 6: COMPUTE EXPECTED VALUE (EV)
            # -------------------------
            channel_ev = {}

            for ch in channel_probs:
                channel_ev[ch] = channel_probs[ch] * channel_impact[ch]

            # -------------------------
            # STEP 7: RANK CHANNELS (DESCENDING EV)
            # -------------------------
            ranked_channels = sorted(
                channel_ev.keys(),
                key=lambda x: channel_ev[x],
                reverse=True
            )

            # -------------------------
            # STEP 8: OUTPUT STRUCTURE
            # -------------------------
            return {
                "channel_probs": channel_probs,
                "channel_impact": channel_impact,
                "channel_ev": channel_ev,
                "ranked_channels": ranked_channels,
                "best_channel": ranked_channels[0]
            }
    

    # -------------------------
    # Public API
    # -------------------------

    def generate_all_traits(self, user):
        return {
            "price_sensitivity": self.generate_price_sensitivity(user),
            "engagement_affinity": self.generate_engagement_affinity(user),
            #"channel_preference": self.generate_channel_preference(user),
            #"channel_preference": self.apply_channel_preference(user)
        }