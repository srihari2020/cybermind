from pathlib import Path
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from knowledge.retrieval.index import PersistentVectorIndex
from knowledge.ingestion.parsers import parse_cisa_kev, parse_mitre_enterprise

client = OpenAI(base_url="http://localhost:11434/v1", api_key="cybermind-local")
llm_model = "qwen3.5:4b"

index = PersistentVectorIndex(Path('data/processed/knowledge.index.json'))
embedder = SentenceTransformer("BAAI/bge-small-en-v1.5")

cisa_docs = parse_cisa_kev(Path('data/raw/knowledge/cisa/known_exploited_vulnerabilities.json'))
mitre_docs = parse_mitre_enterprise(Path('data/raw/knowledge/mitre_attack/enterprise-attack.json'))
all_docs = {doc["source_id"]: doc["content"] for doc in cisa_docs + mitre_docs}

# UPDATED QUERY: Using semantic description rather than just a raw ID
query = "What is the Apache Log4j2 Deserialization of Untrusted Data vulnerability, and what is the required action to mitigate it?"
print(f"\n[USER QUESTION]: {query}\n")

# BGE models specifically require this prefix for queries to align the vector space
bge_instruction = "Represent this sentence for searching relevant passages: "
query_vector = embedder.encode(bge_instruction + query, normalize_embeddings=True)

matches = index.search(query_vector, top_k=3)

evidence_texts = []
for match in matches:
    if match.source_id in all_docs:
        full_text = all_docs[match.source_id]
        safe_text = full_text[:1000] + "... [TRUNCATED]"
        evidence_texts.append(f"Source ID: {match.source_id}\nContent: {safe_text}")

context_block = "\n\n".join(evidence_texts)
print(f"   -> Retrieved {len(matches)} highly relevant records.")

system_prompt = (
    "You are CyberMind, a cybersecurity AI. "
    "Use the provided Evidence Context to answer the user's question. "
    "If the answer is not in the context, explicitly state 'I do not have enough evidence.' "
    "Be concise and cite the Source IDs."
)

user_prompt = f"Evidence Context:\n{context_block}\n\nQuestion: {query}"

print("\n2. Generating evidence-based response via Local LLM...")
print("================ CYBERMIND RESPONSE ================\n")

response = client.chat.completions.create(
    model=llm_model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    stream=True, 
    temperature=0.1 
)

for chunk in response:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)

print("\n\n====================================================")
