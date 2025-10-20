# KidSafe Food Analyzer - Technical Architecture

**Version:** 1.0  
**Last Updated:** October 16, 2025  
**Status:** Planning Phase

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Scoring Algorithm](#scoring-algorithm)
7. [RAG Pipeline](#rag-pipeline)
8. [Multi-Agent System](#multi-agent-system)
9. [Deployment Strategy](#deployment-strategy)
10. [Security & Privacy](#security--privacy)
11. [Scalability Considerations](#scalability-considerations)

---

## System Overview

KidSafe Food Analyzer is a multi-agent RAG application that analyzes food ingredient lists to provide safety assessments for children. The system combines:

- **Retrieval-Augmented Generation (RAG)** for evidence-based ingredient evaluation
- **Multi-Agent Architecture** for specialized domain analysis
- **Advanced Retrieval Techniques** for high-precision information retrieval
- **Structured Scoring System** for consistent, transparent evaluations

### Key Characteristics

- **Input**: Text-based ingredient list (comma or newline separated)
- **Processing**: Parallel multi-agent analysis with RAG-backed knowledge
- **Output**: Percentage safety score (0-100) + detailed categorical breakdown + explanations
- **Latency Target**: < 10 seconds per analysis
- **Accuracy Target**: > 95% on allergen detection, > 85% on overall safety assessment

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface Layer                       │
│                        (Streamlit)                              │
└────────────────────────┬───────────────────────────────────────┘
                         │ Ingredient List Input
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Application Logic Layer                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Supervisor Agent (LangGraph)                   │  │
│  │  - Parse ingredients                                      │  │
│  │  - Route to specialist agents                             │  │
│  │  - Aggregate results                                      │  │
│  │  - Calculate final score                                  │  │
│  └────┬───────────────┬───────────────┬──────────────┬───────┘  │
│       │               │               │              │           │
│       │               │               │              │           │
│  ┌────▼───────┐ ┌────▼────────┐ ┌────▼───────┐ ┌───▼───────┐  │
│  │ Allergen   │ │  Additive   │ │ Nutrition  │ │  Safety   │  │
│  │   Agent    │ │    Agent    │ │   Agent    │ │   Agent   │  │
│  │            │ │             │ │            │ │           │  │
│  │ RAG Tool   │ │  RAG Tool   │ │ RAG Tool   │ │ RAG Tool  │  │
│  └────┬───────┘ └────┬────────┘ └────┬───────┘ └───┬───────┘  │
│       │              │               │              │           │
│       └──────────────┴───────────────┴──────────────┘           │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                             │ Query with metadata filters
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Pipeline Layer                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │             Advanced Retrieval System                     │  │
│  │  1. Query Decomposition (LLM)                            │  │
│  │  2. Hybrid Search (Semantic + Keyword)                   │  │
│  │  3. Metadata Filtering (by document type)                │  │
│  │  4. Cross-Encoder Re-ranking                             │  │
│  │  5. Parent Document Retrieval                            │  │
│  │  6. [Optional] HyDE Enhancement                          │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐  │
│  │              Qdrant Vector Database                       │  │
│  │  - Embeddings: text-embedding-3-large (3072 dim)         │  │
│  │  - Collections by document type                          │  │
│  │  - Metadata: source, date, authority, type               │  │
│  │  - Hybrid index: Vector + Keyword                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │ Retrieve relevant guidelines
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Base Layer                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               Structured Documents                        │  │
│  │  - FDA Food Labeling & Nutrition Guides                  │  │
│  │  - FDA Food Additives Status List                        │  │
│  │  - USDA Dietary Guidelines                               │  │
│  │  - AAP Nutrition & Safety Guidelines                     │  │
│  │  - Research Papers on Additives & Child Health           │  │
│  │  - Allergen Database (FALCPA)                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    External Services Layer                      │
│  - OpenAI API (GPT-4o, text-embedding-3-large)                 │
│  - Tavily Search API (real-time ingredient research)            │
│  - LangSmith (monitoring & tracing)                             │
│  - [Future] OpenFDA API (recalls, adverse events)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. User Interface Layer

**Technology:** Streamlit

**Components:**
- **Input Panel**: Text area for ingredient list input
- **Analysis Progress**: Real-time feedback showing agent execution
- **Score Display**: Large, color-coded percentage (green/yellow/red)
- **Category Tabs**: Tabbed interface for detailed breakdowns
  - Allergens tab
  - Additives & Preservatives tab
  - Nutritional Analysis tab
  - Physical Safety tab
- **Ingredient Details**: Expandable accordion for each concerning ingredient
- **Source Citations**: Links to FDA/USDA/AAP documents referenced

**UI/UX Principles:**
- Mobile-first design (even in web MVP)
- Maximum 3 clicks to get answer
- Color coding for quick interpretation (green = safe, yellow = moderate, red = concerning)
- Progressive disclosure (summary → details → sources)

### 2. Application Logic Layer

#### Supervisor Agent

**Framework:** LangGraph

**Responsibilities:**
1. **Parsing**: Split ingredient list into individual components
2. **Normalization**: Clean ingredient names (remove quantities, punctuation)
3. **Routing**: Dispatch each ingredient to relevant specialist agents
4. **Aggregation**: Collect and synthesize specialist reports
5. **Scoring**: Apply weighted formula to calculate final score
6. **Report Generation**: Compile comprehensive safety report

**State Schema:**
```python
{
    "ingredient_list": List[str],
    "normalized_ingredients": List[str],
    "allergen_report": Dict,
    "additive_report": Dict,
    "nutrition_report": Dict,
    "safety_report": Dict,
    "category_scores": Dict[str, float],
    "final_score": float,
    "detailed_report": Dict
}
```

#### Specialist Agents

##### Allergen Detection Agent
- **Domain**: Major food allergens (FDA FALCPA list)
- **RAG Filter**: `document_type == "allergen_database"`
- **Queries**: "Is {ingredient} a known allergen?", "Does {ingredient} contain hidden allergens?"
- **Output**: List of detected allergens with severity levels

##### Additive & Preservative Agent
- **Domain**: Artificial colors, flavors, preservatives, sweeteners
- **RAG Filter**: `document_type == "additive_regulation"`
- **Queries**: "What are health concerns for {ingredient}?", "Is {ingredient} FDA approved?"
- **Output**: List of additives with safety scores and health impact explanations

##### Nutritional Analysis Agent
- **Domain**: Sugar, sodium, fats, nutritional density
- **RAG Filter**: `document_type == "nutrition_guideline"`
- **Queries**: "What are recommended limits for {nutrient} in children?", "Is {quantity}g excessive?"
- **Output**: Nutritional quality score with comparisons to daily limits

##### Physical Safety Agent
- **Domain**: Choking hazards, texture/form concerns
- **RAG Filter**: `document_type == "safety_standard"`
- **Queries**: "Is {ingredient/form} a choking hazard?", "Age recommendations for {food type}?"
- **Output**: Physical safety concerns and age appropriateness

**Agent Tool Kit:**
- RAG Search Tool (domain-specific)
- Scoring Rubric Lookup
- Citation Tracker

### 3. RAG Pipeline Layer

#### Advanced Retrieval System

**Stage 1: Query Preprocessing**
- Decompose complex queries into atomic questions
- Expand ingredient names with synonyms (e.g., "HFCS" → "High Fructose Corn Syrup")
- Generate hypothetical answers (HyDE) for semantic matching

**Stage 2: Hybrid Search**
- Vector similarity search (semantic understanding)
- Keyword BM25 search (exact ingredient name matching)
- Combined weighted score: `0.6 * semantic + 0.4 * keyword`
- Retrieve top-20 candidates

**Stage 3: Filtering**
- Apply metadata filters based on agent context
- Filter by document recency (prioritize newer guidelines)
- Filter by source authority (FDA > blog posts)

**Stage 4: Re-ranking**
- Cross-encoder model scores query-chunk relevance
- Re-rank top-20 to get best top-5
- Model: `cross-encoder/ms-marco-MiniLM-L-12-v2`

**Stage 5: Context Enhancement**
- Retrieve parent document sections for top chunks
- Combine chunk (for precision) + parent (for context)
- Attach source metadata for citations

**Performance Metrics:**
- Latency: 2-3 seconds per ingredient query
- Context Precision: > 0.80
- Context Recall: > 0.75

#### Qdrant Vector Database

**Configuration:**
- **Embedding Model**: OpenAI text-embedding-3-large (3072 dimensions)
- **Distance Metric**: Cosine similarity
- **Collections**: Separate collections per document type for optimized filtering
  - `allergen_docs`
  - `additive_docs`
  - `nutrition_docs`
  - `safety_docs`
- **Indexing**: HNSW (Hierarchical Navigable Small World) for fast approximate search
- **Payload Storage**: Full chunks + metadata (source, date, page, section)

**Metadata Schema:**
```json
{
    "text": "Full chunk text...",
    "source": "FDA Food Labeling Guide",
    "document_type": "allergen_database",
    "authority": "FDA",
    "publication_date": "2024-01-15",
    "page": 42,
    "section": "Major Food Allergens",
    "parent_doc_id": "fda_labeling_2024"
}
```

### 4. Knowledge Base Layer

#### Document Corpus

| Document Type | Source | # Pages | # Chunks | Update Frequency |
|---------------|--------|---------|----------|------------------|
| FDA Food Labeling Guide | FDA.gov | ~200 | ~400 | Annually |
| FDA Food Additives List | FDA.gov | ~50 | ~100 | Quarterly |
| USDA Dietary Guidelines | DietaryGuidelines.gov | ~150 | ~300 | Every 5 years |
| AAP Nutrition Guidelines | HealthyChildren.org | ~100 | ~200 | Annually |
| AAP Choking Prevention | AAP.org | ~30 | ~60 | As needed |
| Research Papers | PubMed | Variable | ~500 | Continuous |

**Total Corpus Size**: ~1,000 pages → ~1,560 chunks

#### Chunking Strategy

**Method**: Hierarchical Semantic Chunking

**Parameters:**
- Base chunk size: 500-800 tokens
- Overlap: 100 tokens
- Hierarchy: Document > Section > Subsection > Chunk
- Splitting logic: Respect section boundaries, preserve complete guidelines

**Example:**
```
Document: FDA Food Labeling Guide
├── Section: Allergen Labeling Requirements
│   ├── Subsection: Major Food Allergens
│   │   ├── Chunk 1: "The Food Allergen Labeling and Consumer Protection Act..."
│   │   ├── Chunk 2: "The eight major allergens are: milk, eggs, fish..."
│   └── Subsection: Cross-Contamination Warnings
│       └── Chunk 3: "Manufacturers may include precautionary statements..."
```

Each chunk stores:
- Parent section ID (for context retrieval)
- Sibling chunk IDs (for sequential reading)
- Full metadata path (Document > Section > Subsection)

### 5. External Services Layer

**OpenAI API**
- GPT-4o: Agent reasoning, query decomposition, report generation
- text-embedding-3-large: Document and query embeddings
- Usage: ~5K tokens per analysis (input + output)
- Cost estimate: $0.05 per analysis

**Tavily Search API**
- Real-time search for recent studies, recalls, updates
- Fallback when RAG returns low-confidence results
- Usage: 1-2 searches per analysis (if needed)

**LangSmith**
- Trace all agent interactions and LLM calls
- Debug retrieval quality and agent decisions
- Monitor latency and token usage
- Track evaluation metrics over time

**OpenFDA API** (Future)
- Query food recall database
- Check adverse event reports
- Cross-reference ingredients against safety alerts

---

## Data Flow

### End-to-End Analysis Flow

```
1. User Input
   ↓
   "Sugar, Red 40, Wheat Flour, BHT, Natural Flavor"

2. Supervisor Agent: Parse & Normalize
   ↓
   ["sugar", "red 40", "wheat flour", "bht", "natural flavor"]

3. Supervisor Agent: Route to Specialists (Parallel Execution)
   ↓
   ┌─────────────┬──────────────┬─────────────┬──────────────┐
   │  Allergen   │   Additive   │  Nutrition  │   Safety     │
   │    Agent    │     Agent    │    Agent    │    Agent     │
   └─────────────┴──────────────┴─────────────┴──────────────┘
        │              │              │              │
        ▼              ▼              ▼              ▼
   RAG Query    RAG Query      RAG Query      RAG Query
   "wheat"      "red 40"       "sugar"        "choking"
        │              │              │              │
        ▼              ▼              ▼              ▼
   Qdrant       Qdrant         Qdrant         Qdrant
   (allergen)   (additive)     (nutrition)    (safety)
        │              │              │              │
        ▼              ▼              ▼              ▼
   [Wheat is a  [Red 40 linked [High sugar    [No choking
    major        to behavior    exceeds daily  hazards
    allergen]    concerns]      limit]         detected]

4. Specialist Agents: Generate Domain Reports
   ↓
   {
     "allergen_report": {"score": 70, "findings": ["wheat detected"]},
     "additive_report": {"score": 35, "findings": ["red 40 concerns"]},
     "nutrition_report": {"score": 40, "findings": ["high sugar"]},
     "safety_report": {"score": 90, "findings": ["no concerns"]}
   }

5. Supervisor Agent: Calculate Weighted Score
   ↓
   Final Score = (70 × 0.30) + (35 × 0.25) + (40 × 0.25) + (90 × 0.20)
              = 21 + 8.75 + 10 + 18
              = 57.75 → 58/100

6. Supervisor Agent: Generate Detailed Report
   ↓
   {
     "final_score": 58,
     "category_scores": {...},
     "detailed_findings": {...},
     "recommendations": "Avoid due to artificial dyes...",
     "citations": [...]
   }

7. UI: Display Results to User
   ↓
   [Large score display: 58/100 🟡]
   [Category breakdown tabs]
   [Detailed explanations per ingredient]
```

---

## Technology Stack

### Core Technologies

| Layer | Technology | Version | Justification |
|-------|-----------|---------|---------------|
| **Language** | Python | 3.11 | Best AI/ML ecosystem support |
| **Dependency Management** | uv | Latest | Fast, reliable Python package management |
| **LLM** | OpenAI GPT-4o | Latest | Strong reasoning, function calling, structured output |
| **Embeddings** | text-embedding-3-large | Latest | High-dimensional (3072), excellent for technical domains |
| **Orchestration** | LangGraph | 0.2+ | Stateful multi-agent workflows, observability |
| **Vector DB** | Qdrant | 1.11+ | Hybrid search, metadata filtering, local/cloud flexibility |
| **Monitoring** | LangSmith | Latest | Native LangChain/LangGraph tracing |
| **Evaluation** | RAGAS | 0.1+ | RAG-specific metrics (faithfulness, precision, recall) |
| **Web Framework** | Streamlit | 1.39+ | Rapid prototyping, built-in components |
| **PDF Processing** | pypdf | 3.17+ | Extract text from regulatory PDFs |
| **Search API** | Tavily | Latest | Real-time search for recent information |

### Development Tools

- **IDE**: VSCode / Cursor (with AI assistance)
- **Version Control**: Git / GitHub
- **Environment**: Docker for Qdrant, Python venv for application
- **Testing**: pytest for unit/integration tests
- **Notebooks**: Jupyter for exploration and evaluation analysis

### Production Considerations (Future)

- **Web Hosting**: Streamlit Cloud (MVP), then AWS/GCP
- **Vector DB**: Qdrant Cloud (for production scale)
- **Monitoring**: LangSmith + DataDog for production observability
- **CI/CD**: GitHub Actions for automated testing and deployment
- **Security**: API key management via AWS Secrets Manager

---

## Scoring Algorithm

### Weighted Scoring Formula

```
Final Score = Σ (Category Score × Weight)

Where:
  Allergen Score      × 0.30  (30% weight - highest priority)
  Additive Score      × 0.25  (25% weight)
  Nutrition Score     × 0.25  (25% weight)
  Physical Safety Score × 0.20  (20% weight)
```

### Category Scoring Logic

#### 1. Allergen Score (0-100)

**Base Score:** 100

**Deductions:**
- Major allergen detected (peanuts, tree nuts, shellfish): **Score = 0** (auto-fail)
- Common allergen (milk, eggs, soy, wheat): **-30 points**
- Minor allergen or sensitivity (corn, sesame): **-15 points**
- "May contain" warning: **-10 points**
- Ambiguous ingredient (natural flavoring): **-5 points per instance**

**Floor:** Minimum score is 0

**Output:** 
- Score (0-100)
- List of detected allergens with severity
- Warning text for life-threatening allergens

#### 2. Additive Score (0-100)

**Base Score:** 100

**Deductions (per additive):**
- Banned/restricted in other countries: **-50 points**
- Linked to behavioral concerns (Red 40, Yellow 5): **-40 points**
- Controversial preservative (BHT, BHA): **-30 points**
- Artificial sweetener (aspartame, sucralose): **-20 points**
- GRAS but limited studies: **-15 points**
- Natural preservative (ascorbic acid): **-5 points**

**Cumulative:** Deductions stack for multiple additives
**Floor:** Minimum score is 0

**Output:**
- Score (0-100)
- List of concerning additives
- Health impact explanations per additive
- Scientific citations

#### 3. Nutrition Score (0-100)

**Base Score:** 100

**Deductions:**

*Sugar Content:*
- > 20g per serving: **-40 points**
- 15-20g per serving: **-30 points**
- 10-15g per serving: **-20 points**
- 5-10g per serving: **-10 points**
- < 5g per serving: **0 points**

*Sodium Content:*
- > 600mg per serving: **-30 points**
- 400-600mg: **-20 points**
- 200-400mg: **-10 points**
- < 200mg: **0 points**

*Nutritional Density:*
- Refined/processed grains: **-10 points**
- Trans fats present: **-20 points**
- Low protein/fiber: **-10 points**

**Bonuses:**
- Whole grains: **+10 points**
- Good source of protein: **+10 points**
- Good source of fiber: **+10 points**

**Cap:** Maximum 100, minimum 0

**Output:**
- Score (0-100)
- Breakdown by nutrient
- Comparison to daily recommended limits
- Nutritional improvement suggestions

#### 4. Physical Safety Score (0-100)

**Base Score:** 100

**Deductions:**
- High choking risk (whole nuts, hard candies): **-50 points**
- Moderate choking risk (tough textures): **-30 points**
- Minor concern (size/shape): **-15 points**
- Packaging hazard (small parts): **-10 points**

**Output:**
- Score (0-100)
- List of physical safety concerns
- Age recommendations
- Preparation suggestions to reduce risk

### Score Interpretation

| Score Range | Color | Label | Interpretation |
|-------------|-------|-------|----------------|
| 90-100 | 🟢 Green | Excellent | Highly recommended for children |
| 75-89 | 🟢 Light Green | Good | Generally safe with minor concerns |
| 60-74 | 🟡 Yellow | Fair | Acceptable occasionally, not for regular consumption |
| 40-59 | 🟠 Orange | Poor | Not recommended, multiple concerns |
| 0-39 | 🔴 Red | Concerning | Avoid - significant health/safety risks |

### Scoring Rubric Configuration

Stored in: `src/scoring/config/scoring_rubric.json`

**Benefits of JSON Configuration:**
- Easy to update without code changes
- Transparent scoring logic
- Auditable by domain experts
- Version controlled
- Can be customized per user in future (personalization)

---

## RAG Pipeline

### Document Ingestion Pipeline

```
1. Data Collection
   ├── Download PDFs from FDA, USDA, AAP websites
   ├── Web scraping for online-only content
   └── Store in data/raw/

2. Text Extraction
   ├── Use pypdf for PDF parsing
   ├── Clean extracted text (remove headers/footers)
   └── Preserve document structure (sections, headings)

3. Chunking
   ├── Identify section boundaries
   ├── Split into 500-800 token chunks with 100 token overlap
   ├── Maintain parent-child relationships
   └── Enrich with metadata

4. Embedding Generation
   ├── Call OpenAI API for text-embedding-3-large
   ├── Batch process for efficiency (100 chunks per request)
   └── Store embeddings in memory

5. Vector Database Loading
   ├── Create Qdrant collections by document type
   ├── Upload vectors with payloads (text + metadata)
   └── Build HNSW index
   
6. Validation
   ├── Test retrieval with sample queries
   ├── Verify metadata filtering works
   └── Measure baseline retrieval metrics
```

### Query Processing Pipeline

```
User Query: "Is Red 40 safe for kids?"

1. Query Understanding (LLM)
   ├── Extract key terms: ["red 40", "safety", "children"]
   ├── Identify query intent: additive_safety_check
   └── Determine relevant document type: additive_regulation

2. Query Expansion
   ├── Synonyms: "Red 40" → ["Red Dye #40", "Allura Red AC", "E129"]
   ├── Related terms: ["artificial colors", "food dyes", "FD&C Red 40"]
   └── [Optional] HyDE: Generate hypothetical answer for semantic matching

3. Hybrid Search (Qdrant)
   ├── Vector Search: Embed query, find cosine similarity matches (top-20)
   ├── Keyword Search: BM25 on exact terms "Red 40" (top-20)
   └── Merge: Weighted combination 0.6×semantic + 0.4×keyword

4. Metadata Filtering
   ├── Filter: document_type == "additive_regulation"
   ├── Prefer: authority == "FDA" or "peer_reviewed"
   └── Recency: publication_date > 2020

5. Re-ranking (Cross-Encoder)
   ├── Score each of top-20 chunks with cross-encoder
   ├── Re-order by cross-encoder score
   └── Select top-5 for LLM context

6. Context Enhancement
   ├── For each top-5 chunk, retrieve parent section
   ├── Combine: chunk (specific) + parent (context)
   └── Attach citations (source, page, date)

7. LLM Generation
   ├── Prompt: System instructions + Retrieved context + User query
   ├── Generate: Evidence-based answer with score
   └── Cite: Reference specific source documents

8. Response Formatting
   ├── Extract structured data (score, concerns, citations)
   ├── Format for display in UI
   └── Return to Supervisor Agent
```

### Retrieval Evaluation

**Metrics:**
- **Hit Rate**: Percentage of queries where relevant info is in top-K results
- **MRR (Mean Reciprocal Rank)**: Average of 1/rank for first relevant result
- **NDCG (Normalized Discounted Cumulative Gain)**: Quality of ranking
- **Context Precision** (RAGAS): Relevance of retrieved chunks
- **Context Recall** (RAGAS): Coverage of all relevant information

**Target Performance:**
- Hit@5: > 90%
- MRR: > 0.75
- Context Precision: > 0.80
- Context Recall: > 0.75

---

## Multi-Agent System

### LangGraph State Machine

```
StateGraph:
  Nodes:
    - parse_ingredients: Parse and normalize input
    - route_to_agents: Determine which agents to invoke
    - allergen_agent: Allergen detection
    - additive_agent: Additive analysis
    - nutrition_agent: Nutritional evaluation
    - safety_agent: Physical safety check
    - aggregate_results: Collect all agent reports
    - calculate_score: Apply weighted scoring formula
    - generate_report: Create comprehensive output
  
  Edges:
    parse_ingredients → route_to_agents
    route_to_agents → [allergen_agent, additive_agent, nutrition_agent, safety_agent] (parallel)
    [all agents] → aggregate_results
    aggregate_results → calculate_score
    calculate_score → generate_report
    generate_report → END
```

### Agent Communication Protocol

**State Object Schema:**
```python
class AnalysisState(TypedDict):
    # Input
    raw_input: str
    
    # Parsed data
    ingredients: List[str]
    normalized_ingredients: List[str]
    
    # Agent reports
    allergen_report: Optional[AllergenReport]
    additive_report: Optional[AdditiveReport]
    nutrition_report: Optional[NutritionReport]
    safety_report: Optional[SafetyReport]
    
    # Scores
    category_scores: Dict[str, float]
    final_score: float
    
    # Output
    detailed_report: DetailedReport
    citations: List[Citation]
```

**Agent Output Schema:**
```python
class AgentReport(TypedDict):
    category: str  # "allergen", "additive", "nutrition", "safety"
    score: float  # 0-100
    findings: List[Finding]
    concerns: List[Concern]
    citations: List[Citation]
    confidence: float  # 0-1
```

### Error Handling & Fallbacks

**Scenario 1: RAG Returns No Results**
- Fallback: Use Tavily search for real-time information
- If still no results: Flag ingredient as "unknown" and score conservatively (50)

**Scenario 2: Agent Timeout**
- Timeout: 30 seconds per agent
- Fallback: Skip agent, calculate final score without that category
- Warning: Display "Incomplete analysis" message to user

**Scenario 3: Ambiguous Ingredient**
- Example: "Natural Flavoring" (could contain anything)
- Handling: Flag as ambiguous, score conservatively, prompt user for more detail
- Display: "This ingredient could contain allergens - more info needed"

**Scenario 4: Conflicting Information**
- Example: Different studies show opposite results
- Handling: Present both perspectives with source quality indicators
- Scoring: Use more conservative (safer) interpretation

---

## Deployment Strategy

### Phase 1: Local Development (Current)

**Components:**
- Qdrant: Docker container (`localhost:6333`)
- Application: Python virtual environment
- UI: Streamlit local server (`localhost:8501`)

**Setup:**
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Start application
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e .
streamlit run main.py
```

### Phase 2: Cloud Deployment (Post-Certification)

**Architecture:**
```
User → Streamlit Cloud → Backend API (AWS Lambda) → Qdrant Cloud
                              ↓
                         OpenAI API
                         Tavily API
                         LangSmith
```

**Components:**
- **Frontend**: Streamlit Cloud (free tier)
- **Backend**: AWS Lambda + API Gateway (serverless)
- **Vector DB**: Qdrant Cloud (managed)
- **Monitoring**: LangSmith + CloudWatch

**Advantages:**
- Serverless = pay per use (cost-effective for sporadic usage)
- Auto-scaling for traffic spikes
- No server maintenance
- Global CDN for low latency

### Phase 3: Mobile App (Demo Day)

**Tech Stack:**
- React Native + Expo (cross-platform iOS/Android)
- Backend: Reuse Phase 2 API
- OCR: Google Cloud Vision API or Tesseract
- Offline: Local Qdrant instance with pre-computed embeddings

**Features:**
- Camera-based ingredient scanning
- Instant analysis (< 5 seconds)
- Save history
- Barcode scanning (future)

---

## Security & Privacy

### Data Privacy

**User Data:**
- No PII (personally identifiable information) collected
- Ingredient lists are not stored long-term
- Analysis results are ephemeral (not logged)

**API Keys:**
- Stored in environment variables (`.env`)
- Production: Use AWS Secrets Manager
- Never commit to git (`.gitignore` configured)

### API Rate Limiting

**OpenAI:**
- Implement exponential backoff for rate limits
- Cache embeddings for repeated queries
- Monitor token usage to avoid overages

**Qdrant:**
- Local: No limits
- Cloud: Configure query throttling

### Content Safety

**Input Validation:**
- Sanitize user input (prevent injection attacks)
- Limit input length (max 2000 characters)
- Block malicious patterns

**Output Validation:**
- Check LLM responses for hallucinations
- Verify citations exist in source documents
- Flag low-confidence responses

---

## Scalability Considerations

### Current Capacity (MVP)

- **Concurrent Users**: 5-10
- **Queries per minute**: ~10
- **Response time**: 5-10 seconds per query
- **Vector DB size**: ~50 MB (1,500 chunks)

### Optimization Strategies

#### 1. Caching

**Query Cache:**
- Cache identical ingredient lists → responses
- TTL: 24 hours (regulations rarely change daily)
- Cache hit rate estimate: 30-40% (common products)

**Embedding Cache:**
- Cache ingredient embeddings (common ingredients reused)
- Reduces OpenAI API calls by ~60%

#### 2. Batching

**Batch Processing:**
- For product database pre-computation
- Process 100s of products overnight
- Store pre-computed scores for instant lookup

#### 3. Database Optimization

**Qdrant Performance:**
- Use quantization for embeddings (reduce memory)
- Separate collections by document type (faster filtering)
- Index optimization for hybrid search

#### 4. Horizontal Scaling

**Load Balancing:**
- Deploy multiple API instances
- Route traffic via ALB (AWS Application Load Balancer)
- Stateless design enables easy scaling

### Cost Projections

**Per Analysis:**
- OpenAI (GPT-4o): $0.03 (5K tokens)
- OpenAI (embeddings): $0.01 (reused)
- Tavily (optional): $0.005 (1-2 searches)
- **Total**: ~$0.04 per analysis

**Monthly (1000 users, 5 queries each):**
- OpenAI: $200
- Qdrant Cloud: $25 (starter tier)
- Streamlit Cloud: $20
- **Total**: ~$245/month

**At Scale (100K analyses/month):**
- OpenAI: $4,000
- Qdrant Cloud: $200 (scaling tier)
- AWS Lambda: $100
- **Total**: ~$4,300/month

---

## Monitoring & Observability

### Metrics to Track

**Application Metrics:**
- Queries per minute (QPM)
- Average response time
- Error rate (% of failed analyses)
- Cache hit rate
- Token usage (input + output)

**Quality Metrics:**
- RAGAS scores (tracked over time)
- User feedback (thumbs up/down)
- Allergen detection accuracy
- False positive/negative rate

**Cost Metrics:**
- API costs per query
- Cost per user
- Monthly burn rate

### Monitoring Tools

**LangSmith:**
- Trace all LLM calls
- Visualize agent decision paths
- Debug retrieval failures
- A/B test prompt variations

**Streamlit Analytics:**
- Track user sessions
- Monitor page load times
- Identify UI bottlenecks

**Custom Dashboards:**
- Daily analysis volume
- Most common ingredients queried
- Category score distributions
- Popular products

---

## Future Enhancements

### Short-Term (Post-Certification)

1. **Product Database**: Pre-compute scores for 10K+ common products
2. **Barcode Scanning**: Integrate with OpenFoodFacts API
3. **User Accounts**: Save analysis history, favorite products
4. **Comparison Mode**: Compare 2-3 products side-by-side
5. **Export Reports**: PDF export of analysis for sharing

### Medium-Term (Demo Day)

6. **Mobile App**: React Native with OCR
7. **Offline Mode**: Embedded vector DB for in-store use
8. **Personalization**: Custom profiles (allergies, dietary restrictions)
9. **Recommendations**: Suggest healthier alternatives
10. **Social Features**: Share products, community ratings

### Long-Term (Product Launch)

11. **Fine-Tuned Models**: Domain-specific LLM and embeddings
12. **Multi-Language**: Support Spanish, Mandarin, etc.
13. **Retailer Integration**: In-store kiosks, shelf tags
14. **Subscription Model**: Premium features (unlimited scans, alerts)
15. **B2B API**: License to schools, hospitals, food manufacturers

---

## Conclusion

This architecture balances **simplicity for MVP** with **scalability for production**. Key design decisions:

✅ **Multi-agent architecture** for modular, explainable analysis  
✅ **Advanced RAG techniques** for high-precision retrieval  
✅ **Transparent scoring system** for trustworthy results  
✅ **Cloud-native design** for easy scaling  
✅ **Privacy-first approach** (no personal data stored)  

The system is designed to **start simple** (local Streamlit app) and **scale incrementally** (cloud deployment → mobile app → product launch) as the project matures from certification challenge to Demo Day to real product.

