##*************************************************************************
#   init file for the authentication blueprints within the project
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes
