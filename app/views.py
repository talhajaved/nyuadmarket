from flask import render_template, flash, redirect, session, url_for, request, g, make_response
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from app import app, db, lm, oid
from .forms import LoginForm
from .models import User
from app import oauthLogin
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic

AUTHORIZED_GROUPS = ['student']


# Instantiate Authomatic.
authomatic = Authomatic(oauthLogin.oauthconfig, '\x00\x18}{\x9b\xa4(\xaa\xf7[4\xd5Ko\x07S\x03#%_cM\xf2y.\xf6\xf00Kr', report_errors=False)

lm.login_view = "landing"
lm.login_message = "You must be logged in to view the requested page."
lm.login_message_category = "error"

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@app.route('/landing')
def landing():
    if g.user.is_authenticated():
        return redirect(url_for('index'))
    # next_url = request.args.get('next')
    # cache.set('next_url', next_url, 60)
    return render_template('landing.html', title ="Welcome")



@app.route('/index')
@login_required
@login_required
def index():
    user = g.user
    posts = [
        {
            'author': {'net_id': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'net_id': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html',
                           title='Home',
                           user=user,
                           posts=posts)


@app.route('/user/<net_id>')
@login_required
def user(net_id):
    user = User.query.filter_by(net_id=net_id).first()
    if user == None:
        flash('User %s not found.' % net_id)
        return redirect(url_for('index'))
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html',
                           user=user,
                           posts=posts)




#LOGIN AND LOGOUT VIEWS

@app.route('/login', methods=['GET', 'POST'])     
@app.route('/login/<provider_name>/', methods=['GET', 'POST'])    
def login(provider_name='nyuad'):
    """
    Login handler, must accept both GET and POST to be able to use OpenID.
    """
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    
    # We need response object for the WerkzeugAdapter.
    response = make_response()
    
    # Log the user in, pass it the adapter and the provider name.
    result = authomatic.login(WerkzeugAdapter(request, response), provider_name)
   
    
    # If there is no LoginResult object, the login procedure is still pending.
    if result:
        if result.user:
            # We need to update the user to get more info.
            result.user.update()
            #Check if passport returns an error, if so, that means the user is not a student, therefore we redirect the user to landing
            if hasattr(result.user, "error"):
                flash("Sorry, it seems that you are not a student, so you can't use NYUAD Coursereview.", "error")
                return redirect(url_for('landing'))
            #Check the user group, if belongs to any restricted group redirect login
            for gr in result.user.groups:
                print gr
                if gr in AUTHORIZED_GROUPS:
                    authorized = True
                    break
                else:
                    authorized = False
            authorized = True   
            if not authorized:
                flash("Sorry, it seems that you are not a student, so you can't use NYUAD Coursereview.", "error")
                return redirect(url_for('landing'))
            
            #check if the user is in the database already
            user = User.query.filter_by(net_id = result.user.NetID).first()
            if user is None:
                user = User(net_id = result.user.NetID)
                db.session.add(user)
                db.session.commit()
            
            login_user(user)
            flash("You were logged in successfully.", "success")
        # The rest happens inside the template.
        return redirect(url_for('index'))
    
    # Don't forget to return the response.
    return response




@app.route('/logout')
def logout():
    logout_user()
    return redirect('http://passport.sg.nyuad.org/auth/logout')#logout with passport
