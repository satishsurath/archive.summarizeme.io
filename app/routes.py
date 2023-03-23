from flask import render_template
from app import app, db
from app.forms import SummarizeFromText, SummarizeFromURL
from flask import render_template, flash, redirect, url_for

import json

import os
import openai

import trafilatura
from trafilatura import extract
from trafilatura.settings import use_config


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey
from flask_migrate import Migrate

#Used for Writing Timestamp to Database
#from datetime import datetime
#db = SQLAlchemy(app)

@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)



from app.models import Entry_Post

openai.api_key = os.getenv("OPENAI_API_KEY")

openAI_summary = "" 
test2summarize = ""
url = ""

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/admin')
def admin():
    entries = Entry_Post.query.order_by(Entry_Post.id.desc())
    return render_template('admin.html', entries=entries)


@app.route('/summarizeText', methods=['GET', 'POST'])
def summarizeText():
    form = SummarizeFromText()
    global openAI_summary
    global test2summarize
    if form.validate_on_submit():
      openAI_summary = openAI_summarize(form.summarize.data)
      test2summarize = form.summarize.data
      return redirect(url_for('summarizeText'))
    if (openAI_summary):
      write_to_db(0,"0",test2summarize,openAI_summary)
      return render_template('summarizeText.html', title='Summarize From Text', form=form,test2summarize=test2summarize, openAI_summary=openAI_summary.split('\n'))
    else:
        return render_template('summarizeText.html', title='Summarize From Text', form=form)

@app.route('/summarizeURL', methods=['GET', 'POST'])
def summarizeURL():
    form = SummarizeFromURL()
    global openAI_summary
    global test2summarize
    global url
    if form.validate_on_submit():
      newconfig = use_config()
      newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
      downloaded = trafilatura.fetch_url(form.summarize.data)
      url = form.summarize.data
      test2summarize = extract(downloaded, config=newconfig)
      openAI_summary = openAI_summarize(test2summarize)
      return redirect(url_for('summarizeURL'))
    if (openAI_summary):
      write_to_db(1,url,test2summarize,openAI_summary)
      return render_template('summarizeURL.html', title='Summarize From URL', form=form,test2summarize=test2summarize, openAI_summary=openAI_summary.split('\n'))
    else:
        return render_template('summarizeURL.html', title='Summarize From URL', form=form)


def openAI_summarize(form_prompt):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt="Summarize the below text in a few short bullet points: \n\n"+form_prompt,
      temperature=0.7,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=1
    )
    print("\n",form_prompt)
    print("\n",response)
    print("\n",response["choices"][0]["text"][2:])
    text_to_return = response["choices"][0]["text"][2:]
    #text_to_return = text_to_return.split('\n')
    print(text_to_return)
    return text_to_return


def write_to_db(posttype, url, test2summarizedb, openAIsummarydb):
  entry = Entry_Post(posttype = posttype, url = url, test2summarize = test2summarizedb, openAIsummary = openAIsummarydb)       
  db.session.add(entry)
  db.session.commit()
  db.session.close()

#    type = db.Column(db.Integer, index=True) # 0 means Summarize from Text, 1 means from URL...
#    url = db.Column(db.String(2048), index=True) # "0" for Summarize from Text; else URL string
#    test2summarize = db.Column(db.String(214748364), index=True)
#    openAIsummary = db.Column(db.String(214748), index=True)
    