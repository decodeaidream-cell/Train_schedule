# 🚂 IRCTC Tender Schedule Generator - v3.5 (Fail-Safe Dual-Engine Edition)

An automated high-speed web application and document generation engine for creating official IRCTC Tender Schedules in MS Word (`.docx`) format directly from live IndiaRailInfo data with an integrated **4,485-Train Offline Fail-Safe Master Database** and **Auto-Learning Engine**.

---

## 🌐 Live Web Application

- **Live Render URL**: [https://train-schedule-db7n.onrender.com](https://train-schedule-db7n.onrender.com)
- **Local URL**: `http://127.0.0.1:8000`
- **Deployment Platform**: Render Single-Server (FastAPI + Static Frontend)
- **Security Access Key**: `Suhail_Apprentice`

---

## ⚡ Key Features (v3.5 Engine)

- **Fail-Safe Dual-Engine Architecture (`v3.5`)**:
  - **Primary**: Live Multi-Node Scraper with dynamic CDN edge failover (`srv1`, `srv3`, `srv2`, `m`, `indiarailinfo.com`).
  - **Secondary (Zero-Downtime Backup)**: Automatic fallback to the built-in Master Dataset (`backend/all_india_train_pairs_master.json`) containing **4,485 trains** and **2,361 train pairs** across all 18 Railway Zones if internet or scraping fails.
- **🧠 Auto-Learning Engine**:
  - Whenever a new/unregistered train (e.g. newly launched Vande Bharat / Special train) is scraped live from online, the engine automatically and permanently appends it to `all_india_train_pairs_master.json` for future offline availability.
- **📢 Transparent Fallback Status & Warnings**:
  - If scraping fails and offline data is utilized, the system logs a transparent amber notice in both Render console and SSE terminal stream (`⚠️ [OFFLINE BACKUP] Online data nahi mila...`).
- **Inline Universal JS Challenge Verification Solver**:
  - Automatically detects and solves IndiaRailInfo's `data-sig` browser verification challenge tokens (`0:5:2:1:8:1:1:0:{x_val}:{xsig}:0`) across all endpoints.
  - Emulates desktop browser TLS behavior using **Chrome 124 TLS Fingerprinting** via `curl_cffi`.
- **Multistage Fallback Slug Resolver**:
  - Instant Master Cache Slug ➔ Direct Internal Autocomplete (`/shtml/list.shtml`) ➔ DuckDuckGo ➔ Yahoo Search Indexing.
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
- **Server Security Access Shield**: Requires server-side security key authorization before generating documents.

---

## 📁 Project Structure

```text
Prototype_Free_Train_Schedule/
├── backend/
│   ├── main.py                          # FastAPI Server, Scraper, Auto-Learner & docx Generator
│   ├── all_india_train_pairs_master.json# Master Dataset (4,485 Trains, 2,361 Pairs, 18 Zones)
│   ├── legacy_irctc.py                  # Standalone legacy IRCTC official API module
│   ├── requirements.txt                 # Backend Python dependencies
│   └── stats.json                       # Atomic generation stats tracker
├── frontend/
│   ├── index.html                       # Web Interface (Tailwind CSS + FontAwesome)
│   ├── app.js                           # Dynamic API client, validation & SSE Log Streamer
│   └── favicon.svg                      # Train icon favicon
├── test_cloud_simulation.py             # Standalone cloud execution simulation test suite
├── start_software.bat                   # Windows 1-click starter script
├── SOFTWARE_GUIDE.md                    # Comprehensive Hindi/Hinglish User Guide
└── README.md                            # Project documentation
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

To verify end-to-end scraper and document generator performance under cloud runtime constraints:
```bash
python test_cloud_simulation.py
```
