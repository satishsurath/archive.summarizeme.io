
import tiktoken
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


