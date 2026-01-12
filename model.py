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
import random
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from scipy.stats import mannwhitneyu


#Načítame vstup a rozdelíme ho na časť kotrá je lemmatizovaná, na časť kt. obsahuje len funkčné slová a časť ktorá ma len POS
def load(filename):
    b_lemma = []
    b_func = []
    b_pos = []

    d_lemma = []
    d_func = []
    d_pos = []

    typ = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if "," in line and line.endswith(".txt"):
                typ = line.split(",", 1)[1][:-4].lower()
                continue

            if typ not in ("bakalarka", "diplomovka"):
                continue

            for part in line.split("\\"):
                part = part.strip()
                if not part:
                    continue
                if len(part) < 10:
                    continue

                words = part.split()

                if "CONTENT" in words:
                    if typ == "bakalarka":
                        b_pos.append(part)
                    else:
                        d_pos.append(part)
                    continue

                has_func = any(w in FUNC_UPOS for w in words)
                has_cont = any(w in CONT_UPOS for w in words)

                if has_func or has_cont:
                    if typ == "bakalarka":
                        b_func.append(part)
                    else:
                        d_func.append(part)
                else:
                    if typ == "bakalarka":
                        b_lemma.append(part)
                    else:
                        d_lemma.append(part)

    return b_lemma, b_func, b_pos, d_lemma, d_func, d_pos

#funkcia ktora nam rozdeli sadu na trenovaciu a testovaciu

def split_80_20(xs, seed=42):
    rnd = random.Random(seed)
    train = []
    test = []
    for x in xs:
        if rnd.random() < 0.8:
            train.append(x)
        else:
            test.append(x)
    return train, test

#vytvoríme si zoznamy viet z bakalárok v 3 reprezentáciach a rozdelime ich do testovacej a trenovacej sady a nasledne si nacitame aj AI bakalarky v 3 reprezentaciach
b_lemma, b_func, b_pos, d_lemma, d_func, d_pos = load("representations.txt")

b_lemma_tr, b_lemma_te = split_80_20(b_lemma)
b_func_tr,  b_func_te  = split_80_20(b_func)
b_pos_tr,   b_pos_te   = split_80_20(b_pos)

print(len(b_lemma_tr),' - ', len(b_lemma_te))
b_lemma_ai, b_func_ai, b_pos_ai, d_lemma_ai, d_func_ai, d_pos_ai = load("representations_ai.txt")

#natrénujeme model na realnych bakalárkach a ai bakalárkach
def train(b_real, b_ai, typ):
    X = []
    y = []
    if typ == 'word':
        ngram = (2, 5)
    else:
        ngram = (3, 8)
        

    for s in b_real:
        X.append(s)
        y.append(0)

    for s in b_ai:
        X.append(s)
        y.append(1)

    vec = TfidfVectorizer(analyzer=typ,  ngram_range=ngram, min_df=1, max_df=0.98)
    Xv = vec.fit_transform(X)

    clf = LogisticRegression(max_iter=2000, class_weight = 'balanced', solver="liblinear")
    clf.fit(Xv, y)

    return vec, clf

#vytvoríme predikcie pre diplomovky, že aká je šanca že sú AI
def predict_ai_probs(vec, clf, test):
    Xv = vec.transform(test)
    probs = clf.predict_proba(Xv)

    p_ai = []
    for row in probs:
        p_ai.append(float(row[1]))

    return np.array(p_ai, dtype=float)

#vypocitame priemernu pravdepodobnost a pocet pravdepodobnosti > 0,5
def stats(test, p_ai, thr=0.5):
    n = len(test)

    count_ai = 0
    ssum = 0.0

    for p in p_ai:
        ssum += float(p)
        if p > thr:
            count_ai += 1

    avg_p = ssum / n


    return count_ai, avg_p

#vypocitame mann-whitney U test pre hypotezu h0 ze rozdelenie pravdepodobností AI pre diplomové práce nie je posunuté k vyšším hodnotám v porovnaní s testovacou sadou bakalárskych prác
def mw_test_with_effect(x, y):
    res = mannwhitneyu(y, x, alternative="greater")
    nx = len(x)
    ny = len(y)

    print("U:", res.statistic)
    print("p:", res.pvalue)

#postupne zrátame modely a výsledky pre reprezentaciu lemma, func a pos

B = b_lemma_tr
BAI = b_lemma_ai
D = d_lemma
BT = b_lemma_te

vec, clf = train(B, BAI, 'char')
p_ai = predict_ai_probs(vec, clf, D)
pt_ai = predict_ai_probs(vec, clf, BT)

mw_test_with_effect(pt_ai, p_ai)

count_ai, avg_p = stats(BT, pt_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v testovacej sade:", count_ai)
print("priemerna P(AI):", avg_p)

count_ai, avg_p = stats(D, p_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v diplomovkach:", count_ai)
print("priemerna P(AI):", avg_p)

B = b_func_tr
BAI = b_func_ai
D = d_func
BT = b_func_te

vec, clf = train(B, BAI, 'word')
p_ai = predict_ai_probs(vec, clf, D)
pt_ai = predict_ai_probs(vec, clf, BT)

mw_test_with_effect(pt_ai, p_ai)


count_ai, avg_p = stats(BT, pt_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v testovacej sade:", count_ai)
print("priemerna P(AI):", avg_p)

count_ai, avg_p = stats(D, p_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v diplomovkach:", count_ai)
print("priemerna P(AI):", avg_p)

B = b_pos_tr
BAI = b_pos_ai
D = d_pos
BT = b_pos_te

vec, clf = train(B, BAI, 'word')
p_ai = predict_ai_probs(vec, clf, D)
pt_ai = predict_ai_probs(vec, clf, BT)

mw_test_with_effect(pt_ai, p_ai)

count_ai, avg_p = stats(BT, pt_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v testovacej sade:", count_ai)
print("priemerna P(AI):", avg_p)

count_ai, avg_p = stats(D, p_ai, thr=0.5)
print("pocet viet s P(AI) > 0.5 v diplomovkach:", count_ai)
print("priemerna P(AI):", avg_p)

