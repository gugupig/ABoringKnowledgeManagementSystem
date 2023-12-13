# utils/common_utils.py

import re

def clean_text(text):
    """
    Removes all special characters from the text, preserving only alphanumeric characters and newline characters.
    """
    # Replace special characters with an empty string, except for newlines
    cleaned_text = re.sub(r'[^\w\n\s]', '', text)
    return cleaned_text

import uuid

def generate_document_id():
    return str(uuid.uuid4())

# Example usage
if __name__ == "__main__":
    sample_text = "Hello, World! This is a test.\nNew Line here."
    cleaned = clean_text(sample_text)
    print(cleaned)


import fasttext

def detect_language(text):
    model = fasttext.load_model('lid.176.bin')
    text = text.replace('\n', ' ')  # Replace newlines with spaces
    predictions = model.predict(text, k=1)  # k is the number of predictions to return
    # The output is a tuple with two elements. The first element is a list of labels, and the second element is a list of probabilities.
    # We only want the first label, so we get the first element of the first element of the output.
    # The label is a string that starts with '__label__', so we remove the first 9 characters to get the language code.
    print(predictions[0][0][9:])
    return predictions[0][0][9:]

import inspect

from config import SUPPORTED_FILE_TYPE

def get_document_classes(module):
    return {cls.__name__.lower(): cls for name, cls in inspect.getmembers(module, inspect.isclass) if cls.__name__.lower()[:-len('document')] in SUPPORTED_FILE_TYPE}

def convert_keys_to_string(dictionary):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(dictionary, dict):
        return dictionary
    return dict((str(k), convert_keys_to_string(v)) for k, v in dictionary.items())


from datetime import datetime

    
