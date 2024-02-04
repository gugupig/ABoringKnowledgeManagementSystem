#Config file for the application

ES_HOST = 'https://localhost:9200'
ES_HTTP_AUTH = ('elastic', 'dR8dVIqQ5=i3pPSH00zC')
ES_CA_CERTS_PATH = '/root/http_ca.crt'
MONGODB_HOST = "mongodb://admin:Gugupig098@localhost:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.8.0&authMechanism=DEFAULT"
MONGODB_DB = 'ABKMS'

DOCUMENTBANK_ROOT = '/root/gpt_projects/ABoringKnowledgeManagementSystem/DocumentBank'
SUPPORTED_FILE_TYPE = ['pdf','docx','txt']
DOCUMENT_TYPE = ['research_paper', 'research_book', 'personal_document', 'others']
DOCUMENT_LEVEL = ['chunk_level','page_level','document_level']
LOG_FILE_PATH_MONGODB = '/root/gpt_projects/ABoringKnowledgeManagementSystem/Logs/MONGODB.log'
LOG_FILE_PATH_ELASTICSEARCH = '/root/gpt_projects/ABoringKnowledgeManagementSystem/Logs/ELASTIC.log'
LOG_FILE_PATH_DOCUMENT_PROCESSING = '/root/gpt_projects/ABoringKnowledgeManagementSystem/Logs/DOCUMENT_PROCESSING.log'


CHAT_BOT_STATUT_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/chat_bot_statut_cache/chat_bot_statut_cache.pkl"
PDF_VIEWER_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/pdf_viewer_cache/pdf_viewer_cache.pkl"
CROSS_DOCUMENT_SEARCH_CACHE_PATH = "/root/gpt_projects/ABoringKnowledgeManagementSystem/WebApp/WebUI/static/cross_document_search_cache/cross_document_search_cache.pkl"


EMBEDDING_DINENSION = 1024
TEXT_SPLIT_SIZE = 512
LANGUAGE_CODE = ['en','fr','zh-cn','zh-tw']

if __name__ == "__main__":
    pass