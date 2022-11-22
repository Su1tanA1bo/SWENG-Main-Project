##*************************************************************************
#  Main file for webapp. Imports everything from ./app directory
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************

from app import create_app, db, cli
from app.models import User, Post

app = create_app()
cli.register(app)

#shell processor necessary for flask commands
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}
