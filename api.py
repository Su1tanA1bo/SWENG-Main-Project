##*************************************************************************
#   api calls are made in this file
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from bisect import bisect_left, insort
from pprint import pprint
from requests import get


def is_present(x, list):
    i = bisect_left(list, x)
    if i != len(list) and list[i] == x:
        return True
    return False


if __name__ == '__main__':
    username = "taylorj8"
    repo = "protocol"
    auth = "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"

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{username}/{repo}/commits?&per_page=100"

    response = get(url, headers=headers).json()

    dates = {}
    for entry in response:
        name = entry["committer"]["login"]
        time = entry["commit"]["author"]["date"]

        if name in dates:
            insort(dates[name], time)
        else:
            dates[name] = [time]

    pprint(dates)

