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
- **Summarize From Text and URL** 
- **Unlimited Token Support with Chunking:** Say goodbye to token size limits! Our new chunking feature allows you to summarize any length of text or URL seamlessly, providing a consistent and efficient experience.
- **Hash-Based Database Storage for Faster Retrieval:** We've optimized the retrieval process by storing the hash of the text being summarized in our database. This enables quicker access to existing summaries, saving you time and effort.
- **Saving the data to a local SQLite file** saves all files to a local sqlite file
- **Stats for nerds** Displaying additional stats and raw JSON output

### Features to be added:

- Extract Text from a PDF file and Summarize it
- Privacy Notice
- Enable Sessions
- SPAM Protection
- Integration of Additional LLMs (by Google for example)