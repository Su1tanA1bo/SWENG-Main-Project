##*************************************************************************
#   pull data from github using graphql query
#   replaced api.py for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************

from complexity import run_Complexity_Checker
from data_structures import *
from queries import *
from radon.complexity import cc_rank
from requests import post

GROUP_STATS = "All Users"
user_list = {GROUP_STATS: UserStats()}
branch_names = []
latest_commit = []
Repo_Complexity_Score = 0


def run_branch_query(owner, repo, auth):
    global branch_names

    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    # for pagination
    has_next_page = True
    end_cursor = None

    # query can only fetch 100 commits, so keeps fetching until all commits fetched
    while has_next_page:

        # gets the query and performs call, on subsequent call passes in end_cursor for pagination
        query = get_branch_query(owner, repo, end_cursor)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # trims the result of the api call to remove unnecessary nesting
        pprint(request.json())
        trimmed_request = request.json()["data"]["repository"]["refs"]

        # determines if all commits have been fetched
        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        # if api call was successful, adds the commits to the commit list
        if request.status_code == 200:
            for node in trimmed_request["nodes"]:
                branch_names.append(node["name"])
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# first api call - gets a list of commits and information about them
def run_commit_query(owner, repo, branch, headers):
    # stores the list of commits
    commit_list = []
    # for pagination
    has_next_page = True
    end_cursor = None

    # query can only fetch 100 commits, so keeps fetching until all commits fetched
    while has_next_page:

        # gets the query and performs call, on subsequent call passes in end_cursor for pagination
        query = get_commit_query(owner, repo, branch, end_cursor)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # trims the result of the api call to remove unnecessary nesting
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]

        # determines if all commits have been fetched
        has_next_page = trimmed_request["pageInfo"]["hasNextPage"]
        if has_next_page:
            end_cursor = trimmed_request["pageInfo"]["endCursor"]

        # if api call was successful, adds the commits to the commit list
        if request.status_code == 200:
            commit_list += trimmed_request["edges"]
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    # processes list of commits
    commit_info(commit_list)


# second api call - text from every file in latest commit
def run_text_query(owner, repo, branch, headers):
    # gets the query and performs call
    query = get_text_query(owner, repo, branch)
    request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    # trims the result of the api call to remove unnecessary nesting
    trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["history"]["nodes"][0]["tree"]["entries"]

    # if api call was successful, calls function to process the result into file objects
    if request.status_code == 200:
        store_files(trimmed_request)
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


# final api call - blames each line of code in every file of the latest commit
def run_blame_query(owner, repo, branch, headers):
    # iterates over the files stored in latest_commit - a separate call must be done for each file
    for file in latest_commit:
        # gets query, passing in file path
        query = get_blame_query(owner, repo, branch, file.path)
        request = post('https://api.github.com/graphql', json={'query': query}, headers=headers)
        # trims the result of the api call to remove unnecessary nesting
        trimmed_request = request.json()["data"]["repository"]["ref"]["target"]["blame"]["ranges"]

        # if api call was successful, calls to assign blame to each user
        if request.status_code == 200:
            assign_blame(trimmed_request)
        else:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def get_Complexity_Values():
    #   will return repo complexity score and individual complexity score of each file.
    #   dictionary with individual file complexity scores will be represented like:
    #   Dictionary with key being filename and value being a list with index 0 being complexity value (number)
    #   and index 1 being complexity rank (A,B,C...) or ->
    #   { 'fileName.py' = [ FileComplexityValue, FileComplexityRank ] }

    number_of_functions_scanned = 0
    total_complexity_score = 0
    number_of_files_scanned = 0
    codeComplexityValuesDict = {}
    for file in latest_commit:
        if file.extension == ".py":
            complexityResults = run_Complexity_Checker(file)
            number_of_functions_scanned += complexityResults[0]
            total_complexity_score += complexityResults[1]
            number_of_files_scanned += 1
            codeComplexityValuesDict[file.name] = [complexityResults[2], complexityResults[3]]
            print(codeComplexityValuesDict)

    global Repo_Complexity_Score
    Repo_Complexity_Score = total_complexity_score / number_of_functions_scanned
    Repo_Complexity_Rank = cc_rank(Repo_Complexity_Score)
    # print(f"Repo Complexity Score = {Repo_Complexity_Score}")
    # print(f"Repo Complexity Rank = {Repo_Complexity_Rank}")


