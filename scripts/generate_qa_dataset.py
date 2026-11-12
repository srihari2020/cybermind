import json
import random
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm
from knowledge.ingestion.parsers import parse_cisa_kev, parse_mitre_enterprise

client = OpenAI(base_url="http://localhost:11434/v1", api_key="cybermind-local")
llm_model = "qwen3.5:4b"
output_file = Path('data/processed/synthetic_qa_dataset.jsonl')

print("1. Loading raw cybersecurity datasets from local SSD...")
cisa_docs = parse_cisa_kev(Path('data/raw/knowledge/cisa/known_exploited_vulnerabilities.json'))
mitre_docs = parse_mitre_enterprise(Path('data/raw/knowledge/mitre_attack/enterprise-attack.json'))
all_docs = cisa_docs + mitre_docs

# Define our 4 difficulty tiers to build a well-rounded Mentor AI
task_prompts = [
    # BEGINNER
    "Act as a friendly cybersecurity mentor. Write a basic, easy-to-understand question about the core concept in this context, and answer it using simple analogies suitable for a beginner.",
    
    # MEDIUM
    "Act as a cybersecurity instructor. Write an intermediate-level question about how this vulnerability/technique works practically, and provide a clear, structured answer.",
    
    # HARD
    "Act as a senior security engineer. Write a highly technical, advanced question based on this context, and provide a complex, detailed answer focusing on the underlying architecture.",
    
    # EXTRA SKILLS / GUIDANCE
    "Act as a career guide. Based on the context provided, write a question asking what specific extra skills, tools, or certifications a user should learn to defend against this, and provide a guiding answer."
]

print(f"\n2. Generating Multi-Tiered Curriculum Q&A for {len(all_docs)} records...")
print("   (Note: You can press Ctrl+C to stop at any time. Data is saved continuously.)\n")

with open(output_file, 'a') as f:
    for doc in tqdm(all_docs, desc="Generating QA Pairs"):
        context = doc['content'][:1500] 
        
        # Randomly select a difficulty level for this specific record
        selected_task = random.choice(task_prompts)
        
        system_prompt = "You are a strict data engineering AI. You only output raw, valid JSON. Never output conversational text."
        user_prompt = (
            f"Context:\n{context}\n\n"
            f"Task: {selected_task}\n"
            "Output ONLY valid JSON in this exact format:\n"
            '{"instruction": "<the question>", "output": "<the detailed answer>"}'
        )
        
        try:
            response = client.chat.completions.create(
                model=llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3 # Slightly higher temperature allows for better analogies/guidance
            )
            
            raw_output = response.choices[0].message.content.strip()
            clean_output = raw_output.replace('```json', '').replace('```', '').strip()
            
            parsed_json = json.loads(clean_output)
            f.write(json.dumps(parsed_json) + '\n')
            
        except Exception as e:
            pass

print(f"\n3. Data generation paused/completed. Data saved to {output_file}")
