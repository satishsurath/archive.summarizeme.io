
import tiktoken
import time
import requests
import time
import hashlib
from flask import request
from app import app
# -------------------- Utility functions --------------------

#This is the function that will be called to summarize the text
def num_tokens_from_string(prompt):
    encoding = tiktoken.get_encoding("cl100k_base")
    num_tokens = len(encoding.encode(prompt))
    return num_tokens

#calculate average sentence length in tokens
def avg_sentence_length(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    return len(tokens)/len(text.split('.')) 

# Custom Jinja filter to replace newline characters with <br> tags
def nl2br(value):
    return value.replace('\n', '<br>')

# Return the value of the preferred locale from a MultiLocaleString
def preferred_locale_value(multi_locale_string):
    """
    Extract the value of the preferred locale from a MultiLocaleString

    https://docs.microsoft.com/en-us/linkedin/shared/references/v2/object-types#multilocalestring
    """
    preferred = multi_locale_string["preferredLocale"]
    locale = "{language}_{country}".format(
        language=preferred["language"], country=preferred["country"]
    )
    return multi_locale_string["localized"][locale]

def get_short_url(hash, host):
    base_url = "https://fwd.summarizeme.io/yourls-api.php"
    secret_token = app.config['YOURLS_SECRET_TOKEN']  # Your secret signature token
    print(secret_token)
    action = "shorturl"
    format = "json"

    share_url = f"https://{host}/share/{hash}"

    timestamp = int(time.time())
    print(timestamp)
    signature = hashlib.md5(f"{timestamp}{secret_token}".encode('utf-8')).hexdigest()
    print(signature)

    payload = {
        "timestamp": timestamp,
        "signature": signature,
        "action": action,
        "format": format,
        "url": share_url,
    }
    print(payload)

    response = requests.get(base_url, params=payload)
    print(response)
    data = response.json()

    if data["status"] == "success":
        return data["shorturl"]
    else:
        return None


def get_existing_short_url(long_url):
    base_url = "https://fwd.summarizeme.io/yourls-api.php"
    secret_token = app.config['YOURLS_SECRET_TOKEN']  # Your secret signature token
    action = "contract"
    format = "json"

    timestamp = int(time.time())
    signature = hashlib.md5(f"{timestamp}{secret_token}".encode('utf-8')).hexdigest()

    payload = {
        "timestamp": timestamp,
        "signature": signature,
        "action": action,
        "format": format,
        "url": long_url,
    }
    print(payload)

    response = requests.get(base_url, params=payload)
    print(response)
    data = response.json()
    print(data)

    if data["url_exists"]:
        return data["links"]["link_1"]["shorturl"]
    else:
        return None
