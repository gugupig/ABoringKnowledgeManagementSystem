from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize
import numpy as np


def cluster_embeddings(embeddings, num_clusters):
    normalized_embeddings = normalize(embeddings)
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(normalized_embeddings)
    return kmeans.cluster_centers_

