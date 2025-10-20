# Advanced Retrieval Strategies

The KidSafe Food Analyzer now supports multiple advanced retrieval strategies to improve the accuracy and relevance of ingredient analysis.

## Available Strategies

### 1. **Ensemble (Recommended)** ⭐
Combines multiple retrieval methods using Reciprocal Rank Fusion (RRF) for robust performance.

**Components:**
- Naive Vector Search (semantic similarity)
- BM25 Keyword Search (sparse retrieval)
- Cohere Rerank (if API key provided) - re-scores results for precision

**When to use:**
- Default choice for production
- Best overall accuracy across different query types
- Handles both semantic and keyword-based queries

**Trade-offs:**
- Slightly higher latency (combines multiple strategies)
- Requires Cohere API key for reranking (optional but recommended)

---

### 2. **Naive (Baseline)**
Simple dense vector search using cosine similarity.

**How it works:**
- Embeds query using OpenAI embeddings
- Finds top-k most similar chunks in vector space
- Fast and straightforward

**When to use:**
- Testing and comparison baseline
- When speed is critical
- When query and documents are semantically similar

**Trade-offs:**
- May miss keyword-specific matches
- Performance depends on embedding quality

---

### 3. **BM25 (Keyword-Based)**
Sparse retrieval using Best Matching 25 algorithm.

**How it works:**
- Traditional TF-IDF based ranking
- Excels at exact keyword matches
- No neural embeddings required

**When to use:**
- Queries with specific ingredient names
- When exact terminology matters
- Technical/scientific ingredient terms

**Trade-offs:**
- Doesn't understand semantic similarity
- May miss synonyms or related concepts

---

### 4. **Multi-Query**
LLM-powered query expansion for better recall.

**How it works:**
- Uses GPT-4o-mini to generate multiple query variants
- Retrieves documents for each variant
- Combines and deduplicates results

**When to use:**
- Complex or ambiguous queries
- When you want higher recall
- Exploring different query perspectives

**Trade-offs:**
- Higher latency (extra LLM call)
- Higher cost (additional API calls)
- May retrieve more irrelevant results

---

### 5. **Compression with Cohere Rerank**
Two-stage retrieval with reranking.

**How it works:**
1. Retrieve k documents using naive search
2. Use Cohere's rerank model to re-score
3. Return top-n highest scoring documents

**When to use:**
- When precision is critical
- Have Cohere API key available
- Willing to trade speed for accuracy

**Trade-offs:**
- Requires Cohere API key
- Additional API latency
- Higher cost per query

## Performance Comparison

| Strategy | Latency | Cost | Precision | Recall | Best For |
|----------|---------|------|-----------|--------|----------|
| **Ensemble** | Medium | Medium | High | High | Production (default) |
| **Naive** | Low | Low | Medium | Medium | Baseline/Speed |
| **BM25** | Lowest | Lowest | Medium | Low | Keyword matching |
| **Multi-Query** | High | High | Medium | High | Complex queries |
| **Compression** | High | High | Highest | Medium | Maximum precision |

## How to Use

### Web Interface

1. Go to the API Configuration section
2. Select your preferred retrieval strategy from the dropdown
3. Default is "Ensemble (Recommended)"
4. Click "Initialize System"

### Programmatic Access

```python
from backend.advanced_retrieval import AdvancedRetrievalManager

# Initialize manager
retrieval_manager = AdvancedRetrievalManager(
    vectorstore=vectorstore,
    documents=chunks,
    openai_api_key=openai_key,
    cohere_api_key=cohere_key  # Optional
)

# Get specific retriever
naive_retriever = retrieval_manager.get_naive_retriever(k=5)
bm25_retriever = retrieval_manager.get_bm25_retriever(k=5)
ensemble_retriever = retrieval_manager.get_ensemble_retriever(k=5)

# Compare strategies
results = retrieval_manager.compare_retrievers("Natural flavors in cereal", k=5)
```

## Ensemble Configuration

The ensemble retriever can be customized:

```python
# Equal weights (default)
ensemble = retrieval_manager.get_ensemble_retriever(
    k=5,
    use_compression=True,  # Include Cohere rerank if available
    weights=[0.4, 0.3, 0.3]  # [naive, bm25, compression]
)

# Without compression
ensemble = retrieval_manager.get_ensemble_retriever(
    k=5,
    use_compression=False,
    weights=[0.5, 0.5]  # [naive, bm25]
)
```

## Best Practices

1. **Start with Ensemble**: It's the recommended default for production use

2. **Provide Cohere API Key**: Significantly improves ensemble performance with reranking

3. **Use Naive for Testing**: Good baseline to compare improvements

4. **BM25 for Specific Terms**: When you know exact ingredient names matter

5. **Monitor in LangSmith**: All retrievals are traced - check which strategy performs best

## API Keys Required

| Strategy | OpenAI | LangSmith | Cohere | Tavily |
|----------|--------|-----------|--------|--------|
| Naive | ✅ | ✅ | ❌ | ❌ |
| BM25 | ✅ | ✅ | ❌ | ❌ |
| Multi-Query | ✅ | ✅ | ❌ | ❌ |
| Compression | ✅ | ✅ | ✅ | ❌ |
| Ensemble (basic) | ✅ | ✅ | ❌ | ❌ |
| Ensemble (full) | ✅ | ✅ | ✅ | ❌ |

**Note:** Tavily is reserved for future web search integration.

## Troubleshooting

**"Compression retriever unavailable"**
- Provide a Cohere API key in the configuration
- System will fall back to naive retrieval

**Slow performance with Multi-Query**
- Expected - generates multiple query variants
- Consider using Ensemble instead

**No results from BM25**
- BM25 requires exact keyword matches
- Try Naive or Ensemble for semantic understanding

## Future Enhancements

- [ ] Parent Document Retriever (small-to-big)
- [ ] Semantic Chunker with percentile boundaries
- [ ] Custom weighted ensemble configurations
- [ ] A/B testing framework
- [ ] Persistent retrieval performance metrics

## References

- LangChain Retrievers: https://python.langchain.com/docs/modules/data_connection/retrievers/
- Cohere Rerank: https://docs.cohere.com/docs/reranking
- BM25 Algorithm: https://en.wikipedia.org/wiki/Okapi_BM25
- Session 09 Reference Code: `aie8-s09-adv-retrieval-main/`

