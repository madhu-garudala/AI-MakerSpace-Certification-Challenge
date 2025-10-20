# RAGAS Evaluation Guide

## Overview

This guide explains how to evaluate the KidSafe Food Analyzer RAG pipeline using the RAGAS framework with a golden test dataset.

## What is Evaluated

### RAGAS Metrics

1. **Faithfulness** (0-1 scale)
   - Measures if the response is grounded in the retrieved context
   - Detects hallucinations and unsupported claims
   - Higher is better (>0.8 is excellent)

2. **Response Relevancy** (0-1 scale)
   - Measures how well the response addresses the user's question
   - Checks for irrelevant or tangential information
   - Higher is better (>0.8 is excellent)

3. **Context Precision** (0-1 scale)
   - Measures if relevant contexts are ranked higher than irrelevant ones
   - Evaluates retrieval quality
   - Higher is better (>0.8 is excellent)

4. **Context Recall** (0-1 scale)
   - Measures if all facts from the reference answer were retrieved
   - Checks retrieval completeness
   - Higher is better (>0.8 is excellent)

## Golden Test Dataset

The evaluation uses **7 carefully crafted test cases**:

| Test Case | Type | Expected Verdict | Key Aspects |
|-----------|------|------------------|-------------|
| **Holy Crap Organic Cereal** | Simple, Clean | GOOD | Only 3 organic ingredients, no additives |
| **Post Honey Bunch Oats with BHT** | Multiple Concerns | BAD | BHT, corn syrup, caramel color |
| **Seven Sundays Cereal** | Mostly Good | GOOD | Whole grains, minimal processing |
| **Generic Cereal with Natural Flavors** | Ambiguous Ingredient | NEUTRAL/CONCERNING | Tests "natural flavors" understanding |
| **Earth's Best Oatmeal Cereal** | Technical Terms | GOOD | Tests enzyme/fortification knowledge |
| **Processed Cereal with Multiple Additives** | Worst Case | BAD | Multiple artificial additives, preservatives |
| **RX Cereal** | Mixed Ingredients | MOSTLY GOOD | Natural flavors concern in otherwise good cereal |

### Why These Test Cases?

- **Coverage**: Range from very good to very bad products
- **Complexity**: Simple to complex ingredient lists
- **Edge Cases**: Ambiguous terms like "natural flavors"
- **Technical Knowledge**: Enzymes, fortification, preservatives
- **Real-World**: Based on actual cereals from our dataset

## How to Run

### 1. Prerequisites

```bash
cd /path/to/AI-MakerSpace-Certification-Challenge
pip install -e .  # Ensure all dependencies installed
```

### 2. Run Evaluation

```bash
python -m backend.ragas_evaluation
```

### 3. Provide API Keys

When prompted, enter:
- **OpenAI API Key** (required)
- **LangSmith API Key** (required)
- **Cohere API Key** (optional but recommended)

### 4. Select Retrieval Strategy

Choose from:
1. **Ensemble** (recommended) - Combines naive + BM25 + reranking
2. **Naive** - Simple vector search baseline
3. **BM25** - Keyword-based search

### 5. Wait for Results

The evaluation will:
- Load and index the FDA Food Labeling Guide PDF (~30 seconds)
- Run analysis on 7 test cases (~2-3 minutes)
- Evaluate with RAGAS metrics (~2-3 minutes)
- Display detailed results

**Total time: ~5-7 minutes**

## Output

### Console Output

The script provides:

1. **Individual Test Case Scores**
   ```
   Test Case                               | Faithfulness | Response Relevancy | Context Precision | Context Recall
   Holy Crap Organic Cereal               | 0.9234      | 0.8876            | 0.9123           | 0.8654
   Post Honey Bunch Oats with BHT         | 0.8901      | 0.9234            | 0.8567           | 0.8923
   ...
   ```

2. **Average Scores**
   ```
   faithfulness................................ 0.8945
   response_relevancy.......................... 0.8756
   context_precision........................... 0.8634
   context_recall.............................. 0.8523
   ```

3. **Performance Analysis**
   - Metric interpretation (Excellent/Good/Needs Improvement)
   - Overall pipeline assessment
   - Strategy-specific insights
   - Recommendations for improvement

### CSV Output

Results saved to: `ragas_evaluation_results_{strategy}.csv`

Contains:
- Test case names
- Expected verdicts
- All metric scores
- Full responses and contexts

