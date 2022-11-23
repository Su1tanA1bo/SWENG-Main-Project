##*************************************************************************
#   pull data from github using graphql query
#   replaced api.py for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************


from commit import Commit
from pprint import pprint
from requests import post
from user import UserStats


user_list = {"universal": UserStats()}
file_names = []
blames = {}


def run_query(owner, repo, branch, auth):
    
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }
    has_next_page = True
    commit_list = []
    end_cursor = None

    while has_next_page:
        query = get_query(owner, repo, branch, end_cursor)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        pprint(request.json())
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]

        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        if request.status_code == 200:
            commit_list += trimmed_request["edges"]
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    return commit_list


def query_last_commit(owner, repo, branch, auth):
    global file_names
    global blames

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    # for name in file_names:
    query = get_bl_query(owner, repo, branch)
    request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    # pprint(request.json())
    trimmed_request = request.json()["data"]["repository"]["object"]["entries"]
    pprint(trimmed_request)

    if request.status_code == 200:
        blames["name"] = trimmed_request
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def commit_info(commit_list):
    global user_list
    global file_names

    # gets file names in most recent commit
    entries = commit_list[0]["node"]["tree"]["entries"]
    for entry in entries:
        file_names.append(entry["name"])

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


def get_query(repo, owner, branch, end_cursor=None):

    if end_cursor is not None:
        after = f', after: "{end_cursor}"'
    else:
        after = ""

    query = """
    {
        repository(name: "%s", owner: "%s") {
            ref(qualifiedName: "%s") {
                target {
                    ... on Commit {
                        history(first: 100%s) {
                            pageInfo {
                                hasNextPage
                                endCursor
                            }
                            edges {
                                node {
                                    oid
                                    message
                                    committedDate
                                    additions
                                    deletions
                                    author {
                                        name
                                    }
                                    tree {
                                        entries{
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (owner, repo, branch, after)

    return query


def get_bl_query(repo, owner, branch):

    query = """
    {
        repository(name: "%s", owner: "%s") {
            object(expression: "HEAD:") {
                ... on Tree {
                    entries {
                        name
                        object {
                            ... on Blob {
                                text
                            }
                            ... on Tree {
                                entries {
                                    name
                                    object {
                                        ... on Blob {
                                            text
                                        }
                                        ... on Tree {
                                            entries {
                                                name
                                                object {
                                                    ... on Blob {
                                                        text
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (owner, repo)

    return query


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


def get_stats(owner, repo, branch, auth):
    result = run_query(owner, repo, branch, auth)  # Execute the query
    # pprint(result)

    commit_info(result)
    query_last_commit(owner, repo, branch, auth)

    print_stats()


if __name__ == '__main__':
    owner = "Su1tanA1bo"
    repo = "SWENG-Main-Project"
    branch = "main"
    auth = "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"

    get_stats(owner, repo, branch, auth)
