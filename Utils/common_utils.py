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

def is_valid_arxiv_id(arxiv_id):
    # Regular expression pattern for arXiv IDs
    # Format: arXiv:YYMM.number{vV}
    # YYMM - two-digit year and month
    # number - zero-padded sequence number, 4-digits from 0704 to 1412, 5-digits from 1501 onwards
    # vV - optional version number
    pattern = r'(\d{2})(\d{2})\.(\d{4,5})(v\d+)?$'
    
    match = re.match(pattern, arxiv_id)
    if not match:
        return False

    # Extract year and month to handle the change in number length
    year, month, _, _ = match.groups()
    year, month = int(year), int(month)

    # Check the number of digits in 'number' based on year and month
    if year == 14 and month <= 12 or year < 14:
        return len(match.group(3)) == 4  # Should be 4 digits
    else:
        return len(match.group(3)) == 5  # Should be 5 digits

import arxiv

def get_arxiv_metadata(arxiv_id):
    metadata = {}
    search_by_id = arxiv.Search(id_list=[arxiv_id])
    result = list(search_by_id.results())
    if result:
        metadata['Authors'] = [str(a) for a in result[0].authors] if result[0].authors else []
        metadata['Title'] = result[0].title if result[0].title else ''
        metadata['Categories'] = result[0].categories if result[0].categories else []
        metadata['Summary'] = result[0].summary if result[0].summary else ''
        metadata['Published'] = result[0].published.timestamp() if result[0].published else ''
        metadata['Updated'] = result[0].updated.timestamp() if result[0].updated else ''
        return metadata
    else:
        return {}

