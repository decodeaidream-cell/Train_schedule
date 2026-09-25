"""
================================================================================
  LEGACY IRCTC OFFICIAL JSON API MODULE - FULL ENGINE
================================================================================
  This module contains the original legacy IRCTC API fetch engine.
  It queries IRCTC's official JSON API endpoints directly using an active
  session Cookie and GREQ authentication token.

  Endpoint:
    GET https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/{train_no}
================================================================================
"""

import sys
import requests
import urllib3
from typing import Optional, List

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import re

_DAY_ALIASES = {
    "M": "MON", "MO": "MON", "MON": "MON", "MONDAY": "MON", "MONDAYS": "MON",
    "T": "TUE", "TU": "TUE", "TUE": "TUE", "TUES": "TUE", "TUESDAY": "TUE", "TUESDAYS": "TUE",
    "W": "WED", "WE": "WED", "WED": "WED", "WEDNESDAY": "WED", "WEDNESDAYS": "WED",
    "TH": "THU", "THU": "THU", "THUR": "THU", "THURS": "THU", "THURSDAY": "THU", "THURSDAYS": "THU",
    "F": "FRI", "FR": "FRI", "FRI": "FRI", "FRIDAY": "FRI", "FRIDAYS": "FRI",
    "SA": "SAT", "SAT": "SAT", "SATURDAY": "SAT", "SATURDAYS": "SAT",
    "SU": "SUN", "SUN": "SUN", "SUNDAY": "SUN", "SUNDAYS": "SUN"
}

_DAY_NAMES = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]


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


def _format_run_days(days_input: str) -> str:
    """
    Official IRCTC Tender Frequency Formatting:
      - 7 days or 'DAILY': '(DAILY)'
      - 1 day:  '01 DAY (SAT)'
      - 2 days: '02 DAYS (TUE, FRI)'
      - 3 days: '03 DAYS (MON, WED, FRI)'
      - 4 days: '04 DAYS (Except \u2013 MON, THU, SUN)' [shows 3 missing days]
      - 5 days: '05 DAYS (Except \u2013 TUE, FRI)'      [shows 2 missing days]
      - 6 days: '06 DAYS (Except \u2013 SUN)'           [shows 1 missing day]
    """
    if not days_input or str(days_input).strip() == "":
        return "(DAILY)"

    s = str(days_input).strip().upper()
    if s in ("DAILY", "(DAILY)", "ALL DAYS", "EVERYDAY", "ALL", "7 DAYS", "07 DAYS"):
        return "(DAILY)"

    if len(s) == 7 and all(c in "01" for c in s):
        active = [_DAY_NAMES[i] for i, c in enumerate(s) if c == "1"]
        missing = [_DAY_NAMES[i] for i, c in enumerate(s) if c == "0"]
        count = len(active)
        if count == 7 or count == 0:
            return "(DAILY)"
        if count in (4, 5, 6):
            missing_str = ", ".join(missing)
            return f"{count:02d} DAYS (Except \u2013 {missing_str})"
        label = "DAY" if count == 1 else "DAYS"
        active_str = ", ".join(active)
        return f"{count:02d} {label} ({active_str})"

    except_match = re.search(r"\b(?:EXCEPT|EXC)\b[:\s\u2013\-]*(.*)", s)
    if except_match:
        except_part = except_match.group(1)
        raw_tokens = re.findall(r"[A-Za-z]+", except_part)
        missing_days = []
        for tok in raw_tokens:
            tok_clean = tok.strip().upper()
            if tok_clean in _DAY_ALIASES:
                canonical = _DAY_ALIASES[tok_clean]
                if canonical not in missing_days:
                    missing_days.append(canonical)
        missing_sorted = sorted(missing_days, key=lambda d: _DAY_NAMES.index(d))
        active_sorted = [d for d in _DAY_NAMES if d not in missing_sorted]
        count = len(active_sorted)
        if count == 7 or count == 0:
            return "(DAILY)"
        if count in (4, 5, 6):
            missing_str = ", ".join(missing_sorted)
            return f"{count:02d} DAYS (Except \u2013 {missing_str})"
        label = "DAY" if count == 1 else "DAYS"
        active_str = ", ".join(active_sorted)
        return f"{count:02d} {label} ({active_str})"

    raw_tokens = re.findall(r"[A-Za-z]+", s)
    parsed_days = []
    for tok in raw_tokens:
        tok_clean = tok.strip().upper()
        if tok_clean in ("DAY", "DAYS", "DAYSS", "DAYSSS", "DAILY", "EX", "UPTO", "WEEKLY", "TRAIN", "EXCEPT", "EXC"):
            continue
        if tok_clean in _DAY_ALIASES:
            canonical = _DAY_ALIASES[tok_clean]
            if canonical not in parsed_days:
                parsed_days.append(canonical)

    if not parsed_days or len(parsed_days) == 7:
        return "(DAILY)"

    active_sorted = sorted(parsed_days, key=lambda d: _DAY_NAMES.index(d))
    missing_sorted = [d for d in _DAY_NAMES if d not in active_sorted]
    count = len(active_sorted)
    if count == 7 or count == 0:
        return "(DAILY)"
    if count in (4, 5, 6):
        missing_str = ", ".join(missing_sorted)
        return f"{count:02d} DAYS (Except \u2013 {missing_str})"
    label = "DAY" if count == 1 else "DAYS"
    active_str = ", ".join(active_sorted)
    return f"{count:02d} {label} ({active_str})"


