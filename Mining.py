from distutils.dir_util import copy_tree
import os
import shutil
from urllib.parse import urlparse
from git import Repo
import argparse
import zipfile
import requests


class URLError(Exception):
    """URL exception"""
    pass


class NumberCommitError(Exception):
    """Number of Commit exception"""
    pass


class WrongArgument(Exception):
    """Wrong argument exception"""
    pass


class NoModeSpecified(Exception):
    """No mode specified exception"""
    pass


def url_validator(url):
    try:
        result = urlparse(url)
        return bool(result.scheme)
    except:
        return False


parser = argparse.ArgumentParser()
parser.add_argument("url", help="git url of your android project")
parser.add_argument("path", help="Path where clones will be store.")
parser.add_argument("n", help="Number of clone", type=int)
parser.add_argument("-file", help="if url is a txt that contains all android project url (one url per line)"
                    , action="store_true")
parser.add_argument("-commitMode", help="if you want to work with commit"
                    , action="store_true")
parser.add_argument("-dateMode", help="if you want to work with date"
                    , action="store_true")
parser.add_argument("-releaseMode", help="if you want to work with release (GitHub Project)"
                    , action="store_true")
parser.add_argument("step", help="Step of commit/day/release between each clone", type=int)
args = parser.parse_args()

if args.file and not args.url.endswith(".txt"):
    parser.error("-file requires a txt file in url")


path = ""
if args.path[-1] == "/":
    path = args.path
else:
    path = args.path + "/"


shutil.rmtree(path + "tmp", ignore_errors=True)


def clone_commit(url):
    if not url_validator(url):
        raise URLError("url not correct")
    number = len(os.walk(path).__next__()[1])
    repo = Repo.clone_from(url, path + "tmp")
    commits = list(repo.iter_commits())
    if len(commits) < args.n * args.step:
        raise NumberCommitError("Not enough commit with the specified args")
    commits.clear()
    for i in range(number, number + args.n):
        tmp_list = list(repo.iter_commits(max_count=1, skip=args.step * (i - number)))
        commits.append(tmp_list)
        project_name = url.replace("https://github.com/", "").replace(".git", "").replace("/", "_")
        f = open(path + "tmp/" + project_name + ".projectName", "w+")
        f.close()
        shutil.copytree(path + "tmp", path + str(i + 1))
        tmp_repo = Repo(path + str(i + 1))
        git_obj = tmp_repo.git
        git_obj.checkout(tmp_list[0].hexsha)
    shutil.rmtree(path + "tmp", ignore_errors=True)


def clone_date(url):
    if not url_validator(url):
        raise URLError("url not correct")
    number = sum(os.path.isdir(os.path.join(path, i)) for i in os.listdir(path))
    repo = Repo.clone_from(url, path + "tmp")
    commits = list(repo.iter_commits())
    tmp_list = list(repo.iter_commits(max_count=1, skip=0))
    commits.append(tmp_list)
    project_name = url.replace("https://github.com/", "").replace(".git", "").replace("/", "_")
    f = open(path + "tmp/" + project_name + ".projectName", "w+")
    f.close()
    shutil.copytree(path + "tmp", path + str(number + 1))
    tmp_repo = Repo(path + str(number + 1))
    git_obj = tmp_repo.git
    git_obj.checkout(tmp_list[0].hexsha)
    prev_date = tmp_list[0].committed_datetime
    index = 1
    for i in range(number+1, number + args.n):
        while index < (len(commits)-1):
            if (prev_date-commits[index].committed_datetime).days >= args.step:
                project_name = url.replace("https://github.com/", "").replace(".git", "").replace("/", "_")
                f = open(path + "tmp/" + project_name + ".projectName", "w+")
                f.close()
                shutil.copytree(path + "tmp", path + str(i + 1))
                tmp_repo = Repo(path + str(i + 1))
                git_obj = tmp_repo.git
                git_obj.checkout(commits[index].hexsha)
                prev_date = commits[index].committed_datetime
                index += 1
                break
            index += 1
        if index > (len(commits)-1):
            raise NumberCommitError("Not enough commit with the specified args")
    shutil.rmtree(path + "tmp", ignore_errors=True)


def clone_release(url):
    if not url_validator(url):
        raise URLError("url not correct")
    number = sum(os.path.isdir(os.path.join(path, i)) for i in os.listdir(path))
    tmp_url = url.replace(".git", "")
    tmp_url = tmp_url.replace("https://github.com/", "")
    r = requests.get(url='https://api.github.com/repos/' + tmp_url + "/releases")
    json_list = r.json()
    if len(json_list) < args.n * args.step:
        raise NumberCommitError("Not enough commit with the specified args")
    os.makedirs(path + "tmp/")
    for i in range(number, number + args.n):
        with open(path + "tmp/" + "tmp.zip", "w+b") as zip_file:
            # get request
            response = requests.get(json_list[args.step * (i - number)]['zipball_url'])
            # write to file
            zip_file.write(response.content)
        with zipfile.ZipFile(path + "tmp/" + "tmp.zip", "r") as zip_ref:
            zip_ref.extractall(path + "tmp/")
        os.remove(path + "tmp/" + "tmp.zip")
        project_name = url.replace("https://github.com/", "").replace(".git", "").replace("/", "_")
        f = open(path + "tmp/" + os.walk(path + "tmp/").__next__()[1][0] + "/" + project_name + ".projectName", "w+")
        f.close()
        shutil.copytree(path + "tmp/" + os.walk(path + "tmp/").__next__()[1][0], path + str(i + 1))
        shutil.rmtree(path + "tmp", ignore_errors=True)
        os.makedirs(path + "tmp/")
    shutil.rmtree(path + "tmp", ignore_errors=True)


if args.commitMode:
    if args.file:
        with open(args.url) as file:
            [clone_commit(line.rstrip('\n')) for line in file]
    else:
        clone_commit(args.url)

elif args.dateMode:
    clone_date(args.url)

elif args.releaseMode:
    clone_release(args.url)

else:
    raise NoModeSpecified
