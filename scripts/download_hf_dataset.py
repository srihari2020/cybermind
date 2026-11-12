import json
from pathlib import Path
from datasets import load_dataset

output_file = Path('data/processed/hf_cyber_qa.jsonl')

print("1. Connecting to Hugging Face to download the Cybersecurity Instruction dataset...")
# Load the open-source defensive cybersecurity dataset
dataset = load_dataset("Trendyol/Trendyol-Cybersecurity-Instruction-Tuning-Dataset", split="train")

# Select a subset of 500 records so we can quickly test our Phase 5 training loop
subset = dataset.select(range(500))

print(f"2. Successfully downloaded {len(subset)} records. Formatting for local training...")

with open(output_file, 'w') as f:
    for row in subset:
        # The Trendyol dataset uses 'user' for the question and 'assistant' for the answer
        instruction = row.get("user", "")
        output = row.get("assistant", "")
        
        # Save in the strict JSONL format required for our LoRA fine-tuning
        formatted_record = {
            "instruction": instruction,
            "output": output
        }
        f.write(json.dumps(formatted_record) + '\n')

print(f"3. Success! High-quality training dataset saved offline to {output_file}")
