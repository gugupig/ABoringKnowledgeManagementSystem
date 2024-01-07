from DocumentProcessing.pdf_processing.pdf_processor import (
    extract_text_from_pdf, 
    extract_toc_from_pdf, 
    extract_notes_from_pdf, 
    extract_pdf_metadata,
    structured_metadata_for_paper
    
)
from DocumentProcessing.docx_processing.docx_processor import (
    extract_text_from_docx, 
    extract_word_metadata
)
from DocumentProcessing.txt_processing.txt_processor import extract_text_from_txt

from DocumentIndexing.MongoDB.documentstore import upload_document_to_mongodb
from DocumentIndexing.Elastic.IndexSettingsGenerator import *
from Utils.common_utils import detect_language
from config import EMBEDDING_DINENSION


class Document:
    def __init__(self, document_id, file_path, document_type):
        self.document_id = document_id
        self.file_path = file_path
        self.document_type = document_type
        self.ElsaticIndexSetting = {}
        self.total_page_number = 1

    def process_document(self):
        raise NotImplementedError("This method should be implemented by subclass.")
    
    def generate_index_settings(self):
        # Test stage,only return base mapping
        if True:
            self.ElsaticIndexSetting = GeneralIndexSettings(EMBEDDING_DINENSION).get_base_mapping()

    def set_language(self):
        try:
            text_sample = self.text[1][0:500]
        except:
            text_sample = self.text[1]
        self.language = detect_language(text_sample)

    
class PDFDocument(Document):
    file_type = 'pdf'

    def __init__(self, document_id, file_path, document_type):
        super().__init__(document_id, file_path, document_type)
        self.metadata = {}
        self.text = {}
        #self.toc = {}
        self.notes = ''
        self.language = ''

    def process_document(self):
        self.text = extract_text_from_pdf(self.file_path)
        self.metadata = structured_metadata_for_paper(self.file_path)
        #self.toc = extract_toc_from_pdf(self.file_path)
        self.notes = extract_notes_from_pdf(self.file_path)
        self.set_language()
        self.total_page_number = len(self.text)

        
        

class DOCXDocument(Document):
    file_type = 'docx'

    def __init__(self, document_id, file_path, document_type):
        super().__init__(document_id, file_path, document_type)
        self.metadata = {}
        self.text = {}
        self.language = ''

    def process_document(self):
        self.text = extract_text_from_docx(self.file_path)
        self.metadata = extract_word_metadata(self.file_path)
        self.set_language()
        self.total_page_number = len(self.text)


class TXTDocument(Document):
    file_type = 'txt'

    def __init__(self, document_id, file_location, document_type):
        super().__init__(document_id, file_location, document_type)
        self.text = {}
        self.language = ''

    def process_document(self):
        self.text = extract_text_from_txt(self.file_path)
        self.language = detect_language(self.text)
        self.set_language()
        self.total_page_number = len(self.text)


