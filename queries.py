##*************************************************************************
#   contains GraphQL queries for pulling data
#
#   @author	 Jamie Taylor
#   @Creation Date: 23/11/2022
##*************************************************************************


def get_commit_query(repo, owner, branch, end_cursor=None):

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


def get_text_query(repo, owner):

    # query - pulls info from files nested up to four levels deep
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
    """ % (owner, repo)

    return query


def get_blame_query(repo, owner, branch, path):

    # query - pulls info from files nested up to four levels deep
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