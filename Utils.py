import hashlib
import os
import re
import shutil
import sys


class FolderNotEmptyError(Exception):
    pass


def create_and_clean_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)
    clean_folder(path)


def clean_folder(path):
    if [f for f in os.listdir(path) if not f.startswith('.')]:
        if query_yes_no("Rm " + path):
            for the_file in os.listdir(path):
                file_path = os.path.join(path, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(e)
        else:
            raise FolderNotEmptyError(path + " is not empty")


def clean_location_class(location):
    return re.sub(r'[$][0-9a-zA-Z_]*', "", re.sub(r'^[0-9a-zA-Z_]*[#]', "", location))


def clean_location_function(location):
    return re.sub(r'[$][0-9a-zA-Z_]*', "", location)


def query_yes_no(question, default="yes"):
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def sha256_checksum(filename, block_size=65536):
    sha256 = hashlib.sha256()
    with open(filename, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()
