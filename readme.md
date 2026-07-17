# Insurance AI Copilot 🚗

Enterprise AI Assistant for Insurance CRM

## Project Overview

Insurance AI Copilot is a production-ready, enterprise-grade AI application foundation built with Python and Streamlit. It is designed to serve as the base platform for an intelligent insurance CRM assistant, providing a clean, modular, and scalable starting point for future feature development.

This repository currently contains the application foundation only — a configured Streamlit shell, session state management, and safe styling support — ready for enterprise-scale extension.

## Features

- Wide, enterprise-ready page layout with expanded sidebar
- Centralized session state initialization
- Safe, fail-tolerant CSS loading mechanism
- Professional startup loading experience
- Clean routing placeholder for future page architecture
- PEP8-compliant, type-hinted, modular codebase

## Architecture

The application follows a modular, function-based architecture within a single entry point, structured for straightforward extraction into a multi-page or service-oriented layout as the project scales:

- **Page Configuration Layer** — Streamlit page settings (title, icon, layout, sidebar state)
- **Session State Layer** — Centralized, idempotent session state initialization
- **Styling Layer** — Optional, safely-loaded external stylesheet
- **Presentation Layer** — Loading experience, home placeholder, and footer
- **Routing Layer** — Placeholder entry point for future page/router integration

## Folder Structure

```
insurance-ai-copilot/
├── app.py
├── requirements.txt
└── README.md
```

## Installation

**Prerequisites:** Python 3.11

```bash
# Clone the repository
git clone <repository-url>
cd insurance-ai-copilot

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Run Project

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`.

## Future Scope

- Multi-page navigation and routing implementation
- Authentication and role-based access control
- AI-powered customer and policy insights
- Claims triage and risk scoring modules
- Integration with CRM and policy management data sources
- Custom theming and enterprise branding via `assets/style.css`

## License

This project is licensed under the MIT License.