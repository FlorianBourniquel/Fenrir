from collections import defaultdict
from typing import Dict, List


class CommitVersion:
    def __init__(self, name, commit, date):
        self.name = name
        self.commit = commit
        self.date = date
        self.antiPatterns: Dict[str, List[AntiPattern]] = defaultdict(list)

    def __str__(self):
        return "{0} {1} {2}".format(self.commit, self.date, self.antiPatterns)
    __repr__ = __str__


class AntiPattern:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "{0}".format(self.name)

    __repr__ = __str__
