# KidSafe Food Analyzer - Quick Start Guide

## Overview

This application uses **LangGraph** for RAG workflow orchestration, **Qdrant** for vector storage, and **RAGAS** for evaluation. It analyzes cereal ingredients using FDA food labeling guidelines to help parents make informed decisions.

## Prerequisites

- Python 3.11+
- API Keys:
  - **OpenAI API Key** (required) - for embeddings and LLM
  - **LangSmith API Key** (required) - for tracing and observability
  - **Cohere API Key** (optional) - for advanced reranking
  - **Tavily API Key** (optional) - for web search

## Installation

1. **Install dependencies:**
   ```bash
   pip install -e .
   # or using uv:
   # uv sync
   ```

2. **Verify the PDF document exists:**
   ```bash
   ls Data/Input/Food-Labeling-Guide-\(PDF\).pdf
   ```

## Running the Application

### Start the Web Server

```bash
python main.py
```

The server will start on `http://localhost:5001`

### Using the Web Interface

1. **Configure API Keys:**
   - Open `http://localhost:5001` in your browser
   - Enter your OpenAI API Key (required)
   - Enter your LangSmith API Key (required)
   - Optionally add Cohere and Tavily keys
   - Click "Initialize System" (this takes ~30 seconds to load and index the PDF)

2. **Analyze a Cereal:**
   - Select a cereal from the dropdown
   - Click "Analyze Ingredients"
   - Wait ~10 seconds for the AI analysis
   - Review the detailed ingredient breakdown

## Offline Evaluation with RAGAS

To evaluate the RAG system using RAGAS metrics:

```bash
cd /path/to/AI-MakerSpace-Certification-Challenge
python -m backend.evaluation
```

This will:
- Load the Food Labeling PDF into Qdrant
- Run 4 test cases through the RAG pipeline
- Evaluate using 5 RAGAS metrics:
  - Faithfulness
  - ResponseRelevancy
  - LLMContextRecall
  - ContextEntityRecall
  - FactualCorrectness
- Display results and average scores

## Architecture

### Backend Components

```
backend/
├── __init__.py
├── config.py           # Configuration and paths
├── vector_store.py     # Qdrant vector store setup
├── rag_engine.py       # LangGraph workflow for RAG
└── evaluation.py       # RAGAS evaluation script
```

### RAG Workflow (LangGraph)

The application uses a **state-based LangGraph workflow**:

1. **State Definition:** `IngredientAnalysisState` tracks:
   - Cereal name and ingredients
   - User question
   - Retrieved context
   - Final analysis

2. **Graph Nodes:**
   - `retrieve`: Fetches relevant FDA guidelines from vector store
   - `analyze`: Generates detailed ingredient analysis using LLM

3. **Workflow:**
   ```
   START → retrieve → analyze → END
   ```

### Retrieval Strategy

- **Current:** Simple naive vector search (k=5)
- **Future:** Can upgrade to Ensemble retriever with:
  - BM25 (sparse keyword search)
  - Multi-query expansion
  - Cohere reranking
  - Parent document retrieval

## API Endpoints

- `GET /` - Main web interface
- `POST /api/configure` - Initialize system with API keys
- `POST /api/analyze` - Analyze cereal ingredients
- `GET /api/status` - Check if system is initialized
- `GET /api/cereals` - Get list of cereals

## Observability

All requests are traced in **LangSmith**:
- Project: `KidSafe-Food-Analyzer`
- View traces at: https://smith.langchain.com/

## Troubleshooting

### Port Already in Use

If you see "Address already in use":
```bash
# Kill the existing process
pkill -f "python3 main.py"

# Or use a different port (edit main.py line 153)
```

### Import Errors

Make sure you're in the correct directory and dependencies are installed:
```bash
cd /path/to/AI-MakerSpace-Certification-Challenge
pip install -e .
```

### PDF Not Found

Ensure the PDF is in the correct location:
```bash
Data/Input/Food-Labeling-Guide-(PDF).pdf
```

## Next Steps

1. **Test the basic functionality** - Analyze a few cereals
2. **Run RAGAS evaluation** - See how well the system performs
3. **Check LangSmith traces** - Understand the RAG workflow
4. **Upgrade to Ensemble retriever** - Improve retrieval quality (future enhancement)

## Development Notes

- Vector store is in-memory (resets on restart) - can be changed to persistent
- Uses `gpt-4o-mini` for cost-effective inference
- Chunk size: 1000 tokens, overlap: 200 tokens
- Retrieves top 5 most relevant chunks per query

## Questions or Issues?

Check the logs in the terminal where you ran `python main.py` for detailed debugging information.

