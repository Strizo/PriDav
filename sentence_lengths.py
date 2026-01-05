import numpy as np
from scipy.stats import entropy
import stanza
import glob
import os

# stanza.download("sk")
nlp = stanza.Pipeline("sk", processors="tokenize", tokenize_no_ssplit=False)
print("Running my file")

def sentence_lengths(text):
    doc = nlp(text)
    lengths = []
    for sent in doc.sentences:
        tokens = [w.text for w in sent.words if w.text.isalpha()]
        if len(tokens) > 2: #nechceme príliš krátke vety
            lengths.append(len(tokens))

    return lengths

def sentence_length_entropy(lengths, bin_width=2):
    if len(lengths) < 20:
        return np.nan
    
    bins = np.arange(min(lengths), max(lengths) + bin_width, bin_width)
    hist, _ = np.histogram(lengths, bins, density=True)
    hist = hist[hist > 0]

    return entropy(hist)

results = []

for bc_path in glob.glob("prace/*,bakalarka.txt"):
    dip_path = bc_path.replace(",bakalarka.txt", ",diplomovka.txt")

    with open(bc_path, encoding="utf-8") as f:
        bc_text = f.read()
    with open(dip_path, encoding="utf-8") as f:
        dip_text = f.read()

    bc_lengths = sentence_lengths(bc_text)
    dip_lengths = sentence_lengths(dip_text)

    results.append({
        "student": os.path.basename(bc_path).split(",")[0],
        "bc_entropy": sentence_length_entropy(bc_lengths),
        "mgr_entropy": sentence_length_entropy(dip_lengths),
    })