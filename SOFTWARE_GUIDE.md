# 🚂 IRCTC Tender Schedule Generator - Ekdam Desi / Dehati Guide (v3.2)

> **Pranaam Bhaiya!** Ye hai aapke IRCTC Tender Schedule Generator software (v3.2) ki poori kahani — ekdam aasan desi/dehati bhasha me, bina kisi bhabhka ke! 🚀

---

## 🌐 Live Website Access
* **Live Domain**: [https://irctc-schedule.duckdns.org](https://irctc-schedule.duckdns.org)
* **Security Password**: `Suhail_Apprentice`

---

## 🧐 Ye Software Kaho Toh Hai Kya?

Pehle kya hota tha? Tender ka schedule banane me ghanto lagte the — IRCTC ki website kholo, cookie-token copy karo, captcha bharo, ek-ek train search karo aur MS Word me haath se table banao. 

Ab ye sab jhanjhat **KHATAM**! Ye software bina kisi login, cookie ya captcha ke **IndiaRailInfo** se live train data khud khinch ke lata hai aur seconds me **ekdam chakachak MS Word (.docx) tender schedule file** ready karke de deta hai.

---

## ⚡ v3.2 Engine Ki Khas Superpowers (Naya Protection Auto-Bypass)

1. **Automatic JS Verification Challenge Solver**:
   * IndiaRailInfo ne cloud servers ko rokne ke liye jo naya Javascript verification guard (`iri-xsig`) lagaya tha, usko ye engine real-time decode karke automatically handshake pass kar leta hai (`0:5:2:1:8:1:1:0:{x_val}:{xsig}:0`).
   * Aapko browser me na cookie dalna padega, na koi code change karna padega!

2. **Multi-Stage Yahoo Slug Resolver**:
   * Naye Amrit Bharat / Special Trains (jaise `22363` / `22364`) ke liye multi-stage resolver search engine indexing se direct exact train ID slug decode kar leta hai.

3. **100% Verified Benchmark (8/8 Trains Pass)**:
   * Amrit Bharat, Vande Bharat, Rajdhani, Shatabdi, aur Festival Specials sab par 100% accuracy verify ho chuki hai!

---

## 🛠️ Pura System Kaise Kaam Karta Hai? (Step-by-Step)

### 1️⃣ Pehla Kadam: Train Pair Daalna ya Bulk PDF Upload Karna
- **Manual Tariqa**: Aap frontend page par UP Train (jaise `12601`) aur DOWN Train (jaise `12602`) daalo. Agar aap `12601-02` likhoge toh system apne aap samajh ke UP aur DOWN dono fill kar dega.
- **Bulk PDF Tariqa**: Agar aapke paas lamba-choura Tender PDF hai, toh sidhe **Drag & Drop** kardo! Software me laga **PyMuPDF / OCR Parser Engine** poore PDF ko chhan ke saare 5-digit train pairs automatic extract karke list me daal dega!

---

### 2️⃣ Doosra Kadam: Tender Schedule Ka Type Chunna & Validation
Har tender ka format alag hota hai, isliye aap 5 alag-alag types me se chun sakte ho:
1. **Normal (ETE Schedule)**: Standard 5-row wala schedule table.
2. **Sections Schedule**: Jisme dynamic section exclude karne wala input box milta hai. *(Mandatory: Excluded Sections fill karna zaroori hai!)*
3. **WCB Schedule**: Jisme niche `Coaches` (e.g. `20 Coaches`) ki extra row jud jati hai.
4. **TOD Schedule**: Jisme `UPTO <Date/Station>` daalne ke alag boxes aate hain. *(Mandatory: UPTO details fill karna zaroori hai!)*
5. **TOD+WCB Schedule**: TOD aur WCB dono ka zabardast combo!

> **🛡️ Strict Input Validation Guard**: TOD ya Sections select karne par agar aapne unke required textboxes (`UPTO Date` ya `Excluded Sections`) nahi bhare, toh system warning alert dega aur khali box par focus kar dega. Galat ya adhoora pair add nahi hone dega!

---

### 🔒 Khas Suraksha: Security Access Key (Un-bypassable Server Shield)
- Jaise hi aap **"Generate Word Document"** button dabaney jaoge, ek stylish **Security Access Modal** popup hoga.
- Document tabhi banega jab aap Security Key daaloge: **`Suhail_Apprentice`**
- **Inspect Element Protected**: Ye password frontend HTML/JS me saved **NAHI** hai! Password verification sidhe Python Backend Server (`backend/main.py`) me hoti hai.
- Galat password daalne par Python server **HTTP 401 Access Denied** bolkar block kar dega aur **kisi bhi halat me Word file nahi banne dega**!

---

### 3️⃣ Teesra Kadam: Live Terminal Stream Engine (Ekdam Live Magic!)
Password sahi daalne ke baad:
- Client-side fake logs nahi, balki **Real-Time Server-Sent Events (SSE)** chalu ho jata hai!
- Backend Python server par jo-jo live log chalega (jaise `🔍 Scraping 22363...`, `✅ Fetched Dhanbad - Coimbatore Amrit Bharat Express`, `✨ Table Built`), **wahi exact line frontend ke black terminal screen par live type hoke aayegi**!
- Terminal box apne aap **smooth bottom scroll** karega — aapko haath se scrollbar chhoone ki zarurat hi nahi padegi!

---

### 4️⃣ Chautha Kadam: Word Table Styling & End-of-Doc Service Table ("Jodi / Husband-Wife")
Backend engine python-docx ke zariye MS Word document taiyar karta hai:
- **Font & Size**: Poora document *Times New Roman* font me banega (Body cell: 13pt, Headers: 14pt Bold).
- **Full-Width & Centered**: Table 100% page width (`17.0cm`) par faila hoga aur **page ke bilkul CENTER me** align hoga (`WD_TABLE_ALIGNMENT.CENTER`). Right side me koi khali safed jagah nahi bachegi.
- **Bold Prefixes & Format**: Running Between me **`Ex- `**, **`Dep:- `**, **`Arr:- `** ekdam bold rangeen punctuation ke saath aayenge.
- **Exact Timings & Route**: Departure aur Arrival timings (`1610 hrs`, `1830 hrs`) aur origin/destination station codes 100% verified.
- **Accurate Running Days**: Daily, 1-day weekly (`01 DAY SAT`), 2-day weekly (`02 DAYS MON, FRI`), aur 6-day Shatabdi/Vande Bharat (`06 DAYS Ex-WED`) sabka exact frequency bitmask format me print hoga.
- **Train Pair Label**: `22363-64, DHN-CBE, Dhanbad - Coimbatore Amrit Bharat Express` format me station codes aur Clean Train Name ke beech perfect comma (`, `) aayega.
- **"Husband-Wife" Jodi Service Table**: Document ke bilkul last me har train pair ki ek 2x8 Kitchen Service table (`Day`, `Service`, `Station`, `Time`... `Nil`) **<u>Train no.22363-64</u>** heading ke saath jud jayegi!

---

### 5️⃣ Panchva Kadam: Instant Automatic File Download!
Jaise hi last table ban ke taiyar hoga:
- Server bolta hai `🎉 DOCUMENT GENERATION COMPLETED SUCCESSFULLY!`
- Browser aapke computer me **`IRCTC_Tender_Schedules.docx`** file automatic download kar deta hai.
- Sath hi kitne minutes ki mehanat bachi, uska **Stats Dashboard** (`stats.json`) bhi real-time update ho jata hai!

---

## ⚙️ Software Ke Andar Ke Main Kal-Purze (Architecture):

| Purza (Component) | File Location | Kya Kaam Karta Hai? |
| :--- | :--- | :--- |
| **Backend Engine** | `backend/main.py` | FastAPI server, IndiaRailInfo Scraper v3.2 (Challenge Solver & Slug Resolver), python-docx Generator, SSE Streamer & Security Guard |
| **Legacy IRCTC Engine** | `backend/legacy_irctc.py` | Standalone legacy IRCTC official JSON API module (Local testing ke liye) |
| **Frontend UI** | `frontend/index.html` | Modern Dark/Light Blue theme UI, Inputs, Password Modal, Live Terminal Stream Viewport |
| **Frontend Logic** | `frontend/app.js` | Dynamic Input Toggle, Validation Guard, Password Submission, ReadableStream SSE Log Consumer & Auto-Download |
| **Stats Engine** | `backend/stats.json` | Atomic thread-safe file me generated files aur saved time ka record rakhta hai |

---

## 🎯 Ek Line Me Bole Toh:

> **"Kahi koi login nahi karna, captcha nahi bharna... bas train number daalo ya PDF phenko, `Suhail_Apprentice` password daalo aur ekdam perfect, centered, formatted MS Word Tender Schedule ready!"** 🚀

*Handcrafted with ❤️ for P&T Department Personal Software!*
