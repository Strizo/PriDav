import pandas as pd
import stanza
from scipy.stats import entropy

nlp = stanza.Pipeline("sk")
names = ['obuch', 'kissova', 'kurillova', 'sismicova', 'spakova', 'hervay', 'mizikova', 'podracka', 'adamov', 'zigo', 'klackova', 'prokofiiev', 'moravska', 'chladna', 'hilkovic', 'petrikova', 'glosova', 'mrazik', 'posvancz', 'galanda', 'marecek', 'rescak', 'baloghova', 'stefankoviscova', 'hudackova', 'kosarova', 'hubcikova', 'vago', 'cincar', 'pelikan']
print("PRIEZVISKO,TYP,VALUE")

for name in names:
    for type in ['bakalarka','diplomovka']:
        with open("prace/"+name+","+type+".txt", "r", encoding="utf-8") as f: #"C:\\Users\\skalo\\OneDrive\\Documents\\Pridav group\\prace\\"+
            doc = nlp(f.read())
            occurences = {}
            total = 0
            pk = []
            for sent in doc.sentences:
                s = []
                for word in sent.words:
                    if word.deprel != None: s.append(word.deprel)
                    #print(word.deprel,end=" ")
                s = " ".join(s)
                if s in occurences.keys(): occurences[s] += 1
                else: occurences[s] = 1
                total += 1
            
            #print(sorted(occurences.items(), key=lambda x: x[1], reverse=True)[:10])
            for i in occurences.values(): pk.append(i/total)
            print(name+","+type+","+str(entropy(pk)))
            
                

