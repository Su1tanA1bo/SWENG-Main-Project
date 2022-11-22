from requests import post


def run_query(query, auth): # A simple function to use requests.post to make the API call. Note the json= section.
    
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }
    params = {"per_page": 1}
    
    request = post('https://api.github.com/graphql', json={'query': query}, headers=headers, params=params)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        
# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query = """
{
  viewer {
    login
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""

result = run_query(query) # Execute the query
remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
print("Remaining rate limit - {}".format(remaining_rate_limit))