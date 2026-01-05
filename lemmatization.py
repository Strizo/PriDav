import sys
import stanza

sys.stdout.reconfigure(encoding="utf-8", errors="ignore")

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

if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    print(lemmatize(text))
