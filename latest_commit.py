##*************************************************************************
#   data structure containing additional information about the latest commit
#
#   @author	 Jamie Taylor
#   @Creation Date: 23/11/2022
##*************************************************************************


class LatestCommit:

    def __init__(self, commit=None, file=None):
        self.commit = commit
        if file is not None:
            self.files = [file]
        else:
            self.files = []

    def setCommit(self, commit):
        self.commit = commit

    def add(self, file):
        self.files.append(file)

    def to_dict(self):
        return {
            "commit": self.commit,
            "files": self.files
        }
