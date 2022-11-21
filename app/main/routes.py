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
from app.main.forms import EditProfileForm, EmptyForm, PostForm, AddUserToRepo
from app.models import User, Post, Repository
from app.main import bp

#function for updating time user was last seen at. Currently in UTC, will update later
@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        g.locale = str(get_locale())
        db.session.commit()

#function for handling webapp home page. Displays all posts from followed users.
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #adding new posts
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    #displaying posts of followed users
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    #giving new pages to view next posts in sequence
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


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
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

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
@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


#function for handling webapp home page. Displays all posts from followed users.

@bp.route('/repo/<reponame>', methods=['GET', 'POST'])
@login_required
def repo(reponame):
    repo = Repository.query.filter_by(reponame=reponame).first_or_404()
    username = current_user.username
    user = repo.membered.query.filter_by(username=username).first()
    if user is None:
            flash(_('You do not have access to this repo!'))
            return redirect(url_for('main.user', username=username))

    ##TODO: All other data needed to be displayed on repo page goes here

    ##show a form to add users to repo only if owner of the form
    addform = EmptyForm
    if(current_user.id == repo.owner_id):
        addform = AddUserToRepo()
        if form.validate_on_submit():
            user_form = User.query.filter_by(username=addform.username.data).first()
            if(user_form is not None):
                repo.add_to(user_form)
                db.session.commit()
                flash(_('User added to repo'))
            else:
                flash(_('User not found'))

    return render_template('repo.html', user=user, addform=addform) ##TODO: Make repo.html file as part of frontend/change filename here
