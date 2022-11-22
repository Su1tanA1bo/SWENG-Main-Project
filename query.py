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


def run_query(owner, repo, auth):
    
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    query = get_query(owner, repo, "main")
    request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()["data"]["repository"]["ref"]["target"]["history"]["edges"]
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_query(repo, owner, branch):

    # The GraphQL query defined as a multi-line string.
    query = """
    {
      repository(name: "%s", owner: "%s") {
        ref(qualifiedName: "%s") {
          target {
            ... on Commit {
              id
              history(first: 100) {
                pageInfo {
                  hasNextPage
                }
                edges {
                  node {
                    oid
                    message
                    additions
                    deletions
                    author {
                      name
                      date
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """ % (owner, repo, branch)
    return query


def commit_info(commit_list):
    user_list = {"universal": UserStats()}
    for commit in commit_list:
        name = commit["node"]["author"]["name"]
        date = commit["node"]["author"]["date"]
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
    owner = "taylorj8"
    repo = "protocol"
    auth = "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"

    result = run_query(owner, repo, auth)  # Execute the query
    commit_info(result)
