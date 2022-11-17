##*************************************************************************
#   data structure containing all relevant data about a commit
#
#   @author	 Jamie Taylor
#   @Creation Date: 17/11/2022
##*************************************************************************


class Commit:

    def __init__(self, sha, message, date, time, additions, deletions):
        self.sha = sha
        self.message = message
        self.date = date
        self.time = time
        self.additions = additions
        self.deletions = deletions
        self.total_changes = additions + deletions

    def __repr__(self):
        return f"Message: {self.message}\n" \
               f"Sha: {self.sha}\n" \
               f"Additions: {self.additions}\n" \
               f"Deletions: {self.deletions}"