# assigns the info about the commits to each user
def commit_info(commit_list):
    global user_list

    # gets info from commit_list (json format) and stores the results in a commit object
    for commit_json in commit_list:
        name = commit_json["node"]["author"]["name"]
        sha = commit_json["node"]["oid"]
        message = commit_json["node"]["message"]

        date = commit_json["node"]["committedDate"]
        day = date[:10]
        time = date[11:-1]

        additions = commit_json["node"]["additions"]
        deletions = commit_json["node"]["deletions"]
        commit = Commit(name, sha, message, day, time, additions, deletions)

        # adds the commit to a user if it exists, or makes a new user with the commit if it doesn't
        if name in user_list:
            user_list[name].add(commit)
        else:
            user_list[name] = UserStats(commit)
        # adds the commit to the "Group" user - represents group stats
        user_list[GROUP_STATS].add(commit)


# recursively traverses the tree of files storing each file in a fileContents object
def store_files(tree, path=""):
    global latest_commit

    for entry in tree:
        if "text" in entry["object"]:
            # if contains "text" field, makes new file object and adds it to the latest_commit list
            latest_commit.append(FileContents(entry["name"], path, entry["object"]["text"]))
        elif "entries" in entry["object"]:
            # if nested, goes one level down
            store_files(entry["object"]["entries"], path + entry["name"] + '/')


# assigns lines of code written to each user
def assign_blame(blame_list):
    global user_list, latest_commit

    # iterates through blame_list (json format) and gets the lines written by each user
    for blame in blame_list:
        lines = blame["endingLine"] - blame["startingLine"] + 1
        user_list[blame["commit"]["author"]["name"]].add_to_lines(lines)
        user_list[GROUP_STATS].add_to_lines(lines)

    # calculates the percentage of code each user owns
    for name in user_list:
        user_list[name].calculate_code_ownership(user_list[GROUP_STATS].lines_written)


# prints the results to the console for testing purposes
def print_stats():
    print(f"\nBranches: {branch_names}\n")
    print("\nFiles:\n")
    for file in latest_commit:
        print(f"Name: {file.name}\n"
              f"Path: {file.path}\n")
        # f"Contents:\n{file.contents}\n")

    print("\nUsers:\n")
    for name in user_list:
        print(f"User: {name}\n"
              f"Total commits: {user_list[name].total_commits()}\n"
              f"Days committed: {user_list[name].days_committed}\n"
              f"Most commits: {user_list[name].most_commits[1]} on {user_list[name].most_commits[0]}\n"
              f"Least commits: {user_list[name].least_commits[1]} on {user_list[name].least_commits[0]}\n"
              f"Average frequency: {user_list[name].avg_freq} commits per day\n"
              f"Average commit size: {user_list[name].avg_no_changes} changes\n"
              f"Lines written: {user_list[name].lines_written}\n"
              f"Percentage ownership: {user_list[name].code_ownership}%")

        if name == GROUP_STATS:
            print(
                f"Largest commit: {user_list[name].most_changes[0]} changes by {user_list[name].most_changes[1].author}\n")
        else:
            print(f"Largest commit: {user_list[name].most_changes[0]} changes\n")
        # user_list[name].print_commits()


# resets the stats
def reset_stats():
    global Repo_Complexity_Score, user_list, latest_commit, branch_names

    user_list = {GROUP_STATS: UserStats()}
    branch_names = []
    latest_commit = []
    Repo_Complexity_Score = 0


# gathers all the api calls into a single function
def get_stats(owner, repo, branch, auth):
    # reset the stats before running queries in case data was fetched previously
    reset_stats()

    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

    run_commit_query(owner, repo, branch, headers)
    run_text_query(owner, repo, branch, headers)
    run_blame_query(owner, repo, branch, headers)
    # resolve the stats for each user
    for name in user_list:
        user_list[name].resolve_stats()


# main function for testing code
if __name__ == '__main__':
    owner = "Moeto88"
    repo = "SWENG_Group43"
    branch = "master"
    auth = "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"

    run_branch_query(owner, repo, auth)

    print(f"Gathering data from {repo}, branch {branch}...")
    get_stats(owner, repo, branch, auth)
    get_Complexity_Values()
    print_stats()

    # run_branch_query(owner, repo, auth)
    #
    # print(f"Gathering data from {repo}, branch {branch} again...")
    # get_stats(owner, repo, branch, auth)
    # get_Complexity_Values()
    # print_stats()
