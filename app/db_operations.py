
import os
import json


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
