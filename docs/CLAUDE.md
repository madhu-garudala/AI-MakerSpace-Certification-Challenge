# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a certification challenge project for AI Engineering Bootcamp Cohort 8 - **KidSafe Food Analyzer**.

**Project Vision**: An AI-powered web application that helps parents assess the safety of store-bought food products for children by analyzing ingredient lists and providing percentage-based safety scores with detailed explanations.

**Core Problem**: Parents struggle to quickly evaluate whether food products are safe for their children, unable to identify harmful ingredients, allergens, or concerning additives while shopping.

**Solution Approach**: Agentic RAG system with multi-agent architecture that analyzes ingredients across multiple safety dimensions (allergens, additives, nutrition, physical safety) using evidence-based guidelines from FDA, USDA, and AAP.

**Target Audience**: All parents and caregivers seeking to make informed food purchasing decisions for children of any age.

This project uses `uv` for dependency management and will implement a production-grade AI application using LangGraph for orchestration, Qdrant for vector storage, and Streamlit for the user interface.

## Python Environment

- **Python Version**: 3.11 (specified in `.python-version`)
- **Package Manager**: `uv` for dependency management
- **Dependencies**: Managed via `pyproject.toml`

### Setup

```bash
# Create and activate virtual environment
uv venv --python 3.11
source .venv/bin/activate  # Linux/WSL/Mac
# Or on Windows:
# .venv\Scripts\activate

# Install dependencies (as they are added)
uv pip install -e .
```

### Key Dependencies (To Be Added)

- **LLM & Embeddings**: `openai` for GPT-4o and text-embedding-3-large
- **Orchestration**: `langgraph`, `langchain`, `langchain-community`
- **Vector Database**: `qdrant-client` for semantic search
- **Monitoring**: `langsmith` for tracing and debugging
- **Evaluation**: `ragas` for RAG evaluation metrics
- **Web Interface**: `streamlit` for interactive UI
- **Data Processing**: `pypdf`, `beautifulsoup4` for document parsing
- **Search API**: `tavily-python` for real-time search

### Running the Application

```bash
# Run the Streamlit web interface
streamlit run main.py

# Or for backend testing
python main.py
```

## Project Structure

```
certification-challenge-template/
├── main.py                              # Streamlit web application entry point
├── pyproject.toml                       # Python dependencies and project config
├── .python-version                      # Python 3.11 specification
├── README.md                            # Project overview and documentation
├── CLAUDE.md                            # This file - development guidance
├── docs/
│   ├── certification-challenge.md       # Original challenge requirements
│   ├── certification-challenge-plan.md  # Complete deliverables (Tasks 1-7)
│   └── architecture.md                  # Technical architecture decisions
├── src/                                 # Application source code (to be created)
│   ├── agents/                          # Multi-agent system implementation
│   │   ├── supervisor.py                # Supervisor agent coordinator
│   │   ├── allergen_agent.py            # Allergen detection specialist
│   │   ├── additive_agent.py            # Additive & preservative analyst
│   │   ├── nutrition_agent.py           # Nutritional evaluation specialist
│   │   └── safety_agent.py              # Physical safety assessor
│   ├── rag/                             # RAG pipeline components
│   │   ├── vector_store.py              # Qdrant vector database interface
│   │   ├── retrieval.py                 # Advanced retrieval techniques
│   │   ├── chunking.py                  # Hierarchical chunking strategy
│   │   └── embeddings.py                # Embedding generation
│   ├── scoring/                         # Scoring logic
│   │   ├── rubric.py                    # Scoring rubric loader
│   │   ├── calculator.py                # Score calculation and weighting
│   │   └── config/                      # Scoring configuration files
│   │       └── scoring_rubric.json      # Ingredient scoring rules
│   ├── data/                            # Data ingestion and processing
│   │   ├── ingest.py                    # Document download and processing
│   │   ├── parsers.py                   # PDF and web content parsers
│   │   └── sources.py                   # Data source definitions
│   ├── ui/                              # User interface components
│   │   ├── app.py                       # Main Streamlit app
│   │   └── components.py                # Reusable UI components
│   └── utils/                           # Utility functions
│       ├── config.py                    # Configuration management
│       └── logging.py                   # Logging setup
├── data/                                # RAG knowledge base (gitignored)
│   ├── raw/                             # Downloaded PDF/documents
│   ├── processed/                       # Chunked and processed data
│   └── vector_db/                       # Qdrant database files
├── tests/                               # Test suite
│   ├── test_agents.py                   # Agent unit tests
│   ├── test_rag.py                      # RAG pipeline tests
│   ├── test_scoring.py                  # Scoring logic tests
│   └── golden_dataset/                  # Golden test dataset for RAGAS
│       ├── test_cases.json              # 50 test ingredient lists
│       └── expected_outputs.json        # Ground truth scores
└── notebooks/                           # Jupyter notebooks for exploration
    ├── 01_data_exploration.ipynb        # FDA/USDA document analysis
    ├── 02_embedding_experiments.ipynb   # Embedding model comparison
    ├── 03_retrieval_evaluation.ipynb    # Retrieval technique testing
    └── 04_ragas_evaluation.ipynb        # RAGAS metrics analysis
```

