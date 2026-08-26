"""
================================================================================
  RENDER CLOUD ENVIRONMENT SIMULATION TEST SUITE
================================================================================
  This script simulates how the backend executes in a headless Linux/Cloud
  environment (Render / AWS / GCP) using curl_cffi, multi-node rotation,
  and multistage slug resolution (Direct API + DuckDuckGo + Yahoo).
================================================================================
"""

import sys
import os
import time
import re
import urllib.parse
from typing import Optional, Dict, Any, List

sys.stdout.reconfigure(encoding='utf-8')

from curl_cffi import requests
from bs4 import BeautifulSoup
from docx import Document

print("=" * 70)
print(" ☁️  STARTING RENDER CLOUD SIMULATION TEST FOR INDIARAILINFO")
print("=" * 70)

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

def _solve_challenge_on_session(session: requests.Session, html: str, domain: str) -> bool:
    try:
        sig_match = re.search(r'data-sig=[\'"]([^\'"]+)[\'"]', html)
        if sig_match:
            sig = sig_match.group(1)
            x_val = sig.split("|")[-1] if "|" in sig else "55"
            token = f"0:5:2:1:8:1:1:0:{x_val}:{sig}:0"
            verify_url = f"https://{domain}/verify-browser?t={token}"
            rv = session.get(verify_url, timeout=8)
            time.sleep(0.4)
            return rv.status_code == 200
    except Exception:
        pass
    return False

def create_cloud_session() -> tuple[requests.Session, str]:
    for node in IRI_NODES:
        session = requests.Session(impersonate="chrome124")
        session.headers.update(BROWSER_HEADERS)
        session.headers["Referer"] = f"https://{node}/"
        try:
            r = session.get(f"https://{node}/", timeout=6)
            if r.status_code == 200:
                if "data-sig" in r.text or "iri-xsig" in r.text:
                    _solve_challenge_on_session(session, r.text, node)
                print(f"  [CLOUD DISCOVERY] Connected & Verified on Node: https://{node}/")
                return session, node
        except Exception:
            continue
    def_s = requests.Session(impersonate="chrome124")
    def_s.headers.update(BROWSER_HEADERS)
    return def_s, "srv1.indiarailinfo.com"

def _extract_id_from_url(url: str, train_no: str) -> Optional[str]:
    if not url:
        return None
    patterns = [
        r'/train/[^/]+/(\d+)',
        r'/train/(\d+)',
        r'indiarailinfo\.com/train/[^/]+/(\d+)',
        r'indiarailinfo\.com/train/(\d+)'
    ]
    for pat in patterns:
        m = re.search(pat, url)
        if m:
            candidate = m.group(1)
            if candidate != train_no and len(candidate) >= 3:
                return candidate
    nums = re.findall(r'\b\d{3,7}\b', url)
    for num in nums:
        if num != train_no and len(num) >= 3:
            return num
    return None

