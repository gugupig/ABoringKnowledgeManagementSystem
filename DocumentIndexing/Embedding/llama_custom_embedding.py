from typing import Any, List
from sentence_transformers import SentenceTransformer
from llama_index.embeddings.base import BaseEmbedding

class MultilingualEmbeddings(BaseEmbedding):
    def __init__(
        self,
        model_name: str = 'sentence-transformers/distiluse-base-multilingual-cased-v2',
        **kwargs: Any,
    ) -> None:
        self._model = SentenceTransformer(model_name)
        super().__init__(**kwargs)

    def _get_query_embedding(self, query: str) -> List[float]:
        embeddings = self._model.encode([query])
        return embeddings[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        embeddings = self._model.encode([text])
        return embeddings[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = self._model.encode(texts)
        return embeddings


embed_model = MultilingualEmbeddings()
service_context = ServiceContext.from_defaults(embed_model=embed_model)