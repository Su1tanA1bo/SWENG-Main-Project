##*************************************************************************
#   pull data from github using graphql query
#   replaced api.py for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************


from pprint import pprint
from requests import post
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
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]
        pprint(trimmed_request)

        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        if request.status_code == 200:
            commit_list += trimmed_request["edges"]
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    return commit_list


def commit_info(commit_list):
    user_list = {"universal": UserStats()}
    for commit in commit_list:
        name = commit["node"]["author"]["name"]
        date = commit["node"]["committedDate"]
        day = date[:10]
        time = date[11:-1]

        sha = commit["node"]["oid"]
        message = commit["node"]["message"]
        additions = commit["node"]["additions"]
        deletions = commit["node"]["deletions"]
        commit = make_commit(name, sha, message, day, time, additions, deletions)

        if name in user_list:
            user_list[name].add(commit)
        else:
            user_list[name] = UserStats(commit)
        user_list["universal"].add(commit)

    print_stats(user_list)


def get_query(repo, owner, branch, end_cursor):

    after = ""
    if end_cursor is not None:
        after = f', after: "{end_cursor}"'

    # The GraphQL query defined as a multi-line string.
    query = """
    {
        repository(name: "%s", owner: "%s") {
            ref(qualifiedName: "%s") {
                target {
                    ... on Commit {
                        id
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
                                    blame(path: "requirements.txt") {
                                        ranges {
                                            commit {
                                                author {
                                                    name
                                                }
                                            }
                                            startingLine
                                            endingLine
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
    owner = "Su1tanA1bo"
    repo = "SWENG-Main-Project"
    branch = "blame"
    auth = "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"

    result = run_query(owner, repo, branch, auth)  # Execute the query
    # pprint(result)
    commit_info(result)
