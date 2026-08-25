"""
================================================================================
  RENDER CLOUD ENVIRONMENT SIMULATION TEST SUITE
================================================================================
  This script simulates how the backend executes in a headless Linux/Cloud
  environment (Render / AWS / GCP) using curl_cffi and dynamic multi-node
  IndiaRailInfo CDN rotation + challenge resolution.
================================================================================
"""

import sys
import os
import time
import re
from typing import Optional, Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

from curl_cffi import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

print("=" * 70)
print(" ☁️  STARTING RENDER CLOUD SIMULATION TEST FOR INDIARAILINFO")
print("=" * 70)

# CDN nodes available for failover
IRI_NODES = [
    "srv1.indiarailinfo.com",
    "srv3.indiarailinfo.com",
    "srv2.indiarailinfo.com",
    "m.indiarailinfo.com",
    "indiarailinfo.com"
]

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1",
}

def create_cloud_session() -> tuple[requests.Session, str]:
    """Simulate cloud server establishing verified connection to active CDN node."""
    for node in IRI_NODES:
        session = requests.Session(impersonate="chrome124")
        session.headers.update(BROWSER_HEADERS)
        session.headers["Referer"] = f"https://{node}/"
        try:
            r = session.get(f"https://{node}/", timeout=6)
            if r.status_code == 200 and "iri-xsig" in r.text:
                soup = BeautifulSoup(r.text, "html.parser")
                xsig_div = soup.find("div", id="iri-xsig")
                if xsig_div:
                    xsig = xsig_div.get("data-sig")
                    x_val = xsig.split("|")[-1] if "|" in xsig else "24"
                    verify_url = f"https://{node}/verify-browser?t=0:5:2:1:8:1:1:0:{x_val}:{xsig}:0"
                    session.get(verify_url, timeout=6)
                    time.sleep(0.3)
                    print(f"  [CLOUD DISCOVERY] Connected & Verified on Node: https://{node}/")
                    return session, node
        except Exception:
            continue
    return None, None

def simulate_fetch_train(train_no: str, session: requests.Session, node: str) -> Optional[Dict[str, Any]]:
    """Fetch and parse train schedule from verified node."""
    train_no = str(train_no).strip()
    
    # 1. Resolve train ID
    list_url = f"https://{node}/shtml/list.shtml?LappGetTrainList/{train_no}/0/0/0"
    r_list = session.get(list_url, timeout=8)
    slug = train_no
    soup_l = BeautifulSoup(r_list.text, "html.parser")
    for tr in soup_l.find_all("tr", class_=re.compile(r"rowM1", re.IGNORECASE)):
        tds = tr.find_all("td")
        if tds and tds[0].get_text().strip().isdigit():
            slug = tds[0].get_text().strip()
            break
            
    # 2. Fetch train details
    train_url = f"https://{node}/train/{slug}"
    r_train = session.get(train_url, timeout=12)
    if r_train.status_code != 200 or len(r_train.text) < 3000:
        return None
        
    soup = BeautifulSoup(r_train.text, "html.parser")
    title = soup.title.string if soup.title else f"TRAIN {train_no}"
    
    train_name = f"TRAIN {train_no}"
    if "/" in title:
        parts = title.split("/", 1)[1].strip().split(" - ")
        name_parts = [p.strip() for p in parts if not re.search(r"\b\w+\s+to\s+\w+\b", p, re.IGNORECASE) and "Railway Enquiry" not in p]
        if name_parts:
            train_name = " - ".join(name_parts)
            
    station_codes = []
    for a in soup.find_all("a", href=re.compile(r"/station/map/.*#st")):
        txt = a.get_text().strip()
        if 2 <= len(txt) <= 5 and txt.isupper() and txt not in station_codes:
            station_codes.append(txt)
            
    if len(station_codes) < 2:
        return None
        
    origin_code = station_codes[0]
    dest_code = station_codes[-1]
    
    dep_m = re.search(r"Departs\s*@\s*(?:<[^>]+>\s*)*([0-2]?\d:[0-5]\d)", r_train.text, re.IGNORECASE | re.DOTALL)
    arr_m = re.search(r"Arrives\s*@\s*(?:<[^>]+>\s*)*([0-2]?\d:[0-5]\d)", r_train.text, re.IGNORECASE | re.DOTALL)
    
    dep_time = dep_m.group(1).replace(":", "") + " hrs" if dep_m else "---"
    arr_time = arr_m.group(1).replace(":", "") + " hrs" if arr_m else "---"
    
    return {
        "train_number": train_no,
        "train_name": train_name,
        "origin_code": origin_code,
        "dest_code": dest_code,
        "dep_time": dep_time,
        "arr_time": arr_time,
        "station_codes": station_codes,
        "coaches": "20 Coaches",
        "run_days": "(DAILY)"
    }

# ── RUN TEST SCENARIO ──────────────────────────────────────────────────────────
print("\n[STEP 1] Initializing Cloud Worker Session...")
session, node = create_cloud_session()

if not session:
    print("❌ FAILED: Could not connect to any IndiaRailInfo node.")
    sys.exit(1)

test_pairs = [
    ("22363", "22364", "wcb"),
    ("12601", "12602", "normal"),
    ("03639", "03639", "sections")
]

print(f"\n[STEP 2] Processing {len(test_pairs)} Train Pairs on Cloud Node ({node})...")

doc = Document()
processed = 0

for idx, (up_no, dn_no, stype) in enumerate(test_pairs, start=1):
    print(f"\n  [Pair #{idx}] Fetching {up_no} ⇄ {dn_no} [{stype.upper()}]...")
    
    up = simulate_fetch_train(up_no, session, node)
    dn = simulate_fetch_train(dn_no, session, node)
    
    if up and dn:
        print(f"    UP   : {up['train_name']} ({up['origin_code']} -> {up['dest_code']}) | Dep: {up['dep_time']}")
        print(f"    DOWN : {dn['train_name']} ({dn['origin_code']} -> {dn['dest_code']}) | Dep: {dn['dep_time']}")
        print(f"    Route: {len(up['station_codes'])} stations identified.")
        
        # Build Table
        t = doc.add_table(rows=5, cols=3)
        t.style = "Table Grid"
        p = t.cell(0, 0).paragraphs[0]
        p.text = f"{up_no}-{dn_no[-2:]}, {up['origin_code']}-{dn['dest_code']}, {up['train_name']}"
        
        processed += 1
        print("    Status: PASS ✅ (Table Formatted)")
    else:
        print("    Status: FAIL ❌")

print("\n[STEP 3] Generating & Saving Word (.docx) Output...")
out_filename = "cloud_simulation_result.docx"
doc.save(out_filename)
file_size = os.path.getsize(out_filename)

print(f"  Word Document Generated: {out_filename} ({file_size} bytes)")

print("\n" + "=" * 70)
print(f" 🎯 CLOUD SIMULATION SUMMARY: {processed}/{len(test_pairs)} Pairs Successfully Built!")
print("=" * 70)
