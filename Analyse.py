import argparse
import csv
import datetime
import os
import shlex
import subprocess
import time
from git import Repo
import shutil
from shutil import copyfile, copy2
from AntiPatterns import CommitVersion, AntiPattern


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


def create_and_clean_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

    if [f for f in os.listdir(path) if not f.startswith('.')]:
        for the_file in os.listdir(path):
            file_path = os.path.join(path, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)


def fill_results(apName, key, full_name, res):
    for ap in res:
        if ap.name == key:
            ap.antiPatterns[apName].append(AntiPattern(full_name))



parser = argparse.ArgumentParser()
parser.add_argument("-apk", help="if set program will except only apk in path")
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

if args.apk is not None:
    print("apk")
else:
    subFolder = [f for f in os.listdir(args.path)
                 if os.path.isdir(os.path.join(args.path, f))]
    for folder in subFolder:
        os.system("cd " + args.path + folder + " ; gradlew assembleDebug")
        for root, dirs, files in os.walk(args.path + folder):
            for file in files:
                if file.endswith(".apk"):
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
with cd("./out/csv"):
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

print(results)
