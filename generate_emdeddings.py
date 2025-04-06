import json
import chromadb
from chromadb.api.types import Documents, Embeddings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import re

class LocalEmbeddingFunction:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def __call__(self, input: Documents) -> Embeddings:
        return self.model.encode(input).tolist()

class RAGEnhancer:
    def __init__(self, json_path: str):
        self.json_path = json_path
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
        self.website_data = self._load_data()
    
    # [Rest of the methods remain the same as your original generate_embeddings.py]
    
    def _load_data(self) -> Dict:
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _semantic_chunking(self, text: str, max_chars: int = 1000) -> List[Dict]:
        chunks = []
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chars:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    chunks.append({
                        "text": current_chunk.strip(),
                        "char_count": len(current_chunk),
                        "sentence_count": len(re.findall(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', current_chunk)) + 1
                    })
                current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append({
                "text": current_chunk.strip(),
                "char_count": len(current_chunk),
                "sentence_count": 1
            })
        return chunks
    
    def _process_page(self, page_id: str, page_data: Dict):
        self.collections["pages"].add(
            documents=[page_data["content"]],
            metadatas=[{
                "url": page_data["url"],
                "title": page_data["title"],
                "depth": page_data["depth"]
            }],
            ids=[page_id]
        )
        
        chunks = self._semantic_chunking(page_data["content"])
        for i, chunk in enumerate(chunks):
            chunk_id = f"{page_id}_chunk_{i}"
            self.collections["sections"].add(
                documents=[chunk["text"]],
                metadatas=[{
                    "page_url": page_data["url"],
                    "page_title": page_data["title"],
                    "chunk_length": chunk["char_count"],
                    "sentence_count": chunk["sentence_count"],
                    "depth": page_data["depth"]
                }],
                ids=[chunk_id]
            )
    
    def generate_embeddings(self):
        for page_id, page_data in self.website_data.items():
            self._process_page(page_id, page_data)
        print(f"Generated embeddings for {len(self.website_data)} pages")

if __name__ == "__main__":
    enhancer = RAGEnhancer("scraped_website.json")
    enhancer.generate_embeddings()