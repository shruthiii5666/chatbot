from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.processor import QueryProcessor

app = FastAPI()
processor = QueryProcessor()

# Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to localhost or specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG Chatbot API"}

@app.post("/query")
def query_bot(request: QueryRequest):
    results = processor.hierarchical_retrieve(request.question)
    if not results["sections"]["documents"][0]:
        return {"answer": "No relevant information found."}
    answers = []
    for i, (text, score, metadata) in enumerate(zip(
        results["sections"]["documents"][0],
        results["sections"]["distances"][0],
        results["sections"]["metadatas"][0]
    )):
        answers.append({
            "rank": i + 1,
            "relevance": round(1 - score, 2),
            "source": metadata.get("page_title", "Unknown"),
            "content": text
        })
    return {"answers": answers}
