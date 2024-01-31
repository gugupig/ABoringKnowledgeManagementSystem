from pymongo import MongoClient
from config import MONGODB_HOST, MONGODB_DB
from datetime import datetime
from Utils.common_utils import detect_language,convert_keys_to_string

def upload_document_to_mongodb(document):
    """
    Uploads a document's text and metadata to the MongoDB database 'ABKMS'.

    Args:
    page_data (dict): A dictionary where the key is the page number and the value is the text on that page.
    metadata (dict): A dictionary containing the metadata of the document.

    Returns:
    ObjectId: The unique ID of the inserted document.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[MONGODB_DB]
    collection = db[document.document_type]

    # Combine page data and metadata into one document
    mongodocument = {
        '_id': document.document_id,
        'file_type': document.file_type,
        'file_path': document.file_path,
        'upload_date': datetime.now(),
        'document_page_count': document.total_page_number,
        'document_tags': document.tags,
        'document_title': document.document_title,
        'document_summary': document.document_summary,
        'acheived': False,
    }
    if hasattr(document, 'text'):
        mongodocument['text'] = document.text
        mongodocument['language'] = document.language

    if document.file_type == 'pdf':
        mongodocument['metadata'] = document.metadata
        mongodocument['notes'] = document.notes
    elif document.file_type == 'docx':
        mongodocument['metadata'] = document.metadata
    
    #convert_keys_to_string(mongodocument)
    mongodocument = convert_keys_to_string(mongodocument)
    
    # Insert the document into the collection
    result = collection.insert_one(mongodocument)

    # Return the unique ID of the inserted document
    return result

def delete_document_from_mongodb(db_name,collection_name,document_id):
    """
    Deletes a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be deleted.

    Returns:
    ObjectId: The unique ID of the deleted document.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Delete the document from the collection
    result = collection.delete_one({'_id': document_id})

    # Return the unique ID of the deleted document
    return result.deletedocument_id

def update_document_in_mongodb(page_data, metadata,db_name,collection_name,document_id):
    """
    Updates a document in the MongoDB database 'ABKMS'.

    Args:
    page_data (dict): A dictionary where the key is the page number and the value is the text on that page.
    metadata (dict): A dictionary containing the metadata of the document.
    document_id (ObjectId): The unique ID of the document to be updated.

    Returns:
    ObjectId: The unique ID of the updated document.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Combine page data and metadata into one document
    document = {
        '_id': document_id,
        'metadata': metadata,
        'page_data': page_data,
        
    }

    # Update the document in the collection
    result = collection.update_one({'_id': document_id}, {'$set': document})

    # Return the unique ID of the updated document
    return result.upsertedocument_id

def get_document_from_mongodb_id(collection_name,document_id):
    """
    Gets a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be retrieved.

    Returns:
    dict: A dictionary containing the document's metadata and page data.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[MONGODB_DB]
    collection = db[collection_name]

    # Get the document from the collection
    document = collection.find_one({'_id': document_id})

    # Return the document
    return document

import json
def get_document_from_collection(collection_name,output_to_file = False):
    """
    Gets a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be retrieved.

    Returns:
    dict: A dictionary containing the document's metadata and page data.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[MONGODB_DB]
    collection = db[collection_name]

    # Get the document from the collection
    documents = list(collection.find({},{'text': 0}))
    if output_to_file:
        with open(f"/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/document_list_cache/{collection_name}.json",'w') as f:
            json.dump(documents,f,default=str,indent=4,ensure_ascii=False)

    # Return the document
    return documents


if __name__ == "__main__":
    pass