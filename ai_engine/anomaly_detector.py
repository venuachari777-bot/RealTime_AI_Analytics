import numpy as np
from sklearn.ensemble import IsolationForest

class TransactionAnomalyDetector:
    def __init__(self, contamination=0.08):
        """
        Unsupervised Anomaly Detection using Isolation Forest.
        Contamination: Expected proportion of outliers in the data.
        """
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        self.is_fitted = False
        self._warmup_baseline()

    def _warmup_baseline(self):
        """Train on an initial synthetic baseline of normal transactions."""
        # Typical normal distribution between ₹100 and ₹5,000
        normal_amounts = np.random.normal(loc=2000, scale=1200, size=(500, 1))
        normal_amounts = np.clip(normal_amounts, 50, 7000)
        
        # Add a few high value samples for contrast
        synthetic_spikes = np.random.uniform(40000, 95000, size=(25, 1))
        training_data = np.vstack([normal_amounts, synthetic_spikes])
        
        self.model.fit(training_data)
        self.is_fitted = True

    def predict_anomaly(self, amount, device):
        """
        Returns:
            is_anomaly (bool): True if flagged as fraud/anomaly
            risk_score (float): Anomaly severity score
        """
        feature = np.array([[amount]])
        # Isolation Forest outputs -1 for anomalies, 1 for normal
        prediction = self.model.predict(feature)[0]
        decision_score = self.model.decision_function(feature)[0]
        
        # Custom rule: Unknown_Proxy + high value gets prioritized
        heuristic_flag = (device == "Unknown_Proxy" and amount > 20000)
        
        is_anomaly = bool(prediction == -1 or heuristic_flag)
        risk_score = round(float(-decision_score), 3)  # Higher means more anomalous
        
        return is_anomaly, risk_score

if __name__ == "__main__":
    detector = TransactionAnomalyDetector()
    test_cases = [
        (450.0, "Mobile_Android"),
        (2300.0, "Web_Chrome"),
        (78500.0, "Unknown_Proxy")
    ]
    print("\n--- Model Test Cases ---")
    for amt, dev in test_cases:
        flagged, score = detector.predict_anomaly(amt, dev)
        print(f"Amount: ₹{amt:8.2f} | Device: {dev:15s} | Flagged: {flagged} | Risk Score: {score}")