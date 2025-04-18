import chromadb
from chromadb.api.types import Documents, Embeddings
from sentence_transformers import SentenceTransformer

class LocalEmbeddingFunction:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()

class QueryProcessor:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="chroma_db")
        self.embedding_function = LocalEmbeddingFunction()

        self.collections = {
            "pages": self.client.get_or_create_collection(
                name="pages",
                embedding_function=self.embedding_function
            ),
            "sections": self.client.get_or_create_collection(
                name="sections",
                embedding_function=self.embedding_function
            )
        }

    def hierarchical_retrieve(self, query: str, top_n_sections: int = 2):
        results = self.collections["sections"].query(
            query_texts=[query],
            n_results=top_n_sections
        )
        return {
            "sections": {
                "documents": results["documents"],
                "distances": results["distances"],
                "metadatas": results["metadatas"]
            }
        }
