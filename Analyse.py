import argparse
import csv
import datetime
from pathlib import Path
import os
import pickle
import json
import shutil
import subprocess
from shutil import copy2

import jsonpickle
from git import Repo

from AntiPatterns import CommitVersion, AntiPatternInstance
from Utils import clean_folder, create_and_clean_folder, sha256_checksum


class CSVFormatError(Exception):
    """URL exception"""
    pass


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def fill_results(apName, key, full_name, res, map_sha):
    for ap in res:
        if ap.name == map_sha[key]:
            ap.antiPatterns.setdefault(apName, []).append(AntiPatternInstance(full_name))


def check_if_folder_already_process(folders):
    res = folders.copy()
    for sub_folder in folders:
        for sub_root, sub_dirs, sub_files in os.walk(args.path + sub_folder):
            for sub_file in sub_files:
                if sub_file.endswith(".apk"):
                    tmp_repo = Repo(args.path + sub_folder)
                    tmp_sha = tmp_repo.head.object.hexsha
                    short_sha = tmp_repo.git.rev_parse(tmp_sha, short=7)
                    my_file = Path(args.out + sub_file.replace(".apk", "-") + short_sha + ".txt")
                    if my_file.exists():
                        res.remove(sub_folder)
                        break

    return res


parser = argparse.ArgumentParser()
parser.add_argument("-apk", help="if set program will except only apk in path", action="store_true")
parser.add_argument("path", help="Path where clones are stored")
parser.add_argument("out", help="output path")
args = parser.parse_args()

apkFolder = args.out + "apk/"
dbFolder = args.out + "db/"
csvFolder = args.out + "csv/"
create_and_clean_folder(apkFolder)
create_and_clean_folder(dbFolder)
create_and_clean_folder(csvFolder)

results = []
map_sha_name = {}

if args.apk:
    print("apk not implemented")
else:
    subFolder = [f for f in os.listdir(args.path)
                 if os.path.isdir(os.path.join(args.path, f))]

    subFolder = check_if_folder_already_process(subFolder)
    print(subFolder)
    for folder in subFolder:
        os.system("cd " + args.path + folder + " ; ./gradlew assembleDebug")
        for root, dirs, files in os.walk(args.path + folder):
            for file in files:
                if file.endswith(".apk"):
                    print(args.path + folder)
                    tmpRepo = Repo(args.path + folder)
                    sha = tmpRepo.head.object.hexsha
                    shortSha = tmpRepo.git.rev_parse(sha, short=7)
                    finalFile = apkFolder + file.replace(".apk", "-") + shortSha + ".apk"
                    copy2(os.path.join(root, file), finalFile)
                    results.append(CommitVersion(file.replace(".apk", "-") + shortSha, shortSha,
                                                 tmpRepo.head.object.committed_date))
                    map_sha_name[sha256_checksum(finalFile)] = file.replace(".apk", "-") + shortSha
                    break

proc = subprocess.Popen(['java', '-jar', './libs/Paprika.jar', 'analyse',
                         '-db', dbFolder, '-a', './android-platforms-master/', '-omp',
                         apkFolder], stdout=subprocess.PIPE)
tmp = proc.stdout.read()
print(tmp)

results.sort(key=lambda x: x.date, reverse=False)
print(results)
with cd(args.out + "csv/"):
    subprocess.call(["java", "-jar", "../../libs/Paprika.jar", "query", "-db", "../db", "-d", "-r", "ALLAP"])

for filename in os.listdir(csvFolder):
    apName = filename.split("_")[-1].split(".")[0]
    if apName != "ARGB8888":
        with open(os.path.join(csvFolder, filename), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'app_key' in row:
                    fill_results(apName, row["app_key"], row["full_name"], results, map_sha_name)
                else:
                    if 'm.app_key' in row:
                        fill_results(apName, row["m.app_key"], row["full_name"], results, map_sha_name)
                    else:
                        raise CSVFormatError(filename + "malformed")

for o in results:
    out_s = open(args.out + o.name + ".txt", "w")
    json = jsonpickle.encode(o, unpicklable=False)
    out_s.write(json)
    out_s.flush()
    out_s.close()
