"""
================================================================================
  IRCTC Schedule Generator - Suhail Edition v2.0 (Unlimited)
  Backend: FastAPI
  Source : IRCTC Official JSON API
  Output : IRCTC_Tender_Schedules.docx

  IRCTC Flow per train:
    GET /trnscheduleenquiry/{train_no} -> JSON Schedule
================================================================================
"""

import os
import sys
import re
import asyncio
import io

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
except Exception:
    pass
import json
import uuid
import time
import tempfile
from typing import List, Optional, Tuple

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pdfplumber

from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Global lazy OCR reader (loads ~300MB model on first use, then cached in RAM)
_ocr_reader = None

def _get_ocr_reader():
    """Lazily initialise easyocr.Reader once and reuse across requests."""
    global _ocr_reader
    if _ocr_reader is None:
        print("[OCR] Loading easyocr model (first-time only, please wait)...")
        import easyocr
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
        print("[OCR] Model loaded.")
    return _ocr_reader


# ==============================================================================
# SECTION 1 - CONFIG & APP SETUP
# ==============================================================================

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
SCRAPE_DELAY = 2.0    # seconds between train requests

_SUFFIX_RE = re.compile(r"\s*\([A-Z]{2,4}\)\s*$", re.IGNORECASE)
_DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]

app = FastAPI(title="IRCTC Schedule Generator - Suhail Edition v2.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# PEHLE DATA YAHN SE AATA THA (LEGACY CODE - IRCTC OFFICIAL API)
# ==============================================================================
# [PURANA TARIQA]: Pehle train data official IRCTC JSON API se aata tha.
# Isme terminal me har baar IRCTC Cookie aur GREQ Token manually daalna padta tha.
# Aapke kehne par is purane code ko niche comment kar diya gaya hai reference ke liye:
#
# print("\n==================================================")
# print("IRCTC AUTHENTICATION SETUP")
# print("==================================================")
# IRCTC_COOKIE = input("[AUTH] Paste IRCTC Cookie: ").strip()
# IRCTC_GREQ = input("[AUTH] Paste IRCTC greq token: ").strip()
# print("==================================================\n")
#
# IRCTC_HEADERS = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#     "cookie": IRCTC_COOKIE,
#     "greq": IRCTC_GREQ,
#     "bmirak": "webbm"
# }
#
# def fetch_train_irctc(train_no: str, headers: dict) -> Optional[dict]:
#     """Fetch train schedule from IRCTC Official JSON API."""
#     url = f"https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/{train_no}"
#     try:
#         response = requests.get(url, headers=headers, verify=False, timeout=15)
#         data = response.json()
#         days_bitmask = "".join([
#             "1" if data.get("trainRunsOnMon") == "Y" else "0",
#             "1" if data.get("trainRunsOnTue") == "Y" else "0",
#             "1" if data.get("trainRunsOnWed") == "Y" else "0",
#             "1" if data.get("trainRunsOnThu") == "Y" else "0",
#             "1" if data.get("trainRunsOnFri") == "Y" else "0",
#             "1" if data.get("trainRunsOnSat") == "Y" else "0",
#             "1" if data.get("trainRunsOnSun") == "Y" else "0",
#         ])
#         stations = data.get("stationList", [])
#         if len(stations) < 2: return None
#         origin, dest = stations[0], stations[-1]
#         return {
#             "train_number": str(data.get("trainNumber", train_no)),
#             "train_name": str(data.get("trainName", f"TRAIN {train_no}")),
#             "origin_code": str(data.get("stationFrom", origin.get("stationCode"))),
#             "dest_code": str(data.get("stationTo", dest.get("stationCode"))),
#             "dep_time": _normalise_time(origin.get("departureTime", "")),
#             "arr_time": _normalise_time(dest.get("arrivalTime", "")),
#             "run_days": _format_run_days(days_bitmask),
#             "station_codes": [stn.get("stationCode", "") for stn in stations],
#         }
#     except Exception as e:
#         return None
# ==============================================================================


# ==============================================================================
# AB DATA YAHN SE AA RAHA HAI (ACTIVE CODE - INDIARAILINFO SCRAPER)
# ==============================================================================
# [NAYA TARIQA]: Ab live train schedule data direct https://indiarailinfo.com/ se
# automatically web scrape hokar aata hai. Isme KOI Cookie ya Token ki zaroorat nahi hai.
# ==============================================================================

import urllib.parse
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

os.system('')  # Enable ANSI terminal colors in Windows CMD / PowerShell

class C:
    RESET      = "\033[0m"
    BOLD       = "\033[1m"
    DIM        = "\033[2m"
    RED        = "\033[31m"
    GREEN      = "\033[32m"
    YELLOW     = "\033[33m"
    BLUE       = "\033[34m"
    MAGENTA    = "\033[35m"
    CYAN       = "\033[36m"
    WHITE      = "\033[37m"
    
    B_RED      = "\033[91m"
    B_GREEN    = "\033[92m"
    B_YELLOW   = "\033[93m"
    B_BLUE     = "\033[94m"
    B_MAGENTA  = "\033[95m"
    B_CYAN     = "\033[96m"
    B_WHITE    = "\033[97m"

print(f"\n{C.B_CYAN}{C.BOLD}=" * 65 + f"{C.RESET}")
print(f"  {C.B_YELLOW}{C.BOLD}🚂 IRCTC TENDER SCHEDULE GENERATOR ENGINE  v3.0{C.RESET}  {C.B_GREEN}● ONLINE{C.RESET}")
print(f"  {C.B_CYAN}⚡ IndiaRailInfo Scraper Initialised | No Cookies/Tokens Required{C.RESET}")
print(f"  {C.B_MAGENTA}🎨 Vibrant ANSI Console Output Active{C.RESET}")
print(f"{C.B_CYAN}{C.BOLD}=" * 65 + f"{C.RESET}\n")

_iri_session = curl_requests.Session(impersonate="chrome120")
_iri_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Referer": "https://indiarailinfo.com/"
})

