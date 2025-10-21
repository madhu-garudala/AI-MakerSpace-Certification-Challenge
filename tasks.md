# KidSafe Food Analyzer - Certification Challenge Tasks

**Project**: AI-powered food safety analyzer for parents  
**Cohort**: AI Engineering Bootcamp Cohort 8  
**Due**: October 21, 2025 by 7:00 PM ET

---

## 📌 Executive Summary

**Problem**: Parents struggle to quickly assess whether store-bought food products are safe for their children based on ingredient lists, unable to identify harmful allergens, additives, or nutritional concerns while shopping.

**Solution**: KidSafe Food Analyzer - A web-based agentic RAG application that provides percentage-based safety scores (0-100%) with detailed categorical breakdowns for any ingredient list.

**Audience**: All parents and caregivers making food purchasing decisions for children.

---

## Task 1: Problem & Audience Definition

### Problem Statement
Parents lack a quick, reliable way to assess the safety and appropriateness of store-bought food products for their children based on ingredient lists, leading to uncertainty and potential health risks.

### Why This is a Problem
- **Information Overload**: 20-50+ ingredients per product, most unrecognizable
- **Hidden Dangers**: Artificial dyes, allergens, excessive sugar/sodium
- **Allergen Complexity**: 1 in 13 children have food allergies (6M+ in US)
- **Time Pressure**: Working parents need quick decisions during shopping
- **Conflicting Information**: Mixed messages from various sources

### Target Users
- Parents with children who have allergies/dietary restrictions
- Health-conscious parents seeking informed choices  
- Any parent shopping for store-bought food products

### Key User Questions
1. "Is this cereal safe for my 5-year-old?"
2. "What's wrong with Red Dye #40?"
3. "Is this a choking hazard for my toddler?"
4. "My child has a peanut allergy - any risk?"
5. "How much sugar is too much?"
6. "What are side effects of these preservatives?"
7. "Is 'all natural' really healthy?"

---

## Task 2: Proposed Solution

### User Experience
1. **Input**: Parent types/pastes ingredient list into web app
2. **Analysis**: AI agents analyze across 4 safety dimensions (allergens, additives, nutrition, physical safety)
3. **Score**: Receive percentage score (0-100%) with color coding 🟢🟡🔴
4. **Breakdown**: View detailed analysis by category with explanations
5. **Decision**: Make informed purchase decision with confidence

### Technology Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **LLM** | OpenAI GPT-4o | Strong reasoning, function calling, structured output |
| **Embeddings** | text-embedding-3-large | 3072-dim, excellent for technical domains |
| **Orchestration** | LangGraph | Stateful multi-agent coordination, observability |
| **Vector DB** | Qdrant | Hybrid search, metadata filtering, local+cloud |
| **Monitoring** | LangSmith | Native LangChain/LangGraph tracing |
| **Evaluation** | RAGAS | RAG-specific metrics (faithfulness, precision, recall) |
| **UI** | Streamlit | Rapid prototyping, built-in components |
| **Search API** | Tavily | Real-time ingredient research |

### Multi-Agent Architecture

```
Supervisor Agent (Coordinator)
├── Allergen Agent → RAG Tool (allergen database)
├── Additive Agent → RAG Tool (FDA regulations)
├── Nutrition Agent → RAG Tool (USDA guidelines)
└── Safety Agent → RAG Tool (AAP safety standards)
```

**Agentic Reasoning**: Each specialist agent independently analyzes ingredients in their domain using RAG-retrieved evidence, then the Supervisor synthesizes results with a weighted scoring formula.

### Scoring Formula
```
Final Score = (Allergen × 0.30) + (Additive × 0.25) + (Nutrition × 0.25) + (Safety × 0.20)
```

**Weights Justification**:
- **30% Allergen**: Highest - life-threatening risk
- **25% Additive**: High - behavioral/health impacts
- **25% Nutrition**: High - long-term health
- **20% Safety**: Important - choking hazards

---

## Task 3: Data Sources & Strategy

### Primary Data Sources

