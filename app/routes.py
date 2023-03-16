from flask import render_template
from app import app
from app.forms import SummarizeFromText, SummarizeFromURL
from flask import render_template, flash, redirect, url_for

import json

import os
import openai

import trafilatura
from trafilatura import extract

openai.api_key = os.getenv("OPENAI_API_KEY")

openAI_summary = "" 
test2summarize = ""

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


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
      return render_template('summarizeText.html', title='Summarize From Text', form=form,test2summarize=test2summarize, openAI_summary=openAI_summary)
    else:
        return render_template('summarizeText.html', title='Summarize From Text', form=form)

@app.route('/summarizeURL', methods=['GET', 'POST'])
def summarizeURL():
    form = SummarizeFromURL()
    global openAI_summary
    global test2summarize
    if form.validate_on_submit():
     # print(form.summarize.data)
     # downloaded = trafilatura.fetch_url(form.summarize.data)
     # print("ok------1")
     # test2summarize = "ok"
     # print(downloaded)
     # print("ok------2")
      openAI_summary = openAI_summarize(form.summarize.data)
      return redirect(url_for('summarizeURL'))
    if (openAI_summary):
      return render_template('summarizeURL.html', title='Summarize From URL', form=form,test2summarize=test2summarize, openAI_summary=openAI_summary)
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
    print("\n",response["choices"][0]["text"])
    text_to_return = response["choices"][0]["text"]
    text_to_return = text_to_return.split('\n')
    print(text_to_return)
    return text_to_return
    