from langchain_core.embeddings import Embeddings
from model2vec import StaticModel
from typing import List


class Model2VecEmbeddings(Embeddings):
    """Custom LangChain embeddings wrapper for model2vec StaticModel."""

    def __init__(self, model_name: str):
        self.model = StaticModel.from_pretrained(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode([text])
        return embedding[0].tolist()
