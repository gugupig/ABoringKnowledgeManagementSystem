import openai
import toml
from sentence_transformers import SentenceTransformer

class TextEmbedder:
    def __init__(self, local_model_name='sentence-transformers/distiluse-base-multilingual-cased-v2', config_file='/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentIndexing/Embedding/secrets.toml'):
        self.local_model = SentenceTransformer(local_model_name)
        self.config = self.load_config(config_file)
        openai.api_key = self.config["openai"]["api_key"]

    def load_config(self, file_path):
        with open(file_path, "r") as file:
            return toml.load(file)

    def embed_texts(self, text_list):
        response = openai.Embedding.create(input=text_list, engine="text-similarity-babbage-001")
        return [embedding['embedding'] for embedding in response['data']]

    def embeddings_multilingual(self, sentences):
        return self.local_model.encode(sentences)

    def embedding_listoftext(self, text_list, embedding_type='local'):
        if embedding_type == 'local':
            return self.embeddings_multilingual(text_list)
        elif embedding_type == 'oai':
            return self.embed_texts(text_list)
        else:
            raise ValueError(f'Invalid embedding type: {embedding_type}')
        
    def embedding_listoftext_generator(self, text_list, embedding_type='local'):
        if embedding_type == 'local':
            # For local model, process in batches
            for text in text_list:
                yield self.embeddings_multilingual([text])[0]
        elif embedding_type == 'oai':
            # For OpenAI API, process one by one
            for text in text_list:
                yield self.embed_texts([text])[0]
        else:
            raise ValueError(f'Invalid embedding type: {embedding_type}')

