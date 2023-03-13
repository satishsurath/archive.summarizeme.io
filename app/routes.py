from flask import render_template
from app import app
from app.forms import LoginForm, Summarize4Me
from flask import render_template, flash, redirect, url_for

import json

import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

openAI_summary = "" 
test2summarize = ""

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/summarize', methods=['GET', 'POST'])
def summarize():
    form = Summarize4Me()
    global openAI_summary
    global test2summarize
    if form.validate_on_submit():
        flash('Summary requested for:{}...'.format(form.summarize.data)[0:100])
        openAI_summary = openAI_summarize(form.summarize.data)
        test2summarize = form.summarize.data
        return redirect(url_for('summarize'))
    if (openAI_summary):
      return render_template('summarize.html', title='Summarize', form=form,test2summarize=test2summarize, openAI_summary=openAI_summary)
    else:
        return render_template('summarize.html', title='Summarize', form=form)

def openAI_summarize(form_prompt):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=form_prompt+"\n\nTl;dr",
      temperature=0.7,
      max_tokens=60,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=1
    )
    print("\n",form_prompt)
    print("\n",response)
    print("\n",response["choices"][0]["text"])
    text_to_return = response["choices"][0]["text"]
    return text_to_return
    