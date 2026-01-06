import re
import numpy as np
import glob
import pandas as pd
from scipy.stats import wilcoxon

citation_pattern = re.compile(r"\([^()]+,\s*\d{4}\)")

def extract_citations(text):
    return citation_pattern.findall(text)

def split_references(text):
    parts = re.split(r"\n\s*(literatúra|references)\s*\n", text, flags=re.I)
    if len(parts) > 1:
        return parts[0], parts[-1]
    return text, ""

doi_pattern = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.I)

def citation_quality_score(text):
    body, refs = split_references(text)

    citations = extract_citations(body)
    ref_count = sum(1 for line in refs.splitlines() if len(line.strip()) > 20)

    if len(citations) == 0:
        return np.nan

    missing_refs = max(0, len(citations) - ref_count)
    doi_errors = sum(
        "doi" in r.lower() and not doi_pattern.search(r)
        for r in refs.splitlines()
    )

    score = (missing_refs + doi_errors) / len(citations)
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
        "bc_citation_score": citation_quality_score(bc_text),
        "dip_citation_score": citation_quality_score(dip_text),
    })

df = pd.DataFrame(results).dropna()
print((df["bc_citation_score"] == df["dip_citation_score"]).mean())

stat, p = wilcoxon(df["bc_citation_score"], df["dip_citation_score"], alternative="less")
print(stat, p)