from flask import render_template, flash, redirect, session, url_for, request, g, make_response
from flask.ext.login import login_user, logout_user, current_user, \
    login_required
from datetime import datetime
from app import app, db, lm, oid
from app import oauthLogin
from .forms import LoginForm, EditForm, PostForm, SearchForm, CommentForm
from .models import User, Post, Comment
from config import POSTS_PER_PAGE, MAX_SEARCH_RESULTS, AUTHORIZED_GROUPS, COMMENTS_PER_PAGE
from authomatic.adapters import WerkzeugAdapter
from authomatic import Authomatic
from datetime import datetime



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
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
        g.search_form = SearchForm()


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/landing')
def landing():
    if g.user.is_authenticated():
        return redirect(url_for('index'))
    # next_url = request.args.get('next')
    # cache.set('next_url', next_url, 60)
    return render_template('landing.html', title ="Welcome")


@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, timestamp=datetime.utcnow(),
                    author=g.user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts)


# @app.route('/login', methods=['GET', 'POST'])
# @oid.loginhandler
# def login():
#     if g.user is not None and g.user.is_authenticated():
#         return redirect(url_for('index'))
#     form = LoginForm()
#     if form.validate_on_submit():
#         session['remember_me'] = form.remember_me.data
#         return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
#     return render_template('login.html',
#                            title='Sign In',
#                            form=form,
#                            providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


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
            user = User.query.filter_by(nickname = result.user.NetID).first()
            if user is None:
                user = User(nickname = result.user.NetID, email = result.user.NetID + "@nyu.edu")
                db.session.add(user)
                db.session.commit()
                db.session.add(user.follow(user))
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


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    posts = user.posts.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=user,
                           posts=posts)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form)


@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname=nickname))


@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))




@app.route('/post/<int:id>', methods=['GET', 'POST'])
@app.route('/post/<int:id>/<int:page>', methods=['GET', 'POST'])
@login_required
def post(id, page = 1):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.comment.data, timestamp=datetime.utcnow(),
                    author=g.user, post=post )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment is now live!')
        return redirect(url_for('.post', id=post.id))
    comments = post.comments.paginate(page, COMMENTS_PER_PAGE, False)
    
    return render_template('single_post.html', post = post, form = form, comments = comments)

   