| Source | Type | Purpose | Size |
|--------|------|---------|------|
| **FDA Food Labeling Guide** | PDF | Regulatory standards, allergen definitions | ~200 pages |
| **FDA Food Additives List** | PDF/CSV | Approved additives, GRAS substances | ~50 pages |
| **USDA Dietary Guidelines** | PDF | Daily limits for sugar/sodium/fats | ~150 pages |
| **AAP Nutrition Guidelines** | Web/PDF | Age-appropriate nutrition recommendations | ~100 pages |
| **AAP Choking Prevention** | PDF | Physical safety, choking hazard lists | ~30 pages |
| **Research Studies** | PDF | Food dye/additive effects on children | ~50 papers |

**Total Corpus**: ~1,000 pages → ~1,500 chunks

### External APIs
- **Tavily Search**: Real-time research for recent studies, recalls, FDA warnings
- **OpenFDA** (future): Food recall database, adverse events

### Chunking Strategy

**Method**: Hierarchical Semantic Chunking
- **Size**: 500-800 tokens per chunk
- **Overlap**: 100 tokens (preserve context at boundaries)
- **Hierarchy**: Document → Section → Subsection → Chunk
- **Metadata**: source, document_type, authority, publication_date, page, section
- **Parent-Child Links**: Each chunk linked to parent section for context retrieval

**Why This Strategy**:
- Regulatory documents have natural hierarchical structure
- Guidelines often have conditions ("for children under 3") that need context
- Metadata filtering allows agents to query relevant document types only
- Optimal balance: enough context without overwhelming LLM


---

## Task 4: End-to-End Prototype

### Implementation Components

**1. Data Ingestion Pipeline**
- Download FDA, USDA, AAP documents
- Extract text with pypdf
- Apply hierarchical chunking
- Generate embeddings (text-embedding-3-large)
- Load into Qdrant collections (by document type)

**2. RAG Retrieval System**
- Semantic search with Qdrant
- Metadata filtering by document type
- Return top-5 chunks with source citations

**3. Multi-Agent System (LangGraph)**
- Parse ingredient list into normalized components
- Route to 4 specialist agents (parallel execution)
- Each agent: query RAG → analyze → score → report
- Supervisor aggregates and calculates final weighted score

**4. Streamlit Web Interface**
- Text input for ingredient list
- Real-time analysis progress
- Large color-coded score display
- Tabbed category breakdowns
- Expandable ingredient details
- Source citations

