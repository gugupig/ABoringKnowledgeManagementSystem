from DocumentIndexing.Elastic import IndexSettingsGenerator
from DocumentIndexing.Elastic import search_engine
from config import *



# THIS ONLY NEED TO BE RUN ONCE

# Create the mapping for the index
indexsetting = IndexSettingsGenerator.GeneralIndexSettings(EMBEDDING_DINENSION)
mapping = indexsetting.get_base_mapping()

# Create the index
eleasticengine = search_engine.SearchEngine()
for index_name in DOCUMENT_TYPE:
    eleasticengine.create_index(index_name,mapping)
