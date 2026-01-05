stanza.download("sk")
nlp = stanza.Pipeline("sk", processors="tokenize,pos,lemma")

def lemmatize(text: str) -> str:
    """Lemmatizácia + odstránenie stop-slov."""
    doc = nlp(text)
    lemmas = []
    for sent in doc.sentences:
        for w in sent.words:
            lemma = (w.lemma or "").lower()
            lemmas.append(lemma)
    return " ".join(lemmas)
