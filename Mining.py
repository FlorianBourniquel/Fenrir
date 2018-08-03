import os
import shutil
from urllib.parse import urlparse
from git import Repo
import argparse


class URLError(Exception):
    """URL exception"""
    pass


class NumberCommitError(Exception):
    """Number of Commit exception"""
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
parser.add_argument("step", help="Step of commit between each clone", type=int)
args = parser.parse_args()

if args.file and not args.url.endswith(".txt"):
    parser.error("-file requires a txt file in url")


path = ""
if args.path[-1] == "/":
    path = args.path
else:
    path = args.path + "/"


shutil.rmtree(path + "tmp", ignore_errors=True)


def clone(url):
    if not url_validator(url):
        raise URLError("url not correct")
    number = sum(os.path.isdir(os.path.join(path, i)) for i in os.listdir(path))
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


if args.file:
    with open(args.url) as file:
        [clone(line.rstrip('\n')) for line in file]

else:
    clone(args.url)

