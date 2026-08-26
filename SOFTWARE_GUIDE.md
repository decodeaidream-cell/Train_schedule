# 🚂 IRCTC Tender Schedule Generator - Ekdam Desi / Dehati Guide (v3.5)

> **Pranaam Bhaiya!** Ye hai aapke IRCTC Tender Schedule Generator software (v3.5 - Fail-Safe Dual-Engine Edition) ki poori kahani — ekdam aasan desi/dehati bhasha me! 🚆✨

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

## ⚡ v3.5 Engine Ki Khas Superpowers (Fail-Safe Dual-Engine)

1. **Fail-Safe Dual-Engine (0% Downtime Guarantee)**:
   * **Primary Engine (Live Scraping)**: Direct IndiaRailInfo se live high-speed scraping (`srv1`, `srv3`, etc.).
   * **Secondary Engine (Offline Master Backup)**: Agar internet chala gaya ya website block hui, toh software rukega nahi! Backend me lage **4,485 Trains aur 2,361 Train Pairs** ke Master Database (`backend/all_india_train_pairs_master.json`) se data utha kar Word file ready kar dega!

2. **🧠 Auto-Learning Engine (Nayi Trains Khud Save Ho Jayengi)**:
   * Agar koi nayi Vande Bharat / Amrit Bharat ya Special train launch hui jo database me pehle nahi thi:
   * Software use online live scrape karega aur **hamesha ke liye offline database me auto-save kar dega!**

3. **📢 Transparent Fallback Warning**:
   * Agar online data na milne par offline backup use hota hai, toh software terminal aur logs me saaf amber warning show karega:
     `⚠️ [OFFLINE BACKUP] Online data nahi mila tha (Scraper failed) -> Train ka data Master Offline Database se liya gaya hai.`

4. **Inline Universal JS Verification Challenge Solver**:
   * IndiaRailInfo ke security token ko real-time auto-solve karke handshake pass karta hai.

5. **Real Chrome 124 TLS Fingerprinting**:
   * `curl_cffi` ke sath real desktop browser TLS fingerprint bhejta hai, jisse Render cloud server ko Cloudflare firewall block nahi karta.

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
