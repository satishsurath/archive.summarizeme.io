import os
import openai
import json
import trafilatura
import tiktoken
import nltk
import hashlib
from nltk.tokenize import sent_tokenize
from app import app, db, login_manager
from app.forms import SummarizeFromText, SummarizeFromURL, openAI_debug_form, DeleteEntry, UploadPDFForm
from app.models import Entry_Post
from flask import render_template, flash, redirect, url_for, request, session
from trafilatura import extract
from trafilatura.settings import use_config
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Float, Integer, String, MetaData, ForeignKey
from flask_migrate import Migrate
from flask_login import login_required, current_user, UserMixin
from flask_login import login_user, logout_user, login_required
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
from pdfminer.high_level import extract_text
from io import BytesIO


# -------------------- Utility functions --------------------

#This is the function that will be called to summarize the text
def num_tokens_from_string(prompt):
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(prompt))
    return num_tokens

#This is the function that will be called to trip the text to the maximum number of tokens
def trim_text_to_tokens(text, max_tokens):
    encoding = tiktoken.get_encoding("cl100k_base")
    return encoding.decode(encoding.encode(text)[:max_tokens])

#calculate average sentence length in tokens
def avg_sentence_length(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)/len(text.split('.')) 

#Used to inject the enumerate function into the templates
@app.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf())

# Custom Jinja filter to replace newline characters with <br> tags
def nl2br(value):
    return value.replace('\n', '<br>')


# -------------------- Basic Authentication --------------------


#Define the Username and Password to access the Logs
summarizeMeUser = os.getenv("summarizeMeUser") or "user1"
summarizeMePassword = os.getenv("summarizeMePassword") or "pass1"
users = {summarizeMeUser:{'pw':summarizeMePassword}}
 
class User(UserMixin):
  pass

#Define the Username and Password to access the Logs and Debugging  
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



# -------------------- Flask app configurations --------------------
app.jinja_env.filters['nl2br'] = nl2br
openai.api_key = os.getenv("OPENAI_API_KEY")
nltk.download('punkt')

# -------------------- Global variables --------------------

openAI_summary = "" 
openAI_summary_JSON = ""
text2summarize = ""
url = ""
global_is_trimmed = False
global_form_prompt = ""
global_number_of_chunks = 0
content_written = False
global_pdf_filename = ""


# -------------------- Session variables --------------------




# -------------------- Routes --------------------
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/privacy-policy')
def privacypolicy():
    return render_template('privacy.html')

@app.route('/summarizeText', methods=['GET', 'POST'])
def summarizeText():
    form = SummarizeFromText()
    if form.validate_on_submit():
        text2summarize = form.summarize.data
        text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
        #Check if the text has already been summarized
        if check_if_hash_exists(text2summarize_hash):
            #Get the summary from the database
            openAI_summary = get_summary_from_hash(text2summarize_hash)
            openAI_summary_JSON = read_from_file_json(text2summarize_hash + ".json")
            session['is_trimmed'] = False
            session['form_prompt'] = text2summarize
            session['number_of_chunks'] = "Retrieved from Database"
        else:
            #Summarize the text using OpenAI API
            openAI_summary_JSON, session['is_trimmed'], session['form_prompt'], session['number_of_chunks'] = openAI_summarize_chunk(text2summarize)
            openAI_summary = openAI_summary_JSON["choices"][0]['message']['content']
        # Now, we have all the data, Save the summary to the Session variables
        session['openAI_summary'] = openAI_summary
        session['openAI_summary_JSON'] = openAI_summary_JSON
        session['text2summarize'] = text2summarize
        session['url'] = ""
        session['content_written'] = False
        # Reload the page so we can process the template with all the Session Variables
        return redirect(url_for('summarizeText'))
    # Check if Session variables are set
    if session.get('openAI_summary'):
        text2summarize = session.get('text2summarize')
        #Recheck if the text2summarize is not None
        if text2summarize is not None:
            text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
        else:
            #If the text2summarize is None, then we have an Error. Let the user know
            flash("Unable to extract content from the provided URL. Please try another URL.")
            return redirect(url_for('summarizeText'))
        #Check if the text has already been written to Database or if it exists in the database
        if not check_if_hash_exists(text2summarize_hash) and not session.get('content_written', False):
            #Write the content to the database
            write_to_db(0, "0", text2summarize, session['openAI_summary'])
            #Write the json to the file
            write_json_to_file(text2summarize_hash + ".json", session['openAI_summary_JSON'])
            if check_folder_exists(app.config['UPLOAD_CONTENT']):
                #Write the content to the file
                write_content_to_file(text2summarize_hash + ".txt", text2summarize)
            #Set the content_written to True
            session['content_written'] = True
        token_count = num_tokens_from_string(text2summarize)
        avg_tokens_per_sentence = avg_sentence_length(text2summarize)
        #Check if the openAI_summary_JSON is not None
        if session['openAI_summary_JSON']:
            openAI_summary_str = json.dumps(session['openAI_summary_JSON'], indent=4)
        else:
            #If the openAI_summary_JSON is None, then we don't have the JSON. Let the user know
            openAI_summary_str = "Retrieved from Database"
        return render_template(
            'summarizeText.html',
            title='Summarize Text',
            form=form,
            text2summarize=text2summarize.split('\n'),
            openAI_summary=session['openAI_summary'].split('\n'),
            token_count=token_count, avg_tokens_per_sentence=avg_tokens_per_sentence,
            openAI_json=openAI_summary_str,
            is_trimmed=session['is_trimmed'],
            form_prompt_nerds=session['form_prompt'],
            number_of_chunks=session['number_of_chunks'],
            text2summarize_hash=text2summarize_hash
        )
    else:
        session['content_written'] = False
        return render_template('summarizeText.html', title='Summarize Text', form=form)


