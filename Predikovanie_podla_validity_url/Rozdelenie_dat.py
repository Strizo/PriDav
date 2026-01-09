#!/usr/bin/env python3
import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HTTP_RE = re.compile(r"^\s*HTTP\s+(\d{3})\s*$", re.IGNORECASE)

def is_nan_str(x: str) -> bool:
    if x is None:
        return True
    s = str(x).strip().lower()
    return s in ("", "nan", "none", "null")

def normalize_label(x: str) -> str:
    return "NaN" if is_nan_str(x) else str(x).strip()

def safe_int(x: str, default=None):
    try:
        return int(str(x).strip())
    except Exception:
        return default

def categorize_info(info: str) -> str:

    if info is None:
        return "other"
    s = str(info).strip()

    m = HTTP_RE.match(s)
    if m:
        code = int(m.group(1))
        if 400 <= code <= 499:
            return f"http_{code}"
        if 500 <= code <= 599:
            return "http_5xx"
        return f"http_{code}"

    s_low = s.lower()
    if "timeout" in s_low:
        return "timeout"
    if "ssl" in s_low:
        return "ssl"
    if "connection" in s_low:
        return "connection"
    return "other"

def majority_vote(values: list[str]) -> str:
    cleaned = [normalize_label(v) for v in values if not is_nan_str(v)]
    if not cleaned:
        return "NaN"
    c = Counter(cleaned)
    top = max(c.values())
    winners = sorted([k for k, v in c.items() if v == top])
    return winners[0]

def year_to_bin(year_str: str) -> str:
    y = safe_int(year_str, default=None)
    if y is None:
        return "year_nan"
    if 2021 <= y <= 2022:
        return "2021-2022"
    if 20023 <= y <= 2024:
        return "2023-2024"
    return "year_other"

def stratified_split(rows: list[dict], seed: int, train_ratio: float, val_ratio: float):
    """
    Stratifikácia podľa kombinácie: typ_prace + year_bin
    """
    rng = random.Random(seed)
    groups = defaultdict(list)

    for r in rows:
        key = (r["typ_prace"], r["year_bin"])
        groups[key].append(r)

    train, val, test = [], [], []

    for key, items in groups.items():
        rng.shuffle(items)
        n = len(items)

        n_train = int(round(n * train_ratio))
        n_val = int(round(n * val_ratio))

        if n_train + n_val > n:
            n_val = max(0, n - n_train)

        train.extend(items[:n_train])
        val.extend(items[n_train:n_train + n_val])
        test.extend(items[n_train + n_val:])

    rng.shuffle(train)
    rng.shuffle(val)
    rng.shuffle(test)
    return train, val, test

def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source_file",
        "year",
        "typ_prace",
        "total_urls",
        "bad_urls",
        "bad_rate",
        "bad_by_type_json",
        "bad_by_info_json",
        "year_bin",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser(
        description="Agreguje URL-CSV na úroveň dokumentu + stratifikovaný train/val/test split podľa typu práce aj roku."
    )
    ap.add_argument("input_csv", help="CSV so stĺpcami: url,ok,info,year,typ_prace,source_file")
    ap.add_argument("--outdir", default="out_dataset", help="Výstupný priečinok (default: out_dataset)")
    ap.add_argument("--seed", type=int, default=42, help="Seed pre split (default: 42)")
    ap.add_argument("--train", type=float, default=0.60, help="Train ratio (default: 0.60)")
    ap.add_argument("--val", type=float, default=0.10, help="Val ratio (default: 0.10)")
    ap.add_argument("--write-all", action="store_true", help="Zapíše aj all_docs.csv")
    args = ap.parse_args()

    if args.train <= 0 or args.val < 0 or args.train + args.val >= 1:
        raise SystemExit("Zlé pomery splitu. Musí platiť: train>0, val>=0, train+val<1")

    in_path = Path(args.input_csv)
    if not in_path.exists():
        raise SystemExit(f"Neexistuje: {in_path}")

    docs = defaultdict(list)
    with in_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"url", "ok", "info", "year", "typ_prace", "source_file"}
        if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
            raise SystemExit(f"CSV musí mať stĺpce: {sorted(required)}")

        for row in reader:
            src = normalize_label(row.get("source_file", ""))
            if src == "NaN":
                continue
            docs[src].append(row)

    if not docs:
        raise SystemExit("V CSV sa nenašli žiadne validné riadky so source_file.")

    doc_rows = []
    for source_file, rows in docs.items():
        year_major = majority_vote([r.get("year", "") for r in rows])
        typ_major = majority_vote([r.get("typ_prace", "") for r in rows])
        ybin = year_to_bin(year_major)

        total_urls = len(rows)
        bad_by_type = Counter()
        bad_by_info = Counter()
        bad_urls = 0

        for r in rows:
            ok_val = safe_int(r.get("ok", ""), default=None)
            info = normalize_label(r.get("info", ""))
            if ok_val == 0:
                bad_urls += 1
                bad_by_info[info] += 1
                bad_by_type[categorize_info(info)] += 1

        bad_rate = (bad_urls / total_urls) if total_urls > 0 else 0.0

        doc_rows.append({
            "source_file": source_file,
            "year": year_major,
            "typ_prace": typ_major,
            "total_urls": total_urls,
            "bad_urls": bad_urls,
            "bad_rate": f"{bad_rate:.6f}",
            "bad_by_type_json": json.dumps(dict(bad_by_type), ensure_ascii=False),
            "bad_by_info_json": json.dumps(dict(bad_by_info), ensure_ascii=False),
            "year_bin": ybin,
        })

    train_rows, val_rows, test_rows = stratified_split(
        doc_rows, seed=args.seed, train_ratio=args.train, val_ratio=args.val
    )

    outdir = Path(args.outdir)
    write_csv(outdir / "train.csv", train_rows)
    write_csv(outdir / "val.csv", val_rows)
    write_csv(outdir / "test.csv", test_rows)

    if args.write_all:
        write_csv(outdir / "all_docs.csv", doc_rows)

    print("Hotovo.")
    print(f"Dokumenty spolu: {len(doc_rows)}")
    print(f"Train: {len(train_rows)} | Val: {len(val_rows)} | Test: {len(test_rows)}")
    print(f"Výstup: {outdir.resolve()}")

if __name__ == "__main__":
    main()