##*************************************************************************
#   data structure containing all relevant data about a user
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint


class UserStats:

    def __init__(self, name, commit):
        self.name = name
        self.commits = [commit]

        self.days_committed = None
        self.avg_freq = -1
        self.most_commits = -1
        self.least_commits = -1

        self.most_additions = (-1, None)
        self.least_additions = (-1, None)
        self.most_deletions = (-1, None)
        self.least_deletions = (-1, None)
        self.most_changes = (-1, None)
        self.least_changes = (-1, None)

        self.avg_no_additions = -1
        self.avg_no_deletions = -1
        self.avg_no_changes = -1

    def add(self, commit):
        self.commits.append(commit)

    def find_days_committed(self):
        days = set()
        for commit in self.commits:
            days.add(commit["date"])
        return len(days)

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

        commits_per_day = {}
        for commit in self.commits:
            total_changes += commit["changes"]
            total_additions += commit["additions"]
            total_deletions += commit["deletions"]

            if commit["changes"] > most_changes:
                most_changes = commit["changes"]
                self.most_changes = (most_changes, commit)
            if commit["changes"] < least_changes:
                least_changes = commit["changes"]
                self.least_changes = (least_changes, commit)

            if commit["additions"] > most_additions:
                most_additions = commit["additions"]
                self.most_additions = (most_additions, commit)
            if commit["additions"] < least_additions:
                least_additions = commit["additions"]
                self.least_additions = (least_additions, commit)

            if commit["deletions"] > most_deletions:
                most_deletions = commit["deletions"]
                self.most_deletions = (most_deletions, commit)
            if commit["deletions"] < least_deletions:
                least_deletions = commit["deletions"]
                self.least_deletions = (least_deletions, commit)

            if commit["date"] in commits_per_day:
                commits_per_day[commit["date"]] += 1
            else:
                commits_per_day[commit["date"]] = 1

        most_commits = 0
        least_commits = float('inf')

        for day in commits_per_day:
            if commits_per_day[day] > most_commits:
                most_commits = commits_per_day[day]
                self.most_commits = (day, most_commits)
            if commits_per_day[day] < least_commits:
                least_commits = commits_per_day[day]
                self.least_commits = (day, least_commits)

        self.avg_no_changes = round(total_changes / len(self.commits))
        self.avg_no_additions = round(total_additions / len(self.commits))
        self.avg_no_deletions = round(total_deletions / len(self.commits))

    def total_commits(self):
        return len(self.commits)

    def print_commits(self):
        pprint(self.commits)