def setup_irctc_auth_cli() -> dict:
    """
    Interactive CLI helper to prompt user for active IRCTC Cookie & GREQ Token.
    """
    print("\n==================================================")
    print(" 🔐 IRCTC AUTHENTICATION SETUP")
    print("==================================================")
    cookie = input("[AUTH] Paste IRCTC Cookie: ").strip()
    greq = input("[AUTH] Paste IRCTC greq token: ").strip()
    print("==================================================\n")

    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "cookie": cookie,
        "greq": greq,
        "bmirak": "webbm",
        "Accept": "application/json, text/plain, */*"
    }


def fetch_train_irctc(train_no: str, headers: dict) -> Optional[dict]:
    """
    Fetch train schedule directly from IRCTC Official JSON API.
    """
    train_no = str(train_no).strip()
    url = f"https://www.irctc.co.in/eticketing/protected/mapps1/trnscheduleenquiry/{train_no}"
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        if response.status_code != 200:
            print(f"[WARN] IRCTC API returned status code {response.status_code} for train {train_no}")
            return None

        data = response.json()
        days_bitmask = "".join([
            "1" if data.get("trainRunsOnMon") == "Y" else "0",
            "1" if data.get("trainRunsOnTue") == "Y" else "0",
            "1" if data.get("trainRunsOnWed") == "Y" else "0",
            "1" if data.get("trainRunsOnThu") == "Y" else "0",
            "1" if data.get("trainRunsOnFri") == "Y" else "0",
            "1" if data.get("trainRunsOnSat") == "Y" else "0",
            "1" if data.get("trainRunsOnSun") == "Y" else "0",
        ])

        stations = data.get("stationList", [])
        if len(stations) < 2:
            print(f"[WARN] Insufficient stations returned by IRCTC API for train {train_no}")
            return None

        origin = stations[0]
        dest = stations[-1]

        origin_code = str(data.get("stationFrom", origin.get("stationCode", ""))).strip()
        dest_code = str(data.get("stationTo", dest.get("stationCode", ""))).strip()

        dep_raw = origin.get("departureTime", "") or origin.get("departureTime", "")
        arr_raw = dest.get("arrivalTime", "") or dest.get("arrivalTime", "")

        station_codes = [stn.get("stationCode", "").strip() for stn in stations if stn.get("stationCode")]

        return {
            "train_number": str(data.get("trainNumber", train_no)),
            "train_name": str(data.get("trainName", f"TRAIN {train_no}")).strip(),
            "origin_code": origin_code,
            "dest_code": dest_code,
            "dep_time": _normalise_time(dep_raw),
            "arr_time": _normalise_time(arr_raw),
            "run_days": _format_run_days(days_bitmask),
            "days_bitmask": days_bitmask,
            "station_codes": station_codes,
            "coaches": "20 Coaches"
        }
    except Exception as e:
        print(f"[ERROR] IRCTC API Fetch Error for train {train_no}: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) > 1:
        tn = sys.argv[1]
        print(f"Testing IRCTC API fetch for train {tn}...")
        headers = setup_irctc_auth_cli()
        res = fetch_train_irctc(tn, headers)
        print("Result:", res)
    else:
        print("Usage: python backend/legacy_irctc.py <train_number>")
