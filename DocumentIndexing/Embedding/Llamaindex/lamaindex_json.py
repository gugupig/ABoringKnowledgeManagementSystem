from llama_index import LlamaIndex
from llama_index.service_context import ServiceContext
from llama_index.embeddings.base import BaseEmbeddings
from DocumentIndexing.Embedding.llama_custom_embedding import MultilingualEmbeddings

# Create an instance of MultilingualEmbeddings
embed_model = MultilingualEmbeddings(instructor_model_name="my_model_name")
service_context = ServiceContext.from_defaults(embed_model=embed_model)

# Create an instance of LlamaIndex
index = LlamaIndex(service_context=service_context)

# Index a folder full of JSON files
index.index_folder(folder_path="/path/to/your/folder",  ="your_collection_id")