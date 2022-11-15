##*************************************************************************
#   file adding additional flask commands for ease of translation
#
#   @author	 Indigo Bosworth
#   @Creation Date: 15/11/2022
#         
#
##*************************************************************************

import os
import click
from app import app


@app.cli.group()
def translate():
    """Translation and localization commands."""
    pass

#Adds a flask command to add a new language LANG "flask translate init LANG"
@translate.command()
@click.argument('lang')
def init(lang):
    """Initialize a new language."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system(
            'pybabel init -i messages.pot -d app/translations -l ' + lang):
        raise RuntimeError('init command failed')
    os.remove('messages.pot')

#Adds a flask command to update all translations "flask translate update"
@translate.command()
def update():
    """Update all languages."""
    if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
        raise RuntimeError('extract command failed')
    if os.system('pybabel update -i messages.pot -d app/translations'):
        raise RuntimeError('update command failed')
    os.remove('messages.pot')

#Adds a flask command to compile all translations "flask translate compile"
@translate.command()
def compile():
    """Compile all languages."""
    if os.system('pybabel compile -d app/translations'):
        raise RuntimeError('compile command failed')