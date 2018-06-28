import os
import re
import shutil


def create_and_clean_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)
    clean_folder(path)


def clean_folder(path):
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


def clean_location(location):
    return re.sub(r'[$][0-9a-zA-Z_]*', "", re.sub(r'^[0-9a-zA-Z_]*[#]', "", location))

