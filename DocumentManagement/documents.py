from DocumentProcessing.pdf_processing.pdf_processor import SpacyPdfProcessor
from DocumentProcessing.docx_processing.docx_processor import (
    extract_text_from_docx, 
    extract_word_metadata
)
from DocumentProcessing.txt_processing.txt_processor import extract_text_from_txt
from DocumentIndexing.Elastic.IndexSettingsGenerator import *
from config import EMBEDDING_DINENSION
from Utils.common_utils import detect_language, is_valid_arxiv_id, get_arxiv_metadata  

class Document:
    def __init__(self, document_id, file_path, document_type,file_name):
        self.document_id = document_id
        self.document_original_name = file_name
        self.file_path = file_path
        self.document_type = document_type
        self.tags = []
        self.ElsaticIndexSetting = {}
        self.total_page_number = 1
        self.document_summary = ''
        self.document_title = ''
        #self.document_summary_vector = ''
        #self.document_title_vector = ''
            
    def process_document(self):
        raise NotImplementedError("This method should be implemented by subclass.")
    
    def generate_index_settings(self):
        # Test stage,only return base mapping
        if True:
            self.ElsaticIndexSetting = GeneralIndexSettings(EMBEDDING_DINENSION).chunk_level_mapping()

    
class PDFDocument(Document):
    file_type = 'pdf'

    def __init__(self, document_id, file_path, document_type,file_name):
        super().__init__(document_id, file_path, document_type,file_name)
        self.metadata = {}
        self.text = {}
        #self.toc = {}
        self.notes = ''
        self.language = ''
        self.summary = ''

    def process_document(self):
        processor = SpacyPdfProcessor(self.file_path)
        self.language = processor.language
        self.text = processor.extract_text_from_pdf()
        if is_valid_arxiv_id(self.document_original_name):
            self.metadata = get_arxiv_metadata(self.document_original_name)
        else:
            self.metadata = {'Title':processor.get_title(), 'Authors':[], 'Published':'','Updated':'','Summary':'','Categories':[]}
        self.document_summary = self.metadata.pop('Summary', '')
        self.document_title = self.metadata.get('Title', '')
        #self.toc = extract_toc_from_pdf(self.file_path)
        self.notes = processor.extract_notes_from_pdf()
        self.total_page_number = processor.last

        
        

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


