import re
import stanza
stanza.download("sk")

nlp = stanza.Pipeline(
    lang="sk",
    processors="tokenize,pos,lemma",
    use_gpu=True
)

#POS tagy si rozdelíme na funkčné a významové slová, kedže obsah každej bakalárskej práce sa mení tak nás nezaujíma obsah ale forma a preto sa chceme pozrieť na funkčné slová

FUNC_UPOS = {
    "ADP",   
    "CCONJ", 
    "SCONJ", 
    "PRON",  
    "PART",  
    "AUX",   
    "DET",   
}

CONT_UPOS = {
    "NOUN",
    "PROPN",
    "VERB",
    "ADJ",
    "ADV",
    "NUM",
}

#Interpunčné znamienka tiež nechceme nahradiť POS tagom, lebo bodky nám pomáhajú deliť vety a ostatné znaky nám môžu tiež prezradiť čo to o štýle písania človeka. Preto si najčstejšie znaky nahradíme vlastnými značkami

PUNCT = {
    ".": "DOT",
    ",": "COMMA",
    ";": "SEMICOLON",
    ":": "COLON",
    "?": "QUESTION",
    "!": "EXCLAMATION",
    "-": "DASH",
    "–": "DASH",
}
PUNCTS = '.,;:?!-–—'

#funkcia ktorá načíta vstup, ktorý máme formátovaný že vždy je najprv názov a potom bakalárska práca a na konci prázdny riadok a ďaľší nazov atď
def load_doc(filename="vystup.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    docs = {}
    blocks = [b.strip("\n") for b in content.split("\n\n") if b.strip()]
    for block in blocks:
        lines = block.split("\n")
        file_name = lines[0].strip()
        text = "\n".join(lines[1:]).strip()
        docs[file_name] = text

    return docs

#očistíme text
def clean_text(text: str) -> str:

    text = re.sub(r"\([^)]*\)", " ", text) #odstránime všetok text v zátvorkách, kedže väčšinou sa jedná o citácie
    text = re.sub(r"\[[^\]]*\]", " ", text) #odstránime všetok text v zátvorkách, kedže väčšinou sa jedná o citácie
    text = re.sub(r"\d+", " ", text) #odstránime všetky čísla 
    text = re.sub(r"(?:\s*\.\s*){2,}", ". ", text) #nahradíme reťazce zložené len z bodiek jednou bodkou, lebo po lemmatizácii nám vzniklo vela úsekov s veľa bodkami
    text = re.sub(r"\s+", " ", text) #rovnako ako medzery nahradíme aj dlhšie medzery len jednou medzerou

    text = text.strip()

    return text

#aplikujeme očistenie textu na všetky texty
def clean_docs(doc_dict: dict[str, str]) -> dict[str, str]:
    cleaned = {}
    for name, text in doc_dict.items():
        cleaned[name] = clean_text(text)

    return cleaned

#Vytvoríme 3 reprezentácie textu, najprv lemmatizovaný, takže v základnom tvare všetky slová, potom všetky významové slová nahradíme slovom CONTENT, kedže obsah práce nás nezaujíma len jazykové vlastnosti a nakoniec  nahradíme všetky slová ich POS značkami
def make_representations(text: str, nlp):
    doc = nlp(text)
    lemmas = []
    func = []
    pos = []

    for s in doc.sentences:
        for w in s.words:
            if w.text in PUNCTS:
                lemmas.append(w.text)
                func.append(w.text)
                pos.append(PUNCT[w.text])
            else:
                try:
                    lemma = w.lemma.lower()
                    upos = w.upos
                    lemmas.append(lemma)

                    if upos in FUNC_UPOS:
                        func.append(lemma)
                    else:
                        func.append("CONTENT")
                except:
                    continue
                
                pos.append(upos)
                
    l_text = (" ".join(lemmas)).replace('.', '\n')
    f_text = (" ".join(func)).replace('.', '\n')
    p_text = (" ".join(pos)).replace('DOT', '\n')
    
    return {"lemmas": l_text, "func": f_text, "pos": p_text,}

#funckia ktorá pre všetky texty vyrobí všetky reprezentácie a dá ich do súboru
def three_representations(docs: dict[str, str], filename="representations.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for name in list(docs.keys()):
            print(name)
            text = cleaned_docs[name]
            reps = make_representations(text, nlp)
            f.write(name + '\n')
            f.write(reps["lemmas"])
            f.write('/\n')
            f.write(reps["func"])
            f.write('/\n')
            f.write(reps["pos"])
            f.write('///\n')
                    
        
        
# otestovanie týchto funkcií a následná aplikácia na všetky práce vyrobené ľuďmi
docs = load_doc("vystup.txt")
cleaned_docs = clean_docs(docs)

name = list(cleaned_docs.keys())[0]
text = cleaned_docs[name]
repres = make_three_representations(text, nlp)

three_representations(cleaned_docs)
