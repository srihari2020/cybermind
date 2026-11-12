import torch
from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTTrainer, SFTConfig

model_id = "Qwen/Qwen2.5-1.5B" 
dataset_path = "data/processed/hf_cyber_qa.jsonl"
output_dir = "model/cybermind-v1-lora"

print(f"1. Loading local dataset from {dataset_path}...")
dataset = load_dataset("json", data_files=dataset_path, split="train")

def format_record(example):
    formatted_text = f"Instruction: {example['instruction']}\n\nResponse: {example['output']}"
    return {"text": formatted_text}

print("2. Formatting dataset...")
dataset = dataset.map(format_record)

print("3. Configuring 4-bit Quantization for RTX 5060...")
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

print(f"4. Loading base model '{model_id}' into VRAM...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=bnb_config,
    device_map="auto" 
)
model = prepare_model_for_kbit_training(model)

print("5. Configuring LoRA adapters...")
peft_config = LoraConfig(
    r=8, 
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"], 
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM"
)

print("\n6. Initializing the modern PyTorch Trainer (SFTConfig)...")
training_args = SFTConfig(
    output_dir=output_dir,
    dataset_text_field="text",          # Perfectly compliant with trl 1.17+
    per_device_train_batch_size=1,      
    gradient_accumulation_steps=4,      
    optim="paged_adamw_8bit",           
    learning_rate=2e-4,
    fp16=False,
    bf16=True,                          
    max_steps=25,                       
    logging_steps=5,
    save_steps=25,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    peft_config=peft_config,
    args=training_args,
)

print("\n🔥 STARTING PHASE 5 FINE-TUNING 🔥")
trainer.train()

print(f"\n✅ Training complete! Model adapters saved to {output_dir}")
