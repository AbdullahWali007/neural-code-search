import streamlit as st
import faiss
import json
import numpy as np
import torch
import time
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.util.quantization import quantize_embeddings

# --- 1. PREMIUM UI CONFIGURATION ---
st.set_page_config(page_title="Neural Code Search", page_icon="🔍", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    
    /* Glassmorphism Search Results Cards */
    .search-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        margin-bottom: 0px; /* Streamlit code block handles bottom margin */
        transition: all 0.3s ease;
    }
    .search-card:hover {
        border: 1px solid rgba(88, 166, 255, 0.4);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    }
    
    .func-name {
        color: #58A6FF;
        font-family: 'SF Mono', Consolas, monospace;
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-badge {
        background: rgba(88, 166, 255, 0.15);
        color: #58A6FF;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CACHED ENGINE LOADING ---
@st.cache_resource(show_spinner=False)
def load_search_engine():
    model_path = Path("./finetuned-pandas-coder")
    index_path = Path("pandas_binary.faiss")
    meta_path = Path("corpus_metadata.json")

    # Error Boundaries: Ensure user ran earlier phases
    if not model_path.exists() or not index_path.exists() or not meta_path.exists():
        return None, None, None

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    
    model = SentenceTransformer(str(model_path), device=device)
    index = faiss.read_index_binary(str(index_path))
    
    with meta_path.open("r", encoding="utf-8") as f:
        metadata = json.load(f)
        
    return model, index, metadata

# --- 3. CORE APP LOGIC ---
def main():
    st.title("🔍 Neural Code Search")
    st.markdown("Semantic search powered by **Multiple Negatives Ranking Loss (MNRL)** embeddings and a highly compressed **FAISS Binary Index**.")

    with st.spinner("Initializing ML Engine..."):
        model, index, metadata = load_search_engine()

    if not model or not index or not metadata:
        st.error("🚨 Missing critical engine files! Please ensure you have completed Phase 4 (Training) and Phase 5 (Indexing).")
        st.stop()

    # Search Bar
    query = st.text_input("Describe what you want the code to do...", placeholder="e.g., drop rows with missing values")

    if query:
        start_time = time.time()
        
        # 1. Embed the query (Standard Float32)
        query_embedding = model.encode(query, convert_to_tensor=True)
        
        # 2. STAGE 1: Broad Sweep with Binary Search (Ultra-fast Hamming distance)
        binary_query = quantize_embeddings(query_embedding.unsqueeze(0), precision="ubinary")
        binary_query_np = np.asarray(binary_query, dtype=np.uint8)
        
        # Retrieve top 20 candidates
        _, binary_indices = index.search(binary_query_np, k=20)
        candidate_indices = [int(idx) for idx in binary_indices[0] if idx != -1]
        
        # 3. STAGE 2: The Re-ranker (High Precision Cosine Similarity)
        # Fetch the actual code for the top 20 candidates
        candidate_snippets = [metadata[idx]["code"] for idx in candidate_indices]
        
        # Dynamically re-embed the Top 20 snippets in float32 (Takes ~10-20ms)
        candidate_embeddings = model.encode(candidate_snippets, convert_to_tensor=True)
        
        # Calculate exact Cosine Similarity between original query and candidate snippets
        cos_scores = util.cos_sim(query_embedding, candidate_embeddings)[0]
        
        # Sort by best float32 scores
        top_results = torch.topk(cos_scores, k=5)
        
        search_time = (time.time() - start_time) * 1000 
        
        st.caption(f"⚡ Searched {index.ntotal} vectors using 2-Stage BQ-Rerank in **{search_time:.1f}ms**")
        
        # 4. Render Results
        for score, rank_idx in zip(top_results[0], top_results[1]):
            # Map the local rank_idx back to the global corpus metadata index
            global_idx = candidate_indices[rank_idx]
            result_meta = metadata[global_idx]
            sim_percentage = float(score) * 100
            
            st.markdown(f"""
            <div class="search-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div class="func-name">{result_meta['function_name']}</div>
                    <div class="metric-badge">{sim_percentage:.1f}% Match</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Streamlit's code block perfectly attaches below the card
            st.code(result_meta['code'], language='python')

if __name__ == "__main__":
    main()