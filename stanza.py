import sys

path = sys.argv[1]

with open(path, "r") as f:
    text = f.read()

import stanza
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


print(lemmatize(text))
