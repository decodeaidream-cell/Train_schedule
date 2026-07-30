# 🚂 IRCTC Tender Schedule Generator

An automated web application and document generation engine for creating IRCTC Tender Schedules in MS Word (`.docx`) format from live train data.

---

## 🌟 Key Features

- **No Manual Entry / No Cookies Needed**: Scrapes live train schedules automatically via `IndiaRailInfo`.
- **Bulk PDF Tender Extractor**: Drag and drop tender PDF files to automatically extract all 5-digit train pairs using `PyMuPDF` and fallback `OCR`.
- **Multiple Schedule Templates**:
  1. **Normal (ETE Schedule)**
  2. **Sections Schedule** (dynamic section excluder)
  3. **WCB Schedule** (coaches row)
  4. **TOD Schedule** (`UPTO <Date>` frequency handling)
  5. **TOD + WCB Combined Schedule**
- **Single-Server Deployment**: Backend (`FastAPI`) directly serves the frontend (`HTML/CSS/JS`) on port `8000`.
- **Live SSE Terminal Streaming**: Real-time server logs streamed to the frontend viewport.
- **Server Security Access Shield**: Requires security key authorization before generating documents.

---

## 🛠️ Project Structure

```text
Prototype_Free_Train_Schedule/
├── backend/
│   ├── main.py              # FastAPI server, IndiaRailInfo Scraper & python-docx Generator
│   ├── requirements.txt     # Backend Python dependencies
│   └── stats.json           # Atomic stats tracker
├── frontend/
│   ├── index.html           # Web Interface (Tailwind CSS)
│   └── app.js               # Dynamic API client & SSE Log Streamer
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
venv\Scripts\activate
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

To host both frontend and backend together on cloud platforms (e.g. Render, Railway, Heroku):

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
