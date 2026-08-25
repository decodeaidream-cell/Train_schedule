# 🚂 IRCTC Tender Schedule Generator - v3.3 (Suhail Edition)

An automated high-speed web application and document generation engine for creating official IRCTC Tender Schedules in MS Word (`.docx`) format directly from live IndiaRailInfo data without requiring cookies, tokens, or captchas.

---

## 🌐 Live Web Application

- **Live Render URL**: [https://train-schedule-db7n.onrender.com](https://train-schedule-db7n.onrender.com)
- **Local URL**: `http://127.0.0.1:8000`
- **Deployment Platform**: Render Single-Server (FastAPI + Static Frontend)
- **Security Access Key**: `Suhail_Apprentice`

---

## ⚡ Key Features (v3.3 Engine)

- **Dynamic Multi-Node CDN Failover Engine (`v3.3`)**:
  - Automatically probes and connects to active unblocked IndiaRailInfo CDN edge nodes (`srv1.indiarailinfo.com`, `srv3.indiarailinfo.com`, `srv2.indiarailinfo.com`, `m.indiarailinfo.com`, `indiarailinfo.com`).
  - Guarantees 100% cloud uptime even if specific edge nodes are throttled or geo-restricted by Cloudflare.
- **Inline Universal JS Challenge Verification Solver**:
  - Automatically detects and solves IndiaRailInfo's `data-sig` browser verification challenge tokens (`0:5:2:1:8:1:1:0:{x_val}:{xsig}:0`) across all endpoints (Root, `list.shtml`, and `/train/{id}`).
  - Emulates real desktop browser behavior using **Chrome 124 TLS Fingerprinting** via `curl_cffi`.
- **Zero-Dependency Direct Internal Autocomplete API**:
  - Instant slug ID resolution via `/shtml/list.shtml?LappGetTrainList/{train_no}/0/0/0` in < 0.3s without relying on third-party search engines.
- **Unbuffered Real-Time `[RENDER LOG]` Stream**:
  - Live console diagnostics in the Render dashboard and SSE frontend terminal showing exact node connections, challenge resolution, HTTP status codes, and document generation metrics.
- **Precision Timings & Running Days**:
  - Exact `HHMM hrs` departure and arrival time extraction.
  - Opacity-based active day grid bitmask parser for 100% accurate frequency strings (`01 DAY (SAT)`, `02 DAYS (MON, FRI)`, `(DAILY)`).
  - Train title clutter cleaner (automatically strips `(PT)`, `(SF)`, `(Mail)` and route noise).
  - Same-station safeguard (`origin_code != dest_code`).
- **Bulk PDF Tender Extractor**: Drag and drop tender PDF files to automatically extract all 5-digit train pairs using `PyMuPDF` with fallback `OCR`.
- **Multiple Schedule Templates**:
  1. **Normal (ETE Schedule)**
  2. **Sections Schedule** (dynamic catering section excluder)
  3. **WCB Schedule** (coaches row)
  4. **TOD Schedule** (`UPTO <Date/Station>` frequency handling)
  5. **TOD + WCB Combined Schedule**
- **Mandatory Input Validation**: Ensures required fields (`TOD UPTO` dates/stations and `Catering Exclusion Sections`) are filled before adding pairs.
- **Single-Server Unified Hosting**: FastAPI directly mounts and serves `frontend/` static assets on port `8000` or Render `$PORT`.
- **Server Security Access Shield**: Requires server-side security key authorization before generating documents.

---

## 📁 Project Structure

```text
Prototype_Free_Train_Schedule/
├── backend/
│   ├── main.py              # FastAPI server, Multi-Node IndiaRailInfo Scraper & python-docx Generator
│   ├── legacy_irctc.py      # Standalone legacy IRCTC official API module (Local reference)
│   ├── requirements.txt     # Backend Python dependencies
│   └── stats.json           # Atomic stats tracker
├── frontend/
│   ├── index.html           # Web Interface (Tailwind CSS + FontAwesome)
│   ├── app.js               # Dynamic API client, validation & SSE Log Streamer
│   └── favicon.svg          # Train icon favicon
├── test_cloud_simulation.py # Standalone cloud execution simulation test suite
├── start_software.bat       # Windows 1-click starter script
├── SOFTWARE_GUIDE.md        # Comprehensive Hindi/Hinglish User Guide
└── README.md                # Project documentation
```

---

## 🚀 Running Locally

1. **Prerequisites**: Python 3.10+ installed.
2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Start the Server**:
   Double click `start_software.bat` or run:
   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
4. **Open in Browser**:
   Visit `http://127.0.0.1:8000`

---

## 🧪 Cloud Simulation Testing

To verify end-to-end scraper and document generator performance under cloud runtime constraints, run:
```bash
python test_cloud_simulation.py
```
This tests:
- Active CDN discovery
- Challenge verification token solver
- 3 real train pairs (`22363-64`, `12601-02`, `03639-03639`)
- Word `.docx` table construction and file generation
