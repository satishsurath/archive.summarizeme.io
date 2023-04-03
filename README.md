# Summarize4Me

AI-powered text summarization made simple. Condense articles, web pages, and PDFs effortlessly. Save time and boost productivity with Summarize4Me.

[**🔗 Try the live demo here!**](https://ai.sati.sh/index)

## 🚧 Work in Progress 🚧

### ✅ Implemented Features:
- **Summarize Text, URLs and PDF files:** Easily summarize content from plain text, web pages or PDF files.
- **Unlimited Token Support with Chunking:** No more token size limits! The chunking feature allows seamless summarization of any length of text or URL, providing a smooth and efficient experience.
- **Local SQLite File Storage:** Automatically save all files to a local SQLite file.\
- **User Session Support:** for additional Security
- **Hash-Based Database Storage for Fast Retrieval:** Optimize the retrieval process by storing the text's hash in our database, allowing for quicker access to existing summaries and saving time.
- **Stats for Nerds:** Display additional statistics and raw JSON output.
- **Dark Mode Support:** Enhance your experience with our dark mode feature.

### 🔜 Upcoming Features:

- Add a Privacy Notice.
- Implement SPAM Protection.
- Integrate additional LLMs (e.g., Google-based models).

## 💻 Installation

1. Create and activate a [new Python virtual environment (venv) or a new conda environment.](/docs/new-virtual-python-env.md)

   
2. Clone this repository:
   ```shell
   git clone git@github.com:satishsurath/summarize4me.git
    ```

3. Set up your OpenAI API Key as an environment variable. [Request an API key here.](https://openai.com/blog/openai-api)
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

