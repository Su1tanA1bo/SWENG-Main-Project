##*************************************************************************
#   file contains data structure
#   UserStats - stats about users
#   Commit - information on commits
#   FileContents - contents of the files
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint


class UserStats:
    def __init__(self, commit=None):

        # list of commits - if has init parameter, initialised with
        if commit is None:
            self.commits = []
        else:
            self.commits = [commit]

        # number of days code was committed
        self.days_committed = None
        # average frequency of commits each day that a commit was made
        self.avg_freq = -1
        # highest and lowest number of commits in one day
        self.most_commits = -1
        self.least_commits = -1

        # most and least additions/deletions/changes
        # tuple containing int and a dict representing the commit
        self.most_additions = (-1, None)
        self.least_additions = (-1, None)
        self.most_deletions = (-1, None)
        self.least_deletions = (-1, None)
        self.most_changes = (-1, None)
        self.least_changes = (-1, None)

        # average number of additions/deletions/changes
        # total commits / days committed
        self.avg_no_additions = -1
        self.avg_no_deletions = -1
        self.avg_no_changes = -1

        # blame info
        self.lines_written = -1
        self.code_ownership = -1

    # add a commit to commits list
    def add(self, commit):
        self.commits.append(commit)

    # finds the number of days that a user committed on
    def find_days_committed(self):
        days = set()
        for commit in self.commits:
            days.add(commit.date)
        return len(days)

    # function for adding number of lines written
    def add_to_lines(self, lines):
        self.lines_written += lines

    # calculate percentage of code owner by this user
    def calculate_code_ownership(self, total_lines):
        self.code_ownership = round((self.lines_written / total_lines) * 100, 3)

    # update all the relevant fields for a user
    def resolve_stats(self):
        self.days_committed = self.find_days_committed()
        self.avg_freq = round(len(self.commits) / self.days_committed)

        most_changes = 0
        least_changes = float('inf')

        most_additions = 0
        least_additions = float('inf')

        most_deletions = 0
        least_deletions = float('inf')

        total_changes = 0
        total_additions = 0
        total_deletions = 0

        # dict with date as key, number of commits as value
        commits_per_day = {}
        for commit in self.commits:
            total_changes += commit.changes
            total_additions += commit.additions
            total_deletions += commit.deletions

            # following ifs compare current commit with current biggest/smallest
            if commit.changes > most_changes:
                most_changes = commit.changes
                self.most_changes = (most_changes, commit)
            if commit.changes < least_changes:
                least_changes = commit.changes
                self.least_changes = (least_changes, commit)

            if commit.additions > most_additions:
                most_additions = commit.additions
                self.most_additions = (most_additions, commit)
            if commit.additions < least_additions:
                least_additions = commit.additions
                self.least_additions = (least_additions, commit)

            if commit.deletions > most_deletions:
                most_deletions = commit.deletions
                self.most_deletions = (most_deletions, commit)
            if commit.deletions < least_deletions:
                least_deletions = commit.deletions
                self.least_deletions = (least_deletions, commit)

            # counts commits in each day
            if commit.date in commits_per_day:
                commits_per_day[commit.date] += 1
            else:
                commits_per_day[commit.date] = 1

        most_commits = 0
        least_commits = float('inf')

        # finds the days with the most and least commits
        for day in commits_per_day:
            if commits_per_day[day] > most_commits:
                most_commits = commits_per_day[day]
                self.most_commits = (day, most_commits)
            if commits_per_day[day] < least_commits:
                least_commits = commits_per_day[day]
                self.least_commits = (day, least_commits)

        # gets averages
        self.avg_no_changes = round(total_changes / len(self.commits))
        self.avg_no_additions = round(total_additions / len(self.commits))
        self.avg_no_deletions = round(total_deletions / len(self.commits))

    # getter for total number of commits
    def total_commits(self):
        return len(self.commits)

    # pretty prints the list of commits
    def print_commits(self):
        pprint(self.commits)
        print("\n")


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


class FileContents:

    def __init__(self, name, path, contents):
        self.name = name
        self.path = path + name
        self.contents = contents
        self.extension = Path(name).suffix

    def to_dict(self):
        return {
            "name": self.name,
            "contents": self.contents
        }

    def __repr__(self):
        return f"Name: {self.name}\n" \
               f"Contents: {self.contents}\n"
