# Summarize4Me

Leverage Generative AI and Python Flask to effortlessly summarize text, web pages, and PDF files.

## 🚧 Work in Progress 🚧

### ✅ Implemented Features:
- **Summarize Text and URLs:** Easily summarize content from plain text or web pages.
- **Unlimited Token Support with Chunking:** No more token size limits! The chunking feature allows seamless summarization of any length of text or URL, providing a smooth and efficient experience.
- **Hash-Based Database Storage for Fast Retrieval:** Optimize the retrieval process by storing the text's hash in our database, allowing for quicker access to existing summaries and saving time.
- **Local SQLite File Storage:** Automatically save all files to a local SQLite file.
- **Stats for Nerds:** Display additional statistics and raw JSON output.
- **Dark Mode Support:** Enhance your experience with our dark mode feature.

### 🔜 Upcoming Features:

- Summarize text extracted from PDF files.
- Add a Privacy Notice.
- Enable Session Management.
- Implement SPAM Protection.
- Integrate additional LLMs (e.g., Google-based models).

## 💻 Installation

1. [Create and activate a new Python virtual environment (venv) or a new conda environment.](/docs/new-virtual-python-env.md)

   
2. Clone this repository:
   ```shell
   git clone git@github.com:satishsurath/summarize4me.git
    ```

3. Set up your OpenAI API Key as an environment variable:
```shell
export OPENAI_API_KEY=[YOUR-OPENAI_API_KEY-HERE]
```
4. Configure your admin username and password for log access:
```shell
export summarizeMeUser=[YOUR ADMIN USERNAME HERE]
export summarizeMePassword=[YOUR ADMIN PASSWORD HERE]
```

5. Install all Python dependencies in your environment:
```shell
pip install -r requirements.txt
```
6. Initialize the Database 
```shell
flask db init
flask db migrate -m "entry_post table"
flask db upgrade
```
7. Congratulations! You are ready to run your Flask App!
```shell
flask run
```

