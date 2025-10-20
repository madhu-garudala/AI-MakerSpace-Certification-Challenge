"""
RAGAS Evaluation Script for Golden Test Dataset
Evaluates the RAG pipeline using key metrics: Faithfulness, Response Relevance, Context Precision, Context Recall
"""

import os
import getpass
import pandas as pd
from typing import List, Dict
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics import (
    Faithfulness,
    ContextPrecision,
    ContextRecall,
    ResponseRelevancy
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from backend.vector_store import VectorStoreManager
from backend.rag_engine import IngredientAnalyzer
from backend.advanced_retrieval import AdvancedRetrievalManager


def setup_api_keys():
    """Prompt for API keys if not already set."""
    if not os.environ.get('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY'] = getpass.getpass("Enter your OpenAI API key: ")
    
    if not os.environ.get('LANGCHAIN_API_KEY'):
        os.environ['LANGCHAIN_API_KEY'] = getpass.getpass("Enter your LangSmith API key: ")
    
    cohere_key = input("Enter your Cohere API key (or press Enter to skip): ").strip()
    if cohere_key:
        os.environ['COHERE_API_KEY'] = cohere_key
    
    # Enable LangSmith tracing
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_PROJECT'] = 'KidSafe-RAGAS-Evaluation'


def create_golden_test_dataset() -> List[Dict[str, str]]:
    """
    Create a golden test dataset with ground truth for RAGAS evaluation.
    
    Each test case includes:
    - cereal_name: Name of the product
    - ingredients: Ingredient list
    - user_input: Query/question
    - reference_answer: Ground truth answer for comparison
    - expected_verdict: Expected GOOD/BAD classification
    
    Returns:
        List of test cases
    """
    test_cases = [
        {
            "cereal_name": "Holy Crap Organic Cereal",
            "ingredients": "Organic Chia Seeds, Organic Buckwheat Kernels, Organic Hulled Hemp Seeds",
            "user_input": "Analyze the ingredients in Holy Crap Organic Cereal for child safety and nutrition",
            "reference_answer": "This cereal is very healthy and safe for children. It contains only three organic whole food ingredients: chia seeds (rich in omega-3 fatty acids and fiber), buckwheat (gluten-free whole grain with protein), and hemp seeds (complete protein source with healthy fats). There are no additives, preservatives, artificial ingredients, or added sugars. All ingredients are organic and provide excellent nutrition for children.",
            "expected_verdict": "GOOD"
        },
        {
            "cereal_name": "Post Honey Bunch Oats with BHT",
            "ingredients": "Corn, Whole Grain Wheat, Sugar, Corn Syrup, Canola Oil, Salt, Caramel Color, Natural Flavor, BHT Added To Preserve Freshness",
            "user_input": "Analyze the ingredients in Post Honey Bunch Oats for child safety",
            "reference_answer": "This cereal has several concerning ingredients for children. BHT (butylated hydroxytoluene) is a synthetic preservative that has raised health concerns and is banned in some countries. Corn syrup is a highly processed sweetener that provides empty calories. Caramel color can contain potentially harmful compounds formed during processing. Natural flavors is a vague term that doesn't specify what flavoring agents are used. The high sugar content is also concerning for children's health.",
            "expected_verdict": "BAD"
        },
        {
            "cereal_name": "Seven Sundays Cereal",
            "ingredients": "Sorghum Flakes, Almonds, Coconut Sugar, Salt",
            "user_input": "Is Seven Sundays Cereal safe and healthy for children?",
            "reference_answer": "This cereal is generally good for children. Sorghum is a nutritious whole grain that's gluten-free and high in fiber and protein. Almonds provide healthy fats, protein, and vitamin E. Coconut sugar is a less processed sweetener with a lower glycemic index than regular sugar, though still should be consumed in moderation. Salt in small amounts is acceptable. The ingredient list is short and contains recognizable whole food ingredients with no artificial additives or preservatives.",
            "expected_verdict": "GOOD"
        },
        {
            "cereal_name": "Generic Cereal with Natural Flavors",
            "ingredients": "Whole Grain Wheat, Sugar, Natural Flavors, Citric Acid, Vitamin E",
            "user_input": "What concerns should parents have about cereals with natural flavors?",
            "reference_answer": "Natural flavors is a concerning ingredient because it's a vague term that can include many different substances. Despite the word 'natural', these flavors are highly processed chemical compounds derived from natural sources. The FDA allows thousands of chemicals under this label without requiring disclosure of specific ingredients. For children, this lack of transparency is problematic as some natural flavors may contain allergens or ingredients parents would prefer to avoid. Parents should be aware that 'natural' doesn't necessarily mean healthy or minimally processed.",
            "expected_verdict": "NEUTRAL/CONCERNING"
        },
        {
            "cereal_name": "Earth's Best Oatmeal Cereal",
            "ingredients": "Organic Whole Grain Oat Flour, Alpha Amylase, Tocopherols, Electrolytic Iron",
            "user_input": "Analyze Earth's Best Oatmeal Cereal ingredients for children",
            "reference_answer": "This cereal is good for children. Organic whole grain oat flour is nutritious, providing fiber, protein, and minerals. Alpha amylase is an enzyme that helps break down starches and is safe. Tocopherols are forms of vitamin E, a beneficial antioxidant. Electrolytic iron is added for fortification and is an important mineral for children's development. All ingredients are safe and beneficial, with organic certification ensuring no pesticides or synthetic fertilizers were used.",
            "expected_verdict": "GOOD"
        },
        {
            "cereal_name": "Processed Cereal with Multiple Additives",
            "ingredients": "Corn Flour, Sugar, Corn Syrup, Hydrogenated Vegetable Oil, Artificial Colors (Red 40, Yellow 5), BHA, BHT, Artificial Flavors, TBHQ",
            "user_input": "Evaluate this cereal's safety for children",
            "reference_answer": "This cereal is very concerning for children and should be avoided. It contains multiple problematic ingredients: hydrogenated oils (trans fats linked to heart disease), artificial colors Red 40 and Yellow 5 (linked to hyperactivity in children), BHA and BHT (synthetic preservatives with potential health risks), TBHQ (another preservative with safety concerns), and artificial flavors (unspecified chemical compounds). The high sugar and corn syrup content provides empty calories. This product has no nutritional value and contains multiple ingredients that should not be in children's diets.",
            "expected_verdict": "BAD"
        },
        {
            "cereal_name": "RX Cereal",
            "ingredients": "Brown Rice, Almonds, Whole Grain Sorghum, Coconut Sugar, Pea Protein, Honey, Cocoa, Chocolate, Salt, Natural Flavors, Rosemary Extract",
            "user_input": "Is RX Cereal a healthy choice for children?",
            "reference_answer": "This cereal is mostly good for children with one minor concern. Positive ingredients include brown rice and sorghum (whole grains), almonds (healthy fats and protein), pea protein (plant-based protein), honey (natural sweetener in moderation), cocoa and chocolate (antioxidants), and rosemary extract (natural preservative). However, 'natural flavors' is concerning because it's a vague term that doesn't specify what flavoring agents are used, and these can be highly processed despite being from natural sources. Overall, the cereal is nutritious with mostly whole food ingredients, but the natural flavors reduce transparency.",
            "expected_verdict": "MOSTLY GOOD"
        }
    ]
    
    return test_cases


def run_ragas_evaluation(retrieval_strategy: str = "ensemble"):
    """
    Run comprehensive RAGAS evaluation on the golden test dataset.
    
    Args:
        retrieval_strategy: Which retrieval strategy to use (naive, bm25, ensemble, etc.)
    """
    print("\n" + "="*100)
    print("RAGAS EVALUATION: KIDSAFE FOOD ANALYZER - GOLDEN TEST DATASET")
    print("="*100 + "\n")
    
    # Initialize models
    print("Initializing models...")
    openai_key = os.environ['OPENAI_API_KEY']
    cohere_key = os.environ.get('COHERE_API_KEY')
    
    # Models for RAG system
    chat_model = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", api_key=openai_key)
    
    # Models for RAGAS evaluation
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", api_key=openai_key))
    evaluator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(
        model="text-embedding-3-small", 
        api_key=openai_key
    ))
    
    # Initialize RAG system
    print("Initializing vector store and RAG engine...")
    vector_store_manager = VectorStoreManager(openai_key)
    vectorstore = vector_store_manager.load_and_index_documents()
    chunks = vector_store_manager.get_chunks()
    
    print(f"Initializing advanced retrieval with strategy: {retrieval_strategy}")
    advanced_retrieval_manager = AdvancedRetrievalManager(
        vectorstore=vectorstore,
        documents=chunks,
        openai_api_key=openai_key,
        cohere_api_key=cohere_key if cohere_key else None
    )
    
    # Get retriever based on strategy
    if retrieval_strategy == 'naive':
        retriever = advanced_retrieval_manager.get_naive_retriever(k=5)
    elif retrieval_strategy == 'bm25':
        retriever = advanced_retrieval_manager.get_bm25_retriever(k=5)
    elif retrieval_strategy == 'ensemble':
        use_compression = bool(cohere_key)
        retriever = advanced_retrieval_manager.get_ensemble_retriever(k=5, use_compression=use_compression)
    else:
        print(f"Unknown strategy {retrieval_strategy}, using ensemble")
        use_compression = bool(cohere_key)
        retriever = advanced_retrieval_manager.get_ensemble_retriever(k=5, use_compression=use_compression)
    
    ingredient_analyzer = IngredientAnalyzer(
        retriever, 
        openai_key,
        retrieval_strategy=retrieval_strategy
    )
    
    # Create golden test dataset
    test_cases = create_golden_test_dataset()
    print(f"\nCreated golden test dataset with {len(test_cases)} test cases")
    
    # Collect samples for evaluation
    samples = []
    
    print("\n" + "-"*100)
    print("RUNNING ANALYSIS ON GOLDEN TEST CASES")
    print("-"*100 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}/{len(test_cases)}: {test_case['cereal_name']}")
        print(f"Expected Verdict: {test_case['expected_verdict']}")
        print(f"Ingredients: {test_case['ingredients'][:80]}...")
        
        # Get retrieval context
        retrieved_docs = retriever.invoke(test_case['user_input'])
        contexts = [doc.page_content for doc in retrieved_docs]
        
        print(f"Retrieved {len(contexts)} context chunks")
        
        # Get response
        response = ingredient_analyzer.analyze_ingredients(
            test_case['cereal_name'],
            test_case['ingredients']
        )
        
        print(f"Analysis generated ({len(response)} characters)")
        
        # Check if verdict matches
        verdict_match = test_case['expected_verdict'].upper() in response.upper()
        print(f"Verdict match: {'✅' if verdict_match else '❌'}")
        
        # Create RAGAS sample
        sample = SingleTurnSample(
            user_input=test_case['user_input'],
            response=response,
            retrieved_contexts=contexts,
            reference=test_case['reference_answer']
        )
        samples.append(sample)
    
    # Create evaluation dataset
    print("\n" + "-"*100)
    print("CREATING RAGAS EVALUATION DATASET")
    print("-"*100)
    
    eval_dataset = EvaluationDataset(samples=samples)
    print(f"Created dataset with {len(samples)} samples")
    
    # Define RAGAS metrics
    metrics = [
        Faithfulness(),           # Is response grounded in retrieved context?
        ResponseRelevancy(),      # Does response address the user query?
        ContextPrecision(),       # Are relevant contexts ranked higher?
        ContextRecall()          # Were all relevant facts from reference retrieved?
    ]
    
    print(f"\nEvaluating with {len(metrics)} RAGAS metrics:")
    for metric in metrics:
        print(f"  - {metric.name}")
    
    # Run evaluation
    print("\n" + "-"*100)
    print("RUNNING RAGAS EVALUATION (this may take a few minutes...)")
    print("-"*100 + "\n")
    
    results = evaluate(
        dataset=eval_dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings
    )
    
    # Display results
    print("\n" + "="*100)
    print("RAGAS EVALUATION RESULTS")
    print("="*100 + "\n")
    
    # Convert to DataFrame
    results_df = results.to_pandas()
    
    # Add test case names for better readability
    results_df.insert(0, 'Test Case', [tc['cereal_name'] for tc in test_cases])
    results_df.insert(1, 'Expected Verdict', [tc['expected_verdict'] for tc in test_cases])
    
    # Display individual scores
    print("INDIVIDUAL TEST CASE SCORES:")
    print("-"*100)
    print(results_df.to_string(index=False))
    
    # Calculate and display averages
    print("\n" + "-"*100)
    print("OVERALL AVERAGE SCORES")
    print("-"*100 + "\n")
    
    metric_cols = [col for col in results_df.columns if col not in ['Test Case', 'Expected Verdict', 'user_input', 'response', 'retrieved_contexts', 'reference']]
    
    avg_scores = {}
    for col in metric_cols:
        if col in results_df.columns:
            avg_score = results_df[col].mean()
            avg_scores[col] = avg_score
            print(f"{col:.<50} {avg_score:.4f}")
    
    # Performance Analysis
    print("\n" + "="*100)
    print("PERFORMANCE ANALYSIS & CONCLUSIONS")
    print("="*100 + "\n")
    
    analyze_results(avg_scores, results_df, retrieval_strategy)
    
    # Save results
    output_file = f"ragas_evaluation_results_{retrieval_strategy}.csv"
    results_df.to_csv(output_file, index=False)
    print(f"\n✅ Results saved to: {output_file}")
    
    print("\n" + "="*100)
    print("EVALUATION COMPLETE")
    print("="*100 + "\n")
    
    return results_df, avg_scores


