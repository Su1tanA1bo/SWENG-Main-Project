##*************************************************************************
#   api calls and handling of the response
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint
from requests import get
from user import User


def api_fetch():
    username = "taylorj8"
    repo = "protocol"
    auth = "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"

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{username}/{repo}/commits?&per_page=100"
    response = get(url, headers=headers).json()
    return response


def commit_info(json):
    commits = {}
    for entry in json:
        name = entry["commit"]["author"]["name"]
        date = entry["commit"]["author"]["date"]
        day = date[:10]
        time = date[11:-1]

        if name in commits:
            commits[name].add_commit(day, time)
        else:
            commits[name] = User(name, day, time)

    for name in commits:
        commits[name].resolve_stats()
        print(f"User: {name}\nDays committed: {commits[name].days_committed}\n"
              f"Most commits: {commits[name].most_commits[1]} on {commits[name].most_commits[0]}\n"
              f"Least commits: {commits[name].least_commits[1]} on {commits[name].least_commits[0]}\n"
              f"Average frequency: {commits[name].avg_freq} per day")
        commits[name].print_commits()


if __name__ == '__main__':
    response = api_fetch()
    commit_info(response)
