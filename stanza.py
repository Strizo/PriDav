import sys
import stanza

path = sys.argv[1]

with open(path, "r") as f:
    text = f.read()

stanza.download("sk")
nlp = stanza.Pipeline("sk", processors="tokenize,pos,lemma")

def lemmatize(text: str) -> str:
    doc = nlp(text)
    lemmas = []
    for sent in doc.sentences:
        for w in sent.words:
            lemma = (w.lemma or "").lower()
            lemmas.append(lemma)
    return " ".join(lemmas)


with open(path[:4]+",lemma.txt", "r") as w:
    f.write(lemmatize(text))

# for f in prace/*.txt; do python3 stanza.py "$f"; done