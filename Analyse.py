import argparse
import csv
import datetime
from os.path import isfile, join
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


def fill_final_file_name(apk_folder, current_apk_name, never_the_same_project_name, short_sha, number):
    if never_the_same_project_name:
        only_files = [f for f in os.listdir(apk_folder) if isfile(join(apk_folder, f))]
        for sub_file in only_files:
            index = sub_file.rfind('-')
            sub_file_name = sub_file[:index]
            if sub_file_name == current_apk_name.replace(".apk", ""):
                if number > 1:
                    tmp_index = current_apk_name.rfind('-')
                    tmp_name = sub_file[:tmp_index] + "-" + str(number) + ".apk"
                else:
                    tmp_name = current_apk_name.replace(".apk", "-" + str(number) + ".apk")
                return fill_final_file_name(apk_folder, tmp_name, never_the_same_project_name, short_sha, number+1)
        return current_apk_name.replace(".apk", "-") + short_sha + ".apk"
    else:
        return current_apk_name.replace(".apk", "-") + short_sha + ".apk"


def check_if_folder_already_process(folders):
    res = folders.copy()
    for sub_folder in folders:
        for sub_root, sub_dirs, sub_files in os.walk(args.path + sub_folder):
            for sub_file in sub_files:
                if sub_file.endswith(".apk"):
                    tmp_repo = Repo(args.path + sub_folder)
                    tmp_sha = tmp_repo.head.object.hexsha
                    short_sha = tmp_repo.git.rev_parse(tmp_sha, short=7)
                    only_files = [f for f in os.listdir(args.out) if isfile(join(args.out, f))]
                    for txt_file in only_files:
                        if sub_file.replace(".apk", "") in txt_file and short_sha + ".txt" in txt_file:
                            res.remove(sub_folder)
                            break

    return res


parser = argparse.ArgumentParser()
parser.add_argument("-apk", help="if set program will except only apk in path", action="store_true")
parser.add_argument("-onlyProjectWithMultipleApInMethod", "-opmam",
                    help="if set program keep android project with at least 2 different antipattern in a method",
                    action="store_true")
parser.add_argument("-neverTheSameProjectName", "-nspn",
                    help="if set program will never create a result with the same project name",
                    action="store_true")
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


def analyse(path, res, map_sha, apk_folder):
    project_name = ""
    for root2, dirs2, files2 in os.walk(path):
        for file2 in files2:
            if file2.endswith(".projectName"):
                project_name = file2.replace(".projectName", "")
                break

        for file2 in files2:
            if file2.endswith(".apk") and "unaligned" not in file2:
                print(path)
                tmpRepo = Repo(path)
                sha = tmpRepo.head.object.hexsha
                shortSha = tmpRepo.git.rev_parse(sha, short=7)

                finalFile = fill_final_file_name(apk_folder, project_name + ".apk", args.neverTheSameProjectName,
                                                 shortSha, 1)
                copy2(os.path.join(root2, file2), apk_folder + finalFile)
                res.append(CommitVersion(finalFile.replace(".apk", ""), shortSha,
                                             tmpRepo.head.object.committed_date))
                map_sha[sha256_checksum(apk_folder + finalFile)] = finalFile.replace(".apk", "")
                return


if args.apk:
    print("apk not implemented")
else:
    subFolder = [f for f in os.listdir(args.path)
                 if os.path.isdir(os.path.join(args.path, f))]

    subFolder = check_if_folder_already_process(subFolder)
    for folder in subFolder:
        isNeedToBuild = True
        for root, dirs, files in os.walk(args.path + folder):
            for file in files:
                if file.endswith(".apk") and "unaligned" not in file:
                    isNeedToBuild = False
        if isNeedToBuild:
            os.system("cd " + args.path + folder + " ; chmod +x gradlew")
            os.system("cd " + args.path + folder + " ; ./gradlew assembleDebug")
        analyse(args.path + folder, results, map_sha_name, apkFolder)

if len(results) > 0:
    proc = subprocess.call(['java', '-jar', './libs/Paprika.jar', 'analyse',
                             '-db', dbFolder, '-a', './android-platforms-master/', '-omp',
                             apkFolder])

    results.sort(key=lambda x: x.date, reverse=False)
    print(results)
    with cd(args.out + "csv/"):
        subprocess.call(["java", "-jar", "../../libs/Paprika.jar", "query", "-db", "../db", "-d", "-r", "ALLAP"])

    for filename in os.listdir(csvFolder):
        apName = filename.split("_")[-1].split(".")[0]
        if apName not in ("ARGB8888", "DR"):
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

    if args.onlyProjectWithMultipleApInMethod:
        results = [x for x in results if x.is_contains_ap_in_same_method()]

    for o in results:
        out_s = open(args.out + o.name + ".txt", "w")
        json = jsonpickle.encode(o, unpicklable=False)
        out_s.write(json)
        out_s.flush()
        out_s.close()
