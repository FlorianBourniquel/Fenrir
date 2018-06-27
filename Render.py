import argparse
import os
import pickle
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import seaborn as sns

from Utils import clean_folder, create_and_clean_folder

parser = argparse.ArgumentParser()
parser.add_argument("-progress", help="plot of the anti pattern progression")
parser.add_argument("-same", help="print location where they are several anti patterns ")
parser.add_argument("path", help="Path where clones are stored")
parser.add_argument("out", help="output path")
args = parser.parse_args()

create_and_clean_folder(args.out)
results = []

df2 = pd.DataFrame([["AL",2,3],["IL",2,8],["AL",3,6]], columns=['a', 'b', 'c'])
print(df2)
g = sns.factorplot(x="b", y="c", hue="a", data=df2)
plt.legend()
plt.show()

input("Press any key to close")

file = open(args.path + "out.txt", "rb")
while True:
    try:
        o = pickle.load(file)
    except EOFError:
        break
    else:
        results.append(o)

print(results)

