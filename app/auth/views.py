from flask import render_template, redirect, request, url_for, flash, make_response
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import auth, oauthLogin
from .. import db
from ..models import User
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

# Instantiate Authomatic.
authomatic = Authomatic(oauthLogin.oauthconfig, '\x00\x18}{\x9b\xa4(\xaa\xf7[4\xd5Ko\x07S\x03#%_cM\xf2y.\xf6\xf00Kr', report_errors=False)


@auth.before_app_request
def before_request():
    if current_user.is_authenticated():
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('main.index'))
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    provider_name='nyuad'
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
   
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
            #Check if passport returns an error, if so, that means the user is not a student, therefore we redirect the user to landing
            if hasattr(result.user, "error"):
                flash("Sorry, it seems that you are not a student, so you can't use NYUAD Coursereview.", "error")
                return redirect(url_for('main.landing'))
            
            #check if the user is in the database already
            user = User.query.filter_by(username = result.user.NetID).first()
            if user is None:
                user = User(username = result.user.NetID, email = result.user.NetID + "@nyu.edu")
                db.session.add(user)
                db.session.commit()
                user.follow(user)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("Welcome to NYUAD Market. Since this is your first time on the site, please fill in your profile information.", "success")
                return redirect(url_for('main.edit_profile'))
            
            login_user(user)
            flash("You were logged in successfully.", "success")
        # The rest happens inside the template.
        return redirect(url_for('main.index'))
    
    # Don't forget to return the response.
    return response


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('http://passport.sg.nyuad.org/auth/logout')#logout with passport



