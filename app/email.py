##*************************************************************************
#   file sending and recieving emails
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#   @Primary credit for code basis goes to:
#   https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
##*************************************************************************

from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail

#method for sending emails asynchronously, with threads
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

#Worker method for sending emails
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()