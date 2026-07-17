# 🚗 Insurance AI Copilot

**Enterprise AI Assistant for Insurance CRM**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Online-34d399?style=for-the-badge&logo=render)](https://insurance-ai-copilot.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

🔗 **[Try the Live App →](https://insurance-ai-copilot.onrender.com/)**

---

## 📖 Overview

**Insurance AI Copilot** is a production-ready, enterprise-grade CRM platform for the insurance industry, built entirely on Python and Streamlit. It brings together customer management, policy tracking, claims processing, real-time analytics, and a natural-language AI assistant into a single, modern, dark-themed dashboard — no external backend required.

Whether you're a policy administrator checking on renewals, a claims officer reviewing pending cases, or an executive scanning KPIs, the Copilot gives you a fast, glassmorphic interface backed by a rule-based AI engine that actually understands your data.

---

## ✨ Features

### 🏠 Enterprise Home Dashboard
- Live KPI summary (customers, active policies, renewals due, pending claims)
- AI-generated insights computed directly from your data — no hardcoded numbers
- Quick-action navigation to every module
- Recent activity feed (latest claims + upcoming renewals)
- Real-time system status panel

### 🤖 AI Copilot
- Natural-language Q&A over customers, policies, and claims
- Intent detection for renewal dates, premiums, claim status, and pending claims
- Automatic renewal-reminder email generation
- Conversational chat interface with typing indicators

### 📊 Analytics Dashboard
- Policy status distribution & claim status breakdown (Plotly charts)
- Renewal pipeline tracking
- Filterable, sortable data views

### 👥 Customer Management
- Full-text customer search
- Detailed customer profile cards (vehicle, contact, address)

### 📄 Policy Management
- Status-tagged policy tables (Active / Expired)
- Renewal date tracking with expiry alerts

### 📋 Claims Management
- Status-tagged claims tables (Approved / Pending / Rejected)
- Claim amount and reason tracking

### 🎨 Enterprise UI
- Dark navy glassmorphism theme, fully responsive
- Custom branded background & logo
- Consistent design system across every page

---

## 🏗️ Architecture
insurance-ai-copilot/
├── app.py                     # Application entry point / Home Page
├── requirements.txt
├── README.md
│
├── components/                # Reusable UI components
│   ├── init.py
│   ├── theme.py                # Shared theming (CSS, background, logo)
│   ├── sidebar.py               # Navigation sidebar
│   ├── cards.py                  # Glassmorphism info cards
│   ├── metrics.py                 # KPI metric cards
│   └── chatbot.py                  # AI chat UI
│
├── pages/                     # Multipage app screens (auto-routed by Streamlit)
│   ├── ai_copilot.py            # AI assistant chat page
│   ├── dashboard.py               # Analytics & charts
│   ├── customers.py                 # Customer search & profiles
│   ├── policies.py                    # Policy tracking
│   └── claims.py                        # Claims management
│
├── assets/                    # Branding & styling
│   ├── style.css
│   ├── background.png
│   └── logo.png
│
├── data/                      # CSV data sources
│   ├── customers.csv
│   ├── policies.csv
│   └── claims.csv
│
└── utils/                     # Core business logic
├── ai_engine.py             # Rule-based NLP intent engine
├── data_loader.py            # Cached CSV data access
├── email_generator.py         # Renewal email drafting
└── search.py                    # Fuzzy record search

**Design principles:**
- **Modular** — every page and component is self-contained and independently testable
- **Fail-safe** — missing assets or data never crash the app; everything degrades gracefully
- **Cached** — data loads and asset encoding are cached via `st.cache_data` for performance
- **Zero external AI dependency** — the Copilot's NLP engine is fully rule-based, no API key required to run core features

---

## 🚀 Live Demo

🔗 **[https://insurance-ai-copilot.onrender.com/](https://insurance-ai-copilot.onrender.com/)**

> Hosted on [Render](https://render.com). First load may take a few seconds if the instance is waking from sleep (free-tier cold start).

---

## 🛠️ Installation

**Prerequisites:** Python 3.11+

```bash
# 1. Clone the repository
git clone <repository-url>
cd insurance-ai-copilot

# 2. Create a virtual environment
python -m venv venv

# 3. Activate it
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

## ▶️ Run Locally

```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Streamlit](https://streamlit.io/) |
| Data Processing | [pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/) |
| Visualization | [Plotly](https://plotly.com/python/) |
| AI Engine | Custom rule-based NLP (no external API required) |
| Styling | Custom CSS — dark enterprise glassmorphism theme |
| Deployment | [Render](https://render.com) |

---

## 🗺️ Roadmap

- [ ] Authentication & role-based access control
- [ ] LLM-powered upgrade for the AI Copilot (optional OpenAI integration)
- [ ] Claims risk scoring & fraud detection
- [ ] Live CRM / policy system integrations
- [ ] Export reports to PDF/Excel
- [ ] Multi-tenant support

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ using Python + Streamlit</p>