@app.route('/summarizeURL', methods=['GET', 'POST'])
def summarizeURL():
    form = SummarizeFromURL()
    #global openAI_summary, openAI_summary_JSON, text2summarize, url, global_is_trimmed, global_form_prompt, global_number_of_chunks, content_written
    if not session.get('content_written', False):
      if form.validate_on_submit():
        newconfig = use_config()
        newconfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
        downloaded = trafilatura.fetch_url(form.summarize.data)
        if downloaded is None:
          flash("Unable to download content from the provided URL. Please try another URL.")
          return redirect(url_for('summarizeURL'))
        session['url'] = form.summarize.data
        text2summarize = extract(downloaded, config=newconfig)
        if text2summarize is not None:
          text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
        else:
            flash("Unable to extract content from the provided URL. Please try another URL.")
            return redirect(url_for('summarizeURL'))
        #check if the hash exists in the Local Database, before calling the OpenAI API
        if check_if_hash_exists(text2summarize_hash):
          openAI_summary = get_summary_from_hash(text2summarize_hash)
          openAI_summary_JSON = read_from_file_json(text2summarize_hash+".json")
          session['is_trimmed'] = False
          session['form_prompt'] = text2summarize
          session['number_of_chunks'] = "Retrieved from Database"
        else:
          openAI_summary_JSON, session['is_trimmed'], session['form_prompt'], session['number_of_chunks'] = openAI_summarize_chunk(text2summarize)
          openAI_summary = openAI_summary_JSON["choices"][0]['message']['content']
          write_json_to_file(text2summarize_hash+".json",openAI_summary_JSON)
          if check_folder_exists(app.config['UPLOAD_CONTENT']):
            write_content_to_file(text2summarize_hash + ".txt", text2summarize)
        session['openAI_summary_URL'] = openAI_summary
        session['openAI_summary_URL_JSON'] = openAI_summary_JSON
        session['text2summarize_URL'] = text2summarize
        session['url'] = form.summarize.data                
        return redirect(url_for('summarizeURL'))
      #Now that we have the summary, we can render the page
      if session.get('openAI_summary_URL'):
        text2summarize = session.get('text2summarize_URL')
        if text2summarize is not None:
          text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
        else:
          flash("Unable to extract content from the provided URL. Please try another URL.")
          return redirect(url_for('summarizeURL'))                    
        #text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
        # If we calculated the summary with OpenAI API, we need to write it to the database
        if not check_if_hash_exists(text2summarize_hash):
          write_to_db(1,session['url'],text2summarize,session['openAI_summary_URL'])
          session['content_written'] = True
          # Calculate token count and average tokens per sentence
          token_count = num_tokens_from_string(text2summarize)
          avg_tokens_per_sentence = avg_sentence_length(text2summarize)
          openAI_summary_str = json.dumps(session['openAI_summary_URL_JSON'], indent=4)
          return render_template(
            'summarizeURL.html',
            title='Summarize Webpage',
            form=form,
            text2summarize=session['text2summarize_URL'].split('\n'),
            openAI_summary=session['openAI_summary_URL'].split('\n'),
            token_count=token_count,
            avg_tokens_per_sentence=avg_tokens_per_sentence,
            openAI_json=openAI_summary_str,
            is_trimmed=session['is_trimmed'],
            form_prompt_nerds=session['form_prompt'],
            number_of_chunks=session['number_of_chunks'],
            text2summarize_hash=text2summarize_hash
            
          )
        else:
          # the summary was retrieved from the database, so we don't need to write it to DB again
          # Calculate token count and average tokens per sentence
          token_count = num_tokens_from_string(text2summarize)
          avg_tokens_per_sentence = avg_sentence_length(text2summarize)
          if not session.get('openAI_summary_JSON_URL', None):
            openAI_summary_str = "Retrived from Database"
          else:
            openAI_summary_str = json.dumps(session['openAI_summary_JSON_URL'], indent=4)   
          return render_template(
            'summarizeURL.html',
            title='Summarize Webpage',
            form=form,
            text2summarize=text2summarize.split('\n'),
            openAI_summary=session['openAI_summary_URL'].split('\n'),
            token_count=token_count,
            avg_tokens_per_sentence=avg_tokens_per_sentence,
            openAI_json=openAI_summary_str,
            is_trimmed=session['is_trimmed'],
            form_prompt_nerds=session['form_prompt'],
            number_of_chunks=session['number_of_chunks'],
            text2summarize_hash=text2summarize_hash
          )
      else:
        session['content_written'] = False
        clear_session()
        return render_template('summarizeURL.html', title='Summarize Webpage', form=form)
    else:
      session['content_written'] = False
      clear_session()
      return render_template(
        'summarizeURL.html',
        title='Summarize Webpage',
        form=form
      )


