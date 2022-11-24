##*************************************************************************
#   pull data from github using graphql query
#   replaced api.py for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 22/11/2022
##*************************************************************************

from app import db
from commit import Commit
from file_contents import FileContents
from queries import *
from requests import post
from user import UserStats
from radon.visitors import ComplexityVisitor


user_list = {"universal": UserStats()}
latest_commit = []


# first api call - gets a list of commits and information about them
def run_commit_query(owner, repo, branch, auth):
    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

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
def run_text_query(owner, repo, branch, auth):
    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

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
def run_blame_query(owner, repo, branch, auth):
    # stores the authorisation token and accept
    headers = {
        "Authorization": "token " + auth,
        "Accept": "application/vnd.github+json",
    }

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

        # add each commit to the database
        db.session.add(commit)

        # adds the commit to a user if it exists, or makes a new user with the commit if it doesn't
        if name in user_list:
            user_list[name].add(commit)
        else:
            user_list[name] = UserStats(commit)
        # adds the commit to the "universal" user - represents group stats
        user_list["universal"].add(commit)


# recursively traverses the tree of files storing each file in a fileContents object
def store_files(tree, path=""):
    global latest_commit

    for entry in tree:
        if "text" not in entry["object"]:
            # if nested, goes one level down
            store_files(entry["object"]["entries"], path + entry["name"] + '/')
        else:
            # if contains "text" field, makes new file object and adds it to the latest_commit list
            latest_commit.append(FileContents(entry["name"], path, entry["object"]["text"]))


# assigns lines of code written to each user
def assign_blame(blame_list):
    global latest_commit
    global user_list

    # iterates through blame_list (json format) and gets the lines written by each user
    for blame in blame_list:
        lines = blame["endingLine"] - blame["startingLine"] + 1
        user_list[blame["commit"]["author"]["name"]].add_to_lines(lines)
        user_list["universal"].add_to_lines(lines)

    # calculates the percentage of code each user owns
    for name in user_list:
        user_list[name].calculate_code_ownership(user_list["universal"].lines_written)


# prints the results to the console
def print_stats():
    print("\nFiles:\n")
    for file in latest_commit:
        print(f"Name: {file.name}\n"
              f"Path: {file.path}\n"
              f"Contents:\n{file.contents}\n")

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

        if name == "universal":
            print(f"Largest commit: {user_list[name].most_changes[0]} changes by {user_list[name].most_changes[1].author}\n")
        else:
            print(f"Largest commit: {user_list[name].most_changes[0]} changes\n")
        # user_list[name].print_commits()


# gathers all the api calls into a single function
def get_stats(owner, repo, branch, auth):
    run_commit_query(owner, repo, branch, auth)
    run_text_query(owner, repo, branch, auth)
    run_blame_query(owner, repo, branch, auth)

    # resolve the stats for each user and add it to the database
    for name in user_list:
        user_list[name].resolve_stats()
        db.session.add(user_list[name])
    # commit the info to the database
    db.session.commit()


# main function for testing code
if __name__ == '__main__':
    owner = "Su1tanA1bo"
    repo = "SWENG-Main-Project"
    branch = "api-calls"
    auth = "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"

    print(f"Gathering data from {repo}, branch {branch}...")
    get_stats(owner, repo, branch, auth)
    print_stats()
    number_of_files_scanned = 0
    total_complexity_score = 0
    v = ComplexityVisitor
    for file in latest_commit:
        print("name: "+str(file.name))
        print("extension: "+str(file.extension))
        if str(file.extension) == ".py":
             v.from_code(file.contents)
             print(v.complexity)
    
        
