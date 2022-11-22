from app.models import Commit

def listCommits_resolver(obj, info):
    try:
        commits = [commit.to_dict() for commit in Commit.query.all()]
        print(commits)
        payload = {
            "success": True,
            "commits": commits
        }
    except Exception as error:
        payload = {
            "success": False,
            "errors": [str(error)]
        }
    return payload