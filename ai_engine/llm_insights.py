import os
import time
from dotenv import load_dotenv
from google import genai

# Load root .env
load_dotenv()

class SecurityInsightsGenerator:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ Warning: GEMINI_API_KEY not found in .env file.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    def _fallback_summary(self, flagged_transactions, total_volume, anomaly_count):
        """Rule-based analytical summary in case API experiences peak load (503)."""
        high_risk_cities = list(set([t.get("location", "Unknown") for t in flagged_transactions]))
        max_amount = max([t.get("amount", 0) for t in flagged_transactions]) if flagged_transactions else 0
        
        return f"""
[Offline Fallback Incident Briefing]
• Executive Risk Level: HIGH (Automated Metric Triggered)
• Observed Suspicious Patterns: Detected {anomaly_count} flagged spikes out of {total_volume} transactions. High-value transactions peaked at ₹{max_amount:,.2f} concentrated in: {', '.join(high_risk_cities)}.
• Recommended Immediate Action: Enable multi-factor authentication (MFA) challenge for transactions over ₹25,000 originating from proxy nodes.
"""

    def generate_incident_summary(self, flagged_transactions, total_volume, anomaly_count):
        """
        Attempts to generate insights via Gemini. 
        Retries on 503 overload; falls back cleanly if unreachable.
        """
        if not self.client:
            return "Gemini API key is not configured. Please add GEMINI_API_KEY to your .env file."

        prompt = f"""
You are a senior FinTech Fraud Analyst.
Analyze the following batch of live transaction metrics:

Total Transactions Monitored: {total_volume}
Anomalies / High-Risk Flagged: {anomaly_count}
Recent Suspicious Transactions: {flagged_transactions}

Provide a concise, professional security briefing containing:
1. Executive Risk Level (Low, Medium, High, or Critical)
2. Observed Suspicious Patterns (1-2 sentences on cities, device proxies, or amounts)
3. Recommended Immediate Action for the risk ops team (1-2 bullet points)

Keep your response direct, professional, and crisp.
"""
        # Retry up to 2 times with a slight delay
        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                err_str = str(e)
                if "503" in err_str:
                    time.sleep(2)
                    continue
                # If 404 or unsupported, attempt fallback to gemini-2.0-flash
                try:
                    alt_res = self.client.models.generate_content(
                        model="gemini-2.0-flash",
                        contents=prompt
                    )
                    if alt_res and alt_res.text:
                        return alt_res.text
                except Exception:
                    pass

        # Return clean rule-based summary if Google servers are under temporary maintenance
        return self._fallback_summary(flagged_transactions, total_volume, anomaly_count)

if __name__ == "__main__":
    sample_flagged = [
        {"transaction_id": "TXN_101", "amount": 78500.0, "location": "Delhi", "device": "Unknown_Proxy"},
        {"transaction_id": "TXN_102", "amount": 62000.0, "location": "Mumbai", "device": "Unknown_Proxy"}
    ]
    
    generator = SecurityInsightsGenerator()
    briefing = generator.generate_incident_summary(
        flagged_transactions=sample_flagged,
        total_volume=50,
        anomaly_count=2
    )
    print("\n--- AI Incident Briefing ---")
    print(briefing)