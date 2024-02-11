import openai
import toml
import sys
sys.path.append('/root/gpt_projects/ABoringKnowledgeManagementSystem')
from config import TEXT_SPLIT_SIZE
import os


class TextEmbedder:
    def __init__(self, local_model_name='BAAI/bge-m3', config_file='/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentIndexing/Embedding/secrets.toml'):
        self .local_model_name = local_model_name
        if self. local_model_name  == 'sentence-transformers/distiluse-base-multilingual-cased-v2':
            print('Embedding dimension: 512')
            from sentence_transformers import SentenceTransformer
            self.local_model = SentenceTransformer(local_model_name)
        elif self.local_model_name == 'BAAI/bge-m3':
            print('Embedding dimension: 1024')
            from FlagEmbedding import BGEM3FlagModel
            os.environ["TOKENIZERS_PARALLELISM"] = "false"
            self.local_model = BGEM3FlagModel(self.local_model_name,use_fp16=True)
        self.config = self.load_config(config_file)
        openai.api_key = self.config["openai"]["api_key"]

    def load_config(self, file_path):
        with open(file_path, "r") as file:
            return toml.load(file)

    def embed_texts(self, text_list):
        response = openai.Embedding.create(input=text_list, engine="text-similarity-babbage-001")
        return [embedding['embedding'] for embedding in response['data']]

    def embeddings_multilingual(self, sentences):
        if self.local_model_name == 'sentence-transformers/distiluse-base-multilingual-cased-v2':
            return self.local_model.encode(sentences)
        elif self.local_model_name == 'BAAI/bge-m3':
            return self.local_model.encode(sentences, return_dense=True, return_sparse=False, return_colbert_vecs=False,max_length = TEXT_SPLIT_SIZE )['dense_vecs']

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