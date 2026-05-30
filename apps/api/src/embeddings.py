"""
Embeddings wrapper for multilingual legal text retrieval.

Uses intfloat/multilingual-e5-small (384d contextual) with the e5 prefix
convention:
  - Documents (chunks):  "passage: " prefix
  - Queries (user input): "query: " prefix

This replaces the previous model2vec static embeddings (256d) which lacked
contextual understanding and had lower retrieval quality.
"""
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from typing import List


class MultilingualE5Embeddings(Embeddings):
    """LangChain-compatible embeddings wrapper for multilingual-e5-small.

    Implements the INTFLOAT/e5 prefix convention where queries and documents
    are prefixed with role markers before encoding. This is required by the
    model's training objective — without the prefix, retrieval quality drops
    significantly.
    """

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        prefixed = ["passage: " + t for t in texts]
        embeddings = self.model.encode(
            prefixed,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        prefixed = "query: " + text
        embedding = self.model.encode(
            [prefixed],
            normalize_embeddings=True,
        )
        return embedding[0].tolist()