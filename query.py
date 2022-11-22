from pprint import pprint
from requests import post


def run_query(owner, repo, auth):  # A simple function to use requests.post to make the API call. Note the json= section.
    
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }
    
    request = post('https://api.github.com/graphql', json={'query': get_query(owner, repo, "main")}, headers=headers)
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


if __name__ == '__main__':
    owner = "taylorj8"
    repo = "protocol"
    auth = "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"

    result = run_query(owner, repo, auth)  # Execute the query
    pprint(result)

    # remaining_rate_limit = result["data"]["rateLimit"]["remaining"]  # Drill down the dictionary
    # print("Remaining rate limit - {}".format(remaining_rate_limit))
