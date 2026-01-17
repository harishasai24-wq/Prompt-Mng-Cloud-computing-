# 🐆 RiseOfTheJaguar - AI-Assisted Prompt Management System

A full-stack web application for managing, versioning, and evaluating AI prompts using a rule-based evaluation engine with advanced text analytics.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Features

### Core Functionality
- **Prompt Management**: Create, read, update, and delete prompts with full CRUD operations
- **Version Control**: Automatic versioning with change tracking and version comparison
- **AI Evaluation**: Rule-based scoring for clarity, relevance, and length
- **Smart Recommendations**: Get best version recommendations based on evaluations
- **Tag System**: Organize prompts with custom color-coded tags
- **User Authentication**: Secure JWT-based authentication

### Advanced Analytics
- **Readability Analysis**: Flesch Reading Ease scores via TextStat
- **Sentiment Analysis**: Polarity and subjectivity detection via TextBlob
- **Real-time Feedback**: Quick evaluate feature for instant scoring

### Production-Ready Features
- **UI Error Guards**: Global error handlers prevent silent JavaScript crashes
- **Dependency Validation**: Automatic detection of missing script dependencies
- **Defensive Fallbacks**: Graceful degradation if utilities fail to load

## 📁 Project Structure

```
RiseOfTheJaguar/
├── backend/
│   ├── app.py              # Flask application (serves frontend too)
│   ├── config.py           # Configuration settings
│   ├── models.py           # SQLAlchemy ORM models
│   ├── ai_engine.py        # Rule-based AI evaluator + TextStat/TextBlob
│   ├── requirements.txt    # Python dependencies
│   └── routes/
│       ├── auth.py         # Authentication (login, register, profile)
│       ├── prompts.py      # Prompt CRUD + stats
│       ├── versions.py     # Version control with concurrency protection
│       ├── evaluation.py   # AI evaluation + recommendations
│       └── tags.py         # Tag management
├── frontend/
│   ├── index.html          # Login/Register page
│   ├── dashboard.html      # Dashboard with stats
│   ├── prompts.html        # Prompts management
│   ├── versions.html       # Version control UI
│   ├── evaluation.html     # AI evaluation interface
│   ├── css/styles.css      # Premium dark theme styles
│   └── js/
│       ├── sanitize.js     # XSS prevention utilities
│       ├── api.js          # API client with JWT handling
│       └── app.js          # UI utilities + error guards
└── database/
    └── prompt_management.db # SQLite database (auto-created)
```

## 🛠️ Quick Start

### Prerequisites
- Python 3.9+

### One-Command Setup

```bash
# Clone and setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install flask flask-cors flask-jwt-extended flask-sqlalchemy textstat textblob
python app.py init-db
python app.py seed  # Optional: adds demo data
python app.py
```

### Access the Application

**Open in browser: http://localhost:5001**

The Flask server serves both the API and frontend from the same origin (no CORS issues).

## 🔑 Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| `demo` | `demo123` | admin |

Or register a new account through the UI!

## 🔧 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/register` | User registration |
| GET | `/api/auth/me` | Get current user profile |
| PUT | `/api/auth/profile` | Update profile |
| POST | `/api/auth/change-password` | Change password |

### Prompts
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prompts` | List prompts (with filters) |
| POST | `/api/prompts` | Create prompt + initial version |
| GET | `/api/prompts/:id` | Get prompt with versions |
| PUT | `/api/prompts/:id` | Update prompt (auto-versions) |
| DELETE | `/api/prompts/:id` | Delete prompt |
| GET | `/api/prompts/stats` | Get statistics |

### Versions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/prompts/:id/versions` | List versions |
| GET | `/api/versions/:id` | Get version details |
| POST | `/api/versions/:id/set-current` | Set current version |
| DELETE | `/api/versions/:id` | Delete version |
| GET | `/api/versions/compare` | Compare two versions |

### Evaluation
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/evaluate/:version_id` | Evaluate and save |
| POST | `/api/evaluate/prompt/:id` | Evaluate all versions |
| GET | `/api/evaluations/:prompt_id` | Get evaluations |
| GET | `/api/evaluations/version/:id` | Get version evaluation |
| GET | `/api/recommend/:prompt_id` | Get best recommendation |
| POST | `/api/quick-evaluate` | Quick evaluate (no save) |

### Tags
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags` | List all tags |
| POST | `/api/tags` | Create tag |
| POST | `/api/tags/prompts/:id/tags` | Add tag to prompt |
| DELETE | `/api/tags/prompts/:id/tags/:tag_id` | Remove tag |

## 🧠 AI Evaluation Engine

The rule-based engine scores prompts on multiple dimensions:

### Clarity Score (40% weight)
- ✅ Rewards clear action verbs (create, analyze, summarize)
- ❌ Penalizes vague keywords (something, maybe, stuff)
- 📋 Checks for structured formatting (lists, numbers)

### Relevance Score (40% weight)
- 🎯 Matches domain-specific keywords per category
- ✓ Aligns with task type indicators
- 📤 Checks for output format specification

### Length Score (20% weight)
- ✅ Optimal: 15-150 words
- ⚠️ Penalizes: < 5 words or > 300 words

### Advanced Metrics
- 📖 **Readability**: Flesch Reading Ease + Grade Level
- 💭 **Sentiment**: Polarity (-1 to +1) and Subjectivity (0 to 1)

## 🎨 Design Features

- **Premium Dark Theme**: Glassmorphism with vibrant accents
- **Smooth Animations**: Micro-interactions and transitions
- **Fully Responsive**: Works on all device sizes
- **Accessible**: WCAG-compliant color contrast
- **XSS Protected**: All user content is sanitized

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:5001 | xargs kill -9
```

### CORS Errors
Access the app via `http://localhost:5001` (not `file://` protocol)

### Database Reset
```bash
rm database/prompt_management.db
python app.py init-db
python app.py seed
```

### Missing Dependencies
```bash
pip install flask flask-cors flask-jwt-extended flask-sqlalchemy textstat textblob
```

## 🐘 PostgreSQL (Production)

For production, use PostgreSQL instead of SQLite:

```bash
# Set environment variable
export DATABASE_URL="postgresql://user:pass@localhost:5432/prompt_management"

# Run as normal
python app.py init-db
python app.py
```

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask, SQLAlchemy, Flask-JWT-Extended |
| Frontend | Vanilla JS, CSS (no frameworks) |
| Database | SQLite (dev) / PostgreSQL (prod) |
| AI Engine | Rule-based + TextStat + TextBlob |
| Security | JWT, XSS sanitization, CORS |

## 📄 License

MIT License - RiseOfTheJaguar Project
