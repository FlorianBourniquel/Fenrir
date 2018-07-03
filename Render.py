import argparse
import os
import pickle
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from Utils import clean_folder, create_and_clean_folder, clean_location_class, clean_location_function

parser = argparse.ArgumentParser()
parser.add_argument("-progress", help="plot of the anti pattern progression", action="store_true")
parser.add_argument("-sameClass", help="print location by class where they are several anti patterns",
                    action="store_true")
parser.add_argument("-sameFunc", help="print location by class where they are several anti patterns",
                    action="store_true")
parser.add_argument("path", help="Path of the out.txt")
parser.add_argument("out", help="output path")
args = parser.parse_args()

create_and_clean_folder(args.out)
results = []

file = open(args.path, "rb")
while True:
    try:
        o = pickle.load(file)
    except EOFError:
        break
    else:
        results.append(o)

if args.sameClass:
    location_already_processed = []
    for commitVersion in results:
        location_already_processed.clear()
        print("CommitVersion " + commitVersion.commit + "\n")
        print("//////////////\n")
        for key, value in commitVersion.antiPatterns.items():
            for ap in value:
                class_location = clean_location_class(ap.location)
                if class_location not in location_already_processed:
                    tmp = commitVersion.ap_by_class(class_location)
                    if len(tmp) > 1:
                        print("Code smell in " + class_location)
                        for val in tmp:
                            match = re.match(r"^(?:(.*?)#)?(.*?)(?:\$(.*?))?$", val[1])
                            print(val[0] + f"{' in method %s' % (match.group(1)) if match.group(1) else ''}"
                                           f"{' in line {}'.format(match.group(3)) if match.group(3) else ''}")
                        print("\n")
                    location_already_processed.append(class_location)
elif args.sameFunc:
    location_already_processed = []
    for commitVersion in results:
        location_already_processed.clear()
        print("CommitVersion " + commitVersion.commit + "\n")
        print("//////////////\n")
        for key, value in commitVersion.antiPatterns.items():
            if key not in ["BLOB", "SAK", "LIC", "NLMR", "CC"]:
                for ap in value:
                    function_location = clean_location_function(ap.location)
                    if function_location not in location_already_processed:
                        tmp = commitVersion.ap_by_function(function_location)
                        if len(tmp) > 1:
                            tmpString = function_location.split("#")
                            print("Code smell in function " + tmpString[0] + " in class " + tmpString[1])
                            for val in tmp:
                                match = re.match(r"^(?:(.*?)#)?(.*?)(?:\$(.*?))?$", val[1])
                                print(val[0] + f"{' in line {}'.format(match.group(3)) if match.group(3) else ''}")
                            print("\n")
                        location_already_processed.append(function_location)
else:
    tmpTab = []
    for commitVersion in results:
        for key, value in commitVersion.antiPatterns.items():
            if not key == "LM":
                tmpTab.append([commitVersion.commit, key, len(value)])

    df2 = pd.DataFrame(tmpTab, columns=['Commit', 'APName', 'Occurrence'])

    print(df2)
    g = sns.factorplot(x="Commit", y="Occurrence", hue="APName", kind="bar", data=df2)
    g2 = sns.factorplot(x="Commit", y="Occurrence", hue="APName", data=df2)

    ax = g.ax


    def annotate_bars(row, ax=ax):
        for p in ax.patches:
            ax.annotate("%.2f" % p.get_height(), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center',
                        va='center',
                        fontsize=11, color='gray', rotation=90, xytext=(0, 20), textcoords='offset points')


    plot = df2.apply(annotate_bars, ax=ax, axis=1)
    plt.show()
