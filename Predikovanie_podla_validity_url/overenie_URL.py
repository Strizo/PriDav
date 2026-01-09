#!/usr/bin/env python3
import argparse
import csv
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

URL_RE = re.compile(r"""(?xi)\b(https?://[^\s<>"'(){}\[\]]+)""")
TRAILING_PUNCT = ".,;:!?)]]}>'\""

YEAR_MIN = 2000
YEAR_MAX_EXCL = 2027 

def extract_urls(text: str) -> list[str]:
    urls: list[str] = []
    for m in URL_RE.finditer(text):
        u = m.group(1).strip().rstrip(TRAILING_PUNCT)
        p = urlparse(u)
        if p.scheme in ("http", "https") and p.netloc:
            urls.append(u)
    return urls

def find_year_in_text(text: str):

    for tok in re.findall(r"\d+", text):
        try:
            n = int(tok)
        except ValueError:
            continue
        if YEAR_MIN < n < YEAR_MAX_EXCL:
            return n
    return float("nan")

def degree_from_filename(file_path: Path):
    stem = file_path.stem 
    if "," not in stem:
        return float("nan")
    left, right = stem.split(",", 1)
    kind = right.strip().lower()
    if "bakalarka" in kind:
        return "bakalarka"
    if "diplomovka" in kind:
        return "diplomovka"
    return float("nan")

def iter_text_files(root: Path, exts: set[str]) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]

def check_url(url: str, timeout: float) -> tuple[bool, str]:
    headers = {"User-Agent": "url-checker/1.0"}
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code in (405, 403) or r.status_code >= 500:
#            print("wtf")
            r = requests.get(url, allow_redirects=True, timeout=timeout, headers=headers, stream=True)

        code = r.status_code
        return (code < 400), f"HTTP {code}"
    except requests.exceptions.SSLError:
        return False, "SSL error"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.Timeout:
        return False, "Timeout"
    except Exception as e:
        return False, f"Error: {type(e).__name__}"

def nan_to_str(x):
    if isinstance(x, float) and math.isnan(x):
        return "NaN"
    return str(x)

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["url", "ok", "info", "year", "typ_prace", "source_file"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description="Vytiahne URL z textov a skontroluje dostupnosť + export do CSV.")
    ap.add_argument("path", help="Priečinok alebo súbor")
    ap.add_argument("--ext", default=".txt,.md,.log",
                    help="Čiarkou oddelené prípony (default: .txt,.md,.log)")
    ap.add_argument("--timeout", type=float, default=8.0, help="Timeout v sekundách (default: 8)")
    ap.add_argument("--unique", action="store_true",
                    help="Skontrolovať len unikátne URL (naprieč všetkými súbormi) – berie prvý výskyt")
    ap.add_argument("--csv", default=None,
                    help="Cesta k CSV výstupu, napr. out.csv")
    args = ap.parse_args()

    target = Path(args.path)
    exts = {e.strip().lower() if e.strip().startswith(".") else "." + e.strip().lower()
            for e in args.ext.split(",") if e.strip()}

    if not target.exists():
        print(f"Neexistuje: {target}", file=sys.stderr)
        sys.exit(2)

    files = [target] if target.is_file() else iter_text_files(target, exts)

    found: list[dict] = [] 
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        year = find_year_in_text(text)
        typ = degree_from_filename(f)

        urls = extract_urls(text)
        if not urls:
            continue

        for u in urls:
            found.append({
                "url": u,
                "source_file": str(f),
                "year": year,
                "typ_prace": typ
            })

    if not found:
        print("Nenašli sa žiadne URL.")
        return

    if args.unique:
        seen = set()
        uniq = []
        for row in found:
            u = row["url"]
            if u not in seen:
                seen.add(u)
                uniq.append(row)
        found = uniq

    results_csv: list[dict] = []
    ok_count = 0
    bad_count = 0

    for i, row in enumerate(found, 1):
        url = row["url"]
        src = row["source_file"]
        year = row["year"]
        typ = row["typ_prace"]

        ok, info = check_url(url, args.timeout)
        status = "OK" if ok else "BAD"

        print(
            f"[{i}/{len(found)}] {status:3} {url} ({info})  "
            f"<- {src} | rok={nan_to_str(year)} | typ={nan_to_str(typ)}"
        )

        results_csv.append({
            "url": url,
            "ok": "1" if ok else "0",
            "info": info,
            "year": nan_to_str(year),
            "typ_prace": nan_to_str(typ),
            "source_file": src
        })

        if ok:
            ok_count += 1
        else:
            bad_count += 1


#    print('lol')
    if args.csv:
        out = Path(args.csv)
        write_csv(out, results_csv)
        print('Funguje')

if __name__ == "__main__":
    main()