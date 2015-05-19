NYUAD Market

This is the repository for the NYUAD market website. 

The website is developed on python using the Flask microframework and CSS, HTML and javascript have been used for the user interface development. We've started our development on a tutorial provided by Miguel Grinberg.

Installation

An installation of flask with all the modules mentioned in the requirements.txt document is required.

The sqlite database must also be created before the application can run, and the “./manage.py db upgrade” script takes care of that.

Running

To run the application in the development web server just execute ./manage.py runserver.

Using a flask virtual environment to run the application locally is required.