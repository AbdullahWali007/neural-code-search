import json
import logging
import random
import torch
import math
from pathlib import Path
from torch.utils.data import DataLoader, Dataset
from sentence_transformers import SentenceTransformer, InputExample, losses
from sentence_transformers.evaluation import TripletEvaluator

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def get_optimal_device() -> str:
    """Detects the best available hardware accelerator."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def load_triplets(file_path: Path) -> list[InputExample]:
    """Loads the JSONL triplets and converts them into SentenceTransformer InputExamples."""
    if not file_path.exists():
        raise FileNotFoundError(f"Triplets file not found: {file_path}")
        
    examples = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                examples.append(InputExample(
                    texts=[data["query"], data["positive"], data["negative"]]
                ))
    return examples

def main():
    triplets_path = Path("training_triplets.jsonl")
    model_save_path = "finetuned-pandas-coder"
    
    device = get_optimal_device()
    logger.info(f"Hardware detected: [{device.upper()}]. Loading baseline model...")
    
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    
    logger.info(f"Loading training triplets from {triplets_path}...")
    all_examples = load_triplets(triplets_path)
    
    # 1. Train/Validation Split (90/10)
    random.seed(42) # Set seed for reproducibility
    random.shuffle(all_examples)
    
    split_idx = int(len(all_examples) * 0.9)
    train_examples = all_examples[:split_idx]
    val_examples = all_examples[split_idx:]
    
    logger.info(f"Dataset split: {len(train_examples)} Training | {len(val_examples)} Validation")
    
    # 2. Dynamic Batch Sizing
    # MNRL benefits massively from larger batch sizes. 
    batch_size = 32 if device in ["cuda", "mps"] else 16
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
    
    # 3. Setup the Evaluator
    logger.info("Configuring Triplet Evaluator...")
    val_anchors = [ex.texts[0] for ex in val_examples]
    val_positives = [ex.texts[1] for ex in val_examples]
    val_negatives = [ex.texts[2] for ex in val_examples]
    
    evaluator = TripletEvaluator(
        anchors=val_anchors, 
        positives=val_positives, 
        negatives=val_negatives, 
        name="pandas-val",
        show_progress_bar=False
    )
    
    logger.info("Initializing Multiple Negatives Ranking Loss...")
    train_loss = losses.MultipleNegativesRankingLoss(model=model)
    
    # Calculate evaluation steps (evaluate roughly 3 times per epoch)
    eval_steps = math.ceil(len(train_dataloader) / 3)
    
    logger.info("=== STARTING TRAINING LOOP ===")
    logger.info(f"Epochs: 4 | Batch Size: {batch_size} | Eval Steps: {eval_steps}")
    
    # 4. Fine-tune with explicit hyperparameter control and checkpointing
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        evaluator=evaluator,
        epochs=4,
        evaluation_steps=eval_steps,
        warmup_steps=100,
        output_path=model_save_path,
        save_best_model=True, # Critical: Only saves the weights that score highest on the evaluator
        show_progress_bar=True,
        optimizer_params={'lr': 2e-5} # Standard safe learning rate for embedding fine-tuning
    )
    
    logger.info(f"Training complete! Best model successfully written to ./{model_save_path}")

if __name__ == "__main__":
    main()