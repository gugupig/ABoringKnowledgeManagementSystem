from pymongo import MongoClient
from config import MONGODB_HOST, MONGODB_DB
from datetime import datetime
from Utils.common_utils import convert_keys_to_string

def upload_document_to_mongodb(document,client = None,db_name = None,collection_name = None):
    """
    Uploads a document's text and metadata to the MongoDB database 'ABKMS'.

    Args:
    page_data (dict): A dictionary where the key is the page number and the value is the text on that page.
    metadata (dict): A dictionary containing the metadata of the document.

    Returns:
    ObjectId: The unique ID of the inserted document.
    """
    if client is None:
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
        client = MongoClient(MONGODB_HOST)
    # Access the database and collection
        db = client[MONGODB_DB]
        collection = db[document.document_type]
    else:
        client = client
        db = client[db_name]
        collection = db[collection_name]

    # Combine page data and metadata into one document
    mongodocument = {
        '_id': document.document_id,
        'file_type': document.file_type,
        'upload_date': datetime.now(),
        'document_project': document.project, #list of project ids
        'related_documents': document.related_documents, #dict of related documents ids,the key is the relation type
        'document_tags': document.tags, #list of tags,currently the tag options are stored in the local cahce file
        'acheived': False,
    }
    #TODO: add language detection for note
    if hasattr(document, 'text'):
        mongodocument['text'] = document.text
        #Temporary disable and move to pdf document since the note document need something to detect language
        #mongodocument['language'] = document.language 

    if document.file_type == 'pdf':
        mongodocument['file_path'] = document.file_path
        mongodocument['document_page_count'] = document.total_page_number
        mongodocument['document_title'] = document.document_title
        mongodocument['document_summary'] = document.document_summary
        mongodocument['generated_summary'] = document.generated_summary
        mongodocument['metadata'] = document.metadata
        mongodocument['annotation '] = document.annotation
        mongodocument['notes'] = document.notes
        # Move to here to detect language,a temporary fix for note dose not have language detection yet
        mongodocument['language'] = document.language
    elif document.file_type == 'docx':
        mongodocument['metadata'] = document.metadata

    elif document.file_type == 'note':
        mongodocument['note_title'] = document.note_title
        mongodocument['text'] = document.text
        mongodocument['attached_documents'] = document.attached_documents_ids  #list/string(if note_type is pdf_note) of documents ids the note is attached to 
        mongodocument['note_type'] = document.note_type #type of the note,now only has "pdf note" type
        
    
    #convert_keys_to_string(mongodocument)
    mongodocument = convert_keys_to_string(mongodocument)
    
    # Insert the document into the collection
    result = collection.insert_one(mongodocument)

    # Return the unique ID of the inserted document
    return result



def delete_document_from_mongodb(db_name,collection_name,document_id,client = None):
    """
    Deletes a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be deleted.

    Returns:
    ObjectId: The unique ID of the deleted document.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    if client is None:
        client = MongoClient(MONGODB_HOST)

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Delete the document from the collection
    result = collection.delete_one({'_id': document_id})

    # Return the unique ID of the deleted document
    return result

def update_document_in_mongodb(update_data,db_name,collection_name,document_id,client = None):
    """
    Updates a document in the MongoDB database 'ABKMS'.

    """
    if client is None:
        client = MongoClient(MONGODB_HOST)
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Combine page data and metadata into one document
    document = update_data

    # Update the document in the collection
    result = collection.update_one({'_id': document_id}, {'$set': document})

    # Return the unique ID of the updated document
    return result

def get_document_from_mongodb_id(collection_name,document_id,client = None):
    """
    Gets a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be retrieved.

    Returns:
    dict: A dictionary containing the document's metadata and page data.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    if client is None:
        client = MongoClient(MONGODB_HOST)
    else:
        client = client

    # Access the database and collection
    db = client[MONGODB_DB]
    collection = db[collection_name]

    # Get the document from the collection
    document = collection.find({'_id': document_id})

    # Return the document
    return document

def get_document_from_mongodb(collection_name,db_name,query_field,query_terms,client = None):
    """
    Gets a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be retrieved.

    Returns:
    dict: A dictionary containing the document's metadata and page data.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)
    if client is None:
        client = MongoClient(MONGODB_HOST)
        db = client[MONGODB_DB]
    else:
        client = client
        db = client[db_name]

    # Access the database and collection
    db = client[MONGODB_DB]
    collection = db[collection_name]

    # Get the document from the collection
    document = collection.find({query_field: query_terms})

    # Return the document
    return document

from pymongo import MongoClient

def get_document_field_from_mongodb(collection_name, db_name, query_field, query_terms, return_field, client=None):
    """
    Gets a specific field's value from a document in the MongoDB database.

    Args:
    collection_name (str): The name of the collection.
    db_name (str): The name of the database.
    query_field (str): The field name to query.
    query_terms: The value of the query field to match.
    return_field (str): The name of the field whose value is to be returned.
    client (MongoClient, optional): An instance of MongoClient.

    Returns:
    The value of the specified field in the document, or None if the document or field does not exist.
    """
    if client is None:
        client = MongoClient("mongodb_host")  # Replace "mongodb_host" with your MongoDB host
        db = client[db_name]
    else:
        db = client[db_name]

    # Access the collection
    collection = db[collection_name]

    # Get the document from the collection
    document = collection.find_one({query_field: query_terms})

    # Return the value of the specified field
    return document.get(return_field) if document else None


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
    client.close()
    return documents


if __name__ == "__main__":
    pass