_session_verified = False

def _init_iri_session():
    global _session_verified
    if not _session_verified:
        try:
            _iri_session.get("https://indiarailinfo.com/", timeout=10)
            _iri_session.get("https://indiarailinfo.com/verify-browser?t=0:5:2:1:8:1:1:0:0:nosig:0", timeout=10)
            _session_verified = True
        except Exception as e:
            print(f"[IRI] Session init warning: {e}")

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
]

def _get_iri_timetable_url(train_no: str) -> Optional[str]:
    train_no = str(train_no).strip()
    # Strategy 1: Mobile Session Search
    try:
        session = curl_requests.Session(impersonate="chrome120")
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            "Referer": "https://m.indiarailinfo.com/"
        })
        session.get("https://m.indiarailinfo.com/", timeout=6)
        session.get("https://m.indiarailinfo.com/verify-browser?t=0:5:2:1:8:1:1:0:0:nosig:0", timeout=6)
        
        r = session.get(f"https://m.indiarailinfo.com/trains?q={train_no}", timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "/train/" in href and not "/pdf/" in href:
                m = re.search(r"/train/(\d+)", href)
                if m:
                    return f"https://indiarailinfo.com/train/{m.group(1)}"
    except Exception as e:
        print(f"[IRI] Mobile resolution error for {train_no}: {e}")

    # Strategy 2: Search Engine Fallback
    try:
        import random
        headers = {"User-Agent": random.choice(_USER_AGENTS)}
        url_yahoo = f"https://search.yahoo.com/search?p=site:indiarailinfo.com+train+{train_no}"
        r = std_requests.get(url_yahoo, headers=headers, timeout=6)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a"):
            href = a.get("href", "")
            if "RU=" in href:
                unquoted = urllib.parse.unquote(href)
                if "indiarailinfo.com/train/" in unquoted or "indiarailinfo.com/trains/" in unquoted:
                    idx = unquoted.find("https://indiarailinfo.com")
                    if idx != -1:
                        end_idx = unquoted.find("/RK=", idx)
                        return unquoted[idx:end_idx] if end_idx != -1 else unquoted[idx:]
    except Exception:
        pass

    return None

_CLUTTER_PARENS_RE = re.compile(
    r"\s*\((?:PT\d*|SF|Mail|Express|Special|UnReserved|Weekly|Bi-Weekly|Tri-Weekly|Daily|AC|TOD|TOD\+WCB|WCB)\)",
    re.IGNORECASE
)


def _clean_train_name(name: str) -> str:
    if not name:
        return ""
    name = _CLUTTER_PARENS_RE.sub("", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def fetch_train_indiarailinfo(train_no: str) -> Optional[dict]:
    """
    Scrape train schedule directly from IndiaRailInfo with robust HTML parsing.
    """
    train_no = str(train_no).strip()
    print(f"  {C.B_CYAN}🔍 [IRI]{C.RESET} Fetching Schedule for Train {C.B_YELLOW}{train_no}{C.RESET}...")

    # 1. Resolve train ID slug
    train_id = None
    try:
        session_search = curl_requests.Session(impersonate="chrome120")
        session_search.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://m.indiarailinfo.com/"
        })
        session_search.get("https://m.indiarailinfo.com/", timeout=5)
        session_search.get("https://m.indiarailinfo.com/verify-browser?t=0:5:2:1:8:1:1:0:0:nosig:0", timeout=5)
        r_s = session_search.get(f"https://m.indiarailinfo.com/trains?q={train_no}", timeout=6)
        soup_s = BeautifulSoup(r_s.text, "html.parser")
        for a in soup_s.find_all("a"):
            href = a.get("href", "")
            if "/train/" in href and not "/pdf/" in href:
                m = re.search(r"/train/(?:[^/]+/)?(\d+)", href)
                if m:
                    train_id = m.group(1)
                    break
    except Exception as e:
        print(f"  [WARN] Slug resolution fallback for {train_no}: {e}")

    if not train_id:
        train_id = train_no

    iri_url = f"https://indiarailinfo.com/train/{train_id}"
    print(f"  {C.CYAN}🔗 [IRI Source URL]{C.RESET} {C.DIM}-> {iri_url}{C.RESET}")

    try:
        session = curl_requests.Session(impersonate="chrome120")
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://indiarailinfo.com/"
        })
        try:
            session.get("https://indiarailinfo.com/", timeout=5)
            session.get("https://indiarailinfo.com/verify-browser?t=0:5:2:1:8:1:1:0:0:nosig:0", timeout=5)
        except Exception:
            pass

        r = session.get(iri_url, timeout=10)
        if r.status_code != 200 or len(r.text) < 5000:
            time.sleep(1)
            r = session.get(iri_url, timeout=10)

        if r.status_code != 200 or len(r.text) < 5000:
            print(f"  {C.B_RED}⚠️ [WARN]{C.RESET} Failed to load IRI timetable page for train {C.B_YELLOW}{train_no}{C.RESET} (Status {r.status_code})")
            return None

        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string if soup.title else f"TRAIN {train_no}"

        # Train Name
        train_name = f"TRAIN {train_no}"
        m_name = re.search(r"^\d+/([^-(]+)", title)
        if m_name:
            train_name = m_name.group(1).strip()
        train_name = _clean_train_name(train_name)

        # Station Codes in exact order
        station_codes = []
        for a in soup.find_all("a", href=re.compile(r"/station/map/.*#st")):
            txt = a.get_text().strip()
            if 2 <= len(txt) <= 5 and txt.isupper() and txt not in station_codes:
                station_codes.append(txt)

        if len(station_codes) < 2:
            for a in soup.find_all("a", href=re.compile(r"/station/")):
                txt = a.get_text().strip()
                if "/" in txt:
                    code = txt.split("/")[0].strip()
                    if 2 <= len(code) <= 5 and code.isupper() and code not in station_codes:
                        station_codes.append(code)

        if len(station_codes) < 2:
            print(f"  [WARN] Insufficient station codes found for train {train_no}")
            return None

        origin_code = station_codes[0]
        dest_code = station_codes[-1]

        # Safeguard against identical origin and destination codes (e.g. MAS-MAS)
        if origin_code == dest_code and len(station_codes) > 1:
            for c in reversed(station_codes):
                if c != origin_code:
                    dest_code = c
                    break

        # Departure & Arrival Times
        dep_m = re.search(r"Departs\s*@\s*(?:<[^>]+>\s*)*([0-2]?\d:[0-5]\d)", r.text, re.IGNORECASE | re.DOTALL)
        arr_m = re.search(r"Arrives\s*@\s*(?:<[^>]+>\s*)*([0-2]?\d:[0-5]\d)", r.text, re.IGNORECASE | re.DOTALL)

        dep_time = "---"
        if dep_m:
            parts = dep_m.group(1).split(":")
            dep_time = f"{int(parts[0]):02d}{int(parts[1]):02d} hrs"

        arr_time = "---"
        if arr_m:
            parts = arr_m.group(1).split(":")
            arr_time = f"{int(parts[0]):02d}{int(parts[1]):02d} hrs"

        # Running Days Bitmask
        run_days_str = "(DAILY)"
        dep_tag = soup.find(string=re.compile(r"Departs\s*@", re.IGNORECASE))
        if dep_tag and dep_tag.parent:
            dep_cell = dep_tag.parent
            grid = dep_cell.find("table", class_=re.compile(r"deparrgrid"))
            if grid:
                tds = grid.find_all("td")
                if len(tds) == 7:
                    bits = []
                    for td in tds:
                        style = str(td.get("style", ""))
                        if "opacity" in style and ("0.2" in style or "0.3" in style or "0.4" in style):
                            bits.append("0")
                        else:
                            bits.append("1")
                    mon_sun_bits = bits[1:] + bits[:1]
                    run_days_str = _format_run_days("".join(mon_sun_bits))

        # Coaches
        coaches_str = "20 Coaches"
        coach_match = re.search(r"(\d+)\s*(?:LHB|ICF)?\s*Coaches", r.text, re.IGNORECASE)
        if coach_match:
            coaches_str = f"{coach_match.group(1)} Coaches"

        print(f"  {C.B_GREEN}✅ [OK]{C.RESET} Successfully fetched Train {C.B_YELLOW}{train_no}{C.RESET} ({C.B_WHITE}{train_name}{C.RESET}) [{dep_time} - {arr_time}]")
        return {
            "train_number":  train_no,
            "train_name":    train_name,
            "origin_code":   origin_code,
            "dest_code":     dest_code,
            "dep_time":      dep_time,
            "arr_time":      arr_time,
            "run_days":      run_days_str,
            "station_codes": station_codes,
            "coaches":       coaches_str,
        }
    except Exception as e:
        print(f"  [ERROR] IndiaRailInfo scraper error for train {train_no}: {e}")
        return None