**Key Files:**
- `main.py` — Streamlit web application entry point
- `docs/certification-challenge-plan.md` — Complete certification deliverables document
- `src/agents/` — Multi-agent system for ingredient analysis
- `src/rag/` — Advanced RAG implementation
- `tests/golden_dataset/` — Evaluation test cases

## Development Workflow

This project uses the same git workflow as the parent AIE8 repository:
- Work on feature/assignment branches
- Do not commit directly to main
- Follow standard Python .gitignore patterns (already configured)

### Implementation Phases

**Phase 1: Planning & Documentation** (Current - Certification Challenge Tasks 1-3)
- ✅ Problem definition and audience identification
- ✅ Solution architecture and technology stack selection
- ✅ Data source identification and chunking strategy
- 📝 Complete documentation in `docs/certification-challenge-plan.md`

**Phase 2: MVP Development** (Certification Challenge Tasks 4-5)
- Data ingestion pipeline for FDA/USDA/AAP documents
- Qdrant vector database setup and document embedding
- Multi-agent system implementation (Supervisor + 4 specialists)
- Basic RAG retrieval with semantic search
- Streamlit web interface
- Golden test dataset creation (50 test cases)
- Baseline RAGAS evaluation

**Phase 3: Advanced Retrieval** (Certification Challenge Tasks 6-7)
- Hybrid search (semantic + keyword)
- Metadata filtering by document type
- Cross-encoder re-ranking
- Parent document retrieval
- Query decomposition
- HyDE (Hypothetical Document Embeddings)
- Comparative RAGAS evaluation (naive vs. advanced)
- Performance analysis and improvement documentation

**Phase 4: Iteration & Enhancement** (Post-Certification → Demo Day)
- User feedback integration
- Fine-tuned embedding model for ingredient domain
- Alternative product recommendations
- Explainability improvements (citations, confidence scores)
- Mobile app prototype (React Native)
- OCR integration for ingredient label scanning
- Offline mode capability

### Testing Strategy

1. **Unit Tests**: Individual agent functions, scoring logic, retrieval components
2. **Integration Tests**: End-to-end ingredient analysis flow
3. **RAGAS Evaluation**: Systematic evaluation on 50-case golden dataset
4. **User Testing**: Real parent feedback on accuracy and usefulness

### Environment Variables

Create a `.env` file with:
```bash
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
TAVILY_API_KEY=your_tavily_api_key
QDRANT_URL=http://localhost:6333  # or cloud URL
```

### Qdrant Setup

```bash
# Run Qdrant locally with Docker
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/data/vector_db:/qdrant/storage \
    qdrant/qdrant
```

## Domain-Specific Guidance

### Ingredient Analysis Logic

When implementing the scoring system, follow these principles:

