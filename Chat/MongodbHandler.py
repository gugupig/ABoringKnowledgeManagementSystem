import datetime
from Utils.common_utils import convert_keys_to_string

def upload_document_to_mongodb(document,client,db_name):
    """
    Uploads a document's text and metadata to the MongoDB database 'ABKMS'.

    Args:
    page_data (dict): A dictionary where the key is the page number and the value is the text on that page.
    metadata (dict): A dictionary containing the metadata of the document.

    Returns:
    ObjectId: The unique ID of the inserted document.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)

    # Access the database and collection
    db = client[db_name]
    collection = db[document.document_type]

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
    if hasattr(document, 'text'):
        mongodocument['text'] = document.text
        mongodocument['language'] = document.language

    if document.file_type == 'pdf':
        mongodocument['file_path'] = document.file_path
        mongodocument['document_page_count'] = document.total_page_number
        mongodocument['document_title'] = document.document_title
        mongodocument['document_summary'] = document.document_summary  
        mongodocument['metadata'] = document.metadata
        mongodocument['annotation '] = document.annotation
        mongodocument['notes'] = document.notes
    elif document.file_type == 'docx':
        mongodocument['metadata'] = document.metadata

    elif document.file_type == 'note':
        mongodocument['text'] = document.text
        mongodocument['attached_documents'] = document.attached_documents_ids  #list of documents ids the note is attached to
        mongodocument['note_type'] = document.note_type #type of the note,now only has "pdf note" type

    elif document.file_type == 'graph':
        mongodocument['graph_data'] = document.graph_data
        mongodocument['attached_documents'] = document.attached_documents_ids
        
    
    #convert_keys_to_string(mongodocument)
    mongodocument = convert_keys_to_string(mongodocument)
    
    # Insert the document into the collection
    result = collection.insert_one(mongodocument)

    # Return the unique ID of the inserted document
    
    return result


def get_document_from_mongodb_id(client,db_name,collection_name,document_id):
    """
    Gets a document from the MongoDB database 'ABKMS'.

    Args:
    document_id (ObjectId): The unique ID of the document to be retrieved.

    Returns:
    dict: A dictionary containing the document's metadata and page data.
    """
    # Connect to MongoDB (modify the connection string as per your MongoDB setup)

    # Access the database and collection
    db = client[db_name]
    collection = db[collection_name]

    # Get the document from the collection
    document = collection.find_one({'_id': document_id})

    # Return the document
    client.close()
    return document