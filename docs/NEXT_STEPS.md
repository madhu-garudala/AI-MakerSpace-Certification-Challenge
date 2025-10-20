# Next Steps: Implementation Roadmap

This document outlines the implementation plan for **KidSafe Food Analyzer** now that planning and documentation are complete.

---

## ✅ Completed: Planning Phase

- [x] Problem definition and audience identification
- [x] Solution architecture design
- [x] Technology stack selection
- [x] Data source identification
- [x] Scoring algorithm design
- [x] Complete certification challenge documentation (Tasks 1-3)

---

## 🚀 Phase 2: MVP Development (Tasks 4-5)

**Goal**: Build a working end-to-end prototype with basic RAG and evaluation

### Step 1: Environment Setup

```bash
# Create virtual environment
cd /Users/madhugarudala/Desktop/AI_MakerSpace/Code/certification-challenge-template
uv venv --python 3.11
source .venv/bin/activate

# Install core dependencies
uv pip install openai langchain langgraph langchain-community
uv pip install qdrant-client streamlit
uv pip install pypdf beautifulsoup4 requests
uv pip install python-dotenv

# Install evaluation tools
uv pip install ragas datasets

# Install monitoring
uv pip install langsmith
```

### Step 2: Configure API Keys

Create `.env` file:
```bash
OPENAI_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
QDRANT_URL=http://localhost:6333
```

### Step 3: Start Qdrant

```bash
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/data/vector_db:/qdrant/storage \
    qdrant/qdrant
```

### Step 4: Data Ingestion Pipeline

**Priority Documents to Download:**

1. **FDA Food Labeling Guide** (200 pages)
   - URL: https://www.fda.gov/food/guidance-regulation-food-and-dietary-supplements/food-labeling-nutrition
   
2. **FDA Food Additives Status List** (50 pages)
   - URL: https://www.fda.gov/food/food-additives-petitions/food-additive-status-list
   
3. **USDA Dietary Guidelines** (150 pages)
   - URL: https://www.dietaryguidelines.gov/sites/default/files/2021-03/Dietary_Guidelines_for_Americans-2020-2025.pdf
   
4. **AAP Nutrition Resources** (web scraping)
   - URL: https://www.healthychildren.org/English/healthy-living/nutrition/

**Implementation Tasks:**

- [ ] Create `src/data/sources.py` - define data sources
- [ ] Create `src/data/ingest.py` - download and extract PDFs
- [ ] Create `src/data/parsers.py` - parse PDF text
- [ ] Create `src/rag/chunking.py` - implement hierarchical chunking
- [ ] Create `src/rag/embeddings.py` - generate embeddings
- [ ] Create `src/rag/vector_store.py` - load into Qdrant
- [ ] Run ingestion pipeline and verify ~1,500 chunks loaded

**Estimated Time**: 1-2 days

### Step 5: Build RAG Retrieval System

**Implementation Tasks:**

- [ ] Create `src/rag/retrieval.py` - basic semantic search
- [ ] Implement metadata filtering by document type
- [ ] Test retrieval with sample queries:
  - "What are the major food allergens?"
  - "Is Red 40 safe for children?"
  - "How much sugar should children consume daily?"
- [ ] Verify retrieval returns relevant chunks

**Estimated Time**: 1 day

### Step 6: Multi-Agent System

**Implementation Tasks:**

- [ ] Create `src/agents/supervisor.py` - Supervisor Agent with LangGraph
- [ ] Create `src/agents/allergen_agent.py` - Allergen detection
- [ ] Create `src/agents/additive_agent.py` - Additive analysis
- [ ] Create `src/agents/nutrition_agent.py` - Nutritional evaluation
- [ ] Create `src/agents/safety_agent.py` - Physical safety assessment
- [ ] Implement state management (input → parsing → routing → agents → aggregation)
- [ ] Test each agent individually with sample ingredients

**Estimated Time**: 2-3 days

### Step 7: Scoring System

**Implementation Tasks:**

- [ ] Create `src/scoring/config/scoring_rubric.json` - scoring rules (use example provided)
- [ ] Create `src/scoring/rubric.py` - load and query rubric
- [ ] Create `src/scoring/calculator.py` - weighted score calculation
- [ ] Test scoring logic with known ingredients
- [ ] Verify final scores match expected ranges