## Interpreting Results

### Score Ranges

| Score | Rating | Interpretation |
|-------|--------|----------------|
| **0.8 - 1.0** | ✅ Excellent | Production-ready performance |
| **0.6 - 0.8** | ⚠️ Good | Acceptable but improvable |
| **0.0 - 0.6** | ❌ Needs Work | Requires optimization |

### What Good Results Look Like

**High Faithfulness (>0.8)**
- ✅ Responses stick to FDA guidelines
- ✅ No made-up ingredient claims
- ✅ All statements backed by retrieved context

**High Response Relevancy (>0.8)**
- ✅ Directly answers user questions
- ✅ Stays on topic
- ✅ Provides actionable information

**High Context Precision (>0.8)**
- ✅ Most relevant chunks ranked first
- ✅ Retrieval strategy working well
- ✅ Less noise in retrieved contexts

**High Context Recall (>0.8)**
- ✅ All key facts retrieved
- ✅ No missing critical information
- ✅ Comprehensive coverage

## Example Analysis

### Scenario: Ensemble Strategy Results

```
OVERALL AVERAGE SCORES
-----------------------------------------
faithfulness................................ 0.8945
response_relevancy.......................... 0.8756
context_precision........................... 0.8634
context_recall.............................. 0.8523

Overall Pipeline Score: 0.8715
```

**Interpretation:**

✅ **EXCELLENT PERFORMANCE** (0.87 overall)

1. **Faithfulness (0.89)** - Excellent
   - Responses are highly accurate and grounded in FDA guidelines
   - Minimal hallucination
   - Reliable for parents

2. **Response Relevancy (0.88)** - Excellent
   - Directly addresses parent concerns
   - Focused on child safety
   - Good structure with verdict upfront

3. **Context Precision (0.86)** - Excellent
   - Ensemble retriever effectively ranks relevant chunks
   - BM25 + semantic search working well together
   - Reranking improving quality

4. **Context Recall (0.85)** - Excellent
   - Most ground truth facts retrieved
   - Comprehensive FDA guideline coverage
   - Good chunk size (1000 tokens)

**Conclusions:**
- Pipeline is production-ready
- Ensemble strategy recommended for deployment
- Strong performance across all test cases
- Handles both simple and complex ingredient lists well

## Comparing Strategies

Run multiple evaluations to compare:

```bash
# Run with ensemble
python -m backend.ragas_evaluation
# Select: 1 (ensemble)

# Run with naive
python -m backend.ragas_evaluation
# Select: 2 (naive)

# Compare CSV files
ragas_evaluation_results_ensemble.csv
ragas_evaluation_results_naive.csv
```

Expected differences:
- **Ensemble**: Higher context precision (better ranking)
- **Naive**: Slightly lower precision but faster
- **BM25**: Better on exact terms, worse on concepts

## Troubleshooting

### "Module not found" errors
```bash
pip install -e .
```

### Slow evaluation
- Normal for first run (embeddings generation)
- Subsequent runs faster (cached)
- Use naive strategy for quick tests

### Low scores
- Check if PDF loaded correctly
- Verify API keys are valid
- Try different retrieval strategy
- Review LangSmith traces for details

### API rate limits
- RAGAS makes multiple LLM calls
- Consider using GPT-3.5-turbo for evaluation (faster/cheaper)
- Add delays between requests if needed

## LangSmith Tracing

All evaluations are traced in LangSmith:
- Project: `KidSafe-RAGAS-Evaluation`
- View URL: https://smith.langchain.com/

Traces show:
- Each retrieval step
- Retrieved contexts
- LLM responses
- Evaluation judgments

## Next Steps

After evaluation:

1. **Analyze Results**
   - Review individual test case failures
   - Identify patterns in low scores
   - Check LangSmith for detailed traces

2. **Iterate on Prompts**
   - Adjust if faithfulness is low
   - Refine if relevancy needs work
   - Test with new evaluation run

3. **Optimize Retrieval**
   - Try different strategies
   - Adjust k parameter
   - Experiment with chunk sizes

4. **Expand Test Dataset**
   - Add more edge cases
   - Include user-reported issues
   - Test with production queries

## References

- RAGAS Documentation: https://docs.ragas.io/
- LangSmith: https://smith.langchain.com/
- Evaluation Metrics Paper: https://arxiv.org/abs/2309.15217

