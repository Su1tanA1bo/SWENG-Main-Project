##*************************************************************************
#   api calls and handling of the response
#
#   @author	 Jamie Taylor
#   @Creation Date: 16/11/2022
##*************************************************************************

import json
from pprint import pprint

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


def fetch_list(username, repo, auth):

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }
    params = {"per_page": 100}

    another_page = True
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    results = []

    while another_page:  # the list of teams is paginated
        response = get(url, headers=headers, params=params)
        j_response = json.loads(response.text)
        results.append(j_response)
        if "next" in response.links:  # check if there is another page of organisations
            url = response.links["next"]["url"]
        else:
            another_page = False

    return results


def fetch_commit(username, repo, auth, ref):

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json"
    }

    # if ref specified as input, searches for specific commit, otherwise lists all commits
    url = f"https://api.github.com/repos/{username}/{repo}/commits/{ref}"
    response = get(url, headers=headers).json()
    return response


def commit_info(username, repo, auth, json_list):
    user_list = {"universal": UserStats()}
    for j_response in json_list:
        for entry in j_response:
            name = entry["commit"]["author"]["name"]
            date = entry["commit"]["author"]["date"]
            day = date[:10]
            time = date[11:-1]

            sha = entry["sha"]
            commit_json = fetch_commit(username, repo, auth, sha)
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
    username = "taylorj8"
    repo = "protocol"
    auth = "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"

    response = fetch_list(username, repo, auth)
    pprint(response)
    commit_info(username, repo, auth, response)