# ==============================================================================
# SECTION 3 - DATA HELPERS
# ==============================================================================

def _suffix_clean(name: str) -> str:
    return _SUFFIX_RE.sub("", name).strip()


def _normalise_time(raw: str) -> str:
    """
    Convert times to 'HHMM hrs'.
    Supports dot-separated '20.10' or colon-separated '20:10'.
    """
    if not raw:
        return "---"
    raw = raw.strip()
    if raw.lower() in ("first", "last", "source", "destination",
                       "--", "---", "--:--", "--.--", "0", ""):
        return "---"
    normalised = raw.replace(".", ":")
    parts = normalised.split(":")
    if len(parts) >= 2:
        try:
            hh = int(parts[0])
            mm = int(parts[1])
            return f"{hh:02d}{mm:02d} hrs"
        except ValueError:
            pass
    return raw


def _format_run_days(bitmask: str) -> str:
    """
    Conditional frequency formatting:

      7 days  -> (DAILY)
      4 or 5  -> 04 DAYS (Except – MON, THU, SUN)   [show missing days]
      1,2,3,6 -> 03 DAYS (TUE, THU, SUN)             [show running days]

    Index: 0=MON 1=TUE 2=WED 3=THU 4=FRI 5=SAT 6=SUN
    """
    active  = [_DAY_NAMES[i] for i, c in enumerate(bitmask) if c == "1"]
    missing = [_DAY_NAMES[i] for i, c in enumerate(bitmask) if c == "0"]
    count   = len(active)

    if count == 7 or count == 0:
        return "(DAILY)"

    if count in (4, 5):
        # Show the days it does NOT run — shorter and clearer
        return f"{count:02d} DAYS (Except \u2013 {', '.join(missing)})"

    # 1, 2, 3, or 6 days — show the days it runs
    label = "DAY" if count == 1 else "DAYS"
    return f"{count:02d} {label} ({', '.join(active)})"# ==============================================================================