@app.route('/summarizePDF', methods=['GET', 'POST'])
def summarizePDF():
    print("summarizePDF - 1")
    form = UploadPDFForm()
    if not session.get('content_written', False):
        print("summarizePDF - 2")
        if form.validate_on_submit():
            print("summarizePDF - 3")
            # Get the uploaded PDF file
            pdf_file = form.pdf.data
            print("summarizePDF - 4")
            # Read the PDF contents
            text2summarize = extract_text(BytesIO(pdf_file.read()))
            text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
            print("summarizePDF - 5")
            # Save the PDF file to the uploads folder
            filename = secure_filename(text2summarize_hash + pdf_file.filename)
            session['pdf_filename'] = filename
            print("summarizePDF - 5")
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Seek to the beginning of the file before saving, then save the file
            pdf_file.seek(0)
            # Check if folder exists:
            if check_folder_exists(app.config['UPLOAD_FOLDER']):
                pdf_file.save(pdf_path)
                print("summarizePDF - 6")
            # Check if the hash exists in the Local Database, before calling the OpenAI API
            if check_if_hash_exists(text2summarize_hash):
                print("summarizePDF - 7")
                openAI_summary = get_summary_from_hash(text2summarize_hash)
                openAI_summary_JSON = read_from_file_json(text2summarize_hash + ".json")
                session['is_trimmed'] = False
                session['form_prompt'] = text2summarize
                session['number_of_chunks'] = "Retrieved from Database"
            else:
                print("summarizePDF - 8")
                openAI_summary_JSON, session['is_trimmed'], session['form_prompt'], session['number_of_chunks'] = openAI_summarize_chunk(text2summarize)
                openAI_summary = openAI_summary_JSON["choices"][0]['message']['content']
                write_json_to_file(text2summarize_hash + ".json", openAI_summary_JSON)
                if check_folder_exists(app.config['UPLOAD_CONTENT']):
                  write_content_to_file(text2summarize_hash + ".txt", text2summarize)
            print("summarizePDF - 9")
            session['openAI_summary_PDF'] = openAI_summary
            session['openAI_summary_JSON_PDF'] = openAI_summary_JSON
            session['text2summarize_PDF'] = text2summarize
            return redirect(url_for('summarizePDF'))

        # Now that we have the summary, we can render the page
        if session.get('openAI_summary_PDF'):
            print("summarizePDF - 10")
            text2summarize = session.get('text2summarize_PDF')
            if text2summarize is not None:
              text2summarize_hash = hashlib.sha256(text2summarize.encode('utf-8')).hexdigest()
            else:
                flash("Unable to extract content from the provided URL. Please try another URL.")
                return redirect(url_for('summarizePDF'))           
            # If we calculated the summary with OpenAI API, we need to write it to the database
            if not check_if_hash_exists(text2summarize_hash):
                print("summarizePDF - 11")
                write_to_db(2, session['pdf_filename'], text2summarize, session['openAI_summary_PDF'])

                # Calculate token count and average tokens per sentence
                token_count = num_tokens_from_string(text2summarize)
                avg_tokens_per_sentence = avg_sentence_length(text2summarize)
                openAI_summary_str = json.dumps(session['openAI_summary_JSON_PDF'], indent=4)

                return render_template(
                    'summarizePDF.html',
                    title='Summarize PDF',
                    form=form,
                    text2summarize=text2summarize.split('\n'),
                    openAI_summary=session['openAI_summary_PDF'].split('\n'),
                    token_count=token_count,
                    avg_tokens_per_sentence=avg_tokens_per_sentence,
                    openAI_json=openAI_summary_str,
                    is_trimmed=session['is_trimmed'],
                    form_prompt_nerds=session['form_prompt'],
                    number_of_chunks=session['form_prompt'],
                    text2summarize_hash=text2summarize_hash
                  )
            else:
              print("summarizePDF - 12")
              #the summary was retrieved from the database, so we don't need to write it to DB again
              # Calculate token count and average tokens per sentence
              token_count = num_tokens_from_string(text2summarize)
              avg_tokens_per_sentence = avg_sentence_length(text2summarize)
              if not session['openAI_summary_JSON_PDF']:
                openAI_summary_str = "Retrived from Database"
              else:
                openAI_summary_str = json.dumps(session['openAI_summary_JSON_PDF'], indent=4)   
              return render_template(
                'summarizePDF.html',
                title='Summarize PDF',
                form=form,
                text2summarize=text2summarize.split('\n'),
                openAI_summary=session['openAI_summary_PDF'].split('\n'),
                token_count=token_count,
                avg_tokens_per_sentence=avg_tokens_per_sentence,
                openAI_json=openAI_summary_str,
                is_trimmed=session['is_trimmed'],
                form_prompt_nerds=session['form_prompt'],
                number_of_chunks=session['form_prompt'],
                text2summarize_hash=text2summarize_hash
              )
        else:
            print("summarizePDF - 13")
            clear_session()
            session['content_written'] = False
            return render_template('summarizePDF.html',title='Summarize PDF', form=form)
    else:
      
      session['content_written'] = False
      clear_session()
      return render_template(
        'summarizePDF.html',
        title='Summarize PDF',
        form=form
      )
    

