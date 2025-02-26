import chromadb
from generate_embeddings import embeddings, texts

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Create collection
collection = client.get_or_create_collection(name="city_permits")

def store_embeddings():
    """
    Stores multiple document embeddings along with original texts in ChromaDB.
    """
    try:
        for i, (embedding, text) in enumerate(zip(embeddings, texts)):
            collection.add(
                ids=[f"doc{i+1}"],  # Unique ID for each document
                embeddings=[embedding], 
                documents=[text],  # ✅ Store actual text along with embeddings
                metadatas=[{"source": "city_permits"}]
            )
        print("✅ All embeddings stored successfully in ChromaDB!")
    except Exception as e:
        print(f"❌ Error storing embeddings: {e}")

# Store embeddings
store_embeddings()
