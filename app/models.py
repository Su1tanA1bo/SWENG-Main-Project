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
    days_committed = db.Column(db.Integer)
    avg_freq = db.Column(db.Integer)
    most_commits = db.Column(db.Integer)
    least_commits = db.Column(db.Integer)

    most_additions = (-1, None)
    least_additions = (-1, None)
    most_deletions = (-1, None)
    least_deletions = (-1, None)
    most_changes = (-1, None)
    least_changes = (-1, None)

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
        days_committed = -1
        avg_freq = -1
        most_commits = -1
        least_commits = -1

        avg_no_additions = -1
        avg_no_deletions = -1
        avg_no_changes = -1

        #lists and dicts in the user.py need to become tables in models.py
