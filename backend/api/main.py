from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from knowledge.retrieval.index import PersistentVectorIndex
from knowledge.ingestion.parsers import parse_cisa_kev, parse_mitre_enterprise

# Global state to keep the models loaded in VRAM/RAM
ml_engine = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Initializing CyberMind AI Engine in Memory...")
    ml_engine["client"] = OpenAI(base_url="http://localhost:11434/v1", api_key="cybermind-local")
    ml_engine["embedder"] = SentenceTransformer("BAAI/bge-small-en-v1.5")
    ml_engine["index"] = PersistentVectorIndex(Path('data/processed/knowledge.index.json'))
    
    # Load raw text into RAM for instant lookup
    cisa_docs = parse_cisa_kev(Path('data/raw/knowledge/cisa/known_exploited_vulnerabilities.json'))
    mitre_docs = parse_mitre_enterprise(Path('data/raw/knowledge/mitre_attack/enterprise-attack.json'))
    ml_engine["all_docs"] = {doc["source_id"]: doc["content"] for doc in cisa_docs + mitre_docs}
    
    print("✅ CyberMind Engine Ready! Listening for requests...")
    yield
    ml_engine.clear()

app = FastAPI(title="CyberMind API", lifespan=lifespan)

class ChatRequest(BaseModel):
    query: str

@app.post("/api/chat")
def chat_endpoint(request: ChatRequest):
    # 1. Semantic Search
    bge_instruction = "Represent this sentence for searching relevant passages: "
    query_vector = ml_engine["embedder"].encode(bge_instruction + request.query, normalize_embeddings=True)
    matches = ml_engine["index"].search(query_vector, top_k=3)
    
    # 2. Extract Context
    evidence_texts = []
    sources_used = []
    for match in matches:
        if match.source_id in ml_engine["all_docs"]:
            safe_text = ml_engine["all_docs"][match.source_id][:1000]
            evidence_texts.append(f"Source ID: {match.source_id}\nContent: {safe_text}")
            sources_used.append(match.source_id)
            
    context_block = "\n\n".join(evidence_texts)
    
    # 3. LLM Generation
    system_prompt = (
        "You are CyberMind, a cybersecurity AI. "
        "Use the provided Evidence Context to answer the user's question. "
        "If the answer is not in the context, explicitly state 'I do not have enough evidence.' "
        "Be concise and cite the Source IDs."
    )
    
    response = ml_engine["client"].chat.completions.create(
        model="qwen3.5:4b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Evidence Context:\n{context_block}\n\nQuestion: {request.query}"}
        ],
        temperature=0.1
    )
    
    return {
        "query": request.query,
        "answer": response.choices[0].message.content,
        "sources": sources_used
    }
