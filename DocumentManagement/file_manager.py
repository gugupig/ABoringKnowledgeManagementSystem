from config import ES_HOST, MONGODB_HOST, MONGODB_DB, DOCUMENTBANK_ROOT,SUPPORTED_FILE_TYPE, DOCUMENT_TYPE
#from DocumentIndexing.MongoDB.documentstore import uploadDocument,delete_document,update_document
#from file_monitor import FileMonitor
import inspect
import DocumentManagement.documents as documents
#from watchdog.observers import Observer
from django.core.files.storage import FileSystemStorage 
from Utils.common_utils import get_document_classes
import time
import os




class File_Manager:
    def __init__(self):
        self.document_bank_root = DOCUMENTBANK_ROOT
        self.supported_file_types = SUPPORTED_FILE_TYPE
        self.document_types = DOCUMENT_TYPE
        self.file_type_mapping  = get_document_classes(documents)
        print(self.file_type_mapping)

    def upload_file(self, file, document_type, document_id):
        if document_type not in self.document_types:
            raise ValueError(f"Invalid document type. Allowed types: {self.document_types}")

        if not self.is_supported_file_type(file.name):
            raise ValueError("Unsupported file type.")

        # Extract the file extension
        file_name, extension = os.path.splitext(file.name)

        # Construct the path to the sub-folder based on document type
        folder_path = os.path.join(self.document_bank_root, document_type)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Construct the new file name
        new_file_name = f"{document_id}{extension}"

        # Save the file to the folder
        file_path = os.path.join(folder_path, new_file_name)
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        extension = extension.replace('.','')
        document_class = self.file_type_mapping.get(f'{extension}document')
        new_document = document_class(document_id, file_path, document_type, file_name)
        return new_document

    def is_supported_file_type(self, file_name):
        _, file_extension = os.path.splitext(file_name)
        return file_extension.replace('.','') in self.supported_file_types


if __name__ == "__main__":
    '''
  
    def start_monitoring(self):
        event_handler = FileMonitor()
        observer = Observer()
        observer.schedule(event_handler, path=self.document_bank_root, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
'''