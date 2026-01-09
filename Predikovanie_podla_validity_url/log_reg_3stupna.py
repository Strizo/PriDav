#!/usr/bin/env python3
import argparse
import json
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["total_urls"] = pd.to_numeric(df.get("total_urls"), errors="coerce").fillna(0)
    df["bad_urls"] = pd.to_numeric(df.get("bad_urls"), errors="coerce").fillna(0)
    df["bad_rate"] = pd.to_numeric(df.get("bad_rate"), errors="coerce").fillna(0)

    base = df[["total_urls", "bad_urls", "bad_rate"]].reset_index(drop=True)

    rows = []
    for _, r in df.iterrows():
        s = r.get("bad_by_type_json", "{}")
        try:
            d = json.loads(s) if isinstance(s, str) else {}
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

    X = pd.concat([base, err], axis=1)
    return X


def build_target(df: pd.DataFrame) -> np.ndarray:
    year = pd.to_numeric(df.get("year"), errors="coerce")
    return (year >= 2023).astype(int).to_numpy()


def align_columns(X_train: pd.DataFrame, X_test: pd.DataFrame):
    all_cols = sorted(set(X_train.columns) | set(X_test.columns))
    X_train2 = X_train.reindex(columns=all_cols, fill_value=0)
    X_test2 = X_test.reindex(columns=all_cols, fill_value=0)
    return X_train2, X_test2


def main():
    ap = argparse.ArgumentParser(description="Natrénuj finálny LogReg (stupeň 3) na train+val a otestuj na test.")
    ap.add_argument("--train", default="train.csv", help="Cesta k train.csv (default: train.csv)")
    ap.add_argument("--val", default="val.csv", help="Cesta k val.csv (default: val.csv)")
    ap.add_argument("--test", default="test.csv", help="Cesta k test.csv (default: test.csv)")
    ap.add_argument("--show-mistakes", type=int, default=0,
                    help="Vypísať N najistejších chýb na teste (default: 0)")
    args = ap.parse_args()

    train_df = pd.read_csv(args.train)
    val_df = pd.read_csv(args.val)
    test_df = pd.read_csv(args.test)

    train_df = train_df.dropna(subset=["year"])
    val_df = val_df.dropna(subset=["year"])
    test_df = test_df.dropna(subset=["year"])

    fit_df = pd.concat([train_df, val_df], ignore_index=True)

    X_fit = build_features(fit_df)
    X_test = build_features(test_df)
    X_fit, X_test = align_columns(X_fit, X_test)

    y_fit = build_target(fit_df)
    y_test = build_target(test_df)

    model = Pipeline([
        ("poly", PolynomialFeatures(degree=3, include_bias=False)),
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=6000,
            C=0.1,
            class_weight="balanced"
        ))
    ])

    model.fit(X_fit, y_fit)

    y_pred = model.predict(X_test)

    # merania spravnosti
    acc = accuracy_score(y_test, y_pred)
    bacc = balanced_accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred)

    print("=== Výsledok na TEST sete ===")
    print("Trieda 1 = rok >= 2023")
    print(f"accuracy          : {acc:.3f}")
    print(f"balanced_accuracy : {bacc:.3f}")
    print(f"precision (class1): {prec:.3f}")
    print(f"recall (class1)   : {rec:.3f}")
    print(f"f1 (class1)       : {f1:.3f}")
    print("confusion matrix [ [TN FP], [FN TP] ]:")
    print(cm)

    print("\n--- classification report ---")

if __name__ == "__main__":
    main()