##*************************************************************************
#   contains GraphQL queries for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 23/11/2022
##*************************************************************************


# initial query to get all the commits in a branch
def get_commit_query(repo, owner, branch, end_cursor=None):

    # for pagination
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


# query - pulls info from files nested up to four levels deep
# gets the name and text contained in all files
def get_text_query(repo, owner, branch):

    query = """
    {
        repository(name: "%s", owner: "%s") {
            ref(qualifiedName: "%s") {
                target {
                    ... on Commit {
                        history(first: 1) {
                            nodes {
                                tree {
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
                            }
                        }
                    }
                }
            }
        }
    }
    """ % (owner, repo, branch)

    return query


# query for getting the blame info for every line in every file in the latest commit
def get_blame_query(repo, owner, branch, path):

    query = """
    {
        repository(name: "%s", owner: "%s") {
            ref(qualifiedName: "%s") {
                target {
                    ... on Commit {
                        blame(path: "%s") {
                            ranges {
                                startingLine
                                endingLine
                                commit {
                                    author {
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
    """ % (owner, repo, branch, path)

    return query
