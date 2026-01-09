#!/usr/bin/env python3
import argparse, json
import numpy as np
import pandas as pd

from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score,
    precision_score, recall_score, f1_score,
    confusion_matrix
)

def featury(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ["total_urls", "bad_urls", "bad_rate"]:
        df[c] = pd.to_numeric(df.get(c), errors="coerce").fillna(0)

    base = df[["total_urls", "bad_urls", "bad_rate"]].reset_index(drop=True)

    rows = []
    for _, r in df.iterrows():
        try:
            d = json.loads(r.get("bad_by_type_json", "{}"))
            if not isinstance(d, dict):
                d = {}
        except Exception:
            d = {}
        row = {}
        for k, v in d.items():
            try:
                row[f"err_{k}"] = int(v)
            except Exception:
                pass
        rows.append(row)

    err = pd.DataFrame(rows).fillna(0).reset_index(drop=True)

    bad = df["bad_urls"].to_numpy()
    for c in err.columns:
        col = err[c].to_numpy(dtype=float)
        err[c] = np.where(bad > 0, col / bad, 0.0)

    return pd.concat([base, err], axis=1)

def ciel(df: pd.DataFrame) -> np.ndarray:
    y = pd.to_numeric(df.get("year"), errors="coerce")
    return (y >= 2023).astype(int).to_numpy()

def zarovnaj(Xa: pd.DataFrame, Xb: pd.DataFrame):
    cols = sorted(set(Xa.columns) | set(Xb.columns))
    return Xa.reindex(columns=cols, fill_value=0), Xb.reindex(columns=cols, fill_value=0)

def main():
    ap = argparse.ArgumentParser(description="GaussianNB: train+val -> test")
    ap.add_argument("--train", default="train.csv")
    ap.add_argument("--val", default="val.csv")
    ap.add_argument("--test", default="test.csv")
    ap.add_argument("--chyby", type=int, default=0)
    args = ap.parse_args()

    train = pd.read_csv(args.train).dropna(subset=["year"])
    val  = pd.read_csv(args.val).dropna(subset=["year"])
    test = pd.read_csv(args.test).dropna(subset=["year"])

    fit = pd.concat([train, val], ignore_index=True)

    X_fit = featury(fit)
    X_tst = featury(test)
    X_fit, X_tst = zarovnaj(X_fit, X_tst)

    y_fit = ciel(fit)
    y_tst = ciel(test)

    m = GaussianNB()
    m.fit(X_fit, y_fit)

    y_hat = m.predict(X_tst)

    acc  = accuracy_score(y_tst, y_hat)
    bacc = balanced_accuracy_score(y_tst, y_hat)
    prec = precision_score(y_tst, y_hat, zero_division=0)
    rec  = recall_score(y_tst, y_hat, zero_division=0)
    f1   = f1_score(y_tst, y_hat, zero_division=0)
    cm   = confusion_matrix(y_tst, y_hat)

    print("=== TEST ===")
    print("1 = rok >= 2023")
    print(f"acc  : {acc:.3f}")
    print(f"bacc : {bacc:.3f}")
    print(f"prec : {prec:.3f}")
    print(f"rec  : {rec:.3f}")
    print(f"f1   : {f1:.3f}")
    print("cm   : [[TN FP],[FN TP]]")
    print(cm)


if __name__ == "__main__":
    main()