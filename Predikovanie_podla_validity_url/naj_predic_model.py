#!/usr/bin/env python3
import argparse
import json
import numpy as np
import pandas as pd

from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def nacitaj_priprav(csv_path: str):
    df = pd.read_csv(csv_path)

    # cieľ: 0 = <2023, 1 = >=2023
    df["year"] = pd.to_numeric(df.get("year"), errors="coerce")
    df = df.dropna(subset=["year"]).copy()
    y = (df["year"] >= 2023).astype(int).to_numpy()

    df["total_urls"] = pd.to_numeric(df.get("total_urls"), errors="coerce").fillna(0)
    df["bad_urls"] = pd.to_numeric(df.get("bad_urls"), errors="coerce").fillna(0)
    df["bad_rate"] = pd.to_numeric(df.get("bad_rate"), errors="coerce").fillna(0)

    base = df[["total_urls", "bad_urls", "bad_rate"]].reset_index(drop=True)

    err_rows = []
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
        err_rows.append(row)

    err = pd.DataFrame(err_rows).fillna(0).reset_index(drop=True)

    bad = df["bad_urls"].to_numpy()
    for c in err.columns:
        col = err[c].to_numpy(dtype=float)
        err[c] = np.where(bad > 0, col / bad, 0.0)

    X = pd.concat([base, err], axis=1)
    feature_names = X.columns.tolist()
    return X, y, feature_names


def vyhodnot_model(nazov: str, model, X, y):
    loo = LeaveOneOut()

    y_pred = cross_val_predict(model, X, y, cv=loo, method="predict")

    acc = accuracy_score(y, y_pred)
    bacc = balanced_accuracy_score(y, y_pred)
    prec = precision_score(y, y_pred, zero_division=0)
    rec = recall_score(y, y_pred, zero_division=0)
    f1 = f1_score(y, y_pred, zero_division=0)
    cm = confusion_matrix(y, y_pred)

    return {
        "model": nazov,
        "accuracy": acc,
        "balanced_accuracy": bacc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "cm": cm,
    }


def main():
    ap = argparse.ArgumentParser(
        description="LOOCV porovnanie: logistická regresia (1/2/3 stupeň) + Naive Bayes."
    )
    ap.add_argument("csv_path", help="all_docs.csv (agregované dáta)")
    args = ap.parse_args()

    X, y, feature_names = nacitaj_priprav(args.csv_path)
    print(f"Vzorky: {len(y)} | Znaky: {X.shape[1]}")
    print("Cieľ: 0 = <2023, 1 = >=2023\n")

    models = [
        ("LogReg lineárna (stupeň 1)",
         Pipeline([
             ("scaler", StandardScaler()),
             ("clf", LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced"))
         ])),
        ("LogReg polynóm (stupeň 2)",
         Pipeline([
             ("poly", PolynomialFeatures(degree=2, include_bias=False)),
             ("scaler", StandardScaler()),
             ("clf", LogisticRegression(max_iter=4000, C=0.3, class_weight="balanced"))
         ])),
        ("LogReg polynóm (stupeň 3)",
         Pipeline([
             ("poly", PolynomialFeatures(degree=3, include_bias=False)),
             ("scaler", StandardScaler()),
             ("clf", LogisticRegression(max_iter=6000, C=0.1, class_weight="balanced"))
         ])),
        ("Naive Bayes (GaussianNB)",
         GaussianNB()),
    ]

    vysledky = []
    for name, model in models:
        res = vyhodnot_model(name, model, X, y)
        vysledky.append(res)

    vysledky_sorted = sorted(vysledky, key=lambda r: r["balanced_accuracy"], reverse=True)

    print("=== Výsledky (LOOCV) ===")
    for r in vysledky_sorted:
        print(f"\n{r['model']}")
        print(f"  accuracy          : {r['accuracy']:.3f}")
        print(f"  balanced_accuracy : {r['balanced_accuracy']:.3f}")
        print(f"  precision (class1): {r['precision']:.3f}")
        print(f"  recall (class1)   : {r['recall']:.3f}")
        print(f"  f1 (class1)       : {r['f1']:.3f}")
        print("  confusion matrix [ [TN FP], [FN TP] ]:")
        print(f"  {r['cm']}")

if __name__ == "__main__":
    main()