import argparse
import csv
import datetime
import os
import pickle
import shutil
import subprocess
from shutil import copy2

from git import Repo

from AntiPatterns import CommitVersion, AntiPattern
from Utils import clean_folder, create_and_clean_folder


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


def fill_results(apName, key, full_name, res):
    for ap in res:
        if ap.name == key:
            ap.antiPatterns[apName].append(AntiPattern(full_name))


parser = argparse.ArgumentParser()
parser.add_argument("-apk", help="if set program will except only apk in path", action="store_true")
parser.add_argument("path", help="Path where clones are stored")
parser.add_argument("out", help="output path")
args = parser.parse_args()

apkFolder = args.out + "apk/"
dbFolder = args.out + "db/"
csvFolder = args.out + "csv/"
create_and_clean_folder(args.out)
create_and_clean_folder(apkFolder)
create_and_clean_folder(dbFolder)
create_and_clean_folder(csvFolder)

results = []

if args.apk:
    print("apk not implemented")
else:
    subFolder = [f for f in os.listdir(args.path)
                 if os.path.isdir(os.path.join(args.path, f))]
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
                    proc = subprocess.Popen(["aapt", "dump", "badging", finalFile], stdout=subprocess.PIPE)
                    tmp = proc.stdout.read()
                    package = tmp.decode("utf-8").split("package: name='")[1].split("' ")[0]
                    print(package)
                    proc = subprocess.Popen(['java', '-jar', './libs/Paprika.jar', 'analyse',
                                             '-db', dbFolder, '-p',
                                             package, "-k", file.replace(".apk", "-") + shortSha, "-dev",
                                             'mydev', '-cat', 'mycat', '-nd', '100', '-d',
                                             '2017-01-001 10:23:39.050315', '-r', '1.0', '-s',
                                             '1024', '-n', 'Test', '-a', './android-platforms-master/', '-omp', 'true',
                                             '-u', 'unsafe mode',
                                             finalFile], stdout=subprocess.PIPE)
                    tmp = proc.stdout.read()
                    print(tmp)
                    results.append(CommitVersion(file.replace(".apk", "-") + shortSha, shortSha,
                                                 datetime.datetime.fromtimestamp(tmpRepo.head.object.committed_date)))
                    break

results.sort(key=lambda x: x.date, reverse=False)
print(results)
with cd(args.out + "csv/"):
    subprocess.call(["java", "-jar", "../../libs/Paprika.jar", "query", "-db", "../db", "-d", "TRUE", "-r", "ALLAP"])

for filename in os.listdir(csvFolder):
    apName = filename.split("_")[-1].split(".")[0]
    if apName != "ARGB8888":
        with open(os.path.join(csvFolder, filename), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'app_key' in row:
                    fill_results(apName, row["app_key"], row["full_name"], results)
                else:
                    if 'm.app_key' in row:
                        fill_results(apName, row["m.app_key"], row["full_name"], results)
                    else:
                        raise CSVFormatError(filename + "malformed")


clean_folder(args.out)

out_s = open(args.out + "out.txt", "wb")

for o in results:
    pickle.dump(o, out_s)
    out_s.flush()