1. **Safety First**: Allergens and harmful additives should have highest weight
2. **Evidence-Based**: All scoring decisions must reference FDA/USDA/AAP guidelines
3. **Transparency**: Every score must have explainable reasoning
4. **Consistency**: Same ingredient should score same across different products
5. **No Hallucinations**: Only make claims supported by retrieved documents

### Multi-Agent Coordination

The Supervisor Agent orchestrates specialist agents in this order:
1. **Allergen Agent** (parallel) - checks for major allergens
2. **Additive Agent** (parallel) - evaluates artificial ingredients
3. **Nutrition Agent** (parallel) - assesses nutritional content
4. **Safety Agent** (parallel) - checks physical safety concerns
5. **Supervisor synthesizes** - combines scores with weighted formula

Agents run in parallel for efficiency but maintain independent assessments.

### RAG Best Practices for This Domain

- **Chunk size**: 500-800 tokens (regulatory documents need context)
- **Overlap**: 100 tokens (avoid splitting guidelines mid-sentence)
- **Metadata**: Always tag with document_type, source_authority, date
- **Filtering**: Agent queries should filter by relevant document type
- **Citations**: Track source documents for every claim made
- **Freshness**: Flag guidelines older than 2 years for manual review

### Scoring Rubric Design

The `scoring_rubric.json` should define:
- Ingredient safety classifications (safe/moderate/concerning/dangerous)
- Severity scores (0-100 scale)
- Evidence references (FDA regulation numbers, AAP guideline sections)
- Age-specific modifiers (if implemented in future)

Example structure:
```json
{
  "allergens": {
    "major": ["peanuts", "tree nuts", "milk", "eggs", "fish", "shellfish", "soy", "wheat"],
    "severity": {
      "peanuts": {"score": 0, "reason": "Life-threatening allergy risk"},
      "milk": {"score": 20, "reason": "Common allergen, digestive issues"}
    }
  },
  "additives": {
    "red_40": {
      "score": 35,
      "reason": "Linked to hyperactivity in sensitive children",
      "source": "FDA Food Dye Studies 2023"
    }
  }
}
```

## Key Technical Decisions

1. **Why LangGraph over LangChain alone?** 
   - Need stateful multi-agent coordination with complex routing logic
   - Better observability for agent decision paths

2. **Why Qdrant over Pinecone/Weaviate?**
   - Strong hybrid search support (semantic + keyword)
   - Easy local development, smooth cloud migration
   - Excellent metadata filtering performance

3. **Why text-embedding-3-large over smaller models?**
   - Technical domain (chemistry, nutrition) benefits from larger context
   - Better performance on specialized terminology

4. **Why Streamlit over FastAPI + React?**
   - Faster MVP development for certification challenge
   - Built-in components for data visualization
   - Easy deployment (Streamlit Cloud)
   - (Future: Migrate to React Native for mobile)

## Evaluation Metrics Targets

Based on RAGAS framework:

| Metric | Target | Reasoning |
|--------|--------|-----------|
| **Faithfulness** | ≥ 0.90 | Health/safety domain requires high accuracy |
| **Answer Relevancy** | ≥ 0.85 | Responses must directly address safety concerns |
| **Context Precision** | ≥ 0.80 | Retrieve only relevant guidelines |
| **Context Recall** | ≥ 0.75 | Don't miss important safety information |

**Critical Success Metric**: 100% recall on major allergen detection (life-threatening risk)

## Demo Day Vision

**5-Minute Demo Flow:**
1. Show problem (parent in grocery store, confused by label)
2. Live demo: Type ingredient list → instant safety score
3. Walk through detailed breakdown (allergens, additives, nutrition)
4. Show comparison: naive vs. advanced RAG performance
5. Mobile prototype: Scan ingredient label with phone camera
6. Impact: Testimonials from parent beta testers
7. Vision: Future roadmap (personalization, offline mode, partnerships)

**Wow Factor**: Real-time ingredient label scanning with instant analysis
