#!/usr/bin/env python3
import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

URL_RE = re.compile(r"""(?xi)\b(https?://[^\s<>"'(){}\[\]]+)""")
TRAILING_PUNCT = ".,;:!?)]]}>'\""

def extract_urls(text: str) -> list[str]:
    urls = []
    for m in URL_RE.finditer(text):
        u = m.group(1).strip().rstrip(TRAILING_PUNCT)
        p = urlparse(u)
        if p.scheme in ("http", "https") and p.netloc:
            urls.append(u)
    return urls

def iter_text_files(root: Path, exts: set[str]) -> list[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in exts]

def check_url(url: str, timeout: float) -> tuple[bool, str]:
    headers = {"User-Agent": "url-checker/1.0"}
    try:
        r = requests.head(url, allow_redirects=True, timeout=timeout, headers=headers)
        if r.status_code in (405, 403) or r.status_code >= 500:
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

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["url", "ok", "info", "source_file"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(description="Extract URLs from text files and check connectivity.")
    ap.add_argument("path", help="Priečinok alebo súbor")
    ap.add_argument("--ext", default=".txt,.md,.log",
                    help="Čiarkou oddelené prípony (default: .txt,.md,.log)")
    ap.add_argument("--timeout", type=float, default=8.0, help="Timeout v sekundách (default: 8)")
    ap.add_argument("--unique", action="store_true",
                    help="Skontrolovať len unikátne URL (naprieč všetkými súbormi)")
    ap.add_argument("--csv", default=None,
                    help="Cesta k CSV výstupu, napr. out.csv")

    args = ap.parse_args()

    target = Path(args.path)
    exts = {e.strip().lower() if e.strip().startswith(".") else "." + e.strip().lower()
            for e in args.ext.split(",") if e.strip()}

    if not target.exists():
        print(f"Neexistuje: {target}", file=sys.stderr)
        sys.exit(2)

    if target.is_file():
        files = [target]
    else:
        files = iter_text_files(target, exts)

    # nazbierame URL + zdrojový súbor
    found: list[tuple[str, str]] = []  # (url, source_file)
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            for u in extract_urls(text):
                found.append((u, str(f)))
        except Exception:
            continue

    if not found:
        print("Nenašli sa žiadne URL.")
        return

    # unique naprieč všetkými súbormi (ponechá prvý výskyt a jeho source_file)
    if args.unique:
        seen = set()
        uniq = []
        for u, src in found:
            if u not in seen:
                seen.add(u)
                uniq.append((u, src))
        found = uniq

    results_csv: list[dict] = []
    ok_count = 0
    bad_count = 0

    for i, (url, src) in enumerate(found, 1):
        ok, info = check_url(url, args.timeout)
        status = "OK" if ok else "BAD"
        print(f"[{i}/{len(found)}] {status:3} {url} ({info})  <- {src}")

        results_csv.append({
            "url": url,
            "ok": "1" if ok else "0",
            "info": info,
            "source_file": src
        })

        if ok:
            ok_count += 1
        else:
            bad_count += 1

    print("\n=== SUMÁR ===")
    print(f"Spolu URL:        {len(found)}")
    print(f"Dostupné (OK):    {ok_count}")
    print(f"Nedostupné (BAD): {bad_count}")

    if args.csv:
        out = Path(args.csv)
        write_csv(out, results_csv)
        print(f"\nCSV uložené do: {out.resolve()}")

if __name__ == "__main__":
    main()