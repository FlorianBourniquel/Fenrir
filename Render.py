import argparse
import pickle

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

df2 = pd.DataFrame([[1,2,3,4,5]], columns=['a', 'b', 'c', 'd', 'e'], index=['a'])
print(df2)
g = sns.factorplot(x="time", y="pulse", hue="kind", data=df2)


"""while True:
    try:
        o = pickle.load(args.path)
    except EOFError:
        break
    else:
        results.append(o)"""