import json
import faiss
import torch
import numpy as np
import logging
import gc
from pathlib import Path
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from sentence_transformers.quantization import quantize_embeddings

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

def get_optimal_device() -> str:
    if torch.cuda.is_available(): return "cuda"
    if torch.backends.mps.is_available(): return "mps"
    return "cpu"

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
    model_path = "./finetuned-pandas-coder"
    corpus_path = Path("pandas_dataset.jsonl")
    index_save_path = "pandas_binary.faiss"
    metadata_save_path = "corpus_metadata.json"
    
    # Chunk size for processing to prevent RAM/VRAM exhaustion on massive datasets
    CHUNK_SIZE = 10000 
    
    device = get_optimal_device()
    logger.info(f"Loading finetuned model on [{device.upper()}]...")
    model = SentenceTransformer(model_path, device=device)
    
    logger.info("Loading corpus...")
    corpus = load_corpus(corpus_path)
    corpus_code = [item["code"] for item in corpus]
    
    # Extract dimensions from the model dynamically
    dimension = model.get_sentence_embedding_dimension()
    
    logger.info(f"Initializing FAISS Binary Index (Dimension: {dimension} bits)...")
    # faiss.IndexBinaryFlat requires the number of bits, not bytes.
    index = faiss.IndexBinaryFlat(dimension) 
    
    # Variables for tracking portfolio metrics
    total_float_bytes = 0
    total_binary_bytes = 0

    logger.info(f"Processing {len(corpus_code)} snippets in chunks of {CHUNK_SIZE}...")
    
    # Process in chunks to maintain strict memory safety
    for i in tqdm(range(0, len(corpus_code), CHUNK_SIZE), desc="Indexing Batches"):
        batch_code = corpus_code[i : i + CHUNK_SIZE]
        
        # 1. Generate Float32 Embeddings
        float_embeddings = model.encode(
            batch_code, 
            convert_to_tensor=True, 
            show_progress_bar=False,
            batch_size=32 if device != "cpu" else 16
        )
        
        # Track raw memory footprint
        total_float_bytes += float_embeddings.element_size() * float_embeddings.nelement()
        
        # 2. Binary Quantization (Compress to bits)
        binary_embeddings = quantize_embeddings(float_embeddings, precision="ubinary")
        total_binary_bytes += binary_embeddings.nbytes
        
        # 3. Ensure strict type safety for FAISS C++ backend
        binary_numpy = binary_embeddings.cpu().numpy().astype(np.uint8)
        
        # 4. Add to Index
        index.add(binary_numpy)
        
        # Aggressive memory cleanup
        del float_embeddings
        del binary_embeddings
        del binary_numpy
        if device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()

    # --- PORTFOLIO FLEX: Calculate Final Memory Savings ---
    float_size_mb = total_float_bytes / (1024 * 1024)
    binary_size_mb = total_binary_bytes / (1024 * 1024)
    logger.info("--- METRICS ---")
    logger.info(f"Total Vectors Indexed:    {index.ntotal}")
    logger.info(f"Float32 Memory Footprint: {float_size_mb:.4f} MB")
    logger.info(f"Binary Memory Footprint:  {binary_size_mb:.4f} MB")
    logger.info(f"Compression Ratio:        {float_size_mb / binary_size_mb:.1f}x smaller")
    logger.info("---------------")
    
    # Save the index
    faiss.write_index_binary(index, index_save_path)
    logger.info(f"Binary index safely written to {index_save_path}")
    
    # Save the metadata (Required for Phase 6 retrieval mapping)
    logger.info(f"Exporting metadata mapping to {metadata_save_path}...")
    with open(metadata_save_path, "w", encoding="utf-8") as f:
        # We only save what we need to render the UI to save disk space
        compact_metadata = [
            {"id": i, "function_name": item["function_name"], "code": item["code"]} 
            for i, item in enumerate(corpus)
        ]
        json.dump(compact_metadata, f)
        
    logger.info("Phase 5 Complete. Ready for deployment.")

if __name__ == "__main__":
    main()