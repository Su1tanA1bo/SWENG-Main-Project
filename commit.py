##*************************************************************************
#   data structure containing all relevant data about a commit
#
#   @author	 Jamie Taylor
#   @Creation Date: 17/11/2022
##*************************************************************************


class Commit:

    def __init__(self, name, sha, message, date, time, additions, deletions):
        self.author = name
        self.sha = sha
        self.message = message

        self.date = date
        self.time = time

        self.additions = additions
        self.deletions = deletions
        self.changes = additions + deletions

    def to_dict(self):
        return {
            "author": self.author,
            "sha": self.sha,
            "message": self.message,
            "date": self.date,
            "time": self.time,
            "additions": self.additions,
            "deletions": self.deletions,
            "changes": self.additions + self.deletions
        }

    def __repr__(self):
        return f"Author: {self.author}\n" \
               f"Message: {self.message}\n" \
               f"Sha: {self.sha}\n" \
               f"Additions: {self.additions}\n" \
               f"Deletions: {self.deletions}"
