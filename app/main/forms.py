from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User, Repository

#form object for editing user profiles
class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))

#Empty form object with only submit button, useful for following
class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

#Form for submitting new blog posts, which will be added to db
class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

#Form for adding additional users to a repo
class AddUserToRepo(FlaskForm):
    #Enter username as text field
    username = StringField(_l('Username'), validators=[DataRequired()])
    submit = SubmitField(_l('Add User to Repo'))

    ##Only add user to repo if user is on the site
    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            raise ValidationError(_('User not found.'))

#Form for removing users from a repo
class RemoveUserFromRepo(FlaskForm):
    #Enter username as text field
    username = StringField(_l('Username'), validators=[DataRequired()])
    submit = SubmitField(_l('Remove User from Repo'))

    #Come initiaed with the repo you are removing from
    def __init__(self, repo_id, *args, **kwargs):
        super(RemoveUserFromRepo, self).__init__(*args, **kwargs)
        self.repo = Repository.query.filter_by(id=repo_id).first() 

    ##Only add user to repo if user is on the site
    def validate_username(self, username):
        if not self.repo.is_member(self.username.data):
            raise ValidationError(_('User already does not have acess to this repository.'))
