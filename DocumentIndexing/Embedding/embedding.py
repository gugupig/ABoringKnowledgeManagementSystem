import requests
import numpy as np
from config import TEXT_SPLIT_SIZE

def embedding_listoftext(text_list, max_length = TEXT_SPLIT_SIZE ,embedding_type='local',):
    EMBEDDING_API_URL = "http://localhost:5000/embeddings/"
    payload = {
        'text_list': text_list,
        'embedding_type': embedding_type,
        'max_length': max_length
    }
    try:
        response = requests.post(EMBEDDING_API_URL, json=payload)
    except ConnectionError as e:
        print(f"Connection error,please make sure the embedding service is running: {e}")
        raise e
    if response.status_code == 200:
        return np.array(response.json()['embeddings'])

