from flask.ext.wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from .models import User


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def validate(self):
        if not Form.validate(self):
            return False
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user is not None:
            self.nickname.errors.append('This nickname is already in use. '
                                        'Please choose another one.')
            return False
        return True


class PostForm(Form):
    item = StringField('Item', validators=[Required(),Length(1, 64)])
    price = StringField('Price', validators=[Required(),Length(1, 64)])
    contact = StringField('Contact Info', validators=[Required(), Length(1, 64)])
    sold = BooleanField('Sold?')
    body = PageDownField("Post", validators=[Required()])
    submit = SubmitField('Submit')

class CommentForm(Form):
    body = PageDownField('Enter your comment', validators=[Required()])
    submit = SubmitField('Submit')
