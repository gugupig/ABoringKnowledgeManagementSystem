from DocumentIndexing.Elastic import search_engine,knn_cluster


def cluster_search_engine(document_id,index = 'research_paper_chunk_level',limites = 1000,cluster_number = 10,nb_return_per_cluster = 2):
    search_engine_instance = search_engine.SearchEngine()
    _ = search_engine_instance.serach_by_id(index,document_id,limites)
    embeddings = [i['_source']['text_piece_vector'] for i in _['hits']['hits']]
    centroid = knn_cluster.cluster_embeddings(embeddings,cluster_number)
    text_per_cluster = []
    for center in centroid:
        _ = search_engine_instance.vector_search(index,center,document_id = document_id)
        # WARNING: Could end up with less than nb_return_per_cluster results if there are not enough documents in the cluster
        # TODO: Handle this case
        text_per_cluster.append('\n'.join([i['_source']['text_piece'] for i in _['hits']['hits'][:nb_return_per_cluster]]))
    return text_per_cluster

    