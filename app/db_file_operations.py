
import os
import json
import hashlib
from app import app, db, login_manager
from app.models import Entry_Post, oAuthUser, Entry_Posts_oAuthUsers
from flask import session
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
def write_entry_to_db(posttype, url, text2summarizedb, openAIsummarydb):
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

#Given the linkedin.get("me").json, sanitize, verify the JSON file and then save the user info to the database to oAuth table
def write_user_to_db(user_info):
  try:
    user = oAuthUser.query.filter_by(email=user_info['emailAddress']).first()
    if user:
      return True
    else:
      user = oAuthUser(name=user_info['localizedFirstName'], email=user_info['emailAddress'], picture=user_info['profilePicture']['displayImage~']['elements'][0]['identifiers'][0]['identifier'])
      db.session.add(user)
      db.session.commit()
      db.session.close()
      return True
  except:
    return False

#check if user exists in  database to oAuth table, if not create a new user and add to database
def check_if_user_exists(user_info):   
  try:
    user = oAuthUser.query.filter_by(email=user_info['emailAddress']).first()
    if user:
      return True
    else:
      return False
  except:
    return False