#given the hash of the text in the URL, we can retrieve the summary from the database
@app.route('/share/<hash>', methods=['GET', 'POST'])
def share(hash):
  #check if the hash exists in the Local Database, before calling the OpenAI API
  if check_if_hash_exists(hash):
    openAI_summary = get_summary_from_hash(hash)
    return render_template(
      'share.html',
      openAI_summary=openAI_summary.split('\n'),
      hash=hash
    )
  else:
    return render_template('404.html'), 404


# Routes for the login and logout pages
@app.route('/admin-login', methods=['GET', 'POST'])
def adminlogin():
  if request.method == 'POST':
    username = request.form.get('username')
    if request.form.get('pw') == users.get(username, {}).get('pw'):
      user = User()
      user.id = username
      login_user(user)
      return redirect(url_for('logs'))
  return render_template('adminlogin.html')

@app.route('/logout')
def logout():
  logout_user()
  session.clear()  # Clear session data
  return redirect(url_for('index'))

@app.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    form = DeleteEntry()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    entries = Entry_Post.query.order_by(Entry_Post.id.desc()).paginate(page=page, per_page=per_page)
    return render_template('logs.html', entries=entries)   

# writing route for url_for('delete_entry', entry_id=entry.id) 
@app.route('/delete_entry/<entry_id>', methods=['GET', 'POST'])
@login_required
def delete_entry(entry_id):
  # delete the entry from the database
  delete_entry_from_db(entry_id)
  return redirect(url_for('logs')) 

