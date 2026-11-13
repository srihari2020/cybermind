import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base_model_id = "Qwen/Qwen2.5-1.5B-Instruct"
# Pointing precisely to the new V2 checkpoint!
adapter_dir = "model/cybermind-v2-lora/checkpoint-200"
output_dir = "model/cybermind-v2-merged"

print(f"1. Loading Instruct base model '{base_model_id}' into system RAM...")
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id, 
    torch_dtype=torch.bfloat16, 
    device_map="cpu"
)
tokenizer = AutoTokenizer.from_pretrained(base_model_id)

print(f"2. Loading trained V2 LoRA adapters from '{adapter_dir}'...")
model = PeftModel.from_pretrained(base_model, adapter_dir)

print("3. Welding adapters into the base neural network (this requires heavy CPU math)...")
model = model.merge_and_unload()

print(f"4. Saving the standalone CyberMind V2 model to '{output_dir}'...")
model.save_pretrained(output_dir, safe_serialization=True)
tokenizer.save_pretrained(output_dir)

print("✅ Success! V2 Model successfully merged.")
