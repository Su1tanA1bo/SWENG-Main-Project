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
from app.main.forms import EditProfileForm, EmptyForm, AddUserToRepo, RemoveUserFromRepo
from app.models import User, Repository
from app.main import bp
from query import *


#function for updating time user was last seen at. Currently in UTC, will update later
get_stats("Su1tanA1bo", "SWENG-Main-Project", "api-calls", "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")
get_Complexity_Values()

#User List Object
list_user = []

#FOC List objects
list_total_commits = []
list_Avg_Frq = []
list_Most_Commits = []
list_Least_Commits = []

#SOC List objects
list_Most_Changes = []
list_Average_Number_Changes = []
list_Days_Committed = []

#LOC List Objects
list_Lines_Written = []
list_Percentage_Ownership = []
list_Number_Of_Most_Changes = []
list_Number_Of_Least_Changes = []

#CC List Objects
total_repo_complexity_score = Repo_Complexity_Score
number_of_functions_scanned = 0
list_code_complexity_values = []
list_code_complexity_ranks = []
list_file_names = []

#Add commit values to above lists
for name in user_list:
    #FOC
    list_user += [name]
    list_total_commits += [user_list[name].total_commits()]
    list_Avg_Frq += [user_list[name].avg_freq]
    list_Most_Commits += [(user_list[name].most_commits[1])]
    list_Least_Commits += [user_list[name].least_commits[1]]
    #SOC
    list_Most_Changes += [user_list[name].most_changes[0]]
    list_Average_Number_Changes += [user_list[name].avg_no_changes]
    list_Days_Committed += [user_list[name].days_committed]
    #LOC
    list_Lines_Written += [user_list[name].lines_written]
    list_Percentage_Ownership += [user_list[name].code_ownership]
    list_Number_Of_Most_Changes += [user_list[name].most_changes[0]]
    list_Number_Of_Least_Changes += [user_list[name].least_changes[0]]

for file in latest_commit:
    if file.extension == ".py":
        list_file_names += [file.name]
        list_code_complexity_values += [codeComplexityValuesDict[file.name][0]]
        list_code_complexity_ranks += [codeComplexityValuesDict[file.name][1]]


   

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

    

#function for handling indivual user pages on site
@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    form = EmptyForm()
    return render_template('user.html', user=user, )



@bp.route('/FOC')
@login_required
def FOC():
   return render_template("FOC.html", listOfUsers=list_user, listOfComTotal=list_total_commits, listOfAvgFrq=list_Avg_Frq, listOfMostCommits=list_Most_Commits, listOfLeastCommits=list_Least_Commits)

@bp.route('/SOC')
@login_required
def SOC():
    return render_template("SOC.html", listOfUsers=list_user, listOfMostChanges=list_Most_Changes, listOfAverageChanges=list_Average_Number_Changes, listOfDaysCommitted=list_Days_Committed)

@bp.route('/LOC')
@login_required
def LOC():
 return render_template("LOC.html", listOfUsers=list_user, listOfLinesWritten=list_Lines_Written, listOfPercentageOwnership=list_Percentage_Ownership, listOfMostChanges=list_Number_Of_Most_Changes, listOfLeastChanges=list_Number_Of_Least_Changes)

@bp.route('/CC')
@login_required
def CC():
 return render_template("CC.html", listOfFileNames=list_file_names, totalRepoCCScore=total_repo_complexity_score, numberOfFunctionsScanned=number_of_functions_scanned, listOfComplexityValues=list_code_complexity_values, listOfComplexityRanks=list_code_complexity_ranks)

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

#function for handling webapp home page. Displays all posts from followed users.

@bp.route('/repo/<reponame>', methods=['GET', 'POST'])
@login_required
def repo(reponame):
    repo = Repository.query.filter_by(reponame=reponame).first_or_404()

    if not repo.is_member(current_user.username):
        #If user is neither member or owner, redirect to index
        flash(_('You do not have access to this repo!'))
        return redirect(url_for('main.index'))


    ##TODO: All other data needed to be displayed on repo page goes here
    
    ##show a form to add users to repo only if owner of the form
    if(current_user.id == repo.owner_id):
        removeForm = RemoveUserFromRepo(repo.id)
        if removeForm.validate_on_submit() and removeForm.submit_remove.data:
            user_form = User.query.filter_by(username=removeForm.username_remove.data).first()
            if(user_form is not None):
                repo.remove_from(user_form)
                db.session.commit()
                flash(_('User removed from repo'))
            else:
                flash(_('User not found'))

        #add form to add user to repo if user is owner
        addform = AddUserToRepo()
        if addform.validate_on_submit() and addform.submit_add.data:
            user_form = User.query.filter_by(username=addform.username_add.data).first()
            if(user_form is not None):
                if(repo.is_member(user_form.username)):
                    flash(_('User is already a member of repo'))
                else:
                    repo.add_to(user_form)
                    db.session.commit()
                    flash(_('User added to repo'))
            else:
                flash(_('User not found'))

        #render template with forms only if user is owner
        return render_template('repo_owner.html', addform=addform, removeForm=removeForm) 


    ##TODO: Make repo.html file as part of frontend/change filename here
    ##TODO: When the above is done, it will also need to be passed the processed repo info from above
    return render_template('repo_viewer.html')