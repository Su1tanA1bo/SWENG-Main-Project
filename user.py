##*************************************************************************
#   data structure containing all relevant data about a user
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint


def resolve_changes(commits, ref):
    most = (0, None)
    least = (float('inf'), None)

    # if self.commits[day][index] > most:
    #     most = self.commits[day].
    # if self.commits[day][index] < least:
    #     least = self.commits[day][index]

    for commit in commits:
        if commit.total_changes > most[0]:
            most = (commit.total_changes, commit)
        if commit.total_changes < least[0]:
            least = (commit.total_changes, commit)

    return most, least


class User:

    def __init__(self, name, day, time, commit):
        self.name = name
        self.commits = {}
        self.total_commits = 0
        self.add_commit(day, time, commit)

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

    def add_commit(self, day, time, commit):
        if day in self.commits:
            self.commits[day].append({time: commit})
        else:
            self.commits[day] = [{time: commit}]
        self.total_commits += 1

    def resolve_stats(self):
        self.days_committed = len(self.commits)
        self.avg_freq = round(self.total_commits / self.days_committed)

        most_commits = 0
        least_commits = float('inf')

        for day in self.commits:
            if len(self.commits[day]) > most_commits:
                most_commits = len(self.commits[day])
                self.most_commits = (day, most_commits)

            if len(self.commits[day]) < least_commits:
                least_commits = len(self.commits[day])
                self.least_commits = (day, least_commits)

            # self.most_additions, self.least_additions = self.resolve_changes(day, "additions")
            # self.most_deletions, self.least_deletions = self.resolve_changes(day, "deletions")
            self.most_changes, self.least_changes = resolve_changes(self.commits[day], "changes")

    def return_commit_message(self, day, time):
        return self.commits[day][time]["Message"]

    def print_commits(self):
        pprint(self.commits)
