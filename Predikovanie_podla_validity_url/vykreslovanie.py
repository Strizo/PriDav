#!/usr/bin/env python3
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt


def main():
    ap = argparse.ArgumentParser(
        description="Jeden graf: percentuálne typy chýb (stacked stĺpce) + čierna čiara (priemer bad_rate) + kĺzavý priemer + počet prác."
    )
    ap.add_argument("csv_path", help="Cesta k all_docs.csv (1 riadok = 1 práca)")
    ap.add_argument("--out", default=None, help="Ak zadáš, uloží obrázok (napr. graf.png). Inak zobrazí okno.")
    ap.add_argument("--topk", type=int, default=8,
                    help="Koľko najčastejších typov chýb zobraziť (ostatné sa zlúčia do 'iny').")
    ap.add_argument("--ma", type=int, default=3,
                    help="Okno kĺzavého priemeru (v rokoch). Default 3. (1 = bez vyhladzovania)")
    args = ap.parse_args()

    df = pd.read_csv(args.csv_path)

    df["year"] = pd.to_numeric(df.get("year"), errors="coerce")
    df = df.dropna(subset=["year"]).copy()
    df["year"] = df["year"].astype(int)

    df["bad_rate"] = pd.to_numeric(df.get("bad_rate"), errors="coerce")
    df["bad_by_type_json"] = df.get("bad_by_type_json", "{}").fillna("{}")

    docs_per_year = (
        df.groupby("year", as_index=True)
        .size()
        .sort_index()
        .rename("pocet_prac")
    )

    # --- čiara: priemer bad_rate na prácu v danom roku ---
    mean_bad_rate = (
        df.groupby("year", as_index=True)["bad_rate"]
        .mean()
        .sort_index()
        .rename("mean_bad_rate")
    )

    # --- kĺzavý priemer (vyhladenie) ---
    # center=True -> hodnota je "v strede okna" (vizuálne najčistejšie)
    ma_window = max(1, int(args.ma))
    mean_bad_rate_ma = (
        mean_bad_rate.rolling(window=ma_window, center=True, min_periods=1).mean()
        .rename(f"ma_{ma_window}")
    )

    records = []
    for _, r in df.iterrows():
        year = int(r["year"])
        try:
            d = json.loads(r["bad_by_type_json"])
            if not isinstance(d, dict):
                d = {}
        except Exception:
            d = {}

        for typ, pocet in d.items():
            try:
                p = int(pocet)
            except Exception:
                continue
            if p > 0:
                records.append((year, str(typ), p))

    if not records:
        raise SystemExit("V dátach nie sú žiadne nefunkčné odkazy (bad_by_type_json je prázdne).")

    long_df = pd.DataFrame(records, columns=["year", "typ", "pocet"])

    pivot = (
        long_df
        .groupby(["year", "typ"], as_index=False)["pocet"]
        .sum()
        .pivot(index="year", columns="typ", values="pocet")
        .fillna(0)
        .sort_index()
    )

    total_per_type = pivot.sum(axis=0).sort_values(ascending=False)
    top_types = total_per_type.head(args.topk).index.tolist()

    pivot_top = pivot[top_types].copy()
    other_cols = [c for c in pivot.columns if c not in top_types]
    if other_cols:
        pivot_top["iny"] = pivot[other_cols].sum(axis=1)

    pivot = pivot_top

    yearly_totals = pivot.sum(axis=1)
    pivot_pct = pivot.div(yearly_totals.replace(0, pd.NA), axis=0).fillna(0) * 100

    all_years = sorted(set(pivot_pct.index) | set(mean_bad_rate.index) | set(docs_per_year.index))
    pivot_pct = pivot_pct.reindex(all_years).fillna(0)
    mean_bad_rate = mean_bad_rate.reindex(all_years)
    mean_bad_rate_ma = mean_bad_rate_ma.reindex(all_years)
    docs_per_year = docs_per_year.reindex(all_years).fillna(0).astype(int)

    fig, ax_bar = plt.subplots()

    bottom = pd.Series(0.0, index=all_years)
    for col in pivot_pct.columns:
        vals = pivot_pct[col].values
        ax_bar.bar(all_years, vals, bottom=bottom.values, label=col)
        bottom += pivot_pct[col]

    ax_bar.set_xlabel("Rok")
    ax_bar.set_ylabel("Zastúpenie typov chýb (%)")
    ax_bar.set_ylim(0, 100)
    ax_bar.set_title(
        "Nefunkčné odkazy v čase\n"
        "Percentuálne typy chýb (stĺpce) + priemer nefunkčnosti (čiara) + kĺzavý priemer + počet prác"
    )

    ax_line = ax_bar.twinx()
    ax_line.plot(all_years, mean_bad_rate.values, color="black", marker="o", linewidth=1.5, zorder=10, label="Priemer bad_rate")
    ax_line.plot(all_years, mean_bad_rate_ma.values, color="black", linewidth=3, zorder=11, label=f"Kĺzavý priemer ({ma_window})")
    ax_line.set_ylabel("Priemer nefunkčných URL na prácu (mean bad_rate)")
    ax_line.set_ylim(0, 1)


    for y in all_years:
        n = int(docs_per_year.loc[y])
        ax_bar.annotate(
            str(n),
            (y, 100),
            textcoords="offset points",
            xytext=(0, 4),
            ha="center",
            va="bottom",
        )

    ax_bar.legend(title="Typ chyby", loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    ax_line.legend(loc="upper left", bbox_to_anchor=(1.02, 0.55), borderaxespad=0)

    fig.tight_layout()

    if args.out:
        plt.savefig(args.out, bbox_inches="tight", dpi=200)
        print(f"Uložené: {args.out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()