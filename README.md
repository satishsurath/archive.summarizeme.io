# summarize4me

Using Generative AI and Python Flask to Summarize Text, Web Pages and PDF files.

## Installation

- Create a new Python virtual environment (venv) or a new conda environment
- Activate your new Python virtual environment
  

- Clone this repo:
```shell
git clone git@github.com:satishsurath/summarize4me.git
```
- Add OpenAI API Key in as an environment variable:
```shell
export OPENAI_API_KEY=[YOUR-OPENAI_API_KEY-HERE]
```
- Setup your admin username and password to access the logs:
```shell
export summarizeMeUser=[YOUR ADMIN USERNAME HERE]
export summarizeMePassword=[YOUR ADMIN PASSWORD HERE]
```
- Install all the Python dependencies in your environment:
```shell
pip install -r requirements.txt
```
- Initialize the Database 
```shell
flask db init
flask db migrate -m "entry_post table"
flask db upgrade
```
- Congratulations! You are ready to run your Flask App!
```shell
flask run
```

# --- Work in Progress --- 

### Features that work:
- **Summarize From Text** feature works for limited number of characters
- **Summarize From URL** Extract Main Text from a webpage and summarize it
- **Saving the data to a local SQLite file** saves all files to a local sqlite file

### Features to be added:

- Extract Text from a PDF file and Summarize it