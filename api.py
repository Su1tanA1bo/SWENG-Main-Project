##*************************************************************************
#   api calls and handling of the response
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

from requests import get
from user import UserStats


def make_commit(name, sha, message, date, time, additions, deletions):
    return {
        "author": name,
        "sha": sha,
        "message": message,
        "date": date,
        "time": time,
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions
    }


def api_fetch(ref):
    username = "taylorj8"
    repo = "protocol"
    auth = "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"
    queries = "?per_page=100"
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
    user_list = {"universal": UserStats()}
    for entry in json:
        name = entry["commit"]["author"]["name"]
        date = entry["commit"]["author"]["date"]
        day = date[:10]
        time = date[11:-1]

        sha = entry["sha"]
        commit_json = api_fetch(sha)
        message = commit_json["commit"]["message"]
        changes = commit_json["stats"]
        commit = make_commit(name, sha, message, day, time, changes["additions"], changes["deletions"])

        if name in user_list:
            user_list[name].add(commit)
        else:
            user_list[name] = UserStats(commit)
        user_list["universal"].add(commit)

    print_stats(user_list)


def print_stats(user_list):
    for name in user_list:
        user_list[name].resolve_stats()

        print(f"User: {name}\n"
              f"Total commits: {user_list[name].total_commits()}\n"
              f"Days committed: {user_list[name].days_committed}\n"
              f"Most commits: {user_list[name].most_commits[1]} on {user_list[name].most_commits[0]}\n"
              f"Least commits: {user_list[name].least_commits[1]} on {user_list[name].least_commits[0]}\n"
              f"Average frequency: {user_list[name].avg_freq} commits per day\n"
              f"Average commit size: {user_list[name].avg_no_changes} changes")

        if name == "universal":
            print(f"Largest commit: {user_list[name].most_changes[0]} changes by {user_list[name].most_changes[1]['author']}\n")
        else:
            print(f"Largest commit: {user_list[name].most_changes[0]} changes\n")
        # user_list[name].print_commits()


if __name__ == '__main__':
    response = api_fetch(False)
    # pprint(response)
    commit_info(response)