# SECTION 4 - SMART VIA ALGORITHM
# ==============================================================================

def get_smart_via(station_codes: List[str]) -> str:
    if len(station_codes) < 3:
        return "N/A"
    middle = station_codes[1:-1]
    if len(middle) <= 7:
        return ", ".join(middle)
    anchor_first = middle[0]
    anchor_last  = middle[-1]
    inner        = middle[1:-1]
    if len(inner) <= 5:
        chosen = inner[:]
    else:
        step   = (len(inner) - 1) / 4.0
        chosen = [inner[round(i * step)] for i in range(5)]
    return ", ".join([anchor_first] + chosen + [anchor_last])


# ==============================================================================
# SECTION 5 - WORD DOCUMENT UTILITIES
# ==============================================================================

_FONT_NAME = "Times New Roman"
_FONT_SIZE = 13
_HEADER_FONT_SIZE = 14


def _set_cell_valign(cell, align: str = "center") -> None:
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    vAlign = OxmlElement("w:vAlign")
    vAlign.set(qn("w:val"), align)
    tcPr.append(vAlign)


def _merge_row(table, row_idx: int, from_col: int, to_col: int):
    a = table.rows[row_idx].cells[from_col]
    b = table.rows[row_idx].cells[to_col]
    a.merge(b)
    return a


def _write(cell, text: str, *,
           bold: bool = False,
           align=WD_ALIGN_PARAGRAPH.LEFT,
           new_para: bool = False,
           font_size: Optional[float] = None) -> None:
    if not new_para:
        para = cell.paragraphs[0]
        para.clear()
    else:
        para = cell.add_paragraph()
    para.alignment = align
    run            = para.add_run(text)
    run.bold       = bold
    run.font.name  = _FONT_NAME
    run.font.size  = Pt(font_size if font_size else _FONT_SIZE)


def _write_bold_prefix(cell, prefix: str, val: str, *,
                      align=WD_ALIGN_PARAGRAPH.LEFT,
                      new_para: bool = False,
                      font_size: Optional[float] = None) -> None:
    if not new_para:
        para = cell.paragraphs[0]
        para.clear()
    else:
        para = cell.add_paragraph()
    para.alignment = align

    size = font_size if font_size else _FONT_SIZE

    r1 = para.add_run(prefix)
    r1.bold = True
    r1.font.name = _FONT_NAME
    r1.font.size = Pt(size)

    r2 = para.add_run(val)
    r2.bold = False
    r2.font.name = _FONT_NAME
    r2.font.size = Pt(size)


# ==============================================================================
# SECTION 6 - TABLE BUILDER (Dynamic rows based on type)
# ==============================================================================