#writing a route for a login required page where the hash is passed as a parameter and it loads the content from the json and content files
@app.route('/view/<hash>', methods=['GET', 'POST'])
@login_required
def view(hash):
  #check if the hash exists in the Local Database, before calling the OpenAI API
  if check_if_hash_exists(hash):
    openAI_summary = get_summary_from_hash(hash)
    text2summarize = read_from_file_content(hash+".txt")
    openAI_json = read_from_file_json(hash+".json")
    openAI_json_str = json.dumps(openAI_json, indent=4)
    return render_template(
      'view.html',
      openAI_summary=openAI_summary.split('\n'),
      text2summarize=text2summarize.split('\n'),
      openAI_json=openAI_json_str,
      hash=hash
    )
  else:
    return render_template('404.html'), 404

@app.route('/openAI-debug', methods=['GET', 'POST'])
@login_required
def openAI_debug():
    clear_session()
    form = openAI_debug_form()
    global openAI_summary
    global text2summarize
    if form.validate_on_submit():
      openai_api_form_prompt = form.openAI_debug_form_prompt.data
      openai_api_form_key = form.openAI_debug_form_key.data
      text2summarize = openai_api_form_prompt
      openAI_summary = openAI_summarize_debug(openai_api_form_key, openai_api_form_prompt)
      return redirect(url_for('openAI_debug'))
    if (openAI_summary):
      openAI_summary_str = json.dumps(openAI_summary, indent=4)
      return render_template('openai-debug.html', title='openAI-debug', form=form,openai_key = os.getenv("OPENAI_API_KEY"), text2summarize=text2summarize, openAI_summary=openAI_summary_str, just_summary = openAI_summary["choices"][0]['message']['content'] )
    else:
        return render_template('openai-debug.html', title='openAI-debug', form=form, openai_key = os.getenv("OPENAI_API_KEY"))




# -------------------- OpenAI API Functions --------------------

def openAI_summarize_debug(form_openai_key, form_prompt):
    openai.api_key = form_openai_key
    message = {"role": "user", "content": form_prompt}
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[message],
      temperature=0.7,
      max_tokens=2000,
      top_p=1.0,
      frequency_penalty=0.0,
      presence_penalty=1
      )
    print(json.dumps(response, indent=4)) 
    return response

# Functions to call the OpenAI API
def openAI_summarize_chunk(form_prompt):
    global_prompt = "Summarize the below text into a few short bullet points in english. Treat everything below this sentence as text to be summarized: \n\n"
    # Count tokens in the form_prompt
    token_count = num_tokens_from_string(form_prompt)
    max_tokens = 3500
    is_trimmed = False
    # Trim the form_prompt if the token count exceeds the model's maximum limit
    if token_count > max_tokens:
        #print("prompt is too long, trimming...")
        form_prompt_chunks = []
        chunks = [sentence for sentence in sent_tokenize(form_prompt)]
        temp_prompt = ''
        for sentence in chunks:
            if num_tokens_from_string(temp_prompt + sentence) < max_tokens:
                temp_prompt += sentence
            else:
                form_prompt_chunks.append(temp_prompt.strip())
                temp_prompt = sentence
        if temp_prompt != '':
            form_prompt_chunks.append(temp_prompt.strip())
        is_trimmed = True
        completed_messages = []
        openai_responses = []
        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        for chunk in form_prompt_chunks:
            message = {"role": "user", "content": global_prompt + chunk}
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[message],
                temperature=0.7,
                max_tokens=500,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=1
            )
            completed_messages.extend(response["choices"][0]['message']['content'].split('\n')[:-1])
            openai_responses.append(response)
            for key in total_usage:
                total_usage[key] += response["usage"][key]
        completed_messages.append(response["choices"][0]['message']['content'].split('\n')[-1])
        openai_response = openai_responses[-1].copy()
        openai_response["choices"] = [{"message": {"content": '\n'.join(completed_messages)}}]
        openai_response["usage"] = total_usage
        global_number_of_chunks = len(form_prompt_chunks)
        return openai_response, is_trimmed, form_prompt, global_number_of_chunks
    else:
        # The prompt is not too long (its within the max token limit), so we can just call the API
        # print("prompt is not trimmed")
        message = {"role": "user", "content": global_prompt + form_prompt}
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[message],
            temperature=0.7,
            max_tokens=500,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=1
        )
        global_number_of_chunks = 1
        return response, is_trimmed, form_prompt, global_number_of_chunks

