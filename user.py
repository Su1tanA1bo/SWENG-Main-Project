##*************************************************************************
#   data structure containing all relevant data about a user
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint


class User:

    def __init__(self, name, commit):
        self.name = name
        self.commits = {}
        self.total_commits = 0
        self.add(commit)

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

    def add(self, commit):
        if commit.date in self.commits:
            self.commits[commit.date].append(commit)
        else:
            self.commits[commit.date] = [commit]
        self.total_commits += 1

    def resolve_stats(self):
        self.days_committed = len(self.commits)
        self.avg_freq = round(self.total_commits / self.days_committed)

        most_commits = 0
        least_commits = float('inf')

        most_changes = 0
        least_changes = float('inf')

        most_additions = 0
        least_additions = float('inf')

        most_deletions = 0
        least_deletions = float('inf')

        for day in self.commits:
            if len(self.commits[day]) > most_commits:
                most_commits = len(self.commits[day])
                self.most_commits = (day, most_commits)

            if len(self.commits[day]) < least_commits:
                least_commits = len(self.commits[day])
                self.least_commits = (day, least_commits)

                for commit in self.commits[day]:
                    if commit.total_changes > most_changes:
                        most_changes = commit.total_changes
                        self.most_changes = (most_changes, commit)
                    if commit.total_changes < least_changes:
                        least_changes = commit.total_changes
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

    def return_commit_message(self, day, time):
        return self.commits[day][time]["Message"]

    def print_commits(self):
        pprint(self.commits)