**5. Local Deployment**
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Run application  
streamlit run main.py
```

### Test Scenarios
- ✅ Peanut butter (major allergen)
- ✅ Fruit Loops (artificial dyes, high sugar)
- ✅ Organic applesauce (clean ingredients)
- ✅ Processed snack cake (multiple concerns)

**Deliverable**: Working prototype deployed locally, end-to-end flow functional

---

## Task 5: Golden Test Dataset & Baseline Evaluation

### Test Dataset (50 cases)

| Category | Count | Examples |
|----------|-------|----------|
| **Major Allergen Products** | 10 | Peanut butter, milk, eggs, wheat bread |
| **High Sugar Products** | 10 | Candy, sugary cereal, juice boxes |
| **Artificial Additive Products** | 10 | Colored snacks, processed foods with dyes |
| **Clean/Healthy Products** | 10 | Organic applesauce, whole foods |
| **Mixed Concern Products** | 10 | Products with multiple issues |

**Ground Truth Creation**:
- Manually score 20 products using nutrition expert guidelines
- Generate 30 synthetic ingredient lists with GPT-4o (known characteristics)
- Document expected scores and reasoning

### RAGAS Evaluation Metrics

**Baseline Testing** (Naive RAG: basic semantic search, no advanced techniques)

| Metric | Target | Expected Baseline | Description |
|--------|--------|-------------------|-------------|
| **Faithfulness** | ≥ 0.90 | ~0.75 | Are safety claims grounded in retrieved docs? |
| **Answer Relevancy** | ≥ 0.85 | ~0.80 | Does response address the safety question? |
| **Context Precision** | ≥ 0.80 | ~0.65 | Are retrieved chunks relevant? |
| **Context Recall** | ≥ 0.75 | ~0.60 | Do we retrieve all relevant guidelines? |

**Evaluation Process**:
1. Run 50 test cases through naive RAG system
2. Measure RAGAS metrics for each case
3. Calculate averages by category
4. Document failure modes and weak areas
5. Identify specific improvements needed

**Expected Findings**:
- Low context precision (too many irrelevant chunks)
- Missed relevant guidelines (keyword mismatch)
- Hallucinations without proper source attribution
- Better performance on allergens vs. nutritional analysis

**Deliverable**: Baseline results table, failure analysis, improvement roadmap

---

## Task 6: Advanced Retrieval Techniques

### Techniques to Implement

**1. Hybrid Search (Semantic + Keyword)**
- **Why**: Ingredient names are exact terms ("Red 40") - need keyword matching
- **Method**: 0.6 × semantic similarity + 0.4 × BM25 keyword score
- **Expected Impact**: +10-15% context precision

**2. Query Decomposition**
- **Why**: Complex ingredient lists need separate analysis per ingredient
- **Method**: LLM breaks query into atomic sub-queries, parallel retrieval
- **Expected Impact**: +10% context recall

**3. Metadata Filtering**
- **Why**: Each agent needs specific document types only
- **Method**: Filter by document_type before vector search (allergen_db, additive_regulation, etc.)
- **Expected Impact**: +15-20% context precision

**4. Cross-Encoder Re-ranking**
- **Why**: Initial retrieval may rank relevant chunks lower
- **Method**: Retrieve top-20, re-rank with `cross-encoder/ms-marco-MiniLM-L-12-v2`, return top-5
- **Expected Impact**: +15% context precision

**5. Parent Document Retrieval**
- **Why**: Small chunks lose context, but full docs are too long
- **Method**: Retrieve chunk + its parent section for LLM
- **Expected Impact**: +10-15% faithfulness

**6. HyDE (Hypothetical Document Embeddings)**
- **Why**: Query-document mismatch ("Is Red 40 safe?" vs guideline text)
- **Method**: Generate hypothetical answer, embed it, search with that embedding
- **Expected Impact**: +5-10% context recall

### Evaluation Strategy

| Experiment | Techniques | Expected Context Precision |
|------------|-----------|----------------------------|
| Baseline | Naive semantic search | 0.65 |
| Exp 1 | Hybrid search | 0.75 (+10%) |
| Exp 2 | Hybrid + Metadata filtering | 0.80 (+15%) |
| Exp 3 | Hybrid + Metadata + Re-ranking | 0.85 (+20%) |
| Exp 4 | Full stack (all 6) | 0.90 (+25%) |

**Deliverable**: Implementation of all 6 techniques, comparative testing on 50-case dataset

---

## Task 7: Performance Assessment & Future Improvements

### Comparative Results

**Test Setup**: Run 50-case dataset through both systems

| Metric | Naive RAG | Advanced RAG | Improvement | Target Met? |
|--------|-----------|--------------|-------------|-------------|
| **Faithfulness** | 0.75 | 0.92 | +23% | ✅ (>0.90) |
| **Answer Relevancy** | 0.80 | 0.88 | +10% | ✅ (>0.85) |
| **Context Precision** | 0.65 | 0.85 | +31% | ✅ (>0.80) |
| **Context Recall** | 0.60 | 0.78 | +30% | ✅ (>0.75) |
| **Avg Response Time** | 8.2s | 10.1s | +23% | ✅ (<10s target) |

*(Above are expected/example results - populate with actual data after testing)*

### Performance by Category

| Category | Baseline Accuracy | Advanced Accuracy | Notes |
|----------|------------------|-------------------|-------|
| Major Allergens | 85% | 98% | High in both (well-defined lists) |
| High Sugar | 65% | 82% | Improved numeric reasoning |
| Artificial Additives | 58% | 89% | Major improvement (exact matching) |
| Clean Products | 78% | 85% | Minimal difference (simple cases) |
| Mixed Concerns | 52% | 78% | Significant improvement (complex retrieval) |

### Key Findings
1. **Hybrid search dramatically improved** additive detection (Red 40, BHT exact matches)
2. **Re-ranking reduced false positives** by 40% (irrelevant chunks pushed down)
3. **Parent retrieval improved faithfulness** (more context = fewer hallucinations)
4. **Latency acceptable** (+2s from advanced techniques, still under 10s target)

### Failure Modes Still Present
- **Novel ingredients** not in corpus (e.g., brand-new 2025 sweetener)
- **Ambiguous terms** like "natural flavoring" (could be anything)
- **Conflicting research** (different studies, opposite conclusions)

---

## Future Improvements (Post-Certification → Demo Day)

### Phase 1: User Feedback (Weeks 1-2)
- Recruit 10+ parent beta testers
- Collect feedback on accuracy, usefulness, UI
- Iterate based on real user needs
- Document testimonials for Demo Day

### Phase 2: Mobile Prototype (Weeks 3-4)
- Build React Native + Expo mobile app
- Integrate OCR for camera-based ingredient scanning (Google Vision API)
- Test on iOS and Android devices
- Optimize for offline mode (local embeddings)

### Phase 3: Product Database (Weeks 5-6)
- Pre-compute scores for 1,000+ common products
- Build instant lookup by product name or barcode
- Integrate OpenFoodFacts API
- Add "compare products" feature

### Phase 4: Explainability (Weeks 7-8)
- Add source citations for every claim
- Display confidence scores per category
- Implement "Why this score?" detailed breakdown
- Suggest healthier alternatives

### Technical Enhancements
1. **Fine-tune embedding model** on ingredient-safety domain (+10% retrieval)
2. **Query expansion** with ingredient synonym database (HFCS → High Fructose Corn Syrup)
3. **Numerical reasoning agent** for better sugar/sodium comparisons
4. **A/B test scoring rubric** based on user feedback

### Long-Term Vision (Product Launch)
- Multi-language support (Spanish, Mandarin)
- Personalized profiles (child age, allergies)
- Retailer partnerships (in-store kiosks)
- B2B API for schools, hospitals
- Subscription model with premium features

---

## Deliverables Checklist

### GitHub Repository
- [ ] All code committed and pushed
- [ ] README.md with setup instructions
- [ ] Complete documentation in `docs/`
- [ ] `.env.example` with required API keys
- [ ] Working application (can run locally)

### 5-Minute Demo Video (Loom)
- [ ] Problem explanation (30 sec)
- [ ] Live demo showing analysis (2 min)
- [ ] Architecture walkthrough (1 min)
- [ ] RAGAS evaluation results (1 min)
- [ ] Future vision (30 sec)

### Written Documentation
- [x] Task 1: Problem & Audience ✅
- [x] Task 2: Solution Architecture ✅
- [x] Task 3: Data Sources & Strategy ✅
- [ ] Task 4: Working Prototype (complete after implementation)
- [ ] Task 5: Baseline RAGAS Evaluation (populate with actual results)
- [ ] Task 6: Advanced Retrieval Implementation (document techniques)
- [ ] Task 7: Performance Comparison (populate with actual metrics)

### Submission
- **Form**: https://forms.gle/4viHEd5BgAwW7mbi7
- **Deadline**: October 21, 2025 by 7:00 PM ET

---

## Quick Reference

### Core Files
- `README.md` - Project overview
- `CLAUDE.md` - Development guidance  
- `docs/certification-challenge-plan.md` - Full detailed plan
- `docs/architecture.md` - Technical architecture
- `docs/NEXT_STEPS.md` - Implementation roadmap

### Key Commands
```bash
# Setup
uv venv --python 3.11 && source .venv/bin/activate
uv pip install openai langchain langgraph qdrant-client streamlit ragas

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Run app
streamlit run main.py

# Run evaluation
pytest tests/ -v
```

### Success Criteria
✅ Application returns score in < 10 seconds  
✅ RAGAS faithfulness > 0.90  
✅ Clear improvement from naive to advanced RAG  
✅ 5-minute demo video complete  
✅ All documentation complete  
✅ Code runs on fresh clone

---

## Impact Statement

**If successful, KidSafe Food Analyzer could help millions of parents make better food choices, reducing childhood exposure to harmful additives, preventing allergic reactions, and promoting healthier eating habits from an early age.**

**This project demonstrates mastery of**: Product thinking • RAG implementation • Multi-agent systems • Advanced retrieval • Systematic evaluation • Production AI engineering

---

*Good luck! 🚀*

