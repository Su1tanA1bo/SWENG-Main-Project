# SWENG-Main-Project

Trello Board 
https://trello.com/invite/b/JzYBrrIW/ATTI9d8d7bbfa462b537c084dbc08148842b2CD9369B/sweng3main

## Running the app locally
### (Recommended) Run a virtual environment
It is recommended that you do all development with python inside of a virtual environment. 
Due to the large amount of packages and installs needed by this project, a virtual environment prevents any issues of overlapping dependencies from occuring.
As long as you have python installed, you should also have the ability to start a virtual environment. The commands for that are as follows:
* Create a virtual environment:
	`python -m venv venv`
* Activate your new virtual environment (Windows)
	`venv\Scripts\activate`
* Activate your new virtual environment (Not Windows)
	`source venv/bin/activate`
### Install all requirements
Before you can run the app, you must make sure that all required libraries are also installed in your environment. To do this, make sure that you have pulled the file "requirements.txt", and in the same directory as it, run the command:
    `pip install -r requirements.txt`
As you work on the project, you may find yourself adding additional installs. To add these to "requirements.txt", run the command:
    `pip freeze > requirements.txt`

### Starting the app
Once all requirements are installed, to start the application run the command:
    `flask run`
If you are not using the library flask-dotenv, and/or do not have a the file ".flaskenv", you also need to run the commands telling flask to import the webapp. These are
* Tell Flask how to import the webapp (Windows)
	`set FLASK_APP=webapp.py`
* Tell Flask how to import the webapp (Not Windows)
	`export FLASK_APP=webapp.py`

## Using the Database

