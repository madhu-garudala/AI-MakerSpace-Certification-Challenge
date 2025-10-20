"""
RAGAS Evaluation Script for Offline Testing
This script evaluates the RAG system using RAGAS metrics.
"""

import os
import getpass
from typing import List, Dict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import (
    Faithfulness,
    FactualCorrectness,
    ContextEntityRecall,
    ResponseRelevancy,
    LLMContextRecall
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from backend.vector_store import VectorStoreManager
from backend.rag_engine import IngredientAnalyzer


def setup_api_keys():
    """Prompt for API keys if not already set."""
    if not os.environ.get('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = getpass.getpass("Enter your OpenAI API key: ")
    
    if not os.environ.get('LANGCHAIN_API_KEY'):
        os.environ['LANGCHAIN_API_KEY'] = getpass.getpass("Enter your LangSmith API key: ")
    
    # Enable LangSmith tracing
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_PROJECT'] = 'KidSafe-Food-Analyzer-Evaluation'


def create_test_dataset() -> List[Dict[str, str]]:
    """
    Create a test dataset of cereal ingredients for evaluation.
    
    Returns:
        List of test cases with cereal names and ingredients
    """
    test_cases = [
        {
            "cereal_name": "Seven Sundays Cereal",
            "ingredients": "Sorghum Flakes, Almonds, Coconut Sugar, Salt",
            "expected_assessment": "Generally healthy with whole grains and natural ingredients"
        },
        {
            "cereal_name": "Holy Crap Organic Cereal",
            "ingredients": "Organic Chia Seeds, Organic Buckwheat Kernels, Organic Hulled Hemp Seeds",
            "expected_assessment": "Very healthy with organic seeds and no additives"
        },
        {
            "cereal_name": "Post Honey Bunch Oats",
            "ingredients": "Corn, Whole Grain Wheat, Sugar, Whole Grain Rolled Oats, Almonds, Rice, Canola Oil, Corn Syrup, Dried Bananas, Salt, Barley Malt Extract, Molasses, Cinnamon, Honey, Caramel Color, Natural Flavor, BHT Added To Preserve Freshness",
            "expected_assessment": "Contains concerning ingredients like BHT, corn syrup, and caramel color"
        },
        {
            "cereal_name": "RX Cereal",
            "ingredients": "Brown Rice, Almonds, Whole Grain Sorghum, Coconut Sugar, Pea Protein, Honey, Cocoa, Chocolate, Salt, Natural Flavors, Rosemary, Extract",
            "expected_assessment": "Mostly healthy but contains 'Natural Flavors' which can be ambiguous"
        }
    ]
    
    return test_cases


def run_rag_evaluation(test_cases: List[Dict[str, str]]):
    """
    Run RAG evaluation using RAGAS metrics.
    
    Args:
        test_cases: List of test cases with cereal data
    """
    print("\n" + "="*80)
    print("RAGAS RAG EVALUATION FOR KIDSAFE FOOD ANALYZER")
    print("="*80 + "\n")
    
    # Initialize models
    print("Initializing models...")
    openai_key = os.environ['OPENAI_API_KEY']
    
    # Models for the RAG system
    chat_model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    
    # Models for RAGAS evaluation (using wrapper)
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=openai_key))
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key))
    
    # Initialize RAG system
    print("Initializing vector store and RAG engine...")
    vector_store_manager = VectorStoreManager(openai_key)
    vectorstore = vector_store_manager.load_and_index_documents()
    retriever = vector_store_manager.get_retriever(k=5)
    
    ingredient_analyzer = IngredientAnalyzer(retriever, openai_key)
    
    # Collect samples for evaluation
    samples = []
    
    print("\n" + "-"*80)
    print("RUNNING ANALYSIS ON TEST CASES")
    print("-"*80 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}/{len(test_cases)}: {test_case['cereal_name']}")
        print(f"Ingredients: {test_case['ingredients'][:80]}...")
        
        # Create question
        question = f"Analyze these ingredients for {test_case['cereal_name']}: {test_case['ingredients']}"
        
        # Get retrieval context
        retrieved_docs = retriever.invoke(question)
        contexts = [doc.page_content for doc in retrieved_docs]
        
        # Get response
        response = ingredient_analyzer.analyze_ingredients(
            test_case['cereal_name'],
            test_case['ingredients']
        )
        
        print(f"Analysis generated ({len(response)} characters)")
        
        # Create RAGAS sample
        sample = SingleTurnSample(
            user_input=question,
            response=response,
            retrieved_contexts=contexts,
            reference=test_case['expected_assessment']  # Ground truth
        )
        samples.append(sample)
    
    # Create evaluation dataset
    print("\n" + "-"*80)
    print("CREATING EVALUATION DATASET")
    print("-"*80)
    
    eval_dataset = EvaluationDataset(samples=samples)
    print(f"Created dataset with {len(samples)} samples")
    
    # Define metrics
    metrics = [
        Faithfulness(),  # Is the response grounded in the retrieved context?
        ResponseRelevancy(),  # Does the response address the question?
        LLMContextRecall(),  # Were ground-truth facts retrieved?
        ContextEntityRecall(),  # Are key entities from ground truth in context?
        FactualCorrectness()  # Are facts accurate compared to reference?
    ]
    
    print(f"\nEvaluating with {len(metrics)} metrics:")
    for metric in metrics:
        print(f"  - {metric.name}")
    
    # Run evaluation
    print("\n" + "-"*80)
    print("RUNNING RAGAS EVALUATION")
    print("-"*80 + "\n")
    
    results = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings
    )
    
    # Display results
    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80 + "\n")
    
    # Convert results to dataframe for better display
    results_df = results.to_pandas()
    
    print("Individual Test Case Scores:")
    print("-"*80)
    for idx, row in results_df.iterrows():
        print(f"\nTest Case {idx + 1}: {test_cases[idx]['cereal_name']}")
        for metric in metrics:
            metric_name = metric.name
            if metric_name in row:
                score = row[metric_name]
                print(f"  {metric_name:.<40} {score:.3f}")
    
    print("\n" + "-"*80)
    print("OVERALL AVERAGE SCORES")
    print("-"*80 + "\n")
    
    for metric in metrics:
        metric_name = metric.name
        if metric_name in results_df.columns:
            avg_score = results_df[metric_name].mean()
            print(f"{metric_name:.<50} {avg_score:.3f}")
    
    print("\n" + "="*80)
    print("EVALUATION COMPLETE")
    print("="*80 + "\n")
    
    return results


def main():
    """Main evaluation function."""
    # Setup API keys
    setup_api_keys()
    
    # Create test dataset
    test_cases = create_test_dataset()
    
    print(f"\nCreated {len(test_cases)} test cases for evaluation")
    
    # Run evaluation
    results = run_rag_evaluation(test_cases)
    
    # Save results (optional)
    print("Evaluation results have been displayed above.")
    print("Check LangSmith for detailed traces: https://smith.langchain.com/")


if __name__ == "__main__":
    main()

