
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.widgets import TextArea
from wtforms.fields import URLField
from wtforms.validators import DataRequired


class SummarizeFromText(FlaskForm):
    summarize = StringField('Paste / type the text to summarize below:', widget=TextArea())
    submit = SubmitField('Summarize')

class SummarizeFromURL(FlaskForm):
    summarize = URLField('Paste / type the URL of the webpage to summarize below:')
    submit = SubmitField('Summarize')

class openAI_debug_form(FlaskForm):
    openAI_debug_form_key = StringField('Paste your OpenAI API Key (will not be saved)')
    openAI_debug_form_prompt = StringField('OpenAI Input:', widget=TextArea())
    submit = SubmitField('Submit')   

#form to delete the entry
class DeleteEntry(FlaskForm):
    submit = SubmitField('Delete') 