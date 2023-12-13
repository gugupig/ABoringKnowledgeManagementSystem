# Description: This file is the main file for the document processing pipeline
import os
from DocumentIndexing.MongoDB import documentstore
from DocumentIndexing.Elastic import search_engine, IndexSettingsGenerator
from DocumentIndexing.Embedding import text_splitter
from DocumentIndexing.Embedding.embedding_local import embeddings_multilingual
from DocumentManagement.documents import Document
from DocumentManagement.file_manager import File_Manager     
from pymongo.errors import DuplicateKeyError   
from config import ES_HOST, MONGODB_HOST, MONGODB_DB, DOCUMENTBANK_ROOT
from Utils import common_utils
from datetime import datetime
import time

class DocumentProcessPipeline:
    def __init__(self):
        self.search_engine = search_engine.SearchEngine()
        self.index_settings_generator = IndexSettingsGenerator
        self.document_store = documentstore
        self.common_utils = common_utils
        self.document_bank_location = {
            'Research Paper': f'{DOCUMENTBANK_ROOT}/ResearchPaper',
            'Research Book': f'{DOCUMENTBANK_ROOT}/ResearchBook',
            'Article': f'{DOCUMENTBANK_ROOT}/Article',
            'Personal Document': f'{DOCUMENTBANK_ROOT}/PersonalDocument',
            'Other': f'{DOCUMENTBANK_ROOT}/Other'
        }

    def check_file_type(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        return file_extension
    
    def extract(self, document, max_retries=3, retry_delay=1):
        extraction_success = False
        retries = 0
        while retries < max_retries:
            try:
                document.process_document()
                extraction_success = True
                break
            except Exception as e:
                print(e)
                retries += 1
                time.sleep(retry_delay)
        return extraction_success


    def upload_document_documentbank(self, file,document_type, document_id, max_retries=3, retry_delay=1):
        upload_status = False
        #file_path = os.path.join(self.document_bank_location[document_type], self.document_id + '.' + file_type)
        retries = 0
        file_manager = File_Manager()
        while retries < max_retries:
            try:
                new_document = file_manager.upload_file(file, document_type, document_id)
                upload_status = True
                break
            except Exception as e:
                print(e)
                retries += 1
                time.sleep(retry_delay)
        #check if file is uploaded successfully
        if not os.path.exists(new_document.file_path):
            upload_status = False
            print("Document upload but file not found.")
        return upload_status, new_document




    def upload_document_to_mongodb(self,document, max_retries=3, retry_delay=1):
        upload_status = False
        retries = 0
        while retries < max_retries:
            try:
                self.document_store.upload_document_to_mongodb(document)
                upload_status = True
                break
            except DuplicateKeyError:
                print("Document already exists in MongoDB.")
                upload_status = True
                break
            except Exception as e:
                print(e)
                retries += 1
                time.sleep(retry_delay)
        return upload_status
        
    def upload_document_to_elastic(self, document, document_type, file_name, file_type, max_retries=3, retry_delay=1):
        upload_status = False
        retries = 0
        elastic_engine = self.SearchEngine(es_hosts = ES_HOST)
        while retries < max_retries:
            try:
                elastic_engine.upload_document_to_elastic(document, document_type, file_name, file_type)
                upload_status = True
                break
            except Exception as e:
                print(e)
                retries += 1
                time.sleep(retry_delay)
        return upload_status

    def split_document(self, document, max_retries=2, retry_delay=1):
        split_status = False
        retries = 0
        while retries < max_retries:
            try:
                text_pieces = {key: text_splitter.split_text(content) for key, content in document.text.items()}
                split_status = True
                break
            except Exception as e:
                print(e)
                retries += 1
                time.sleep(retry_delay)
        return split_status, text_pieces

    def sub_pipeline_pagebypage(self, document):
        sub_pipeline_status = False
        doc = {
            'document_id_universal' : document.document_id,
            'upload_date': int(datetime.now().timestamp() * 1000),
            'language': document.language,
        }
        if document.file_type == 'pdf' or document.file_type == 'docx':
            doc['metadata'] = document.metadata
            for page_number, page_text in document.text.items():
                splited_text_pagebypage = text_splitter.split_text_with_langchain(page_text)
                splited_embedding_pagebypage = embeddings_multilingual(splited_text_pagebypage)
                print(f'{page_number}/{len(document.text)}')
                for split_no, (split_text, embedding) in enumerate(zip(splited_text_pagebypage, splited_embedding_pagebypage)):
                    doc['document_id_elastic'] = document.document_id + '_' + str(page_number) + '_' + str(split_no)
                    doc['original_page_number'] = page_number
                    doc['text_piece'] = split_text
                    doc['text_piece_vector'] = embedding
                    self.search_engine.index_document(document.document_type, doc)
        else:
            split_text =  text_splitter.split_text_with_langchain(document.text[1])
            splited_embedding_pagebypage = embeddings_multilingual(split_text)
            for split_no, (split_text, embedding) in enumerate(zip(splited_text_pagebypage, splited_embedding_pagebypage)):
                doc['original_page_number'] = 1
                doc['document_id_elastic'] = document.document_id + '_' + str(1) + '_' + str(split_no)
                doc['text_piece'] = split_text
                doc['text_piece_vector'] = embedding
                self.search_engine.index_document(document.document_type, doc)
        sub_pipeline_status = True
        return sub_pipeline_status

    def sub_pipeline_bulk(self, document):
        sub_pipeline_status = False
        splited_text_bulk = {}
        for page_number,page_text in document.text.items():
            splited_text =  text_splitter.split_text_with_langchain(page_text)
            splited_text_bulk[page_number] = (splited_text,embeddings_multilingual(splited_text))
        self.search_engine.bulk_index_documents(document.document_id, splited_text_bulk)
        sub_pipeline_status = True
        return sub_pipeline_status


    def document_pipeline(self, file, document_type):
        # Generate unique document ID at the beginning
        document_id = self.common_utils.generate_document_id()


        # Step 1: Upload document to DocumentBank
        upload_to_bank_status,new_document = self.upload_document_documentbank(file,document_type, document_id)


        if not upload_to_bank_status:
            print("Uploading document to DocumentBank failed.")
            return False
    

        # Step 2: Extract text and metadata from document
        extraction_success = self.extract(new_document)
        if not extraction_success:
            print("Document extraction failed.")
            return False



        # Step 3: Upload document to MongoDB
        upload_to_mongodb_status = self.upload_document_to_mongodb(new_document)
        if not upload_to_mongodb_status:
            print("Uploading document to MongoDB failed.")
            # No rollback needed here as it's the first database operation
            return False

        # Step 4: sub_pipeline depending on document size
        #if new_document.total_page_number > 100:
            #sub_pipeline_status = self.sub_pipeline_bulk(new_document)
        #else:
        sub_pipeline_status = self.sub_pipeline_pagebypage(new_document)
        
        if not sub_pipeline_status:
            print("Sub pipeline failed.")
            #roll back for mongodb
            self.document_store.delete_document_from_mongodb(new_document.document_id)
            return False

        
        

if __name__ == "__main__":
    pass