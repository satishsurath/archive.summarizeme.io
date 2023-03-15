
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.widgets import TextArea
from wtforms.fields import URLField
from wtforms.validators import DataRequired


class SummarizeFromText(FlaskForm):
    summarize = StringField('Paste / type the text to summarize below:', widget=TextArea())
    submit = SubmitField('Summarize')

class SummarizeFromURL(FlaskForm):
    summarize = URLField('Paste / type the text to summarize below:')
    submit = SubmitField('Summarize')