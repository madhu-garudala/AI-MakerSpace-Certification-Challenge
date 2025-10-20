# KidSafe Food Analyzer 🍎

An AI-powered application that helps parents make informed decisions about store-bought food products for their children by analyzing ingredient lists and providing detailed safety assessments.

## Problem Statement

Parents struggle to quickly assess whether store-bought food products are safe and appropriate for their children, often unable to identify harmful ingredients, allergens, or concerning additives while shopping or at home.

## Solution

KidSafe Food Analyzer provides an intelligent, data-driven percentage-based safety score for food products based on their ingredients, along with detailed explanations of concerns, potential side effects, and specific ingredient analysis.

## Target Audience

- Parents with children who have allergies or dietary restrictions
- Health-conscious parents seeking to make informed food choices
- Any parent shopping for store-bought food products who wants to ensure their children's safety

## Project Vision

### Current Phase (Iteration 1)
Web application where parents manually input ingredient lists to receive:
- Overall safety percentage score (0-100%)
- Detailed breakdown by category (allergens, additives, nutrition, safety)
- Specific ingredient concerns and potential side effects
- Evidence-based recommendations

### Future Iterations
- Mobile application with camera-based ingredient scanning (OCR)
- Barcode scanning for instant product lookup
- Personalized profiles for children with specific allergies
- Alternative product recommendations
- Offline mode for in-store use

## Key Features

1. **Percentage-Based Scoring**: Clear numerical rating (not just "approved/not approved")
2. **Multi-Factor Analysis**: 
   - Allergen detection
   - Sugar/sodium content evaluation
   - Artificial additives and preservatives
   - Choking hazards assessment
   - Nutritional value analysis
3. **Detailed Explanations**: Transparent reasoning behind scores
4. **Evidence-Based**: RAG system using pediatric nutrition guidelines, FDA data, and medical research

## Technology Stack

This project is being built as part of the AI Engineering Bootcamp Cohort 8 Certification Challenge, implementing:
- **LangGraph** for RAG workflow orchestration
- **Advanced retrieval strategies**: Naive, BM25, Multi-Query, Compression, Ensemble
- **Qdrant** vector database for semantic search
- **RAGAS** framework for systematic evaluation
- Production-grade AI application architecture with full observability

## Documentation

- See `QUICKSTART.md` for how to run the application
- See `ADVANCED_RETRIEVAL.md` for retrieval strategies guide
- See `IMPLEMENTATION_SUMMARY.md` for what has been built
- See `docs/certification-challenge-plan.md` for complete certification challenge deliverables
- See `docs/architecture.md` for technical architecture decisions
- See `CLAUDE.md` for development guidelines