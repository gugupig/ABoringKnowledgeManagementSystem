class GeneralIndexSettings:
    def __init__(self, vector_dimensions):
        self.vector_dimensions = vector_dimensions

    def get_base_mapping(self):
        return {
            "mappings": {
                "properties": {
                    "document_id_elastic": {"type": "keyword"}, #UUID+_+page_number+_+split_number
                    'document_id_universal': {"type": "keyword"}, #UUID
                    "upload_date": {"type": "date", "format": "epoch_millis"},
                    "original_page_number": {"type": "integer"},
                    "text_piece": {"type": "text"},
                    "language": {"type": "keyword"},
                    "text_piece_vector": {"type": "dense_vector", "dims": self.vector_dimensions},
                    "metadata": {
                                     "type": "object",
                                     "dynamic": True  # Allows dynamic addition of fields within the object
                                }
                }
            }
        }
class AcademicPaperIndexSettings(GeneralIndexSettings):
    def __init__(self, vector_dimensions):
        super().__init__(vector_dimensions)

    def get_academic_mapping(self):
        base_mapping = self.get_base_mapping()
        academic_fields = {
            "title": {"type": "text"},
            "author": {"type": "text"},  # Change to 'keyword' if exact match is needed
            "publication_date": {"type": "date", "format": "yyyy-MM-dd"},
            "keywords": {"type": "text"},  # Could be an array of keywords
            # Add other academic-specific fields here
        }
        base_mapping["mappings"]["properties"].update(academic_fields)
        return base_mapping
