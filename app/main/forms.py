from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    item = StringField('Item', validators=[Required(),Length(1, 64)])
    category = SelectField('Category', choices=[('Beddings','Beddings'), 
        ('Books', 'Books'), 
        ('Clothings', 'Clothings'), 
        ('Currency','Currency'),
        ('Electronics','Electronics'),
        ('Equipment','Equipment'),
        ('Food', 'Food'),  
        ('Furniture','Furniture'),
        ('Stationery', 'Stationery'),
        ('Other','Other'), 
        ('Utensils','Utensils'),
        ('Virtual','Virtual')
        ])
    price = StringField('Price', validators=[Required(),Length(1, 64)])
    contact = StringField('Contact Info', validators=[Required(), Length(1, 64)])
    sold = BooleanField('Sold?')
    body = PageDownField("Post", validators=[Required()])
    submit = SubmitField('Submit')


class CommentForm(Form):
    body = PageDownField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')
