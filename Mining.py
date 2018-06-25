import os
import shutil
from urllib.parse import urlparse
from git import Repo
import argparse

ERROR_INVALID_NAME = 123


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
parser.add_argument("path", help="Path where clones will be store. If not empty everything will be erase")
parser.add_argument("n", help="Number of clone", type=int)
parser.add_argument("step", help="Step of commit between each clone", type=int)
args = parser.parse_args()

if not url_validator(args.url):
    raise URLError("url not correct")

if [f for f in os.listdir(args.path) if not f.startswith('.')]:
    for the_file in os.listdir(args.path):
        file_path = os.path.join(args.path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

repo = Repo.clone_from(args.url, args.path)

ten_commits_past_twenty = list(repo.iter_commits())

if len(ten_commits_past_twenty) < args.n * args.step:
    raise NumberCommitError("Not enough commit with the specified args")

print(args.url)
