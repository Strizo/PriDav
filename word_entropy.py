from scipy.stats import entropy

def word_entropy(title : str, text : str):
    signs = [",",".",":",";","/","@","!","?","*","&","%","$","#","(",")",";","-","_","+","=","“","„"]
    occurences = {}
    total = 0
    pk = []
    
    for w in text.split(' '):
        if w in signs or '0' in w or '1' in w or '2' in w or '3' in w or '4' in w or '5' in w or '6' in w or '7' in w or '8' in w or '9' in w: continue
        if w in occurences.keys(): occurences[w] += 1
        else: occurences[w] = 1
        total += 1
    
    for i in occurences.values(): pk.append(i/total)
    print(title[:-1]+","+str(entropy(pk)))

with open("vystup.txt", "r") as f:
    print("PRIEZVISKO,TYP,VALUE")
    for i in range(60):
        title = f.readline()
        text = f.readline()
        f.readline()
        word_entropy(title[:-4], text)
