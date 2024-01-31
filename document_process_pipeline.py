# Description: This file is the main file for the document processing pipeline
import os
import numpy as np
from DocumentIndexing.MongoDB import documentstore
from DocumentIndexing.Elastic import search_engine
from DocumentIndexing.Embedding.text_splitter import TextSplitter_Spacy
from DocumentIndexing.Embedding.embedding import TextEmbedder
from DocumentManagement.documents import Document
from DocumentManagement.file_manager import File_Manager     
from pymongo.errors import DuplicateKeyError   
from config import ES_HOST, MONGODB_HOST, MONGODB_DB, DOCUMENTBANK_ROOT,EMBEDDING_DINENSION
from Utils import common_utils
from datetime import datetime
import time

class DocumentProcessPipeline:
    def __init__(self):
        self.search_engine = search_engine.SearchEngine()
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
    

    def sub_pipeline_pagebypage(self, document):
        text_splitter = TextSplitter_Spacy()
        embedder = TextEmbedder()
        sub_pipeline_status = False
        base_doc = {
            'document_id_elastic': document.document_id,
            'document_id_universal' :document.document_id,
            'upload_date': int(datetime.now().timestamp() * 1000),
            'language': document.language,
            'document_tags': document.tags,
            'metadata': document.metadata if document.file_type in ['pdf', 'docx'] else {},
            'acheived': False,

        }

        if document.file_type in ['pdf', 'docx']:
            document_doc = base_doc.copy()
            document_doc.update({
                'document_title': document.metadata.get('Title', ''),
                'document_summary': document.document_summary,
                'max_page_number': document.total_page_number,
                'document_title_vector': embedder.embedding_listoftext([document.metadata.get('Title', '')], 'local')[0] if document.metadata.get('Title', '') else None,
                'document_summary_vector': embedder.embedding_listoftext([document.metadata.get('Summary', '')], 'local')[0] if document.document_summary else None,
                'text_piece_vector': np.zeros(EMBEDDING_DINENSION)
            })

            for page_number, page_text in document.text.items():
                splited_text_pagebypage = text_splitter.chunk_sentences_with_sentence_overlap(page_text,128,1,True)
                splited_embedding_pagebypage = embedder.embedding_listoftext(splited_text_pagebypage, 'local')
                page_doc = {
                    **base_doc,
                    'document_id_elastic': f'{document.document_id}_{page_number}',
                    'text_piece_vector': np.mean(splited_embedding_pagebypage, axis=0),
                    'text_piece': page_text,
                    'page_number': page_number,
                    'max_split_number': len(splited_text_pagebypage)
                }
                self.search_engine.index_document(document.document_type+'_page_level', page_doc)
                print(f'{page_number}/{len(document.text)}')

                for split_no, (split_text, embedding) in enumerate(zip(splited_text_pagebypage, splited_embedding_pagebypage)):
                    chunk_doc = {
                        **base_doc,
                        'document_id_elastic': f'{document.document_id}_{page_number}_{split_no + 1}',
                        'page_number': page_number,
                        'chunk_number': split_no + 1,
                        'text_piece': split_text,
                        'text_piece_vector': embedding,
                        'max_split_number': len(splited_text_pagebypage)
                    }
                    self.search_engine.index_document(document.document_type+'_chunk_level', chunk_doc)

                document_doc['text_piece_vector'] += page_doc['text_piece_vector']

            document_doc['text_piece_vector'] /= len(document.text)
            self.search_engine.index_document(document.document_type+'_document_level', document_doc)
        #WIP : Other file type support need to be added   
        else:
            split_text =  text_splitter.split_text_with_langchain(document.text[1])
            splited_embedding_pagebypage = embedder.embedding_listoftext(split_text,'local')
            max_split_nb = len(split_text)
            for split_no, (split_text, embedding) in enumerate(zip(splited_text_pagebypage, splited_embedding_pagebypage)):
                base_doc['original_page_number'] = 1
                base_doc['document_id_elastic'] = document.document_id + '_' + str(1) + '_' + str(split_no) #+ '_' + str(max_split_nb)
                base_doc['text_piece'] = split_text
                base_doc['text_piece_vector'] = embedding
                self.search_engine.index_document(document.document_type,base_doc)

        sub_pipeline_status = True
        return sub_pipeline_status



    def document_pipeline(self, file, document_type,metadata = None,tags = None):
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

        #Addition step: update metadata and tags
        if metadata and new_document.file_type == 'pdf':
            new_document.metadata['Title'] = metadata.get('title', new_document.metadata['Title'])
            new_document.metadata['Authors'] = metadata.get('author', new_document.metadata['Authors'])
            new_document.metadata['Published'] = metadata.get('published', new_document.metadata['Published'])
            new_document.metadata['Updated'] = metadata.get('updated', new_document.metadata['Updated'])
            new_document.metadata['Categories'] = metadata.get('categories', new_document.metadata['Categories'])
        if tags:
            new_document.tags = tags


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
        return document_id

        
        

if __name__ == "__main__":
    pass