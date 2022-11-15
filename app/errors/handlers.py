##*************************************************************************
#   file for handling webpage errors and sending to error pages
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#
##*************************************************************************

from flask import render_template
from app import app, db

#function handles error of type 404
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

#function handles error of type 500
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500