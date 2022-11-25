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
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login

#Followers relational table. Shows an example of a many to many relationship in SQL
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

#Class for database User, containing methods for setting and checking info
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    #defines followers and following as a many to many relationship within user
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

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

    #Methods for allowing users to change their following relationships with other users
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0
    #Complicated query that allows a user to see all their followed posts
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

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

#Class for posts in database.
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

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

    ##TODO: add storage for all the data that a repository holds here

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
            if commit.changes > most_changes:
                most_changes = commit.changes
                self.most_changes = (most_changes, commit)
            if commit.changes < least_changes:
                least_changes = commit.changes
                self.least_changes = (least_changes, commit)

            if commit.additions > most_additions:
                most_additions = commit.additions
                self.most_additions = (most_additions, commit)
            if commit.additions < least_additions:
                least_additions = commit.additions
                self.least_additions = (least_additions, commit)

            if commit.deletions > most_deletions:
                most_deletions = commit.deletions
                self.most_deletions = (most_deletions, commit)
            if commit.deletions < least_deletions:
                least_deletions = commit.deletions
                self.least_deletions = (least_deletions, commit)

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
                self.most_commits = (day, most_commits)
            if commits_per_day[day] < least_commits:
                least_commits = commits_per_day[day]
                self.least_commits = (day, least_commits)

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
