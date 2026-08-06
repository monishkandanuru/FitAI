# FitAI – AI Powered Fitness & Nutrition Coach

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Framework](https://img.shields.io/badge/framework-Flask_3.0+-emerald.svg)](https://flask.palletsprojects.com/)
[![Database](https://img.shields.io/badge/database-SQLite-cyan.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](#)

FitAI is a scalable, production-ready web application foundation for an AI-powered fitness and nutrition coaching platform. Built using Python 3.13, Flask application factory architecture, SQLite database readiness, and a dark glassmorphic responsive UI.

---

## 🌟 Key Highlights & Features

- **Modular Blueprint Architecture**: Uses Flask's Application Factory pattern (`create_app()`) to keep AI routing, database models, and utilities isolated.
- **Configurable Environments**: Pre-configured settings for `Development`, `Production`, and `Testing` with SQLite database integration.
- **Modern UI/UX**: Built with semantic HTML5, glassmorphism dark mode CSS3, and vanilla JavaScript (no heavyweight frontend framework overhead).
- **Live Health Monitoring**: Built-in `/health` API endpoint to monitor backend uptime, database connectivity status, and server latency.
- **Extensible Folder Structure**: Dedicated spaces for models, routes, utility helpers, generated PDF reports, and media uploads.

---

## 📁 Directory Structure

```text
FitAI/
│
├── app.py                # Main Flask application entrypoint & factory (create_app)
├── config.py             # Configuration classes (Development, Production, Testing)
├── requirements.txt      # Python dependencies list
├── README.md             # Project documentation & execution guide
│
├── templates/            # HTML5 Jinja2 Templates
│   ├── base.html         # Base template with glassmorphism layout & header/footer
│   └── index.html        # FitAI homepage with feature showcase & system audit
│
├── static/               # Static Frontend Assets
│   ├── css/
│   │   └── style.css     # CSS custom properties, grid system & animations
│   ├── js/
│   │   └── script.js     # Vanilla JS for health check polling & UI interactions
│   └── images/           # Static media assets directory
│
├── routes/               # Modular Flask Blueprints
│   ├── __init__.py
│   └── main.py           # Core routes ('/' homepage and '/health' endpoint)
│
├── models/               # SQLAlchemy Database Models (User, Workout, Nutrition)
│   └── __init__.py
│
├── utils/                # AI logic helpers, math calculators & image processing
│   └── __init__.py
│
├── reports/              # Storage directory for generated PDF/HTML reports
│   └── .gitkeep
│
└── uploads/              # Storage directory for user file/image uploads
    └── .gitkeep
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.13** or higher installed on your system.
- `pip` (Python package manager).

### 1. Clone or Open Project

Navigate to the project root directory:

```bash
cd FitAI
```

### 2. Create and Activate Virtual Environment

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

Or using Flask CLI:

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=5000
```

Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

---

## ⚙️ Configuration Settings

Environment variables can be customized in `config.py` or provided via `.env`:

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `FLASK_ENV` | `development` | Selects config class (`development`, `production`, `testing`) |
| `DATABASE_URL` | `sqlite:///fitai.db` | SQLite database URI |
| `SECRET_KEY` | `fitai-secret-key-...` | Flask session secret key |
| `PORT` | `5000` | Port for Flask web server |

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Renders the FitAI web homepage |
| `GET` | `/health` | Returns JSON status payload with server health & timestamp |

---

## 🔮 Roadmap & Planned AI Features

1. **🏋️ Workout Generation Blueprint**: LLM-driven exercise routine builder targeting specific muscle hypertrophy/endurance goals.
2. **🥗 Vision Meal Tracker**: Computer vision & multimodal AI endpoint to analyze meal photographs and calculate protein/carbs/fats.
3. **📊 Athletic Analytics Engine**: Historical progression tracking stored in SQLite with dynamic chart visualizations.
4. **🤖 Conversational Coach**: Interactive WebSocket/SSE assistant for real-time recovery advice.

---

## 📝 License

Distributed under the MIT License.
