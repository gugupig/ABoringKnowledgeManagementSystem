from DocumentIndexing.Elastic import search_engine
from DocumentIndexing.Embedding.embedding_local import embeddings_multilingual as embed


def search_one_document(prompt,document_id,index_name='research_paper',return_top_n=1):
    orgnized_results = []
    new_search_engine = search_engine.SearchEngine()
    embedded_query = embed(prompt)
    search_results = new_search_engine.vector_search(index_name=index_name, query_vector=embedded_query,document_id=document_id)
    if search_results['hits']['hits']:
        if len(search_results['hits']['hits']) >= return_top_n:
            search_results = search_results['hits']['hits'][:return_top_n]
        else:
            search_results = search_results['hits']['hits']
    for hit in search_results:
        orgnized_results.append({'Page_number': hit['_source']['original_page_number'],
                                 'Text': hit['_source']['text_piece'],
                                 'Metadata': hit['_source']['metadata']})
    return orgnized_results
        


def one_document_prompt(orgnized_results):
    prompt = """Context:"""
    for i in range(len(orgnized_results)):
        prompt += f"\n{i+1}: {orgnized_results[i]['Text']}"
    return prompt

def two_step_retrival_page (prompt,document_id,index_name='research_paper',return_top_n=1):
    new_search_engine = search_engine.SearchEngine()
    embedded_query = embed(prompt)
    first_step =  new_search_engine.vector_search(index_name=index_name, query_vector=embedded_query,document_id=document_id)
    second_step = {}
    if first_step['hits']['hits']:
        most_relevant_page = [hit['_source']['original_page_number'] for hit in first_step['hits']['hits']]
    if most_relevant_page:
        if len(most_relevant_page) >= return_top_n:
            most_relevant_page = most_relevant_page[:return_top_n]
        else:
            most_relevant_page = most_relevant_page
    for page in most_relevant_page:
        second_step[page]= new_search_engine.retrieve_text_from_page(index_name=index_name, document_id=document_id, page_number=page)
    return second_step

def two_step_prompt_page(second_step):
    prompt = """Context:"""
    for page,page_text in second_step.items():
        prompt += f"\nPage{page}: {page_text}"
    return prompt

#WIP
def two_step_retrival_adjacents(prompt,document_id,index_name='research_paper',return_top_n=1,adjacent_window=2):
    new_search_engine = search_engine.SearchEngine()
    embedded_query = embed(prompt)
    first_step =  new_search_engine.vector_search(index_name=index_name, query_vector=embedded_query,document_id=document_id)
    if first_step['hits']['hits']:
        most_relevant_piece = [hit['_source']['document_id_elastic'] for hit in first_step['hits']['hits']]
    if most_relevant_piece:
        if len(most_relevant_piece) >= return_top_n:
            most_relevant_piece = most_relevant_piece[:return_top_n]
        else:
            most_relevant_piece = most_relevant_piece
    for piece in most_relevant_piece:
        second_step = new_search_engine.retrieve_text_and_its_adjacents(index_name=index_name,start_elastic_doc_id=piece, adjacent_window=adjacent_window)

    return second_step
#WIP
def two_step_prompt_adjacents(second_step):
    prompt = """Context:"""
    for piece in second_step:
        prompt += f"\n{piece}. {second_step[piece]['hits']['hits'][0]['_source']['text_piece']}"
    return prompt
