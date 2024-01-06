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
    
    def vector_search(self, index_name, query_vector, language=None, mod_date_start=None, mod_date_end=None, additional_metadata=None):
        must_queries = [
            {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'text_piece_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        ]

        # Optional language filter
        if language:
            must_queries.append({"term": {"language": language}})

        # Constructing the query
        query = {
            "query": {
                "bool": {
                    "must": must_queries,
                    "filter": []
                }
            }
        }

        # Optional date range filter
        if mod_date_start or mod_date_end:
            date_range_filter = {"range": {"metadata.ModDate": {}}}
            if mod_date_start:
                date_range_filter["range"]["metadata.ModDate"]["gte"] = mod_date_start
            if mod_date_end:
                date_range_filter["range"]["metadata.ModDate"]["lte"] = mod_date_end
            query["query"]["bool"]["filter"].append(date_range_filter)

        # Optional additional metadata criteria
        if additional_metadata:
            for key, value in additional_metadata.items():
                query['query']['bool']['must'].append({"match_all": {f"metadata.{key}": value}})

        return self.es.search(index=index_name, body=query)


    def search_for_terms(self, index_name, word,exact_match = False, language=None, mod_date_start=None, mod_date_end=None, additional_metadata=None):
        if exact_match:
            must_queries = [
                {
                    "match_phrase": {
                        "text_piece": word
                    }
                }
            ]
        else:
            must_queries = [
                {
                    "match": {
                        "text_piece": word
                    }
                }
            ]

        # Optional language filter
        if language:
            must_queries.append({"term": {"language": language}})

        # Constructing the query
        query = {
            "query": {
                "bool": {
                    "must": must_queries,
                    "filter": []
                }
            }
        }

        # Optional date range filter
        if mod_date_start or mod_date_end:
            date_range_filter = {"range": {"metadata.ModDate": {}}}
            if mod_date_start:
                date_range_filter["range"]["metadata.ModDate"]["gte"] = mod_date_start
            if mod_date_end:
                date_range_filter["range"]["metadata.ModDate"]["lte"] = mod_date_end
            query["query"]["bool"]["filter"].append(date_range_filter)

        # Optional additional metadata criteria
        if additional_metadata:
            for key, value in additional_metadata.items():
                query['query']['bool']['must'].append({"match": {f"metadata.{key}": value}})

        return self.es.search(index=index_name, body=query)

