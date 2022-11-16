##*************************************************************************
#   api calls are made in this file
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from requests import get
from pprint import pprint


if __name__ == '__main__':
    username = "taylorj8"
    repo = "protocol"
    auth = "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"

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{username}/{repo}/commits"

    response = get(url, headers=headers).json()

    pprint(response)

