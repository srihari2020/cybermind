from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth.chat_templates import get_chat_template

print("🚀 Initializing CyberMind Fine-Tuning Protocol...")

max_seq_length = 2048 # Keeps memory usage strictly within 8GB VRAM limits

# 1. Load Model in 4-bit Quantization
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen2.5-3B-Instruct",
    max_seq_length = max_seq_length,
    dtype = None,
    load_in_4bit = True, # CRITICAL for RTX 5060 8GB VRAM
)

# 2. Attach LoRA Adapters (Only trains ~2% of the model weights)
model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
)

# 3. Load & Map the Dataset
tokenizer = get_chat_template(tokenizer, chat_template="qwen-2.5")

def format_chat(examples):
    texts = [tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=False) for msg in examples["messages"]]
    return {"text": texts}

print("📂 Loading cybermind_master_intel.jsonl...")
dataset = load_dataset("json", data_files="data/cybermind_master_intel.jsonl", split="train")
dataset = dataset.map(format_chat, batched=True)

# 4. Configure the Trainer
trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Set to False for chat templates
    args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 10,
        max_steps = 60, # Keep it short for a rapid proof-of-concept run
        learning_rate = 2e-4,
        fp16 = not is_bfloat16_supported(),
        bf16 = is_bfloat16_supported(),
        logging_steps = 10,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = "outputs",
    )
)

# 5. Execute Training
print("🔥 Initiating LoRA Training sequence...")
trainer_stats = trainer.train()

# 6. Export to Ollama GGUF
print("📦 Exporting fine-tuned model to GGUF format for Ollama...")
model.save_pretrained_gguf("CyberMind-4B-GGUF", tokenizer, quantization_method = "q4_k_m")
print("✅ CyberMind specializations successfully locked and exported!")
