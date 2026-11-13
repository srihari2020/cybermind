import torch
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTTrainer, SFTConfig

# 1. UPGRADE to the Instruct model (Native Chat Capabilities)
model_id = "Qwen/Qwen2.5-1.5B-Instruct" 
dataset_path = "data/processed/cybermind_curriculum_25k.jsonl"
output_dir = "model/cybermind-v2-lora"

print(f"1. Loading the massive 25,000-record curriculum...")
dataset = load_dataset("json", data_files=dataset_path, split="train")

def format_record(example):
    # Native Qwen ChatML formatting so it never hallucinates "猞" again
    text = (
        "<|im_start|>system\nYou are CyberMind, a cybersecurity expert.<|im_end|>\n"
        f"<|im_start|>user\n{example['instruction']}<|im_end|>\n"
        f"<|im_start|>assistant\n{example['output']}<|im_end|>"
    )
    return {"text": text}

print("2. Formatting dataset into native ChatML...")
dataset = dataset.map(format_record)

print("3. Configuring 4-bit Quantization...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

print(f"4. Loading Instruct model '{model_id}' into VRAM...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto" 
)
model = prepare_model_for_kbit_training(model)

print("5. Configuring Expanded LoRA adapters (Smarter Training)...")
peft_config = LoraConfig(
    r=16,               # Increased complexity
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], # Targeting the full attention mechanism
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

print("\n6. Initializing the PyTorch Trainer...")
training_args = SFTConfig(
    output_dir=output_dir,
    dataset_text_field="text",          
    per_device_train_batch_size=1,      
    gradient_accumulation_steps=4,      
    optim="paged_adamw_8bit",           
    learning_rate=2e-4,
    bf16=True,                          
    max_steps=200,    # 200 steps is enough to see vast improvements without taking hours                  
    logging_steps=10,
    save_steps=200,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    args=training_args,
)

print("\n🔥 STARTING REAL PRODUCTION FINE-TUNING 🔥")
trainer.train()

print(f"\n✅ Training complete! V2 Model adapters saved to {output_dir}")
