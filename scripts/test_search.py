from pathlib import Path
from sentence_transformers import SentenceTransformer
from knowledge.retrieval.index import PersistentVectorIndex

# 1. Setup paths and parameters
index_path = Path('data/processed/knowledge.index.json')
model_name = "BAAI/bge-small-en-v1.5"

print(f"1. Loading vector index from {index_path}...")
index = PersistentVectorIndex(index_path, model_name=model_name)
print(f"   -> Loaded {len(index.entries)} records.")

print(f"\n2. Loading embedding model '{model_name}'...")
# We use the exact same model to ensure the question is mapped to the same mathematical space
model = SentenceTransformer(model_name)

# 3. Define our test queries
queries = [
    "What is Log4Shell?",
    "How do attackers abuse scheduled tasks in Windows?",
]

print("\n3. Executing Semantic Search...")
for query in queries:
    print(f"\n==================================================")
    print(f"QUERY: {query}")
    print(f"==================================================")
    
    # Convert the text question into a vector
    query_vector = model.encode(query, normalize_embeddings=True)
    
    # Search the PersistentVectorIndex
    matches = index.search(query_vector, top_k=2)
    
    for rank, match in enumerate(matches, 1):
        # We need to find the full text of the match from the index entries
        # In a full database this would be a SQL join, but here we just iterate
        entry_text = "Unknown"
        for entry in index.entries:
            if entry.source_id == match.source_id:
                entry_text = entry.title
                break
                
        print(f"\n[Rank {rank}] Source: {match.source_id} | Similarity Score: {match.similarity:.4f}")
        print(f"Title: {entry_text}")

print("\nSearch test complete!")