**Estimated Time**: 1 day

### Step 8: Streamlit UI

**Implementation Tasks:**

- [ ] Create `src/ui/app.py` - main Streamlit application
- [ ] Create `src/ui/components.py` - reusable UI components
- [ ] Implement input panel (text area for ingredients)
- [ ] Implement score display (large percentage with color)
- [ ] Implement category breakdown tabs
- [ ] Implement detailed ingredient explanations
- [ ] Add citations and source links
- [ ] Test end-to-end flow

**Estimated Time**: 2 days

### Step 9: Golden Test Dataset

**Implementation Tasks:**

- [ ] Create `tests/golden_dataset/test_cases.json` - 50 test cases
  - 10 allergen products (peanut butter, milk, etc.)
  - 10 high sugar products (candy, cereal)
  - 10 artificial additive products (colored snacks)
  - 10 clean products (organic, minimal processing)
  - 10 mixed concern products (complex cases)
- [ ] For each test case, manually determine expected score
- [ ] Document reasoning for expected scores
- [ ] Create `tests/golden_dataset/expected_outputs.json`

**Estimated Time**: 1-2 days

### Step 10: Baseline Evaluation (RAGAS)

**Implementation Tasks:**

- [ ] Create `notebooks/04_ragas_evaluation.ipynb`
- [ ] Run all 50 test cases through naive RAG system
- [ ] Measure RAGAS metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Precision
  - Context Recall
- [ ] Create results table in `docs/certification-challenge-plan.md`
- [ ] Document findings and identified weaknesses

**Estimated Time**: 1 day

**Total Phase 2 Estimate**: 10-14 days

---

## 🔬 Phase 3: Advanced Retrieval (Tasks 6-7)

**Goal**: Implement advanced techniques and demonstrate improvement

### Step 1: Hybrid Search

- [ ] Modify `src/rag/retrieval.py` to support hybrid search
- [ ] Configure Qdrant for keyword (BM25) search
- [ ] Implement weighted combination (0.6 semantic + 0.4 keyword)
- [ ] Test on allergen/additive names (exact matching)

### Step 2: Query Decomposition

- [ ] Use LLM to break complex queries into atomic questions
- [ ] Implement parallel retrieval for sub-queries
- [ ] Aggregate results

### Step 3: Cross-Encoder Re-ranking

- [ ] Install sentence-transformers
- [ ] Load `cross-encoder/ms-marco-MiniLM-L-12-v2`
- [ ] Re-rank top-20 results to get best top-5
- [ ] Measure latency impact

### Step 4: Parent Document Retrieval

- [ ] Store parent section IDs in chunk metadata
- [ ] Fetch parent sections for retrieved chunks
- [ ] Provide both chunk + parent to LLM

### Step 5: HyDE (Optional)

- [ ] Generate hypothetical answers for queries
- [ ] Embed hypothetical answers
- [ ] Use for semantic search

### Step 6: Comparative Evaluation

- [ ] Run RAGAS evaluation on advanced RAG system
- [ ] Compare metrics to naive baseline
- [ ] Create comparison table in documentation
- [ ] Analyze performance by category

**Total Phase 3 Estimate**: 5-7 days

---

## 📊 Certification Challenge Submission

**Deliverables Checklist:**

- [ ] **GitHub Repository** (public or shared)
  - [ ] All code committed and pushed
  - [ ] README.md with project overview
  - [ ] Complete documentation in `docs/`
  - [ ] Working code (can be run locally)
  
- [ ] **5-Minute Demo Video** (Loom)
  - [ ] Problem explanation (30 sec)
  - [ ] Live demo of application (2 min)
    - Input ingredient list
    - Show analysis process
    - Display results with explanations
  - [ ] Architecture walkthrough (1 min)
  - [ ] RAGAS evaluation results (1 min)
  - [ ] Future vision (30 sec)
  