def resolve_slug(train_no: str, session: requests.Session, node: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": f"https://{node}/"
    }
    # 1. Direct API
    try:
        url_internal = f"https://{node}/shtml/list.shtml?LappGetTrainList/{train_no}/0/0/0"
        r_int = session.get(url_internal, headers=headers, timeout=6)
        if ("data-sig" in r_int.text or "iri-xsig" in r_int.text) and not ("dropdowntable" in r_int.text):
            _solve_challenge_on_session(session, r_int.text, node)
            r_int = session.get(url_internal, headers=headers, timeout=6)
        if r_int.status_code == 200 and "dropdowntable" in r_int.text:
            soup_int = BeautifulSoup(r_int.text, "html.parser")
            for tr in soup_int.find_all("tr", class_=re.compile(r"rowM1", re.IGNORECASE)):
                tds = tr.find_all("td")
                if tds and tds[0].get_text().strip().isdigit():
                    return tds[0].get_text().strip()
    except Exception:
        pass
        
    # 2. DuckDuckGo
    try:
        url_ddg = f"https://html.duckduckgo.com/html/?q=site:indiarailinfo.com+train+{train_no}"
        r_ddg = session.get(url_ddg, headers=headers, timeout=6)
        if r_ddg.status_code == 200:
            soup_ddg = BeautifulSoup(r_ddg.text, "html.parser")
            for a in soup_ddg.find_all("a"):
                href = a.get("href", "")
                if "indiarailinfo.com/train/" in href or "uddg=" in href:
                    unquoted = urllib.parse.unquote(href)
                    tid = _extract_id_from_url(unquoted, train_no)
                    if tid:
                        return tid
    except Exception:
        pass

    # 3. Yahoo
    try:
        url_y = f"https://search.yahoo.com/search?p=site:indiarailinfo.com+train+{train_no}"
        r_y = session.get(url_y, headers=headers, timeout=6)
        if r_y.status_code == 200:
            soup_y = BeautifulSoup(r_y.text, "html.parser")
            for a in soup_y.find_all("a"):
                href = a.get("href", "")
                if "RU=" in href:
                    unquoted = urllib.parse.unquote(href)
                    tid = _extract_id_from_url(unquoted, train_no)
                    if tid:
                        return tid
    except Exception:
        pass

    return train_no

def simulate_fetch_train(train_no: str, session: requests.Session, node: str) -> Optional[Dict[str, Any]]:
    train_no = str(train_no).strip()
    slug = resolve_slug(train_no, session, node)
    
    train_url = f"https://{node}/train/{slug}"
    r_train = session.get(train_url, timeout=12)
    if ("data-sig" in r_train.text or "iri-xsig" in r_train.text) and len(r_train.text) < 5000:
        _solve_challenge_on_session(session, r_train.text, node)
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
    
    # Days
    run_days = "(DAILY)"
    dep_tag = soup.find(string=re.compile(r"Departs\s*@", re.IGNORECASE))
    if dep_tag and dep_tag.parent:
        grid = dep_tag.parent.find("table", class_=re.compile(r"deparrgrid"))
        if grid:
            tds = grid.find_all("td")
            if len(tds) == 7:
                bits = ["0" if ("opacity" in str(td.get("style", "")) and ("0.2" in str(td.get("style", "")) or "0.3" in str(td.get("style", "")) or "0.4" in str(td.get("style", "")))) else "1" for td in tds]
                mon_sun = bits[1:] + bits[:1]
                active = [["MON","TUE","WED","THU","FRI","SAT","SUN"][i] for i, b in enumerate(mon_sun) if b == "1"]
                run_days = f"{len(active):02d} DAY{'S' if len(active)>1 else ''} ({', '.join(active)})" if len(active) < 7 else "(DAILY)"
    
    return {
        "train_number": train_no,
        "train_name": train_name,
        "origin_code": origin_code,
        "dest_code": dest_code,
        "dep_time": dep_time,
        "arr_time": arr_time,
        "station_codes": station_codes,
        "coaches": "20 Coaches",
        "run_days": run_days
    }

# ── RUN TEST SCENARIO ──────────────────────────────────────────────────────────
session, node = create_cloud_session()

test_pairs = [
    ("22363", "22364", "wcb"),
    ("12603", "12604", "normal")
]

for idx, (up_no, dn_no, stype) in enumerate(test_pairs, start=1):
    print(f"\n[Pair #{idx}] Fetching {up_no} ⇄ {dn_no} [{stype.upper()}]...")
    up = simulate_fetch_train(up_no, session, node)
    dn = simulate_fetch_train(dn_no, session, node)
    
    if up and dn:
        print(f"  UP   : {up['train_name']} | Ex- {up['origin_code']} -> {up['dest_code']} | Dep: {up['dep_time']} | Runs: {up['run_days']}")
        print(f"  DOWN : {dn['train_name']} | Ex- {dn['origin_code']} -> {dn['dest_code']} | Dep: {dn['dep_time']} | Runs: {dn['run_days']}")
        print(f"  Result: PASS ✅")
    else:
        print(f"  Result: FAIL ❌")