def analyze_results(avg_scores: Dict[str, float], results_df: pd.DataFrame, strategy: str):
    """
    Analyze RAGAS results and provide conclusions about pipeline performance.
    """
    print("📊 METRIC INTERPRETATION:\n")
    
    # Faithfulness
    if 'faithfulness' in avg_scores:
        faith_score = avg_scores['faithfulness']
        print(f"1. FAITHFULNESS: {faith_score:.4f}")
        if faith_score >= 0.8:
            print("   ✅ EXCELLENT - Responses are highly grounded in retrieved context")
        elif faith_score >= 0.6:
            print("   ⚠️  GOOD - Mostly factual but some unsupported claims")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Responses contain hallucinations")
        print()
    
    # Response Relevancy
    if 'response_relevancy' in avg_scores:
        rel_score = avg_scores['response_relevancy']
        print(f"2. RESPONSE RELEVANCY: {rel_score:.4f}")
        if rel_score >= 0.8:
            print("   ✅ EXCELLENT - Responses directly address user queries")
        elif rel_score >= 0.6:
            print("   ⚠️  GOOD - Generally relevant but may include tangential info")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Responses often miss the point")
        print()
    
    # Context Precision
    if 'context_precision' in avg_scores:
        prec_score = avg_scores['context_precision']
        print(f"3. CONTEXT PRECISION: {prec_score:.4f}")
        if prec_score >= 0.8:
            print("   ✅ EXCELLENT - Relevant contexts ranked at the top")
        elif prec_score >= 0.6:
            print("   ⚠️  GOOD - Some relevant contexts but ranking could improve")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Retrieval is pulling irrelevant contexts")
        print()
    
    # Context Recall
    if 'context_recall' in avg_scores:
        recall_score = avg_scores['context_recall']
        print(f"4. CONTEXT RECALL: {recall_score:.4f}")
        if recall_score >= 0.8:
            print("   ✅ EXCELLENT - Retrieved contexts contain ground truth facts")
        elif recall_score >= 0.6:
            print("   ⚠️  GOOD - Some facts retrieved but missing key information")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Many ground truth facts not retrieved")
        print()
    
    print("\n" + "-"*100)
    print("🔍 OVERALL CONCLUSIONS:\n")
    
    overall_avg = sum(avg_scores.values()) / len(avg_scores)
    print(f"Overall Pipeline Score: {overall_avg:.4f}\n")
    
    if overall_avg >= 0.8:
        print("✅ EXCELLENT PERFORMANCE")
        print("The RAG pipeline is production-ready with high accuracy across all metrics.")
    elif overall_avg >= 0.6:
        print("⚠️  GOOD PERFORMANCE")
        print("The pipeline works well but has room for improvement in specific areas.")
    else:
        print("❌ NEEDS IMPROVEMENT")
        print("The pipeline requires optimization before production deployment.")
    
    print(f"\n📈 RETRIEVAL STRATEGY: {strategy.upper()}")
    
    # Strategy-specific insights
    if strategy == 'ensemble':
        print("• Ensemble combines multiple retrievers for robust performance")
        print("• Should handle both semantic and keyword-based queries well")
    elif strategy == 'naive':
        print("• Baseline semantic search - good for understanding concepts")
        print("• May miss exact keyword matches")
    elif strategy == 'bm25':
        print("• Keyword-based search - excellent for specific terms")
        print("• May miss semantic similarities")
    
    print("\n💡 RECOMMENDATIONS:")
    
    if avg_scores.get('context_precision', 1.0) < 0.7:
        print("• Consider using ensemble retriever or adding reranking for better precision")
    
    if avg_scores.get('context_recall', 1.0) < 0.7:
        print("• Increase k (number of retrieved docs) or improve chunking strategy")
    
    if avg_scores.get('faithfulness', 1.0) < 0.7:
        print("• Strengthen prompts to emphasize using only provided context")
        print("• Consider adding explicit citations in responses")
    
    if avg_scores.get('response_relevancy', 1.0) < 0.7:
        print("• Refine prompts to focus responses on user questions")
        print("• Reduce verbose explanations in favor of direct answers")
    
    print()


def main():
    """Main evaluation function."""
    print("="*100)
    print("KIDSAFE FOOD ANALYZER - RAGAS EVALUATION")
    print("="*100 + "\n")
    
    # Setup API keys
    setup_api_keys()
    
    # Choose retrieval strategy
    print("\nAvailable retrieval strategies:")
    print("1. ensemble (recommended)")
    print("2. naive")
    print("3. bm25")
    
    choice = input("\nSelect strategy (1-3) or press Enter for ensemble: ").strip()
    
    strategy_map = {
        '1': 'ensemble',
        '2': 'naive',
        '3': 'bm25',
        '': 'ensemble'
    }
    
    strategy = strategy_map.get(choice, 'ensemble')
    
    # Run evaluation
    results_df, avg_scores = run_ragas_evaluation(retrieval_strategy=strategy)
    
    print("\n✅ Evaluation complete!")
    print(f"Check LangSmith for detailed traces: https://smith.langchain.com/")
    print(f"Project: KidSafe-RAGAS-Evaluation")


if __name__ == "__main__":
    main()

