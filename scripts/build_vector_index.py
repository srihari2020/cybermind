import hashlib
from pathlib import Path
from sentence_transformers import SentenceTransformer
from knowledge.ingestion.parsers import parse_cisa_kev, parse_mitre_enterprise
from knowledge.retrieval.index import PersistentVectorIndex, VectorEntry

# 1. Setup paths
cisa_path = Path('data/raw/knowledge/cisa/known_exploited_vulnerabilities.json')
mitre_path = Path('data/raw/knowledge/mitre_attack/enterprise-attack.json')
index_path = Path('data/processed/knowledge.index.json')

# 2. Parse documents
print("1. Parsing raw datasets...")
cisa_docs = parse_cisa_kev(cisa_path)
mitre_docs = parse_mitre_enterprise(mitre_path)
all_docs = cisa_docs + mitre_docs
print(f"   -> Loaded {len(all_docs)} total records.")

# 3. Load embedding model
model_name = "BAAI/bge-small-en-v1.5"
print(f"\n2. Loading embedding model '{model_name}'...")
model = SentenceTransformer(model_name)
dimension = model.get_sentence_embedding_dimension()
print(f"   -> Model loaded. Vector dimension is {dimension}.")

# 4. Generate Vectors
print(f"\n3. Generating vectors for {len(all_docs)} documents...")
print("   -> (This might take a moment. Your GPU will accelerate this!)")
texts = [doc["content"] for doc in all_docs]
# normalize_embeddings=True is required for exact cosine similarity
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)

# 5. Format as VectorEntry objects for the PersistentVectorIndex
print("\n4. Formatting records for the database...")
entries = []
for doc, vector in zip(all_docs, embeddings):
    content_hash = hashlib.sha256(doc["content"].encode('utf-8')).hexdigest()
    entry = VectorEntry(
        source_id=doc["source_id"],
        chunk_id=f"{doc['source_id']}-chunk-0",
        title=f"{doc['source_type'].replace('_', ' ').title()} Record",
        publisher=doc["source_type"].upper(),
        content_hash=content_hash,
        vector=tuple(float(x) for x in vector)
    )
    entries.append(entry)

# 6. Save to Index
print("\n5. Saving to PersistentVectorIndex...")
index = PersistentVectorIndex(index_path)
index.replace(entries, model_name=model_name, dimension=dimension, allow_model_change=True)
print(f"\nSUCCESS! 🚀 {len(entries)} vectors permanently saved to {index_path}")
