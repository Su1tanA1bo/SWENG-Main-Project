##*************************************************************************
#   pull data from github using graphql query
#   replaced api.py for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************


from commit import Commit
from file_contents import FileContents
from latest_commit import LatestCommit
from pprint import pprint
from queries import *
from requests import post
from user import UserStats


user_list = {"universal": UserStats()}
blames = {}
latest_commit = LatestCommit()


def run_commit_query(owner, repo, branch, auth):
    
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }
    has_next_page = True
    commit_list = []
    end_cursor = None

    while has_next_page:
        query = get_commit_query(owner, repo, branch, end_cursor)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # pprint(request.json())
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]

        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        if request.status_code == 200:
            commit_list += trimmed_request["edges"]
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    return commit_list


def run_text_query(owner, repo, branch, auth):
    global blames

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    query = get_text_query(owner, repo, branch)
    request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    # pprint(request.json())
    trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]["nodes"][0]["tree"]["entries"]
    # pprint(trimmed_request)

    if request.status_code == 200:
        store_files(trimmed_request)
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def run_blame_query(owner, repo, branch, auth):
    global blames

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    for file in latest_commit.files:
        query = get_blame_query(owner, repo, branch, file.path)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # pprint(request.json())
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["blame"]["ranges"]
        pprint(trimmed_request)

        if request.status_code == 200:
            assign_blame(trimmed_request)
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def store_files(tree, path=""):
    global latest_commit

    for entry in tree:
        if "text" not in entry["object"]:
            store_files(entry["object"]["entries"], path + entry["name"] + '/')
        else:
            latest_commit.add(FileContents(entry["name"], path, entry["object"]["text"]))


def assign_blame(blame_list):
    global latest_commit
    global user_list

    for blame in blame_list:
        lines = blame["endingLine"] - blame["startingLine"] + 1
        user_list[blame["commit"]["author"]["name"]].add_to_lines(lines)
        user_list["universal"].add_to_lines(lines)

    for name in user_list:
        user_list[name].calculate_code_ownership(user_list["universal"].lines_in_latest_commit)


def commit_info(commit_list):
    global user_list

    for commit in commit_list:
        name = commit["node"]["author"]["name"]
        sha = commit["node"]["oid"]
        message = commit["node"]["message"]

        date = commit["node"]["committedDate"]
        day = date[:10]
        time = date[11:-1]

        additions = commit["node"]["additions"]
        deletions = commit["node"]["deletions"]
        commit_object = Commit(name, sha, message, day, time, additions, deletions)

        if name in user_list:
            user_list[name].add(commit_object)
        else:
            user_list[name] = UserStats(commit_object)
        user_list["universal"].add(commit_object)


def print_stats():
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
            print(f"Largest commit: {user_list[name].most_changes[0]} changes by {user_list[name].most_changes[1].author}\n")
        else:
            print(f"Largest commit: {user_list[name].most_changes[0]} changes\n")
        # user_list[name].print_commits()

    print("\nFiles:\n")
    for file in latest_commit.files:
        print(f"Name: {file.name}\n"
              f"Path: {file.path}\n"
              f"Contents:\n{file.contents}\n")


def get_stats(owner, repo, branch, auth):
    result = run_commit_query(owner, repo, branch, auth)  # Execute the query
    commit_info(result)
    # pprint(result)

    run_text_query(owner, repo, branch, auth)
    run_blame_query(owner, repo, branch, auth)

    print_stats()


if __name__ == '__main__':
    owner = "Su1tanA1bo"
    repo = "SWENG-Main-Project"
    branch = "dev"
    auth = "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"

    get_stats(owner, repo, branch, auth)
