#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests

URL_RE = re.compile(
    r"""(?xi)
    \b
    (https?://[^\s<>"'(){}\[\]]+)
    """
)

# niektoré URL bývajú v texte ukončené bodkou/čiarkou atď.
TRAILING_PUNCT = ".,;:!?)]]}>'\""

def extract_urls(text: str) -> list[str]:
    urls = []
    for m in URL_RE.finditer(text):
        u = m.group(1).strip()
        u = u.rstrip(TRAILING_PUNCT)
        # základná validácia
        p = urlparse(u)
        if p.scheme in ("http", "https") and p.netloc:
            urls.append(u)
    return urls

def iter_text_files(root: Path, exts: set[str]) -> list[Path]:
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            files.append(p)
    return files

def check_url(url: str, timeout: float) -> tuple[bool, str]:
    """
    Vracia: (ok, info)
    ok=True ak je odpoveď < 400
    """
    headers = {"User-Agent": "url-checker/1.0 (+https://example.local)"}

    try:
        # HEAD je rýchly, ale niektoré servery ho odmietajú -> fallback na GET
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

def main():
    ap = argparse.ArgumentParser(description="Extract URLs from text files and check connectivity.")
    ap.add_argument("path", help="Priečinok alebo súbor")
    ap.add_argument("--ext", default=".txt,.md,.log",
                    help="Čiarkou oddelené prípony (default: .txt,.md,.log)")
    ap.add_argument("--timeout", type=float, default=8.0, help="Timeout v sekundách (default: 8)")
    ap.add_argument("--unique", action="store_true", help="Skontrolovať len unikátne URL (default: false)")
    args = ap.parse_args()

    target = Path(args.path)
    exts = {e.strip().lower() if e.strip().startswith(".") else "." + e.strip().lower()
            for e in args.ext.split(",") if e.strip()}

    if not target.exists():
        print(f"Neexistuje: {target}", file=sys.stderr)
        sys.exit(2)

    files: list[Path]
    if target.is_file():
        files = [target]
    else:
        files = iter_text_files(target, exts)

    all_urls: list[str] = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            all_urls.extend(extract_urls(text))
        except Exception:
            # ak niečo zlyhá, preskočíme súbor
            continue

    if args.unique:
        # zachovať poradie
        seen = set()
        uniq = []
        for u in all_urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        all_urls = uniq

    if not all_urls:
        print("Nenašli sa žiadne URL.")
        return

    ok_list = []
    bad_list = []

    for i, url in enumerate(all_urls, 1):
        ok, info = check_url(url, args.timeout)
        status = "OK" if ok else "BAD"
        print(f"[{i}/{len(all_urls)}] {status:3} {url} ({info})")
        (ok_list if ok else bad_list).append((url, info))

    print("\n=== SUMÁR ===")
    print(f"Spolu URL:        {len(all_urls)}")
    print(f"Dostupné (OK):    {len(ok_list)}")
    print(f"Nedostupné (BAD): {len(bad_list)}")

    if bad_list:
        print("\n--- Nedostupné ---")
        for url, info in bad_list:
            print(f"{url}  ->  {info}")

if __name__ == "__main__":
    main()