from scipy.stats import shapiro, ttest_rel, wilcoxon
import sys
import matplotlib.pyplot as plt
import pandas as pd

path = sys.argv[1]
split = sys.argv[2]
pairs = sys.argv[3]
value = sys.argv[4]
before = sys.argv[5]
after = sys.argv[6]
fig = sys.argv[7]

df = pd.read_csv(path)

# shapiro test of normality

normal = True

data_b = df[df[split] == before][value]
if shapiro(data_b).pvalue <= 0.05 : 
    print("data before not normal in")
    normal = False
else : print("data before normal in")

data_a = df[df[split] == after][value]
if shapiro(data_a).pvalue <= 0.05 : 
    print("data after not normal in")
    normal = False
else : print("data after normal in")


if normal:
    print(ttest_rel(data_b, data_a))
else:
    print(wilcoxon(data_b, data_a))
    
plt.hist(data_a, alpha=0.5, label='Dip.') 
plt.hist(data_b, alpha=0.5, label='Bak.') 
plt.legend() 
plt.savefig(fig+"_both.png")

plt.figure()
plt.hist(data_a.to_numpy() - data_b.to_numpy(), alpha=1, label='Difference') 
plt.legend() 
plt.savefig(fig+"_diff.png")