##*************************************************************************
#   api calls and handling of the response
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from commit import Commit
from pprint import pprint
from requests import get
from user import User


def api_fetch(ref):
    username = "taylorj8"
    repo = "protocol"
    auth = "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"
    queries = "?per_page=10"
    if not ref:
        commit = ""
    else:
        commit = "/" + ref

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json"
    }

    # if ref specified as input, searches for specific commit, otherwise lists all commits
    url = f"https://api.github.com/repos/{username}/{repo}/commits{commit}{queries}"
    response = get(url, headers=headers).json()
    return response


def commit_info(json):
    commits = {}
    for entry in json:
        name = entry["commit"]["author"]["name"]
        date = entry["commit"]["author"]["date"]
        day = date[:10]
        time = date[11:-1]

        sha = entry["sha"]
        commit_json = api_fetch(sha)
        message = commit_json["commit"]["message"]
        changes = commit_json["stats"]
        commit = Commit(sha, message, day, time, changes["additions"], changes["deletions"])

        if name in commits:
            commits[name].add(commit)
        else:
            commits[name] = User(name, commit)

    print_stats(commits)


def print_stats(commits):
    for name in commits:
        commits[name].resolve_stats()
        print(f"User: {name}\n"
              f"Total commits: {commits[name].total_commits}\n"
              f"Days committed: {commits[name].days_committed}\n"
              f"Most commits: {commits[name].most_commits[1]} on {commits[name].most_commits[0]}\n"
              f"Least commits: {commits[name].least_commits[1]} on {commits[name].least_commits[0]}\n"
              f"Average frequency: {commits[name].avg_freq} commits per day\n"
              f"Largest commit: {commits[name].most_changes}\n")
        # commits[name].print_commits()


if __name__ == '__main__':
    response = api_fetch(False)
    # pprint(response)
    commit_info(response)
