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

    def delete_document(self,index_name, document_id):
        # Delete the document by its ID
            res = self.es.delete(index=index_name, id=document_id)
            return res
        
    def vector_search(self, index_name, query_vector, vector_field = 'text_piece_vector',language=None, mod_date_start=None, mod_date_end=None, additional_metadata=None, document_id=None, tags=None):
        must_queries = [
            {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{vector_field}') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        ]

        # Optional language filter
        if language:
            must_queries.append({"term": {"language": language}})

        # Filter by document_id
        if document_id:
            must_queries.append({"term": {"document_id_universal": document_id}})

        # Filter by tags
        if tags:
            if isinstance(tags, list): # If multiple tags
                must_queries.append({"terms": {"Tags": tags}})
            else:
                must_queries.append({"term": {"Tags": tags}})

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
            date_range_filter = {"range": {"upload_date": {}}}
            if mod_date_start:
                date_range_filter["range"]["upload_date"]["gte"] = mod_date_start
            if mod_date_end:
                date_range_filter["range"]["upload_date"]["lte"] = mod_date_end
            query["query"]["bool"]["filter"].append(date_range_filter)

        # Optional additional metadata criteria
        if additional_metadata:
            for key, value in additional_metadata.items():
                query['query']['bool']['must'].append({"match": {f"metadata.{key}": value}})

        return self.es.search(index=index_name, body=query)



    def search_for_terms(self, index_name, word,query_field = 'text_piece', exact_match=False, language=None, mod_date_start=None, mod_date_end=None, additional_metadata=None, document_id=None, tags=None):
        if exact_match:
            must_queries = [
                {
                    "match_phrase": {
                       query_field : word
                    }
                }
            ]
        else:
            must_queries = [
                {
                    "match": {
                        query_field : word
                    } 
                }
            ]

        # Optional language filter
        if language:
            must_queries.append({"term": {"language": language}})

        # Filter by document_id
        if document_id:
            must_queries.append({"term": {"document_id_universal": document_id}})

        # Filter by tags
        if tags:
            if isinstance(tags, list): # If multiple tags
                must_queries.append({"terms": {"Tags": tags}})
            else:
                must_queries.append({"term": {"Tags": tags}})

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
            date_range_filter = {"range": {"upload_date": {}}}
            if mod_date_start:
                date_range_filter["range"]["upload_date"]["gte"] = mod_date_start
            if mod_date_end:
                date_range_filter["range"]["upload_date"]["lte"] = mod_date_end
            query["query"]["bool"]["filter"].append(date_range_filter)

        # Optional additional metadata criteria
        if additional_metadata:
            for key, value in additional_metadata.items():
                query['query']['bool']['must'].append({"match": {f"metadata.{key}": value}})

        return self.es.search(index=index_name, body=query)


    def retrieve_text_from_page(self,index_name, document_id, page_number):
        # Construct the query
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"document_id_universal": document_id}},
                        {"term": {"original_page_number": page_number}}
                    ]
                }
            }
        }

        # Execute the query
        response = self.es.search(index=index_name, body=query)
        # Extracting text from the response
        texts = [hit['_source']['text_piece'] for hit in response['hits']['hits']]
        text_in_one_peice = ' '.join(texts)

        return text_in_one_peice
    
    #WIP
    def retrieve_text_and_its_adjacents(self,index_name,start_elastic_doc_id, adjacent_window=2):
        parts = start_elastic_doc_id.split('_')
        document_id, page_number, start_piece_number = parts[0], int(parts[-3]), int(parts[-2])
        max_split_nb = int(parts[-1])

        queries = []
        # Calculate the range of piece numbers to query, ensuring they are within valid bounds
        for i in range(-adjacent_window, adjacent_window + 1):
            piece_number = start_piece_number + i
            if 0 <= piece_number <= max_split_nb:
                queries.append({"term": {"document_id_elastic": f"{document_id}_{page_number}_{piece_number}_{max_split_nb}"}})

        # Construct the Elasticsearch query
        adjacent_pieces_query = {
            "query": {
                "bool": {
                    "should": queries,
                    "minimum_should_match": 1
                }
            }
        }

        # Execute the query
        response = self.es.search(index=index_name, body=adjacent_pieces_query)
        page_texts = {}
        for hit in response['hits']['hits']:
            _, page, piece = hit['_source']['document_id_elastic'].rsplit('_', 2)
            page = int(page)
            piece = int(piece)
            page_texts.setdefault(page, {}).update({piece: hit['_source']['text_piece']})

        # Concatenate the text pieces in the right order for each page
        ordered_texts = {}
        for page, pieces in page_texts.items():
            ordered_pieces = [pieces[piece] for piece in sorted(pieces.keys())]
            ordered_texts[page] = ' '.join(ordered_pieces)

        return ordered_texts



