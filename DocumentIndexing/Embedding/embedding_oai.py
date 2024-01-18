import openai

def embed_texts(text_list):
    """
    Embed a list of texts using OpenAI's GPT-3.5 Embedding API.

    Parameters:
    text_list (list of str): A list of text strings to be embedded.

    Returns:
    list of list: A list containing the embedding vectors for each input text.
    """

    openai.api_key = "your-api-key"  # Replace with your OpenAI API key

    # Splitting the text list into smaller chunks if it's very large
    # This is to ensure that we don't hit API limits for a single request
    chunk_size = 20  # API limit may vary, adjust accordingly
    chunks = [text_list[i:i + chunk_size] for i in range(0, len(text_list), chunk_size)]

    embeddings = []
    for chunk in chunks:
        response = openai.Embedding.create(input=chunk, engine="text-similarity-babbage-001")
        embeddings.extend([embedding['embedding'] for embedding in response['data']])

    return embeddings
