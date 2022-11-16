##*************************************************************************
#   api calls and handling of the response
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from pprint import pprint
from requests import get


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


def commits_per_day(json):
    commits = {}
    for entry in json:
        name = entry["commit"]["author"]["name"]
        date = entry["commit"]["author"]["date"]
        day = date[:10]
        time = date[11:-1]

        if name in commits:
            if day in commits[name]:
                commits[name][day].append(time)
            else:
                commits[name][day] = [time]
        else:
            commits[name] = {day: [time]}

    pprint(commits)


if __name__ == '__main__':
    response = api_fetch()
    commits_per_day(response)