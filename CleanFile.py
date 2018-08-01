import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", help="File path to check")
args = parser.parse_args()
urls = []

with open(args.file) as file:
    [urls.append(line.rstrip('\n')) for line in file]

for x in range(0, len(urls)):
    for y in range(x+1, len(urls)):
        if urls[x] == urls[y]:
            print("same value at line {} and line {} value {}".format(x+1, y+1, urls[x]))
