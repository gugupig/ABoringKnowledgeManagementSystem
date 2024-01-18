import openai
import toml

def load_config(file_path):
    """
    Load configuration from a TOML file.

    Parameters:
    file_path (str): Path to the TOML file.

    Returns:
    dict: Configuration data.
    """
    with open(file_path, "r") as file:
        return toml.load(file)

def embed_texts(text_list):
    """
    Embed a list of texts using OpenAI's GPT-3.5 Embedding API.

    Parameters:
    text_list (list of str): A list of text strings to be embedded.

    Returns:
    list of list: A list containing the embedding vectors for each input text.
    """

    # Load configuration
    config = load_config("secrets.toml")
    openai.api_key = config["openai"]["api_key"]

    # Embedding the texts
    response = openai.Embedding.create(input=text_list, engine="text-similarity-babbage-001")
    return [embedding['embedding'] for embedding in response['data']]

# Example Usage
# texts = ["Hello, world!", "Another example text"]
# embeddings = embed_texts(texts)
# print(embeddings)
