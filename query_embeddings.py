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
            "pages": self.client.get_collection(
                name="pages",
                embedding_function=self.embedding_function
            ),
            "sections": self.client.get_collection(
                name="sections",
                embedding_function=self.embedding_function
            )
        }
    
    def hierarchical_retrieve(self, query: str, top_n_sections: int = 2):
        # Directly retrieve top 2 most relevant sections
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

def main():
    processor = QueryProcessor()
    print("Chatbot ready! Type 'exit' to quit.")
    while True:
        query = input("\nYour question: ")
        if query.lower() == 'exit':
            break
            
        results = processor.hierarchical_retrieve(query)
        
        if not results["sections"]["documents"][0]:
            print("\nNo relevant information found.")
            continue
            
        print("\nTop 2 most relevant answers:")
        for i, (text, score, metadata) in enumerate(zip(
            results["sections"]["documents"][0],
            results["sections"]["distances"][0],
            results["sections"]["metadatas"][0]
        )):
            print(f"\n{i+1}. (Relevance: {1-score:.2f})")
            print(f"Source: {metadata['page_title']}")
            print(f"Content: {text}")
            ##print("-" * 80)

if __name__ == "__main__":
    main()