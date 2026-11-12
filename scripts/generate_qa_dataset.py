import json
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm
from knowledge.ingestion.parsers import parse_cisa_kev, parse_mitre_enterprise

client = OpenAI(base_url="http://localhost:11434/v1", api_key="cybermind-local")
llm_model = "qwen3.5:4b"
output_file = Path('data/processed/synthetic_qa_dataset.jsonl')

print("1. Loading raw cybersecurity datasets...")
cisa_docs = parse_cisa_kev(Path('data/raw/knowledge/cisa/known_exploited_vulnerabilities.json'))
mitre_docs = parse_mitre_enterprise(Path('data/raw/knowledge/mitre_attack/enterprise-attack.json'))
all_docs = cisa_docs + mitre_docs

print(f"\n2. Generating synthetic Q&A pairs for {len(all_docs)} records...")
print("   (Note: You can press Ctrl+C to stop at any time. Data is saved continuously.)\n")

# Open in 'append' mode so we don't overwrite previous work if we stop/restart
with open(output_file, 'a') as f:
    for doc in tqdm(all_docs, desc="Generating QA Pairs"):
        context = doc['content'][:1500] 
        
        system_prompt = "You are a strict data engineering AI. You only output raw, valid JSON. Never output conversational text."
        user_prompt = (
            f"Context:\n{context}\n\n"
            "Task: Act as a cybersecurity instructor. Write one highly technical question based on this context, "
            "and provide the detailed answer. Output ONLY valid JSON in this exact format:\n"
            '{"instruction": "<the question>", "output": "<the detailed answer>"}'
        )
        
        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2 
            )
            
            raw_output = response.choices[0].message.content.strip()
            clean_output = raw_output.replace('```json', '').replace('```', '').strip()
            
            parsed_json = json.loads(clean_output)
            f.write(json.dumps(parsed_json) + '\n')
            
        except Exception as e:
            # If the LLM hallucinates bad JSON, we just skip it and move to the next one
            pass

print(f"\n3. Data generation paused/completed. Data saved to {output_file}")
