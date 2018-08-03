import re
from collections import defaultdict
from typing import Dict, List
from Utils import clean_location_class, clean_location_function


class CommitVersion:
    def __init__(self, name, commit, date):
        self.name = name
        self.commit = commit
        self.date = date
        self.antiPatterns: Dict[str, List[AntiPatternInstance]] = {}

    def __str__(self):
        return "{0} {1} {2}".format(self.commit, self.date, self.antiPatterns)

    __repr__ = __str__

    def ap_by_class(self, location):
        res = []
        for key, value in self.antiPatterns.items():
            for ap in value:
                if clean_location_class(ap.location) == location:
                    res.append([key, ap.location])
        return res

    def ap_by_function(self, location):
        res = []
        for key, value in self.antiPatterns.items():
            for ap in value:
                if clean_location_function(ap.location) == location:
                    res.append([key, ap.location])
        return res

    def is_contains_ap_in_same_method(self):
        already_process = []
        for key, value in self.antiPatterns.items():
            for ap in value:
                if ap.location.functionLocation not in ("", None):
                    for key2, value2 in self.antiPatterns.items():
                        if key2 not in already_process:
                            for ap2 in value2:
                                if ap2 != ap and \
                                        ap2.location.functionLocation not in ("", None) \
                                        and ap.location.classLocation == ap2.location.classLocation \
                                        and ap.location.functionLocation == ap2.location.functionLocation:
                                    return True
            already_process.append(key)
        return False


class AntiPatternInstance:
    def __init__(self, location):
        self.location = Location(location)
        self.data: Dict[str, str] = {}

    def __str__(self):
        return "{0} {1}".format(self.location, self.data)

    __repr__ = __str__


class Location:
    def __init__(self, location):
        match = re.match(r"^(?:(.*?)#)?(.*?)(?:\$(.*?))?$", location)
        self.classLocation = match.group(2)
        self.functionLocation = match.group(1) if match.group(1) else ""
        self.lineLocation = match.group(3) if match.group(3) and match.group(3).isdigit() else ""

    def __str__(self):
        return "{0} {1} {2}".format(self.classLocation, self.functionLocation, self.lineLocation)

    __repr__ = __str__

