import json
import time
import torch
import logging
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def get_optimal_device() -> str:
    """Detects the best available hardware accelerator."""
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def load_corpus(file_path: Path) -> List[Dict[str, str]]:
    """Loads the extracted code-docstring pairs efficiently."""
    if not file_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")
    
    corpus = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                corpus.append(json.loads(line))
    return corpus

def get_or_create_embeddings(model: SentenceTransformer, corpus_code: List[str], cache_path: Path) -> torch.Tensor:
    """Loads embeddings from disk if available, otherwise generates and caches them."""
    if cache_path.exists():
        logger.info(f"Loading cached embeddings from {cache_path}...")
        return torch.load(cache_path, weights_only=True)

    logger.info(f"Cache miss. Embedding {len(corpus_code)} snippets (this might take a minute)...")
    start_time = time.time()
    
    # Increase batch size for better GPU utilization if not on CPU
    batch_size = 32 if model.device.type == "cpu" else 128
    
    corpus_embeddings = model.encode(
        corpus_code, 
        convert_to_tensor=True, 
        show_progress_bar=True,
        batch_size=batch_size
    )
    
    logger.info(f"Embedding complete in {time.time() - start_time:.2f} seconds.")
    
    # Cache the embeddings for future runs
    torch.save(corpus_embeddings, cache_path)
    logger.info(f"Embeddings cached to {cache_path}")
    
    return corpus_embeddings

def main():
    corpus_path = Path("pandas_dataset.jsonl")
    cache_path = Path("baseline_embeddings.pt")
    output_report_path = Path("baseline_eval_results.json")
    
    logger.info("Loading dataset...")
    corpus = load_corpus(corpus_path)
    corpus_code = [item["code"] for item in corpus]
    
    device = get_optimal_device()
    logger.info(f"Loading baseline model: all-MiniLM-L6-v2 on [{device.upper()}]...")
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    
    corpus_embeddings = get_or_create_embeddings(model, corpus_code, cache_path)

    # The Evaluation Set
    queries = [
        "parse a date column from a string",
        "drop rows with missing values",
        "group data by a column and calculate the mean",
        "merge two dataframes together on a specific key",
        "convert dataframe to a dictionary"
    ]

    logger.info("=== RUNNING BASELINE EVALUATION ===")
    
    eval_report: List[Dict[str, Any]] = []

    for query in queries:
        print(f"\nQuery: '{query}'")
        
        query_embedding = model.encode(query, convert_to_tensor=True)
        hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=3)[0]
        
        query_results = {
            "query": query,
            "top_hits": []
        }

        print("Top 3 Results:")
        for i, hit in enumerate(hits):
            idx = int(hit["corpus_id"])
            score = hit["score"]
            func_name = corpus[idx]["function_name"]
            
            # Save to report
            query_results["top_hits"].append({
                "rank": i + 1,
                "function_name": func_name,
                "score": float(score) # Convert tensor float to standard python float for JSON
            })
            
            print(f"  {i+1}. {func_name} (Score: {score:.4f})")
            
        eval_report.append(query_results)
        print("-" * 50)

    # Export the baseline report
    with output_report_path.open("w", encoding="utf-8") as f:
        json.dump(eval_report, f, indent=4)
    
    logger.info(f"Baseline evaluation saved to {output_report_path}. Keep this file for Phase 4 comparison.")

if __name__ == "__main__":
    main()