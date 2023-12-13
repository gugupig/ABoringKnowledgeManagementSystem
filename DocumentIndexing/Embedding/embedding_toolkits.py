import numpy as np
import tiktoken


def cosine_similarity(vec1, vec2):
    # Compute the dot product of vec1 and vec2
    dot_product = np.dot(vec1, vec2)
    # Compute the L2 norm of vec1
    norm_vec1 = np.linalg.norm(vec1)
    # Compute the L2 norm of vec2
    norm_vec2 = np.linalg.norm(vec2)
    # Compute the cosine similarity and return it
    similarity = dot_product / (norm_vec1 * norm_vec2)
    return similarity





from sentence_transformers import SentenceTransformer

def w2v_token_len(text):
    model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
    token = model.tokenize(text)
    return len(token)

def gpt_token_len(string: str, encoding_name = 'gpt2') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


'''
def get_max_token_length(model_name):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    max_token_length = tokenizer.model_max_length
    return max_token_length



def w2v_token_len(text):
    tokenizer = BertTokenizer.from_pretrained('sentence-transformers/distiluse-base-multilingual-cased-v2')
    token = tokenizer(text)
    return len(token['input_ids'])
'''