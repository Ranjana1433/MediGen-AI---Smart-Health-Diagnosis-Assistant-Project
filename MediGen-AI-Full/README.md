# MediGen AI — Smart Health Diagnosis Assistant

An AI + Machine Learning based smart health diagnosis assistant with
**Gmail login (User/Admin roles)**, **voice input/output**, **medicine &
treatment guidance**, **doctor appointment booking**, and **interactive
charts** — built with **FastAPI**, **scikit-learn**, and **Generative AI**.

## Features

- 🔐 **Login & Signup with Gmail** — sign up as a **User** or an **Admin**; Users see only their own history, Admins see everyone's
- 🎤 **Voice input** — click the mic and speak your symptoms; they're matched automatically (Web Speech API)
- 🔊 **Voice output** — "Listen to explanation" reads the AI's answer aloud (Speech Synthesis)
- 🧠 **ML-based disease prediction** using a trained **Random Forest** model
- 🤖 **Generative AI explanation** of every diagnosis (OpenAI GPT, with an automatic offline fallback if no API key is set)
- 💊 **Medicine & treatment guidance** (ilaaj) — common OTC/medicine categories per condition, clearly marked as educational only
- 🩺 **Recommended specialist** per predicted condition (e.g. Cardiologist, Neurologist)
- 📅 **Doctor appointment booking** — pick a doctor/specialty, date, and time slot; view and cancel your upcoming appointments
- ⚠️ Confidence score + severity level (Mild / Moderate / Severe) + top-3 alternative predictions
- 📊 **Interactive charts** (Chart.js) — confidence bar chart per diagnosis, and a severity-breakdown doughnut chart across your history
- 🗂️ Diagnosis history and appointments stored per-user in a local SQLite database
- 🎨 Custom-designed, responsive web frontend (HTML/CSS/JS) — not a generic template
- 📖 REST API (FastAPI) with interactive Swagger docs at `/docs`

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI + Uvicorn |
| ML | Scikit-learn (Random Forest), Pandas, NumPy |
| Generative AI | OpenAI GPT API (gpt-4o-mini) with rule-based fallback |
| Voice | Web Speech API (SpeechRecognition + SpeechSynthesis) — built into the browser, no extra install |
| Charts | Chart.js (via CDN) |
| Auth | SQLite + salted SHA-256 password hashing + server-side session tokens, Gmail-only + role (User/Admin) |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript (custom design, Fraunces + Inter typefaces) |
| Model storage | Joblib |

## Project Structure

```
smart-health-diagnosis-assistant/
├── backend/
│   ├── main.py                     # FastAPI app, routes, auth-protected endpoints
│   ├── auth.py                     # Gmail login/signup/session + role logic
│   ├── database.py                 # Per-user diagnosis history + appointments storage
│   ├── requirements.txt
│   ├── .env.example                # Copy to .env to add your OpenAI key (optional)
│   ├── model/
│   │   ├── generate_dataset.py     # Creates the synthetic training dataset
│   │   ├── dataset.csv             # Symptom-disease training data (pre-generated)
│   │   ├── train_model.py          # Trains & saves the ML model
│   │   ├── disease_model.pkl       # Pre-trained model (already included)
│   │   ├── symptoms.pkl            # Symptom list used by the model
│   │   ├── disease_info.py         # Severity + specialist + precautions + medicines reference data
│   │   └── doctors.py              # Doctor roster used for appointment booking
│   └── genai/
│       └── generative_assistant.py # Generative AI explanation layer
└── frontend/
    ├── login.html                  # Sign in / create account page (Gmail + role)
    ├── auth.js                     # Login/signup logic
    ├── index.html                  # Main dashboard: symptom checker + appointments (protected)
    ├── script.js                   # Symptom picker, voice, diagnosis, charts, history, appointments
    └── style.css                   # Full custom design system
```

## How to Run in VS Code

### 1. Open the folder
Open the `smart-health-diagnosis-assistant` folder in VS Code.

### 2. Create a virtual environment (recommended)

```bash
cd backend
python -m venv venv
```

Activate it:
- **Windows (cmd):** `venv\Scripts\activate`
- **Windows (PowerShell):** `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` then `venv\Scripts\Activate.ps1`
- **Mac/Linux:** `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Enable real Generative AI
The app already works out of the box using a built-in fallback explanation
generator. To use real OpenAI GPT-generated explanations instead, copy
`.env.example` to `.env` and add `OPENAI_API_KEY=sk-xxxxxxxx`.

### 5. Run the server

```bash
uvicorn main:app --reload
```

### 6. Open the app
Go to **http://127.0.0.1:8000** — you'll land on the **login page** first.
Click "Create account", enter a Gmail address (`yourname@gmail.com`),
choose **User** or **Admin**, then sign in. You'll be taken to the
symptom-checker + appointments dashboard.

Voice input needs microphone permission and works best in Chrome/Edge.

API docs: **http://127.0.0.1:8000/docs**

## API Endpoints

| Method | Endpoint | Auth required | Description |
|---|---|---|---|
| POST | `/api/register` | No | Create a new account (Gmail + password + role) |
| POST | `/api/login` | No | Log in, returns a session token + role |
| POST | `/api/logout` | No | Invalidate a session token |
| GET | `/api/symptoms` | No | List all known symptoms |
| POST | `/api/diagnose` | Yes (Bearer token) | Predict disease from symptoms + return AI explanation, medicines, precautions, specialist |
| GET | `/api/history` | Yes (Bearer token) | Get diagnosis history (own for User, everyone's for Admin) |
| GET | `/api/doctors` | No | List doctor roster, optionally filtered by specialty |
| POST | `/api/appointments` | Yes (Bearer token) | Book an appointment with a doctor |
| GET | `/api/appointments` | Yes (Bearer token) | Get appointments (own for User, everyone's for Admin) |
| DELETE | `/api/appointments/{id}` | Yes (Bearer token) | Cancel your own appointment |

## Disclaimer

This project is built for **academic/educational purposes only**. It
provides preliminary, AI-generated suggestions and must **not** be used as
a substitute for professional medical diagnosis, prescription, or treatment.
Medicine names listed are general OTC categories, not dosage advice. The
doctor roster and appointment booking are simulated for demonstration.

## Possible Future Enhancements (for report/viva)

- Multi-language voice input (Hindi/English)
- PDF report generation for each diagnosis / appointment confirmation
- Email/SMS appointment reminders
- Deployment on AWS/Render with Docker
- Password reset via email