def build_pair_table(doc: Document, up: dict, dn: dict, schedule_type: str = "normal", up_upto: str = "", dn_upto: str = "", up_sections: str = "", dn_sections: str = "") -> None:
    """
    Dynamic black-and-white schedule table.
    """
    up_no = up["train_number"]
    dn_no = dn["train_number"]

    raw_name = _clean_train_name(up.get("train_name", ""))
    name_str = f", {raw_name}" if raw_name else ""

    up_orig = up.get('origin_code', '---')
    dn_orig = dn.get('origin_code', '---')

    # Safeguard against identical station codes (e.g. MAS-MAS)
    if up_orig == dn_orig:
        if up.get('dest_code') and up['dest_code'] != up_orig:
            dn_orig = up['dest_code']
        elif dn.get('dest_code') and dn['dest_code'] != up_orig:
            dn_orig = dn['dest_code']

    train_pair_label = (
        f"{up_no}-{dn_no[-2:]}, "
        f"{up_orig}-{dn_orig}{name_str}"
    )

    up_days = up['run_days']
    dn_days = dn['run_days']
    if schedule_type in ("tod", "tod_wcb"):
        up_days = up_days.replace("DAY", "DAYS")
        dn_days = dn_days.replace("DAY", "DAYS")

    freq_up = f"{up_no}- Ex- {up['origin_code']} - {up_days}"
    if schedule_type in ("tod", "tod_wcb") and up_upto and up_upto.strip():
        freq_up += f" UPTO {up_upto.strip()}"

    freq_dn = f"{dn_no}- Ex- {dn['origin_code']} - {dn_days}"
    if schedule_type in ("tod", "tod_wcb") and dn_upto and dn_upto.strip():
        freq_dn += f" UPTO {dn_upto.strip()}"

    via_str = get_smart_via(up["station_codes"])

    rows_count = 5
    if schedule_type in ("sections", "wcb", "tod_wcb"):
        rows_count = 6

    table           = doc.add_table(rows=rows_count, cols=3)
    table.style     = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    col_w = [Cm(4.0), Cm(6.5), Cm(6.5)]
    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = col_w[i]
            _set_cell_valign(cell, "center")

    _write(_merge_row(table, 0, 0, 2), "Detail",
           bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    _write(table.cell(1, 0), "Train No.& Name")
    _write(_merge_row(table, 1, 1, 2), train_pair_label, bold=True)
    
    current_row = 2
    if schedule_type == "sections":
        _write(table.cell(current_row, 0), "Catering Services to be excluded in following sections")
        sections_cell = _merge_row(table, current_row, 1, 2)
        up_sec_text = f"{up_no}- {up_sections.strip()}" if up_sections and up_sections.strip() else f"{up_no}- "
        dn_sec_text = f"{dn_no}- {dn_sections.strip()}" if dn_sections and dn_sections.strip() else f"{dn_no}- "
        _write(sections_cell, up_sec_text, bold=True)
        _write(sections_cell, dn_sec_text, bold=True, new_para=True)
        current_row += 1

    _write(table.cell(current_row, 0), "Frequency")
    fr_cell = _merge_row(table, current_row, 1, 2)
    _write(fr_cell, freq_up, bold=True)
    _write(fr_cell, freq_dn, bold=True, new_para=True)
    current_row += 1
    
    _write(table.cell(current_row, 0), "Running Between")
    left_cell = table.cell(current_row, 1)
    _write_bold_prefix(left_cell, "Ex- ", up['origin_code'])
    _write_bold_prefix(left_cell, "Dep:- ", up['dep_time'], new_para=True)
    _write_bold_prefix(left_cell, "Arr:- ", dn['arr_time'], new_para=True)

    right_cell = table.cell(current_row, 2)
    _write_bold_prefix(right_cell, "Ex- ", dn['origin_code'])
    _write_bold_prefix(right_cell, "Dep:- ", dn['dep_time'], new_para=True)
    _write_bold_prefix(right_cell, "Arr:- ", up['arr_time'], new_para=True)
    current_row += 1
    
    _write(table.cell(current_row, 0), "Via")
    _write(_merge_row(table, current_row, 1, 2), via_str)
    current_row += 1

    if schedule_type in ("wcb", "tod_wcb"):
        _write(table.cell(current_row, 0), "Coaches")
        coaches_val = up.get("coaches", "20 Coaches")
        _write(_merge_row(table, current_row, 1, 2), coaches_val, bold=True)


def build_service_table_with_title(doc: Document, up_no: str, dn_no: str) -> None:
    """
    Appends an 8-column Kitchen/Service details table for a train pair at the end of the document.
    """
    dn_suffix = dn_no[-2:] if len(dn_no) >= 2 else dn_no
    heading_text = f"Train no.{up_no}-{dn_suffix}"

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(heading_text)
    run.bold = True
    run.underline = True
    run.font.name = _FONT_NAME
    run.font.size = Pt(14)

    table = doc.add_table(rows=2, cols=8)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "Day ", "Service", "Station", "Time",
        "Kitchen licensee", "Contact details",
        "Amount of Spl SD to be paid", "IRCTC zone"
    ]
    col_w = [Cm(1.4), Cm(2.2), Cm(2.2), Cm(2.2), Cm(2.5), Cm(2.3), Cm(2.4), Cm(1.8)]

    for row in table.rows:
        for i, cell in enumerate(row.cells):
            cell.width = col_w[i]
            _set_cell_valign(cell, "center")

    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        align = WD_ALIGN_PARAGRAPH.CENTER if i >= 2 else WD_ALIGN_PARAGRAPH.LEFT
        _write(cell, h, bold=True, align=align)

    for i in range(8):
        cell = table.cell(1, i)
        _write(cell, "Nil", bold=True)


# ==============================================================================
# SECTION 7 - REST ENDPOINTS
# ==============================================================================

class TrainPair(BaseModel):
    up: str
    down: str
    schedule_type: Optional[str] = "normal"
    up_upto: Optional[str] = ""
    dn_upto: Optional[str] = ""
    up_sections: Optional[str] = ""
    dn_sections: Optional[str] = ""

class ScheduleRequest(BaseModel):
    pairs: List[TrainPair]
    auth_password: Optional[str] = None


SECURITY_KEY = "Suhail_Apprentice"


def _remove_file(path: str):
    try:
        os.remove(path)
    except Exception:
        pass


# ==============================================================================
# STATS PERSISTENCE  (stats.json lives next to main.py)
# ==============================================================================

STATS_PATH = os.path.join(BASE_DIR, "stats.json")
_STATS_DEFAULT = {"total_generated": 0, "total_trains": 0, "total_time_saved_minutes": 0}


def _load_stats() -> dict:
    try:
        if os.path.exists(STATS_PATH):
            with open(STATS_PATH, "r") as f:
                return json.load(f)
    except (json.decoder.JSONDecodeError, IOError) as e:
        print(f"[WARN] Failed to load stats (file might be corrupted): {e}. Resetting to defaults.")
    except Exception:
        pass
    
    return dict(_STATS_DEFAULT)


