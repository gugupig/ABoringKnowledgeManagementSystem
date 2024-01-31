import numpy as np
import tiktoken
from transformers import AutoTokenizer


def cosine_similarity(self, vec1, vec2):
    # Compute the dot product of vec1 and vec2
    dot_product = np.dot(vec1, vec2)
    # Compute the L2 norm of vec1
    norm_vec1 = np.linalg.norm(vec1)
    # Compute the L2 norm of vec2
    norm_vec2 = np.linalg.norm(vec2)
    # Compute the cosine similarity and return it
    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity


def gpt_token_len(self, string: str, encoding_name='gpt2') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

class token_length_calculator:
    def __init__(self, model_name='sentence-transformers/distiluse-base-multilingual-cased-v2'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)


    def token_length(self, text):
        encoded_input = self.tokenizer.encode_plus(text, add_special_tokens=True, return_tensors='pt')
        input_ids = encoded_input['input_ids'][0]  # Get the input_ids of the first (and only) sequence

        # Count the number of tokens, excluding padding if any
        token_count = len([token for token in input_ids if token != self.tokenizer.pad_token_id])
        return token_count
