# 🛡️ Real-Time AI Fraud & Risk Analytics Platform

An end-to-end real-time analytics streaming engine that monitors live payment transactions, flags anomalous/fraudulent behaviors using Unsupervised Machine Learning (Isolation Forest), and synthesizes automated incident briefings via Google Gemini AI.

---

## 🚀 Key Features
- **Live Transaction Streaming:** Generates and ingests synthetic high-frequency payment events.
- **Real-Time Anomaly Detection:** Applies Scikit-Learn's `Isolation Forest` with risk scoring to catch suspicious spikes and proxy transactions.
- **AI Executive Briefing:** Leverages the Gemini API to analyze flagged transaction batches and generate actionable incident mitigation steps.
- **Interactive Live Dashboard:** Built with Streamlit and Plotly to display real-time scatter plots, device distributions, KPIs, and live event tables.

---

## 🛠️ Tech Stack
- **Language:** Python
- **Machine Learning:** Scikit-Learn (Isolation Forest)
- **AI / LLM:** Google Gemini API (`gemini-3.8-flash` / fallback engine)
- **Visualization & UI:** Streamlit, Plotly Express
- **Data Engineering:** Streaming buffer pipelines, Pandas, NumPy

---

## 📂 Project Architecture

```text
RealTime_AI_Analytics/
├── ai_engine/
│   ├── anomaly_detector.py      # ML Isolation Forest scoring
│   └── llm_insights.py          # Gemini AI incident briefing generator
├── dashboard/
│   └── app.py                   # Streamlit live monitoring dashboard
├── data_pipeline/
│   └── producer.py              # Live high-frequency transaction stream generator
├── .env.example                 # Environment variable template
├── .gitignore                   # Ignores venv, local buffers, and secrets
├── requirements.txt             # Required Python libraries
└── README.md                    # Project documentation