def _save_stats(stats: dict) -> None:
    tmp_name = None
    try:
        # Create temp file in the same directory as stats.json
        fd, tmp_name = tempfile.mkstemp(dir=os.path.dirname(STATS_PATH), text=True)
        with os.fdopen(fd, "w") as f:
            json.dump(stats, f, indent=2)
            f.flush()
            os.fsync(f.fileno())  # Ensure bytes are written to physical disk
            
        # Atomically replace old stats file with the new complete one
        os.replace(tmp_name, STATS_PATH)
    except Exception as e:
        print(f"[WARN] Could not save stats: {e}")
        if tmp_name and os.path.exists(tmp_name):
            try:
                os.remove(tmp_name)
            except Exception:
                pass


def _increment_stats(pairs_count: int) -> None:
    """Called once after a successful document generation."""
    stats = _load_stats()
    stats["total_generated"]          += 1
    stats["total_trains"]             += pairs_count
    stats["total_time_saved_minutes"] += pairs_count * 5   # 5 min saved per pair
    _save_stats(stats)


@app.get("/get-stats")
def get_stats():
    return _load_stats()


_is_generating = False


@app.post("/generate-schedule-stream")
async def generate_schedule_stream(req: ScheduleRequest):
    # Server-side un-bypassable security access check
    if not req.auth_password or req.auth_password.strip() != SECURITY_KEY:
        async def denied_gen():
            yield f"data: {json.dumps({'error': '🔒 Security Access Denied: Invalid or Missing Access Key.', 'type': 'warn'})}\n\n"
        return StreamingResponse(denied_gen(), status_code=401, media_type="text/event-stream")

    global _is_generating
    if _is_generating:
        async def busy_gen():
            yield f"data: {json.dumps({'text': '⚠️ [WARN] A schedule generation is already in progress. Please wait.', 'type': 'warn'})}\n\n"
        return StreamingResponse(busy_gen(), media_type="text/event-stream")

    _is_generating = True

    async def stream_generator():
        global _is_generating
        try:
            yield f"data: {json.dumps({'text': '==================================================', 'type': 'info'})}\n\n"
            yield f"data: {json.dumps({'text': '  IndiaRailInfo Scraper Initialised (No Auth Required)', 'type': 'success'})}\n\n"
            yield f"data: {json.dumps({'text': '==================================================', 'type': 'info'})}\n\n"

            doc     = Document()
            section = doc.sections[0]
            section.top_margin    = Cm(2)
            section.bottom_margin = Cm(2)
            section.left_margin   = Cm(2)
            section.right_margin  = Cm(2)

            generated = 0
            processed_pairs = []

            for pair_idx, pair in enumerate(req.pairs):
                up_no, dn_no = pair.up.strip(), pair.down.strip()
                if not up_no or not dn_no:
                    continue

                header_str = f"[PAIR #{pair_idx + 1}] {up_no} ⇄ {dn_no} [{pair.schedule_type.upper()}]"
                print(f"\n{C.B_BLUE}{C.BOLD}┌──────────────────────────────────────────────────────────────┐{C.RESET}")
                print(f"{C.B_BLUE}{C.BOLD}│ 🚆 PROCESSING {header_str:<46} │{C.RESET}")
                print(f"{C.B_BLUE}{C.BOLD}└──────────────────────────────────────────────────────────────┘{C.RESET}")
                pair_log_text = "\n" + header_str
                yield f"data: {json.dumps({'text': pair_log_text, 'type': 'pair'})}\n\n"
                await asyncio.sleep(0.05)

                # UP Train
                up_msg = f"  🔍 [IRI] Fetching Schedule for Train {up_no}..."
                print(f"  {C.B_CYAN}🔍 [IRI]{C.RESET} Fetching Schedule for Train {C.B_YELLOW}{up_no}{C.RESET}...")
                yield f"data: {json.dumps({'text': up_msg, 'type': 'info'})}\n\n"
                await asyncio.sleep(0.05)

                up_info = fetch_train_indiarailinfo(up_no)
                if not up_info:
                    err_msg = f"  ⚠️ [WARN] Train {up_no} not found on IndiaRailInfo."
                    yield f"data: {json.dumps({'text': err_msg, 'type': 'warn'})}\n\n"
                    yield f"data: {json.dumps({'error': f'Train {up_no} not found on IndiaRailInfo.'})}\n\n"
                    return

                up_ok_msg = f"  ✅ [OK] Successfully fetched Train {up_no} ({up_info['train_name']})"
                yield f"data: {json.dumps({'text': up_ok_msg, 'type': 'success'})}\n\n"
                await asyncio.sleep(0.1)

                # DOWN Train
                dn_msg = f"  🔍 [IRI] Fetching Schedule for Train {dn_no}..."
                print(f"  {C.B_CYAN}🔍 [IRI]{C.RESET} Fetching Schedule for Train {C.B_YELLOW}{dn_no}{C.RESET}...")
                yield f"data: {json.dumps({'text': dn_msg, 'type': 'info'})}\n\n"
                await asyncio.sleep(0.05)

                dn_info = fetch_train_indiarailinfo(dn_no)
                if not dn_info:
                    err_msg = f"  ⚠️ [WARN] Train {dn_no} not found on IndiaRailInfo."
                    yield f"data: {json.dumps({'text': err_msg, 'type': 'warn'})}\n\n"
                    yield f"data: {json.dumps({'error': f'Train {dn_no} not found on IndiaRailInfo.'})}\n\n"
                    return

                dn_ok_msg = f"  ✅ [OK] Successfully fetched Train {dn_no} ({dn_info['train_name']})"
                yield f"data: {json.dumps({'text': dn_ok_msg, 'type': 'success'})}\n\n"
                await asyncio.sleep(0.1)

                if generated > 0:
                    p_gap = doc.add_paragraph()
                    p_gap.paragraph_format.space_before = Pt(6)
                    p_gap.paragraph_format.space_after = Pt(12)

                build_pair_table(doc, up_info, dn_info, pair.schedule_type, up_upto=pair.up_upto or "", dn_upto=pair.dn_upto or "", up_sections=pair.up_sections or "", dn_sections=pair.dn_sections or "")
                processed_pairs.append((up_no, dn_no))
                generated += 1

                built_msg = f"  ✨ [SUCCESS] Table Built: {up_info['origin_code']} ⇄ {dn_info['origin_code']} [{pair.schedule_type.upper()}]"
                print(f"  {C.B_GREEN}✨ [SUCCESS]{C.RESET} Table Built: {C.B_WHITE}{up_info['origin_code']}{C.RESET} ⇄ {C.B_WHITE}{dn_info['origin_code']}{C.RESET} {C.DIM}[{pair.schedule_type.upper()}]{C.RESET}")
                yield f"data: {json.dumps({'text': built_msg, 'type': 'success'})}\n\n"
                await asyncio.sleep(0.1)

            if processed_pairs:
                service_log_text = "\n📋 Appending Kitchen/Service details tables at document end..."
                yield f"data: {json.dumps({'text': service_log_text, 'type': 'info'})}\n\n"
                for up_no, dn_no in processed_pairs:
                    build_service_table_with_title(doc, up_no, dn_no)

            if generated == 0:
                yield f"data: {json.dumps({'error': 'No valid train pairs could be processed.'})}\n\n"
                return

            fname = f"schedule_{uuid.uuid4().hex}.docx"
            out_path = os.path.join(BASE_DIR, fname)
            doc.save(out_path)

            _increment_stats(generated)

            comp_text = f"🎉 [SUCCESS] IRCTC Tender Schedule Word Document Generated! ({generated} Pair{'s' if generated > 1 else ''})"
            print(f"\n{C.B_GREEN}{C.BOLD}============================================================={C.RESET}")
            print(f" {C.B_GREEN}{C.BOLD}🎉 DOCUMENT GENERATION COMPLETED SUCCESSFULLY!{C.RESET}")
            print(f" {C.B_WHITE}📦 Output File:{C.RESET} {C.B_YELLOW}{fname}{C.RESET}")
            print(f" {C.B_CYAN}📊 Main Schedules:{C.RESET} {generated}  |  {C.B_MAGENTA}📋 Service Tables:{C.RESET} {len(processed_pairs)} (at End)")
            print(f"{C.B_GREEN}{C.BOLD}============================================================={C.RESET}\n")

            yield f"data: {json.dumps({'text': comp_text, 'type': 'success', 'done': True, 'filename': fname})}\n\n"

        finally:
            _is_generating = False

    return StreamingResponse(stream_generator(), media_type="text/event-stream")


