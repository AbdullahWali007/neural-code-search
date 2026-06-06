import json
import re
import random
import logging
import heapq
from pathlib import Path
from tqdm import tqdm
from rank_bm25 import BM25Okapi

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def tokenize(text: str) -> list[str]:
    """
    Advanced Python code tokenizer.
    Splits on non-alphanumeric characters AND breaks apart camelCase.
    """
    # Insert a space before capital letters to break camelCase
    text = re.sub(r'(?<!^)(?=[A-Z])', ' ', text)
    # Split by non-alphanumeric
    tokens = re.split(r'[^a-zA-Z0-9]+', text)
    return [t.lower() for t in tokens if len(t) > 1]

def load_corpus(file_path: Path) -> list[dict]:
    if not file_path.exists():
        raise FileNotFoundError(f"Corpus file not found: {file_path}")
        
    corpus = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                corpus.append(json.loads(line))
    return corpus

def main():
    input_path = Path("pandas_dataset.jsonl")
    output_path = Path("training_triplets.jsonl")

    logger.info("Loading dataset...")
    corpus = load_corpus(input_path)
    
    logger.info("Tokenizing code corpus for BM25...")
    tokenized_corpus = [tokenize(item["code"]) for item in tqdm(corpus, desc="Tokenizing")]
    
    logger.info("Building BM25 Index (this takes a moment)...")
    bm25 = BM25Okapi(tokenized_corpus)

    logger.info("Mining hard negatives for each query...")
    
    # Open file immediately for streaming writes
    with output_path.open("w", encoding="utf-8") as f:
        for i, item in enumerate(tqdm(corpus, desc="Mining Triplets")):
            anchor_query = item["docstring"]
            positive_code = item["code"]
            
            # Tokenize the positive code to find structurally similar code
            tokenized_query = tokenize(positive_code)
            
            # Get BM25 scores for all snippets
            scores = bm25.get_scores(tokenized_query)
            
            # OPTIMIZATION: Use heapq to efficiently find the top 10 indices without sorting the whole array
            top_10_indices = heapq.nlargest(10, range(len(scores)), key=scores.__getitem__)
            
            hard_negative_code = None
            
            for idx in top_10_indices:
                if idx != i: # Skip the true positive
                    candidate_code = corpus[idx]["code"]
                    candidate_docstring = corpus[idx]["docstring"]
                    
                    # FALSE NEGATIVE TRAP: Ensure we don't pick an exact code match OR an alias (identical docstring)
                    if candidate_code != positive_code and candidate_docstring != anchor_query:
                        hard_negative_code = candidate_code
                        break
                        
            # Fallback to a random snippet if BM25 fails to find a valid negative
            if not hard_negative_code:
                valid_random_indices = [x for x in range(len(corpus)) if x != i]
                random_idx = random.choice(valid_random_indices)
                hard_negative_code = corpus[random_idx]["code"]

            # Construct triplet and stream directly to disk
            triplet = {
                "query": anchor_query,
                "positive": positive_code,
                "negative": hard_negative_code
            }
            f.write(json.dumps(triplet) + "\n")

    logger.info(f"Phase 3 Complete: Mined {len(corpus)} triplets successfully to {output_path}!")

if __name__ == "__main__":
    main()