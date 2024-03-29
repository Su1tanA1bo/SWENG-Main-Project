##*************************************************************************
#   models file for all objects containied in database of flask app
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************


from datetime import datetime
from hashlib import md5
from pprint import pprint
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

#Class for database User, containing methods for setting and checking info
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    #Methods for handling password resets, and generating/verifying secure tokens
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

#Method for loading a user by their ID
@login.user_loader
def load_user(id):
    return User.query.get(int(id))



#Members relational table. Used by repo to determine membership
repo_members = db.Table('repo_member',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('repo_id', db.Integer, db.ForeignKey('repository.id'))
)

#Class for posts in database.
class Repository(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reponame = db.Column(db.String(64), index=True, unique=True)

    
    code_complexity_value = db.Column(db.Float)
    code_complexity_rank = db.Column(db.String(64))
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #defines members as a many to many relationship within the repo
    members = db.relationship('User', secondary=repo_members,
            backref=db.backref('repos', lazy='dynamic'),
            lazy='dynamic')

    #Methods for allowing users to change their member relationships with repos
    def add_to(self, user):
        if not self.is_member(user.username):
            self.members.append(user)
    def remove_from(self, user):
        if self.is_member(user.username):
            self.members.remove(user)

    # Return true if user is owner, or is member
    def is_member(self, username):
        user = User.query.filter_by(username=username).first()
        if(user is None): return False
        if(user.id == self.owner_id): return True
        return self.members.filter(
            repo_members.c.user_id == user.id).count() > 0


#class for UserStats in the database
class UserStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    days_committed = db.Column(db.Integer)
    avg_freq = db.Column(db.Integer)
    most_commits = db.Column(db.Integer)
    least_commits = db.Column(db.Integer)

    # most and least additions/deletions/changes
    # tuple containing int and a dict representing the commit
    # these tuples are referred to by their sha as an identifier
    # for a flask db one to one relationship
    most_additions = db.Column(db.Integer, db.ForeignKey('commit.sha'))
    least_additions = db.Column(db.Integer, db.ForeignKey('commit.sha'))
    most_deletions = db.Column(db.Integer, db.ForeignKey('commit.sha'))
    least_deletions = db.Column(db.Integer, db.ForeignKey('commit.sha'))
    most_changes = db.Column(db.Integer, db.ForeignKey('commit.sha'))
    least_changes = db.Column(db.Integer, db.ForeignKey('commit.sha'))

    avg_no_additions = db.Column(db.Integer)
    avg_no_deletions = db.Column(db.Integer)
    avg_no_changes = db.Column(db.Integer)

    # blame info
    lines_written = db.Column(db.Integer)
    code_ownership = db.Column(db.Integer)

    #func for initing new object in db
    def __init__(self, commit = None):
        if commit is None:
            self.commits = []
        else:
            self.commits = [commit]
        ##init all the values from UserStats original here
        self.days_committed = -1
        self.avg_freq = -1
        
        self.most_commits = -1
        self.least_commits = -1

        self.avg_no_additions = -1
        self.avg_no_deletions = -1
        self.avg_no_changes = -1

        self.lines_written = -1
        self.code_ownership = -1

    # add a commit to commits list
    def add(self, commit):
        self.commits.append(commit)

    # finds the number of days that a user committed on
    def find_days_committed(self):
        days = set()
        for commit in self.commits:
            days.add(commit.date)
        return len(days)

    # function for adding number of lines written
    def add_to_lines(self, lines):
        self.lines_written += lines

    # calculate percentage of code owner by this user
    def calculate_code_ownership(self, total_lines):
        self.code_ownership = round((self.lines_written / total_lines) * 100, 3)

    # getter for total number of commits
    def total_commits(self):
        return len(self.commits)

    # pretty prints the list of commits
    def print_commits(self):
        pprint(self.commits)
        print("\n")

    # update all the relevant fields for a user
    def resolve_stats(self):
        self.days_committed = self.find_days_committed()
        self.avg_freq = round(len(self.commits) / self.days_committed)

        most_changes = 0
        least_changes = float('inf')

        most_additions = 0
        least_additions = float('inf')

        most_deletions = 0
        least_deletions = float('inf')

        total_changes = 0
        total_additions = 0
        total_deletions = 0

        # dict with date as key, number of commits as value
        commits_per_day = {}
        for commit in self.commits:
            total_changes += commit.changes
            total_additions += commit.additions
            total_deletions += commit.deletions

            # following ifs compare current commit with current biggest/smallest
            tempMostChanges = Commit.query.filter_by(sha=most_changes).first()
            if tempMostChanges is None:
                self.most_changes = commit.sha
            elif commit.changes > tempMostChanges.changes:
                self.most_changes = commit.sha

            tempLeastChanges = Commit.query.filter_by(sha=least_changes).first()
            if tempLeastChanges is None:
                self.least_changes = commit.sha
            elif commit.changes < tempLeastChanges.changes:
                self.least_changes = commit.sha

            tempMostAdditions = Commit.query.filter_by(sha=most_additions).first()
            if tempMostAdditions is None:
                self.most_additions = commit.sha
            elif commit.additions > tempMostAdditions.additions:
                self.most_additions = commit.sha

            tempLeastAdditions = Commit.query.filter_by(sha=least_additions).first()
            if tempLeastAdditions is None:
                self.least_additions = commit.sha
            elif commit.additions < tempLeastAdditions.additions:
                self.least_additions = commit.sha

            tempMostDeletions = Commit.query.filter_by(sha=most_deletions).first()
            if tempMostDeletions is None:
                self.most_deletions = commit.sha
            elif commit.deletions > tempMostDeletions.deletions:
                self.most_deletions = commit.sha

            tempLeastDeletions = Commit.query.filter_by(sha=least_deletions).first()
            if tempLeastDeletions is None:
                self.least_deletions = commit.sha
            elif commit.deletions < tempLeastDeletions.deletions:
                self.least_deletions = commit.sha

            # counts commits in each day
            if commit.date in commits_per_day:
                commits_per_day[commit.date] += 1
            else:
                commits_per_day[commit.date] = 1

        most_commits = 0
        least_commits = float('inf')

        # finds the days with the most and least commits
        for day in commits_per_day:
            if commits_per_day[day] > most_commits:
                most_commits = commits_per_day[day]
                self.most_commits = most_commits
            if commits_per_day[day] < least_commits:
                least_commits = commits_per_day[day]
                self.least_commits = least_commits

        # gets averages
        self.avg_no_changes = round(total_changes / len(self.commits))
        self.avg_no_additions = round(total_additions / len(self.commits))
        self.avg_no_deletions = round(total_deletions / len(self.commits))

#Class for commit in database. Works as a tuple in practie, as tuples cannot be stored in db naturally
class Commit(db.Model):
    author = db.Column(db.String(140), index=True)
    sha = db.Column(db.String(140), index=True, unique=True, primary_key=True)
    message = db.Column(db.String(140), index=True)
    date = db.Column(db.String(10))
    time = db.Column(db.String(12))
    additions = db.Column(db.Integer)
    deletions = db.Column(db.Integer)
    changes = db.Column(db.Integer)


    def __init__(self, name, sha=None, message=None, date=None, time=None, additions=-1, deletions=-1):
        self.author = name
        self.sha = sha
        self.message = message
        self.date = date
        self.time = time
        self.additions = additions
        self.deletions = deletions
        self.changes = additions + deletions

    def to_dict(self):
        return {
            "author": self.author,
            "sha": self.sha,
            "message": self.message,
            "date": self.date,
            "time": self.time,
            "additions": self.additions,
            "deletions": self.deletions,
            "changes": self.additions + self.deletions
        }

    def __repr__(self):
        return f"Author: {self.author}\n" \
               f"Message: {self.message}\n" \
               f"Sha: {self.sha}\n" \
               f"Additions: {self.additions}\n" \
               f"Deletions: {self.deletions}"
