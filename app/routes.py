import os
from flask import render_template, request
from app import app, db, login_manager
from app.forms import SummarizeFromText, SummarizeFromURL
from flask import render_template, flash, redirect, url_for


#For Basic Authentication
########## Begin ---------- Basic Authentication
from flask_login import login_required, current_user, UserMixin
from flask_login import login_user, logout_user, login_required

#Define the Username and Password to access the Logs
summarizeMeUser = os.getenv("summarizeMeUser") or "user1"
summarizeMePassword = os.getenv("summarizeMePassword") or "pass1"

users = {summarizeMeUser:{'pw':summarizeMePassword}}

class User(UserMixin):
  pass

@login_manager.user_loader
def user_loader(username):
  if username not in users:
    return

  user = User()
  user.id = username
  return user

@login_manager.request_loader
def request_loader(request):
  username = request.form.get('username')
  if username not in users:
    return
  user = User()
  user.id = username
  user.is_authenticated = request.form['pw'] == users[username]['pw']
  return user


########## End ---------- Basic Authentication

import json

import os
import openai

import trafilatura
from trafilatura import extract
from trafilatura.settings import use_config


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey
from flask_migrate import Migrate


#Used to inject the enumerate function into the templates
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


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'POST':
    username = request.form.get('username')
    if request.form.get('pw') == users[username]['pw']:
      user = User()
      user.id = username
      login_user(user)
      return redirect(url_for('logs'))
  return render_template('login.html')

@app.route('/logout')
def logout():
  logout_user()
  return redirect(url_for('index'))

@app.route('/logs')
@login_required
def logs():
    entries = Entry_Post.query.order_by(Entry_Post.id.desc())
    return render_template('logs.html', entries=entries)


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
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[{"role": "user", "content": "Summarize the below text in a few short bullet points: \n\n"+form_prompt}],
      temperature=0.7,
      max_tokens=100,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=1
    )

    text_to_return = response["choices"][0]['message']['content']
    print(text_to_return)
    return text_to_return


def write_to_db(posttype, url, test2summarizedb, openAIsummarydb):
  entry = Entry_Post(posttype = posttype, url = url, test2summarize = test2summarizedb, openAIsummary = openAIsummarydb)       
  db.session.add(entry)
  db.session.commit()
  db.session.close()