- [ ] **Written Document** (already in `docs/certification-challenge-plan.md`)
  - [x] Task 1: Problem and Audience
  - [x] Task 2: Solution Architecture
  - [x] Task 3: Data Sources
  - [ ] Task 4: Working Prototype (populate after implementation)
  - [ ] Task 5: Golden Dataset and Baseline RAGAS (populate with actual results)
  - [ ] Task 6: Advanced Retrieval Techniques (populate with implementation details)
  - [ ] Task 7: Performance Comparison (populate with actual metrics)

**Submission Deadline**: October 21, 2025 by 7:00 PM ET

**Submission Link**: https://forms.gle/4viHEd5BgAwW7mbi7

---

## 🎯 Phase 4: Demo Day Enhancements

**Post-certification improvements for Demo Day presentation**

### User Feedback & Iteration

- [ ] Recruit 10+ parent beta testers
- [ ] Collect feedback on accuracy, usefulness, UI
- [ ] Iterate based on feedback
- [ ] Document testimonials

### Mobile Prototype

- [ ] Set up React Native + Expo
- [ ] Build ingredient input screen
- [ ] Integrate camera for OCR (Google Vision API or Tesseract)
- [ ] Display results in mobile-friendly format
- [ ] Test on iOS/Android

### Product Database

- [ ] Scrape ingredient lists for 1,000+ common products
- [ ] Pre-compute safety scores
- [ ] Build search/lookup functionality
- [ ] Add barcode scanning (OpenFoodFacts API)

### Explainability Enhancements

- [ ] Add source citations to every claim
- [ ] Display confidence intervals
- [ ] Implement "Why this score?" detailed breakdown
- [ ] Show alternative products

**Total Phase 4 Estimate**: 3-4 weeks

---

## 📝 Development Best Practices

### Code Quality

- Write docstrings for all functions
- Use type hints (Python 3.11+)
- Follow PEP 8 style guide
- Add comments for complex logic

### Testing

- Unit tests for scoring logic
- Integration tests for agent workflows
- RAGAS evaluation as regression tests
- Manual testing with real products

### Git Workflow

- Create feature branches (`git checkout -b feature/allergen-agent`)
- Commit frequently with clear messages
- Don't commit to main directly
- Push to GitHub regularly (backup!)

### Monitoring

- Enable LangSmith tracing for all LLM calls
- Log agent decisions and scores
- Track token usage and costs
- Monitor response times

---

## 🆘 Getting Unstuck

### Common Issues

**Issue**: PDF parsing fails
- **Solution**: Try alternative libraries (pdfplumber, PyMuPDF)
- **Workaround**: Manually extract text using Adobe/Preview, save as .txt

**Issue**: Qdrant connection refused
- **Solution**: Verify Docker container is running (`docker ps`)
- **Solution**: Check port 6333 is not in use

**Issue**: RAGAS scores are very low
- **Solution**: This is expected for naive baseline! Document findings.
- **Solution**: Review retrieved chunks - are they relevant? If not, improve retrieval.

**Issue**: LangGraph agents not coordinating properly
- **Solution**: Print state at each node to debug
- **Solution**: Use LangSmith to visualize execution graph

**Issue**: Response time is too slow (> 30 seconds)
- **Solution**: Reduce number of chunks retrieved (try top-3 instead of top-5)
- **Solution**: Run agents in parallel (LangGraph supports this)
- **Solution**: Cache embeddings for common ingredients

### Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **RAGAS Tutorial**: https://docs.ragas.io/en/latest/
- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Streamlit Gallery**: https://streamlit.io/gallery

### Getting Help

- Post in AIE8 Discord #certification-challenge channel
- Office hours with instructors
- Pair with cohort members
- Claude Code (you're talking to me right now!)

---

## 🎉 Success Criteria

You've succeeded when:

✅ Application analyzes ingredient list and returns score in < 10 seconds  
✅ RAGAS faithfulness > 0.90 (health/safety domain requirement)  
✅ Can demonstrate clear improvement from naive to advanced RAG  
✅ 5-minute demo video effectively communicates problem, solution, and results  
✅ All documentation is complete and well-organized  
✅ Code runs successfully on a fresh clone of the repo  

**Remember**: The goal is not perfection, but **demonstrating your AI Engineering skills** across the full stack (product thinking, RAG implementation, evaluation, iteration).

Good luck! 🚀

