## About the Project

This repository contains a production-grade Neural Code Search Engine engineered to solve the problem of mapping natural language developer intent directly to source code blocks (specifically targeting the pandas ecosystem). While traditional search relies on keyword matching, this system leverages dense vector embeddings to understand the true semantic behavior of code structures.

The core philosophy of this project is to achieve enterprise-level scaling without the associated infrastructure costs. By combining contrastive machine learning techniques with aggressive vector compression, the entire engine runs with single-digit millisecond latency while maintaining a near-zero memory footprint.

### Core Architectural Pipeline

1. **Context-Aware AST Extraction:** A custom Abstract Syntax Tree (AST) visitor traverses Python repositories, tracking class-level hierarchies to extract code-docstring pairs while automatically preserving method scopes (e.g., parsing methods as ClassName.method_name).
2. **Contrastive Triplet Mining:** To force the model to learn subtle semantic differences, hard negatives are mined dynamically via BM25 lexical overlap. This prevents the model from falling into "false negative traps" (such as matching identical docstrings or method aliases).
3. **Contrastive Fine-Tuning:** An all-MiniLM-L6-v2 transformer is fine-tuned using Multiple Negatives Ranking Loss (MNRL) and tracked via a dynamic validation TripletEvaluator, teaching the model to distinguish correct code behaviors from structural lookalikes.
4. **32x Binary Quantization (BQ):** High-dimensional float32 embeddings are compressed down to raw binary vectors (1s and 0s). This shrinks the vector database footprint by 97%—collapsing the storage of thousands of code arrays down to just 106 KB.
5. **2-Stage Hybrid Retrieval & Reranking:** * **Stage 1:** A FAISS binary index performs an ultra-fast search using bitwise Hamming distance to instantly filter down millions of vectors to a small candidate pool (k=20).
   * **Stage 2:** The top candidates are dynamically re-embedded on-the-fly to calculate exact float32 Cosine Similarity, delivering maximum mathematical precision without requiring massive permanent RAM consumption.

# Neural Code Search Engine

A high-performance semantic code search engine that maps natural language queries to functional Python snippets. Powered by a custom fine-tuned bi-encoder, optimized with 32x Binary Quantization, and executed through a lightning-fast 2-Stage retrieval and reranking pipeline.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-EE4C2C)
![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B)

## About the Project

This repository contains a production-grade Neural Code Search Engine engineered to map natural language developer intent directly to source code blocks (specifically targeting the pandas ecosystem). 

The core philosophy of this project is to achieve enterprise-level scaling without massive infrastructure costs. By combining contrastive machine learning with aggressive vector compression, the engine runs with single-digit millisecond latency while maintaining a near-zero memory footprint.

### Core Architectural Pipeline

1. **Context-Aware AST Extraction:** A custom Abstract Syntax Tree (AST) visitor traverses Python repositories, extracting code-docstring pairs while preserving class-level method scopes.
2. **Contrastive Triplet Mining:** Hard negatives are mined dynamically via BM25 lexical overlap to prevent the model from falling into "false negative traps" (like matching method aliases).
3. **Contrastive Fine-Tuning:** An all-MiniLM-L6-v2 transformer is fine-tuned using Multiple Negatives Ranking Loss (MNRL), teaching the model to distinguish correct code behaviors from structural lookalikes.
4. **32x Binary Quantization (BQ):** High-dimensional float32 embeddings are compressed to raw binary vectors. This shrinks the vector database footprint by 97%—collapsing thousands of code arrays down to just 106 KB.
5. **2-Stage Hybrid Retrieval & Reranking:** * **Stage 1 (Speed):** A FAISS binary index performs an ultra-fast bitwise Hamming distance search to filter down to a small candidate pool.
   * **Stage 2 (Precision):** Top candidates are dynamically re-embedded on-the-fly to calculate exact float32 Cosine Similarity, delivering maximum mathematical precision without massive permanent RAM consumption.

## Performance & Optimization Gains

| Metric | Baseline Model | Fine-Tuned Engine + 2-Stage BQ | Change |
| :--- | :--- | :--- | :--- |
| **Query Accuracy** | Pulls structural lookalikes (e.g., `from_dict` instead of `to_dict`) | Nailed exact operations (`DataFrame.to_dict`) | **Semantic Realignment** |
| **Vector DB Size** | ~3.5 MB (Float32) | **106.25 KB** (Binary) | **32x Compression** |
| **Search Latency** | ~15ms | **< 5ms** (FAISS Hamming + Rerank) | **3x Faster** |

## Installation & Local Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbdullahWali007/neural-code-search.git
   cd neural-code-search


2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```


4. **Run the Streamlit Dashboard:**
```bash
streamlit run app.py
```


*The custom glassmorphism UI will automatically launch in your browser at http://localhost:8501.*

## Repository Structure

* `extract_codebase.py` - AST parser for building the raw dataset.
* `mine_hard_negatives.py` - BM25 lexical mining for contrastive triplets.
* `train_model.py` - MNRL fine-tuning loop with dynamic validation.
* `build_vector_db.py` - BQ compression and FAISS index generation.
* `app.py` - 2-Stage retrieval pipeline and Streamlit frontend.
* `cli_search.py` - Headless terminal testing interface.
