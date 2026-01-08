GENERIC_PHRASES = [
    "v dnešnej dobe",
    "je potrebné zdôrazniť",
    "táto práca sa zameriava",
    "cieľom tejto práce je",
    "v rámci tejto práce",
    "na základe uvedeného",
    "v nasledujúcej kapitole",
    "je možné konštatovať",
    "z hľadiska problematiky",
    "ako už bolo spomenuté",
    "v súčasnosti",
    "vo všeobecnosti platí",
    "na druhej strane",
    "je dôležité poznamenať",
    "v neposlednom rade",
    "z vyššie uvedeného vyplýva",
]

import re
import glob
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon

def generic_phrase_score(text, phrases=GENERIC_PHRASES):
    text_low = text.lower()

    counts = {}
    total = 0

    for p in phrases:
        c = len(re.findall(re.escape(p), text_low))
        counts[p] = c
        total += c
    
    words = re.findall(r"\b\w+\b", text_low)
    n_words = len(words)

    if n_words == 0:
        return 0
    
    score = total / n_words * 1000 # na 1000 slov
    return score

results = []
for bc_path in glob.glob("prace/*,bakalarka.txt"):
    dip_path = bc_path.replace(",bakalarka.txt", ",diplomovka.txt")

    with open(bc_path, encoding="utf-8") as f:
        bc_text = f.read()
    with open(dip_path, encoding="utf-8") as f:
        dip_text = f.read()
    
    results.append({
        "student": bc_path.split("/")[-1].split(",")[0],
        "bc_generic_phrase_score": generic_phrase_score(bc_text),
        "dip_generic_phrase_score": generic_phrase_score(dip_text),
    })

df = pd.DataFrame(results).dropna()

stat, p = wilcoxon(df["bc_generic_phrase_score"], df["dip_generic_phrase_score"], alternative="less")
print(stat, p)