@app.get("/download-file/{filename}")
def download_file(filename: str, background_tasks: BackgroundTasks):
    safe_name = os.path.basename(filename)
    file_path = os.path.join(BASE_DIR, safe_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested schedule file not found.")
    background_tasks.add_task(_remove_file, file_path)
    return FileResponse(
        path=file_path,
        filename="IRCTC_Tender_Schedules.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.post("/extract-trains")
async def extract_trains(file: UploadFile = File(...)):
    """
    PDF parser with robust regex for all train number formats:
      - 20151-52   -> UP: 20151, DOWN: 20152  (2-digit suffix)
      - 13247-13248 -> UP: 13247, DOWN: 13248  (full 5-digit pair)
      - 12601       -> singleton (try to pair with next sequential)
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF.")

    contents = await file.read()
    text = ""

    # ── Extractor 1: PyMuPDF (fitz) — handles non-standard font encodings ────
    # Much better than pdfplumber for government/office-generated PDFs.
    try:
        import fitz  # PyMuPDF
        doc_fitz = fitz.open(stream=contents, filetype="pdf")
        for page in doc_fitz:
            # get_text("text") — plain text with newlines
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text + "\n"

            # get_text("blocks") — text blocks with exact layout
            # Each block: (x0,y0,x1,y1, "text", block_no, block_type)
            for block in page.get_text("blocks"):
                block_text = block[4] if len(block) > 4 else ""
                if block_text.strip():
                    text += block_text.replace("\n", " ") + " "

            # get_text("dict") — span-level detail, catches chars in odd fonts
            block_dict = page.get_text("dict")
            for blk in block_dict.get("blocks", []):
                for line in blk.get("lines", []):
                    line_str = "".join(span["text"] for span in line.get("spans", []))
                    if line_str.strip():
                        text += line_str + " "
            text += "\n"
        doc_fitz.close()
    except Exception as e:
        print(f"  [WARN] PyMuPDF failed: {e}. Falling back to pdfplumber.")

    # ── Extractor 2: pdfplumber — fallback if PyMuPDF got nothing ───────────
    if not text.strip():
        try:
            with pdfplumber.open(io.BytesIO(contents)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    try:
                        tables = page.extract_tables()
                        for tbl in (tables or []):
                            for row in tbl:
                                for cell in row:
                                    if cell:
                                        text += cell.strip().replace("\n", " ") + " "
                            text += "\n"
                    except Exception:
                        pass
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {exc}")

    # ── Extractor 3: OCR via easyocr — for scanned image PDFs ───────────────
    # Triggered only when both text-based extractors return nothing.
    # PyMuPDF renders each PDF page as a 300-DPI image; easyocr reads it.
    if not text.strip():
        print("[OCR] No text layer found. Running OCR on page images...")
        try:
            import fitz
            import numpy as np
            reader = _get_ocr_reader()
            doc_fitz = fitz.open(stream=contents, filetype="pdf")
            for page_num, page in enumerate(doc_fitz):
                # ── Render at 200 DPI (sufficient for large printed numbers) ─
                mat = fitz.Matrix(200 / 72, 200 / 72)
                pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
                img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
                          pix.height, pix.width, 3)

                h, w, _ = img.shape
                
                # ── Dynamic Cropping based on Orientation ────────────────────
                if h > w:
                    orientation = "Portrait"
                    crop_pct = 0.32
                else:
                    orientation = "Landscape"
                    crop_pct = 0.20
                    
                crop_w = max(1, int(w * crop_pct))
                img_crop = img[:, :crop_w, :]
                
                print(f"[OCR] Page {page_num+1} detected as [{orientation}]. Cropping at {int(crop_pct*100)}%...")

                results = reader.readtext(img_crop, detail=0, paragraph=False)
                page_text = " ".join(results)
                
                # ── Safety Net: Full Page Scan Fallback ──────────────────────
                if not re.search(r'\d{5}', page_text):
                    print(f"  [WARN] No train numbers found in {int(crop_pct*100)}% crop. Triggering Full Page Scan...")
                    results = reader.readtext(img, detail=0, paragraph=False)
                    page_text = " ".join(results)

                print(f"  [OCR] Extracted preview: {repr(page_text[:200])}")
                text += page_text + "\n"
            doc_fitz.close()
        except Exception as ocr_err:
            raise HTTPException(
                status_code=500,
                detail=f"PDF has no text layer and OCR also failed: {ocr_err}"
            )

    # Normalise dash variants and invisible chars
    text = (text
            .replace("\u2013", "-")   # en-dash
            .replace("\u2014", "-")   # em-dash
            .replace("\u2011", "-")   # non-breaking hyphen
            .replace("\u00a0", " ")   # non-breaking space
            .replace("\ufb01", "fi")  # ligature fi
            )

    print(f"[PDF] Chars extracted: {len(text)}")
    print(f"[PDF] Text sample: {repr(text[:400])}")

    pairs:      List[List[str]] = []
    used_pairs: set             = set()
    singletons: List[str]       = []

    # --- Pass 1: Full 5-digit pairs  e.g. "13247-13248" or "13247/13248" -----
    full_pair_re = re.compile(r"\b(\d{5})[-/](\d{5})\b")
    for m in full_pair_re.finditer(text):
        a, b = m.group(1), m.group(2)
        key = (a, b)
        if key not in used_pairs:
            pairs.append([a, b])
            used_pairs.add(key)

    # Remove matched positions so Pass 2 doesn't double-count
    text_reduced = full_pair_re.sub("     ", text)   # blank out with spaces

    # --- Pass 2: Suffix pairs  e.g. "20151-52" or "16779-80" -----------------
    # Suffix can be 2-4 digits; DOWN = UP[:(5-len(suffix))] + suffix
    suffix_pair_re = re.compile(r"\b(\d{5})[-/](\d{2,4})\b")
    for m in suffix_pair_re.finditer(text_reduced):
        base   = m.group(1)
        suffix = m.group(2)
        # Build full 5-digit DOWN train number
        prefix_len = 5 - len(suffix)
        down = base[:prefix_len] + suffix
        # Sanity check: result must be 5 digits
        if len(down) != 5 or not down.isdigit():
            continue
        key = (base, down)
        if key not in used_pairs:
            pairs.append([base, down])
            used_pairs.add(key)

    text_reduced = suffix_pair_re.sub("     ", text_reduced)

    # --- Pass 3: Remaining standalone 5-digit numbers -------------------------
    single_re = re.compile(r"\b(\d{5})\b")
    for m in single_re.finditer(text_reduced):
        tn = m.group(1)
        # Skip numbers already captured as part of a pair
        if any(tn == p[0] or (len(p) > 1 and tn == p[1]) for p in pairs):
            continue
        singletons.append(tn)

    # Try to group singletons into sequential pairs (e.g. 12601 + 12602)
    unique_singles = sorted(set(singletons))
    used_singles:  set = set()

    for tn in unique_singles:
        if tn in used_singles:
            continue
        nxt = str(int(tn) + 1).zfill(5)
        if nxt in unique_singles and nxt not in used_singles:
            key = (tn, nxt)
            if key not in used_pairs:
                pairs.append([tn, nxt])
                used_pairs.add(key)
            used_singles.update([tn, nxt])
        else:
            # True singleton — include anyway (user can remove from UI)
            pairs.append([tn])
            used_singles.add(tn)

    print(f"[PDF] Extracted {len(pairs)} pairs from '{file.filename}'")
    for p in pairs:
        print(f"       {p}")

    return {"extracted_pairs": pairs}


# ==============================================================================
# FRONTEND STATIC FILES MOUNT (Single-Server Deployment)
# ==============================================================================
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

