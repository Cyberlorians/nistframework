"""
QLoRA Training Script for CMMC Compliance AI Model

Fine-tunes Qwen2.5-7B-Instruct with QLoRA for cybersecurity compliance
domain specialization. Designed to run on a single 16 GB VRAM GPU.

Usage:
    python training/train_qlora.py --config training/config.yaml

Dependencies:
    pip install torch transformers peft trl bitsandbytes datasets pyyaml
"""

import yaml
import argparse
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig


def load_config(config_path: str) -> dict:
    """Load training configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def setup_quantization(config: dict) -> BitsAndBytesConfig:
    """Configure 4-bit quantization for base model."""
    qconfig = config['model']['quantization']
    return BitsAndBytesConfig(
        load_in_4bit=qconfig['load_in_4bit'],
        bnb_4bit_compute_dtype=getattr(torch, qconfig['bnb_4bit_compute_dtype']),
        bnb_4bit_quant_type=qconfig['bnb_4bit_quant_type'],
        bnb_4bit_use_double_quant=qconfig['bnb_4bit_use_double_quant'],
    )


def setup_lora(config: dict) -> LoraConfig:
    """Configure LoRA adapters."""
    lora_cfg = config['lora']
    return LoraConfig(
        r=lora_cfg['rank'],
        lora_alpha=lora_cfg['alpha'],
        lora_dropout=lora_cfg['dropout'],
        target_modules=lora_cfg['target_modules'],
        bias=lora_cfg['bias'],
        task_type=lora_cfg['task_type'],
    )


def main():
    parser = argparse.ArgumentParser(description='Train CMMC compliance model with QLoRA')
    parser.add_argument('--config', type=str, default='training/config.yaml',
                       help='Path to training config YAML')
    args = parser.parse_args()

    config = load_config(args.config)
    print(f"Loaded config from {args.config}")

    # --- Model Setup ---
    base_model = config['model']['base_model']
    print(f"Loading base model: {base_model}")

    bnb_config = setup_quantization(config)

    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    model = prepare_model_for_kbit_training(model)

    tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # --- LoRA Setup ---
    lora_config = setup_lora(config)
    model = get_peft_model(model, lora_config)

    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable parameters: {trainable:,} / {total:,} ({trainable/total*100:.4f}%)")

    # --- Data Loading ---
    data_config = config['data']
    dataset = load_dataset('json', data_files={
        'train': data_config['train_file'],
        'validation': data_config['val_file'],
    })
    print(f"Train: {len(dataset['train']):,} | Val: {len(dataset['validation']):,}")

    # --- Training ---
    train_config = config['training']

    training_args = SFTConfig(
        output_dir=train_config['output_dir'],
        num_train_epochs=train_config['num_train_epochs'],
        per_device_train_batch_size=train_config['per_device_train_batch_size'],
        per_device_eval_batch_size=train_config['per_device_eval_batch_size'],
        gradient_accumulation_steps=train_config['gradient_accumulation_steps'],
        learning_rate=train_config['learning_rate'],
        lr_scheduler_type=train_config['lr_scheduler_type'],
        warmup_ratio=train_config['warmup_ratio'],
        weight_decay=train_config['weight_decay'],
        max_grad_norm=train_config['max_grad_norm'],
        bf16=train_config['bf16'],
        tf32=train_config['tf32'],
        max_seq_length=train_config['max_seq_length'],
        packing=train_config['packing'],
        eval_strategy=train_config['eval_strategy'],
        eval_steps=train_config['eval_steps'],
        save_strategy=train_config['save_strategy'],
        save_steps=train_config['save_steps'],
        save_total_limit=train_config['save_total_limit'],
        load_best_model_at_end=train_config['load_best_model_at_end'],
        metric_for_best_model=train_config['metric_for_best_model'],
        greater_is_better=train_config['greater_is_better'],
        logging_steps=train_config['logging_steps'],
        report_to=train_config['report_to'],
    )

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset['train'],
        eval_dataset=dataset['validation'],
        tokenizer=tokenizer,
    )

    print("Starting training...")
    trainer.train()

    # Save final adapter
    final_path = Path(train_config['output_dir']) / "final_adapter"
    trainer.save_model(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    print(f"Training complete. Adapter saved to {final_path}")


if __name__ == '__main__':
    main()
