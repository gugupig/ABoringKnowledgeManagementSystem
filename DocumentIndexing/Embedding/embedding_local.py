

from sentence_transformers import SentenceTransformer

def embeddings_multilingual(sentences):
    model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
    embeddings = model.encode(sentences)
    return embeddings


'''
def embeddings_eng(sentences):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    return embeddings
'''