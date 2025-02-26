from generate_embeddings import get_embedding
import chromadb

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="city_permits")

def query_chroma(query_text):
    """
    Searches for relevant information in the ChromaDB vector database.
    """
    query_embedding = get_embedding(query_text)  # Convert query into an embedding

    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3,  # Get top 3 similar documents
            include=["documents", "distances", "metadatas"]  # ✅ Ensure documents are retrieved
        )
        return results
    except Exception as e:
        print(f"❌ Error querying ChromaDB: {e}")
        return None

# Example Query
query_text = "What are the parking permit requirements?"
search_results = query_chroma(query_text)

if search_results and search_results["documents"] and search_results["documents"][0]:
    print("✅ Retrieved documents:")
    for doc, distance in zip(search_results["documents"][0], search_results["distances"][0]):
        print(f"- {doc} (Similarity Score: {1 - distance:.2f})")
else:
    print("❌ No relevant documents found in ChromaDB!")
