# 🚂 IRCTC Tender Schedule Generator - Ekdam Desi / Dehati Guide 

> **Pranaam Bhaiya!** Ye hai aapke IRCTC Tender Schedule Generator software ki poori kahani — ekdam aasan desi/dehati bhasha me, bina kisi bhabhka ke! 🚀

---

## 🧐 Ye Software Kaho Toh Hai Kya?

Pehle kya hota tha? Tender ka schedule banane me ghanto lagte the — IRCTC ki website kholo, cookie-token copy karo, captcha bharo, ek-ek train search karo aur MS Word me haath se table banao. 

Ab ye sab jhanjhat **KHATAM**! Ye software bina kisi login, cookie ya captcha ke **IndiaRailInfo** se live train data khud khinch ke lata hai aur seconds me **ekdam chakachak MS Word (.docx) tender schedule file** ready karke de deta hai.

---

## 🛠️ Pura System Kaise Kaam Karta Hai? (Step-by-Step)

### 1️⃣ Pehla Kadam: Train Pair Daalna ya Bulk PDF Upload Karna
- **Manual Tariqa**: Aap frontend page par UP Train (jaise `12601`) aur DOWN Train (jaise `12602`) daalo. Agar aap `12601-02` likhoge toh system apne aap samajh ke UP aur DOWN dono fill kar dega.
- **Bulk PDF Tariqa**: Agar aapke paas lamba-choura Tender PDF hai, toh sidhe **Drag & Drop** kardo! Software me laga **PyMuPDF / OCR Parser Engine** poore PDF ko chhan ke saare 5-digit train pairs automatic extract karke list me daal dega!

---

### 2️⃣ Doosra Kadam: Tender Schedule Ka Type Chunna
Har tender ka format alag hota hai, isliye aap 5 alag-alag types me se chun sakte ho:
1. **Normal (ETE Schedule)**: Standard 5-row wala schedule table.
2. **Sections Schedule**: Jisme dynamic section exclude karne wala input box milta hai.
3. **WCB Schedule**: Jisme niche `Coaches` (e.g. `20 Coaches`) ki extra row jud jati hai.
4. **TOD Schedule**: Jisme `UPTO <Date>` daalne ke alag boxes aate hain aur frequency line me `UPTO` jud jata hai.
5. **TOD+WCB Schedule**: TOD aur WCB dono ka zabardast combo!

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
- Backend Python server par jo-jo live log chalega (jaise `🔍 Scraping 12601...`, `✅ Fetched MGR Chennai Central`, `✨ Table Built`), **wahi exact line frontend ke black terminal screen par live type hoke aayegi**!
- Terminal box apne aap **smooth bottom scroll** karega — aapko haath se scrollbar chhoone ki zarurat hi nahi padegi!

---

### 4️⃣ Chautha Kadam: Word Table Styling & End-of-Doc Service Table ("Jodi / Husband-Wife")
Backend engine python-docx ke zariye MS Word document taiyar karta hai:
- **Font & Size**: Poora document *Times New Roman* font me banega (Body cell: 13pt, Headers: 14pt Bold).
- **Full-Width & Centered**: Table 100% page width (`17.0cm`) par faila hoga aur **page ke bilkul CENTER me** align hoga (`WD_TABLE_ALIGNMENT.CENTER`). Right side me koi khali safed jagah nahi bachegi.
- **Bold Prefixes & Format**: Running Between me **`Ex- `**, **`Dep:- `**, **`Arr:- `** ekdam bold rangeen punctuation ke saath aayenge.
- **Train Pair Label**: `12604-05, CHZ-MS, Charlapalli` format me station codes aur Train Name ke beech perfect comma (`, `) aayega.
- **"Husband-Wife" Jodi Service Table**: Document ke bilkul last me har train pair ki ek 2x8 Kitchen Service table (`Day`, `Service`, `Station`, `Time`... `Nil`) **<u>Train no.12601-02</u>** heading ke saath jud jayegi!

---

### 5️⃣ Panchva Kadam: Instant Automatic File Download!
Jaise hi last table ban ke taiyar hoga:
- Server bolta hai `🎉 DOCUMENT GENERATION COMPLETED SUCCESSFULLY!`
- Browser aapke computer me **`IRCTC_Live_Schedules.docx`** file automatic download kar deta hai.
- Sath hi kitne minutes ki mehanat bachi, uska **Stats Dashboard** bhi update ho jata hai!

---

## ⚙️ Software Ke Andar Ke Main Kal-Purze (Architecture):

| Purza (Component) | File Location | Kya Kaam Karta Hai? |
| :--- | :--- | :--- |
| **Backend Engine** | `backend/main.py` | FastAPI server, IndiaRailInfo Scraper, python-docx Generator, SSE Real-time Streamer & Server Security Guard |
| **Frontend UI** | `frontend/index.html` | Modern Dark/Light Blue theme UI, Inputs, Password Modal, Live Terminal Stream Viewport |
| **Frontend Logic** | `frontend/app.js` | Dynamic Input Toggle, Password Submission, ReadableStream SSE Log Consumer & Auto-Download |
| **Stats Engine** | `backend/stats.json` | Atomic thread-safe file me generated files aur saved time ka record rakhta hai |

---

## 🎯 Ek Line Me Bole Toh:

> **"Kahi koi login nahi karna, captcha nahi bharna... bas train number daalo ya PDF phenko, `Suhail_Apprentice` password daalo aur ekdam perfect, centered, formatted MS Word Tender Schedule ready!"** 🚀

*Handcrafted with ❤️ for P&T Department Personal Software!*
