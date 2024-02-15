class GeneralIndexSettings:
    def __init__(self, vector_dimensions):
        self.vector_dimensions = vector_dimensions

    def chunk_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID_page_number_chunk_number_max_split_number
                    'document_id_universal': {"type": "keyword"}, #UUID used both in Elastic and MongoDB
                    'page_number': {"type": "integer"},# the page number of on whcih the chunk is located
                    "chunk_number": {"type": "integer"}, # the chunk number on the page
                    "upload_date": {"type": "date", "format": "epoch_millis"}, # the date the chunk was uploaded
                    'max_split_number': {"type": "integer"},# the number of chunks on the page
                    "text_piece": {"type": "text"}, # the text of the chunk
                    "language": {"type": "keyword"}, # the language of the chunk
                    "project" : {"type": "keyword"}, # the project the document belongs to
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},  # the vector representation of the chunk
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"},
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"},
                }
            }
        }

    def page_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID_page_number
                    'document_id_universal': {"type": "keyword"}, #UUID
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    "page_number": {"type": "integer"}, # the page number of the page
                    "max_split_number": {"type": "integer"}, # the number of chunks on the page
                    "text_piece": {"type": "text"},     # the text of the page
                    "language": {"type": "keyword"}, # the language of the page
                    "page_summary": {"type": "text"}, # the summary of the page
                    "page_smmary_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},# the averge of text_piece_vectors of all the chunks on the same page
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"}, # the tags of the page
                    "project" : {"type": "keyword"}, # the project the page belongs to
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"},
                }
            }
        }

    def document_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID
                    'document_id_universal': {"type": "keyword"}, #UUID used both in Elastic and MongoDB
                    "upload_date": {"type": "date", "format": "epoch_millis"}, # the date the document was uploaded
                    "max_page_number": {"type": "integer"} , # the number of pages in the document
                    "document_title": {"type": "keyword"}, # the title of the document
                    "document_summary": {"type": "text"}, # the summary of the document
                    "language": {"type": "keyword"}, # the language of the document
                    "document_title_vector": {"type": "dense_vector", "dims": self.vector_dimensions}, # the vector representation of the title
                    "document_summary_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    'text_piece_vector': {"type": "dense_vector", "dims": self.vector_dimensions}, # the averge of text_piece_vectors of all the pages
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"}, # the tags of the document
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"}, # whether the document has been acheived

                }
            }
        }
    
class ResearchPaperIndex(GeneralIndexSettings):
    def chunk_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID_page_number_chunk_number_max_split_number
                    'document_id_universal': {"type": "keyword"}, #UUID
                    'page_number': {"type": "integer"},# the page number of on whcih the chunk is located
                    "chunk_number": {"type": "integer"}, # the chunk number on the page
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    'max_split_number': {"type": "integer"},# the number of chunks on the page
                    "text_piece": {"type": "text"},
                    "language": {"type": "keyword"},
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"},
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"},
                }
            }
        }

    def page_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID_page_number
                    'document_id_universal': {"type": "keyword"}, #UUID
                    "page_number": {"type": "integer"},
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    "max_split_number": {"type": "integer"},
                    "text_piece": {"type": "text"},
                    "language": {"type": "keyword"},
                    "page_summary": {"type": "text"},
                    "page_smmary_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},# the averge of text_piece_vectors of all the chunks on the same page
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"},
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"},
                }
            }
        }

    def document_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID
                    'document_id_universal': {"type": "keyword"}, #UUID
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    "max_page_number": {"type": "integer"},
                    "document_title": {"type": "keyword"},
                    "document_summary": {"type": "text"},
                    "language": {"type": "keyword"},
                    "document_title_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "document_summary_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    'text_piece_vector': {"type": "dense_vector", "dims": self.vector_dimensions}, # the averge of text_piece_vectors of all the pages
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"},
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "acheived": {"type": "boolean"},

                }
            }
        }
class NoteIndex(GeneralIndexSettings):

    # In this stage,only use chunk level for the note index
    def chunk_level_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID_chunk_number_max_split_number
                    'document_id_universal': {"type": "keyword"}, #UUID
                    "chunk_number": {"type": "integer"}, # the chunk number on the page
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    'max_split_number': {"type": "integer"},# the number of chunks on the page
                    "text_piece": {"type": "text"},
                    "language": {"type": "keyword"},
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                },
                    "document_tags": {"type": "keyword"},
                    "related_documents": {"type": "object",
                                          "dynamic": True,
                                          }, #UUIDs of related documents
                    "attached_documents": {"type": "keyword"}, #UUIDs of documents the note is attached to
                    "acheived": {"type": "boolean"},
                }
            }
        }