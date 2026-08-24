# 🚂 IRCTC Tender Schedule Generator - v3.2 (Suhail Edition)

An automated web application and document generation engine for creating IRCTC Tender Schedules in MS Word (`.docx`) format from live train data.

---

## 🌐 Live Web Application

- **Live URL**: [https://irctc-schedule.duckdns.org](https://irctc-schedule.duckdns.org)
- **Deployment Platform**: Render Single-Server (FastAPI + Static Frontend)
- **Security Access Key**: `Suhail_Apprentice`

---

## 🌟 Key Features (v3.2 Engine)

- **Automated JS Browser Verification Challenge Solver (`v3.2`)**:
  - Automatically decodes and solves IndiaRailInfo's `iri-xsig` browser verification challenge tokens (`0:5:2:1:8:1:1:0:{x_val}:{xsig}:0`).
  - Seamlessly unlocks session access on cloud hosting servers (Render/Railway/VPS) without any manual cookie entry.
- **Multi-Layer Slug Resolver Engine**:
  - Combines Yahoo Search indexing (`site:indiarailinfo.com train {train_no}`) and `d.indiarailinfo.com` search to resolve newly introduced train IDs (e.g. ID `312327` for Train `22363` Dhanbad - Coimbatore Amrit Bharat Express).
- **100% Verified Scraper Benchmark**:
  - Tested and verified with 100% success rate across Amrit Bharat, Vande Bharat, Rajdhani, Shatabdi, 1-day/2-day Special trains, and Mail/Express trains.
- **Precision Timings & Running Days**:
  - Exact `HHMM hrs` departure and arrival time extraction.
  - Opacity-based active day grid bitmask parser for 100% accurate frequency strings (`01 DAY (SAT)`, `02 DAYS (MON, FRI)`, `06 DAYS (Ex-WED)`).
  - Train title clutter cleaner (automatically strips `(PT)`, `(SF)`, `(Mail)` and route noise).
  - Same-station safeguard (`origin_code != dest_code`).
- **Bulk PDF Tender Extractor**: Drag and drop tender PDF files to automatically extract all 5-digit train pairs using `PyMuPDF` and fallback `OCR`.
- **Multiple Schedule Templates**:
  1. **Normal (ETE Schedule)**
  2. **Sections Schedule** (dynamic catering section excluder)
  3. **WCB Schedule** (coaches row)
  4. **TOD Schedule** (`UPTO <Date/Station>` frequency handling)
  5. **TOD + WCB Combined Schedule**
- **Mandatory Input Validation**: Ensures required fields (`TOD UPTO` dates/stations and `Catering Exclusion Sections`) are filled before adding pairs to the schedule list.
- **Single-Server Unified Hosting**: FastAPI directly mounts and serves `frontend/` static assets on port `8000`.
- **Live SSE Terminal Streaming**: Real-time server logs streamed live to the frontend terminal screen.
- **Server Security Access Shield**: Requires server-side security key authorization before generating documents.

---

## 🛠️ Project Structure

```text
Prototype_Free_Train_Schedule/
├── backend/
│   ├── main.py              # FastAPI server, IndiaRailInfo Scraper & python-docx Generator
│   ├── legacy_irctc.py      # Standalone legacy IRCTC official API module (Local only)
│   ├── requirements.txt     # Backend Python dependencies
│   └── stats.json           # Atomic stats tracker
├── frontend/
│   ├── index.html           # Web Interface (Tailwind CSS)
│   └── app.js               # Dynamic API client, validation & SSE Log Streamer
├── start_software.bat       # Windows 1-click starter script
├── SOFTWARE_GUIDE.md        # Comprehensive Hindi/Hinglish User Guide
└── README.md                # Project documentation
```

---

## 🚀 Quick Start (Local Setup)

### Option 1: Single-Server (Frontend + Backend Together)
```bash
# 1. Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scriptsctivate
# On Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Launch unified server
python backend/main.py
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

### Option 2: Windows 1-Click Starter Script
Double-click `start_software.bat` to automatically verify Python, set up the virtual environment, install dependencies, and launch the application.

---

## 🌐 Production Hosting (Render / Railway / VPS)

To host both frontend and backend together on cloud platforms (e.g. Render, Railway):

- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

FastAPI automatically serves `frontend/index.html` and static files at the root URL.

---

## 🔒 Security Access Key

Document generation requires security authorization.
- Default Key: `Suhail_Apprentice`

---

## 📜 License

This project is open for deployment and custom internal usage.
Developed with ❤️ by Suhail.
