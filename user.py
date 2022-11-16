##*************************************************************************
#   data structure containing all relevant data about a user
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint


class User:

    def __init__(self, name, day, time):
        self.name = name
        self.commits = {}
        self.total_commits = 0
        self.add_commit(day, time)

        self.days_committed = None
        self.avg_freq = -1
        self.most_commits = -1
        self.least_commits = -1

    def add_commit(self, day, time):
        if day in self.commits:
            self.commits[day].append(time)
        else:
            self.commits[day] = [time]
        self.total_commits += 1

    def resolve_stats(self):
        self.days_committed = len(self.commits)
        self.avg_freq = round(self.total_commits / self.days_committed)

        most = 0
        least = float('inf')

        for day in self.commits:
            if len(self.commits[day]) > most:
                most = len(self.commits[day])
                self.most_commits = (day, most)
            if len(self.commits[day]) < least:
                least = len(self.commits[day])
                self.least_commits = (day, least)

    def print_commits(self):
        pprint(self.commits)
