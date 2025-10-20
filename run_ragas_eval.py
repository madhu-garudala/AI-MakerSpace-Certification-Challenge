"""
Quick RAGAS evaluation runner with API keys pre-configured.
Edit this file to add your API keys, then run: python3 run_ragas_eval.py
"""

import os
import sys

# ===== CONFIGURE YOUR API KEYS HERE =====
OPENAI_API_KEY = ""  # Add your OpenAI API key here
LANGSMITH_API_KEY = ""  # Your LangSmith key
COHERE_API_KEY = ""  # Optional: Add your Cohere API key here
RETRIEVAL_STRATEGY = "ensemble"  # Options: ensemble, naive, bm25
# =========================================

if __name__ == "__main__":
    print("="*100)
    print("RAGAS EVALUATION RUNNER")
    print("="*100)
    
    # Check if OpenAI key is provided
    if not OPENAI_API_KEY:
        print("\n⚠️  Please edit this file and add your OPENAI_API_KEY")
        print("Then run: python3 run_ragas_eval.py\n")
        sys.exit(1)
    
    # Set environment variables
    os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY
    os.environ['LANGCHAIN_API_KEY'] = LANGSMITH_API_KEY
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_PROJECT'] = 'KidSafe-RAGAS-Evaluation'
    
    if COHERE_API_KEY:
        os.environ['COHERE_API_KEY'] = COHERE_API_KEY
        print(f"\n✅ Using Cohere API for reranking")
    else:
        print(f"\n⚠️  No Cohere key provided - ensemble will use 2 retrievers instead of 3")
    
    print(f"✅ Retrieval strategy: {RETRIEVAL_STRATEGY}")
    print(f"✅ API keys configured\n")
    
    # Import and run the evaluation
    from backend.ragas_evaluation import run_ragas_evaluation
    
    print("Starting RAGAS evaluation...")
    print("This will take approximately 5-7 minutes.\n")
    
    try:
        results_df, avg_scores = run_ragas_evaluation(retrieval_strategy=RETRIEVAL_STRATEGY)
        
        print("\n" + "="*100)
        print("✅ EVALUATION COMPLETE!")
        print("="*100)
        print(f"\nResults saved to: ragas_evaluation_results_{RETRIEVAL_STRATEGY}.csv")
        print(f"LangSmith traces: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"\n❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()

