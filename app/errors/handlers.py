##*************************************************************************
#   file for handling webpage errors and sending to error pages
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************

from flask import render_template
from app import db
from app.errors import bp


#function handles error of type 404
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


#function handles error of type 500
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
