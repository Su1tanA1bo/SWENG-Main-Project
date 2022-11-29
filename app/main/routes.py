##*************************************************************************
#   File handling main routing of the webpages. 
#   Contains functions taking url as input, and then calls html files with passed info
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************

from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models import User, Post
from app.main import bp
from app.models import UserStats 
from query import *


#function for updating time user was last seen at. Currently in UTC, will update later
@bp.route('/get_stats_r', methods=['GET'])
def get_stats_r():
    get_stats("Su1tanA1bo", "SWENG-Main-Project", "api-calls", "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")

    list_user = []
    list_total_commits = []
    list_Avg_Frq = []
    list_Most_Commits = []
    list_Least_Commits = []
    list_Largest_Commit = []
    list_Days_Commited=[]
    list_Avg_Size=[]
    for name in user_list:
        list_user += [name]
        list_total_commits += [user_list[name].total_commits()]
        list_Avg_Frq += [user_list[name].avg_freq]
        list_Most_Commits += [user_list[name].most_commits[1]]
        list_Least_Commits += [user_list[name].least_commits[1]]
        list_Largest_Commit += [user_list[name].most_changes[0]]
        list_Days_Commited += [user_list[name].days_committed]
        list_Avg_Size += [user_list[name].avg_no_changes]

#function for updating time user was last seen at. Currently in UTC, will update later
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.locale = str(get_locale())
        db.session.commit()

#function for handling webapp home page. Displays all posts from followed users.
@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@login_required
def index():
    
    return render_template('index.html', title='Home')


#function for handling explore webpage, which shows new users available to be followed
@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                          next_url=next_url, prev_url=prev_url)
    

#function for handling indivual user pages on site
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    next_url = url_for('main.user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, )



@bp.route('/FOC')
@login_required
def FOC():
   return render_template("FOC.html", listOfUsers=list_user, listOfComTotal=list_total_commits, listOfAvgFrq=list_Avg_Frq, listOfMostCommits=list_Most_Commits, listOfLeastCommits=list_Least_Commits)

@bp.route('/SOC')
@login_required
def SOC():
    
    return render_template("SOC.html", listOfUsers=list_user, listOfLargestCommit=list_Largest_Commit, listOfDays=list_Days_Commited, listOfAvgSize=list_Avg_Size)

@bp.route('/LOC')
@login_required
def LOC():
 return render_template("LOC.html")

@bp.route('/CC')
@login_required
def CC():
 return render_template("CC.html")

#function for handling edit profile page
@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)

#function for handling new follows to user withing webapp
@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))

#function for handling unfollows to user withing webapp

