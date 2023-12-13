# search_engine.py

from elasticsearch import Elasticsearch, helpers
from config import EMBEDDING_DINENSION,ES_HOST,ES_HTTP_AUTH,ES_CA_CERTS_PATH
import json


class SearchEngine:
    def __init__(self, es_hosts=ES_HOST):
        """
        Initialize the Elasticsearch client.
        """
        self.es = Elasticsearch(hosts=es_hosts, http_auth=ES_HTTP_AUTH, verify_certs=True, ca_certs=ES_CA_CERTS_PATH)

    def create_index(self, index_name, index_settings):
        """
        Create an index with the given settings.
        """
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=index_settings)
        else:
            print(f"Index '{index_name}' already exists.")

    def delete_index(self, index_name):
        """
        Delete the specified index.
        """
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name)
        else:
            print(f"Index '{index_name}' does not exist.")

    def index_document(self, index_name, formated_document):
        """
        Index a single document in the specified index.
        """
        self.es.index(index=index_name, id=formated_document['document_id_elastic'], body=formated_document)

    def bulk_index_documents(self, index_name, documents):
        """
        Index multiple documents in the specified index using Elasticsearch bulk API.
        """
        actions = [
            {
                "_index": index_name,
                "_id": doc["document_id"],
                "_source": doc
            }
            for doc in documents
        ]
        helpers.bulk(self.es, actions)

    def search_documents(self, query, indices, size=10):
        """
        Search for documents matching the query across specified indices.
        """
        return self.es.search(index=','.join(indices), body={"query": query, "size": size})

    def delete_document(self,index_name, document_id):
    # Delete the document by its ID
        res = self.es.delete(index=index_name, id=document_id)
        return res
    
    def vector_search(self,index_name, query_vector):
        query = {
            "query": {
                "script_score": {
                    "query": {
                        "match_all": {}  # You can replace this with more specific queries if needed
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'text_piece_vector') + 1.0",
                        "params": {
                            "query_vector": query_vector
                        }
                    }
                }
            }
        }
        return self.es.search(index=index_name, body=query)

    def search_for_terms(self,index_name, term):
        query = {
            "query": {
                "match": {
                    "text_piece": term
                }
            }
        }
        return self.es.search(index=index_name, body=query)
