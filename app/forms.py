
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.widgets import TextArea
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class Summarize4Me(FlaskForm):
    summarize = StringField('Paste / type the text to summarize below:', widget=TextArea())
    submit = SubmitField('Summarize')