# -------------------- Database Operations --------------------

# function to check if the hash of text2summarize is already in the database then retun
def check_if_hash_exists(text2summarize_hash):
  try:
    entry = Entry_Post.query.filter_by(text2summarize_hash=text2summarize_hash).first()
    if entry:
      return True
    else:
      return False
  except:
    return False

# function to return the Summary if the hash of text2summarize is already in the database
def get_summary_from_hash(text2summarize_hash):
  entry = Entry_Post.query.filter_by(text2summarize_hash=text2summarize_hash).first()
  if entry:
    if entry.openAIsummary == None:
      return False
    else:
      return entry.openAIsummary
  else:
    return False

# Function to write to the database
def write_to_db(posttype, url, text2summarizedb, openAIsummarydb):
  try:
      if not session.get('content_written', False):
          text2summarize_hash = hashlib.sha256(text2summarizedb.encode('utf-8')).hexdigest()
          entry = Entry_Post(posttype=posttype, url=url, text2summarize=text2summarizedb, openAIsummary=openAIsummarydb, text2summarize_hash=text2summarize_hash)
          db.session.add(entry)
          db.session.commit()
          db.session.close()
          session['content_written'] = True
          return True
  except Exception as e:  # Catch the exception
      print("Error occurred. Could not write to database.")
      print(f"Error details: {e}")  # Print the details of the error
      return False

# delete_entry_from_db(entry_id)
def delete_entry_from_db(entry_id):
  try:
    entry = Entry_Post.query.filter_by(id=entry_id).first()
    if entry:
      db.session.delete(entry)
      db.session.commit()
      db.session.close()
      return True
    else:
      return False
  except:
    return False
  
#given the text2summarize_hash, return the entire entry
def get_entry_from_hash(text2summarize_hash):
  try:
    entry = Entry_Post.query.filter_by(text2summarize_hash=text2summarize_hash).first()
    if entry:
      return entry
    else:
      return False
  except:
    return False



# -------------------- File Operations --------------------

#given the filename and json contents, write to file and save it to os.path.join(app.config['UPLOAD_FOLDER'], filename)
def write_json_to_file(filename, json_contents):
  if (app.config['WRITE_JSON_LOCALLY'] == 'False'):
    return True
  else:
  #wrap in try catch
    try:
      with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'w') as f:
        json.dump(json_contents, f)
      return True
    except:
      return False
    
#given the filename and text2summarize contents, write to file and save it to os.path.join(app.config['UPLOAD_CONTENT'], filename)
def write_content_to_file(filename, content):
  if (app.config['WRITE_TEXT_LOCALLY'] == 'False'):
    return True
  else:
    try:
      with open(os.path.join(app.config['UPLOAD_CONTENT'], filename), 'w') as f:
        f.write(content)
      return True
    except:
      return False


#Given the filename, read the file and return the json, wrap it in try catch
def read_from_file_json(filename):
  if (app.config['WRITE_JSON_LOCALLY'] == 'False'):
    return False
  else:
    try:
      with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r') as f:
        json_contents = json.load(f)
      return json_contents
    except:
      return False
#Given the filename, read the file and return the contents, wrap it in try catch
def read_from_file_content(filename):
  if (app.config['WRITE_TEXT_LOCALLY'] == 'False'):
    return False
  else:
    try:
      with open(os.path.join(app.config['UPLOAD_CONTENT'], filename), 'r') as f:
        content = f.read()
      return content
    except:
      return False

#check if folder os.path.join(app.config['UPLOAD_FOLDER'] exists, if not create it
def check_folder_exists(folder_path):
  try:
    if not os.path.exists(folder_path):
      os.makedirs(folder_path)
    return True
  except:
    return False



# -------------------- Helper functions  --------------------

#function to clear the session
def clear_session():
  session.pop('content_written', None)
  session.pop('url', None)
  session.pop('text2summarize', None)
  session.pop('openAIsummary', None)
  session.pop('text2summarize_hash', None)
  session.pop('form_prompt', None)
  session.pop('global_prompt', None)
  session.pop('is_trimmed', None)
  session.pop('global_number_of_chunks', None)
  session.pop('openai_response', None)
  session.pop('openai_responses', None)
  session.pop('completed_messages', None)
  session.pop('total_usage', None)
  session.pop('form_prompt_chunks', None)
  session.pop('form_prompt_chunk', None)