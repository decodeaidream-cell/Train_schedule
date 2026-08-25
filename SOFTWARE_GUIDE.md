# 🚂 IRCTC Tender Schedule Generator - Ekdam Desi / Dehati Guide (v3.3)

> **Pranaam Bhaiya!** Ye hai aapke IRCTC Tender Schedule Generator software (v3.3) ki poori kahani — ekdam aasan desi/dehati bhasha me, bina kisi bhabhka ke! 🚆✨

---

## 🌐 Live Website Access
* **Live Render Link**: [https://train-schedule-db7n.onrender.com](https://train-schedule-db7n.onrender.com)
* **Local Link**: `http://127.0.0.1:8000`
* **Security Password**: `Suhail_Apprentice`

---

## 💡 Ye Software Kaho Toh Hai Kya?

Pehle kya hota tha? Tender ka schedule banane me ghanto lagte the — IRCTC ki website kholo, cookie-token copy karo, captcha bharo, ek-ek train search karo aur MS Word me haath se table banao. 

Ab ye sab jhanjhat **KHATAM**! Ye software bina kisi login, cookie ya captcha ke **IndiaRailInfo** se live train data khud khinch ke lata hai aur seconds me **ekdam chakachak MS Word (.docx) tender schedule file** ready karke de deta hai.

---

## ⚡ v3.3 Engine Ki Khas Superpowers (Cloud Compatibility Fix)

1. **Dynamic Multi-Node CDN Failover Engine (`v3.3`)**:
   * IndiaRailInfo ke paas multiple server nodes hain (`srv1`, `srv3`, `srv2`, `m`, `indiarailinfo.com`).
   * Cloud ya Render par agar koi ek node block ya rate-limit hota hai, software automatically dusre unblocked node se connect kar leta hai. 100% 24/7 uptime!

2. **Inline Universal JS Verification Challenge Solver**:
   * IndiaRailInfo ke security guard (`iri-xsig` / `data-sig`) ko software real-time decode karke automatically handshake pass kar leta hai (`0:5:2:1:8:1:1:0:{x_val}:{xsig}:0`).
   * Root page ho, direct autocomplete API ho ya train page — har jagah verification auto-solve hoti hai.

3. **Real Chrome 124 TLS Fingerprinting**:
   * `curl_cffi` ke sath real desktop browser TLS fingerprint bhejta hai, jisse Render ke cloud server ko Cloudflare firewall block nahi karta.

4. **Real-Time Unbuffered `[RENDER LOG]` Stream**:
   * Render dashboard ke logs me har step (CDN Discovery, Slug Resolution, Station Parsing, Document Creation) crystal-clear live dikhta hai.

---

## 📋 Pura System Kaise Kaam Karta Hai? (Step-by-Step)

### 1️⃣ Pehla Kadam: Train Pair Daalna ya Bulk PDF Upload Karna
- **Manual Tariqa**: Aap frontend page par UP Train (jaise `22363`) aur DOWN Train (jaise `22364`) daalo. Agar aap `12601-02` likhoge toh system apne aap samajh ke UP aur DOWN dono fill kar dega.
- **Bulk PDF Tariqa**: Agar aapke paas lamba-choura Tender PDF hai, toh sidhe **Drag & Drop** kardo! Software me laga **PyMuPDF / OCR Parser Engine** poore PDF ko chhan ke saare 5-digit train pairs automatic extract karke list me daal dega!

---

### 2️⃣ Doosra Kadam: Tender Schedule Ka Type Chunna & Validation
Har tender ka format alag hota hai, isliye aap 5 alag-alag types me se chun sakte ho:
1. **Normal (ETE Schedule)**: Standard 5-row wala schedule table.
2. **Sections Schedule**: Jisme dynamic section exclude karne wala input box milta hai. *(Mandatory: Excluded Sections fill karna zaroori hai!)*
3. **WCB Schedule**: Jisme niche `Coaches` (e.g. `20 Coaches`) ki extra row jud jati hai.
4. **TOD Schedule**: Jisme `UPTO <Date/Station>` daalne ke alag boxes aate hain. *(Mandatory: UPTO details fill karna zaroori hai!)*
5. **TOD+WCB Schedule**: TOD aur WCB dono ka zabardast combo!

> **⚠️ Strict Input Validation Guard**: TOD ya Sections select karne par agar aapne unke required textboxes (`UPTO Date` ya `Excluded Sections`) nahi bhare, toh system warning alert dega aur khali box par focus kar dega. Galat ya adhoora pair add nahi hone dega!

---

### 3️⃣ Teesra Kadam: Document Generate Karna
- **"Generate Word Document"** button par click karo.
- Security Key poocha jaye toh daalo: **`Suhail_Apprentice`**
- Niche **Live Scraper Terminal Stream** me live process dikhega aur 2-3 second me **`IRCTC_Tender_Schedules.docx`** file download ho jayegi!

---

### 4️⃣ Word Document Me Kya-Kya Banega?
1. **Train No. & Name**: e.g., `22363-64, DHN-CBE, Dhanbad - Coimbatore Amrit Bharat Express`
2. **Frequency**: Running days ka accurate bitmask — `(DAILY)` ya `01 DAY (SAT)` ya `02 DAYS (MON, FRI)`.
3. **Running Between**: Origin, Departure Time, Destination, Arrival Time (`HHMM hrs` format).
4. **Smart Via**: Route ke important junction stations ka automatic sequence.
5. **Coaches Row**: WCB schedule ke liye (e.g., `20 Coaches`).
6. **End-of-Document Kitchen Service Table**: Document ke last me 8-column wala standardized service / catering table auto-append hota hai.

---

## 🧪 Cloud Simulation Test (Aapke PC Par Test Karna)

Agar aapko check karna hai ki Render cloud par code kaise execute hota hai, toh terminal me bas yeh command chalao:
```bash
python test_cloud_simulation.py
```
Yeh script automatically:
- Active CDN nodes check karegi
- 3 train pairs (`22363-64`, `12601-02`, `03639-03639`) live scrape karegi
- Word `.docx` file generate karke test report de degi!
