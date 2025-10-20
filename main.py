import os
import csv
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Global variables for backend components
vector_store_manager = None
ingredient_analyzer = None
advanced_retrieval_manager = None
api_keys = {}
current_retrieval_strategy = "ensemble"  # Default to ensemble

def load_cereals():
    """Load cereal names from the cereal.csv file."""
    cereals = []
    data_file = os.path.join(os.path.dirname(__file__), 'Data', 'cereal.csv')
    
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Brand_Name'):
                cereals.append({
                    'brand': row['Brand_Name'],
                    'ingredients': row.get('Ingredients', '')
                })
    
    return cereals

@app.route('/')
def index():
    """Serve the main page."""
    cereals = load_cereals()
    return render_template('index.html', cereals=cereals)

@app.route('/api/cereals')
def get_cereals():
    """API endpoint to get cereal list."""
    cereals = load_cereals()
    return jsonify(cereals)

@app.route('/api/configure', methods=['POST'])
def configure_api_keys():
    """Configure API keys and initialize the RAG system."""
    global vector_store_manager, ingredient_analyzer, advanced_retrieval_manager, api_keys, current_retrieval_strategy
    
    try:
        data = request.get_json()
        
        # Validate required keys
        required_keys = ['openai_api_key', 'langsmith_api_key']
        missing_keys = [key for key in required_keys if not data.get(key)]
        
        if missing_keys:
            return jsonify({
                'success': False,
                'error': f'Missing required API keys: {", ".join(missing_keys)}'
            }), 400
        
        # Store API keys
        api_keys = {
            'openai_api_key': data['openai_api_key'],
            'langsmith_api_key': data['langsmith_api_key'],
            'cohere_api_key': data.get('cohere_api_key', ''),
            'tavily_api_key': data.get('tavily_api_key', '')
        }
        
        # Get retrieval strategy from request (default to ensemble)
        retrieval_strategy = data.get('retrieval_strategy', 'ensemble')
        current_retrieval_strategy = retrieval_strategy
        
        # Set environment variables for LangSmith tracing
        os.environ['OPENAI_API_KEY'] = api_keys['openai_api_key']
        os.environ['LANGCHAIN_API_KEY'] = api_keys['langsmith_api_key']
        os.environ['LANGCHAIN_TRACING_V2'] = 'true'
        os.environ['LANGCHAIN_PROJECT'] = 'KidSafe-Food-Analyzer'
        
        if api_keys['cohere_api_key']:
            os.environ['COHERE_API_KEY'] = api_keys['cohere_api_key']
        
        if api_keys['tavily_api_key']:
            os.environ['TAVILY_API_KEY'] = api_keys['tavily_api_key']
        
        # Initialize vector store and RAG system
        from backend.vector_store import VectorStoreManager
        from backend.rag_engine import IngredientAnalyzer
        from backend.advanced_retrieval import AdvancedRetrievalManager
        
        print("Initializing vector store...")
        vector_store_manager = VectorStoreManager(api_keys['openai_api_key'])
        vectorstore = vector_store_manager.load_and_index_documents()
        chunks = vector_store_manager.get_chunks()
        
        print("Initializing advanced retrieval manager...")
        advanced_retrieval_manager = AdvancedRetrievalManager(
            vectorstore=vectorstore,
            documents=chunks,
            openai_api_key=api_keys['openai_api_key'],
            cohere_api_key=api_keys['cohere_api_key'] if api_keys['cohere_api_key'] else None
        )
        
        # Select retriever based on strategy
        print(f"Selecting retrieval strategy: {retrieval_strategy}")
        if retrieval_strategy == 'naive':
            retriever = advanced_retrieval_manager.get_naive_retriever(k=5)
        elif retrieval_strategy == 'bm25':
            retriever = advanced_retrieval_manager.get_bm25_retriever(k=5)
        elif retrieval_strategy == 'multi_query':
            retriever = advanced_retrieval_manager.get_multi_query_retriever(k=5)
        elif retrieval_strategy == 'compression':
            retriever = advanced_retrieval_manager.get_compression_retriever(k=10, top_n=5)
            if retriever is None:
                # Fall back to naive if compression unavailable
                print("Compression unavailable, falling back to naive")
                retriever = advanced_retrieval_manager.get_naive_retriever(k=5)
                retrieval_strategy = 'naive'
        elif retrieval_strategy == 'ensemble':
            use_compression = bool(api_keys['cohere_api_key'])
            retriever = advanced_retrieval_manager.get_ensemble_retriever(k=5, use_compression=use_compression)
        else:
            # Default to ensemble
            use_compression = bool(api_keys['cohere_api_key'])
            retriever = advanced_retrieval_manager.get_ensemble_retriever(k=5, use_compression=use_compression)
        
        print("Initializing ingredient analyzer...")
        ingredient_analyzer = IngredientAnalyzer(
            retriever, 
            api_keys['openai_api_key'],
            retrieval_strategy=retrieval_strategy
        )
        
        message = f'API keys configured and RAG system initialized with {retrieval_strategy} retrieval!'
        
        return jsonify({
            'success': True,
            'message': message,
            'retrieval_strategy': retrieval_strategy
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_ingredients():
    """Analyze ingredients for a cereal product."""
    global ingredient_analyzer
    
    try:
        # Check if system is initialized
        if ingredient_analyzer is None:
            return jsonify({
                'success': False,
                'error': 'System not initialized. Please configure API keys first.'
            }), 400
        
        data = request.get_json()
        cereal_name = data.get('cereal_name')
        ingredients = data.get('ingredients')
        
        if not cereal_name or not ingredients:
            return jsonify({
                'success': False,
                'error': 'Missing cereal_name or ingredients'
            }), 400
        
        print(f"Analyzing ingredients for: {cereal_name}")
        
        # Perform analysis
        analysis = ingredient_analyzer.analyze_ingredients(cereal_name, ingredients)
        
        return jsonify({
            'success': True,
            'cereal_name': cereal_name,
            'ingredients': ingredients,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status')
def get_status():
    """Check if the RAG system is initialized."""
    return jsonify({
        'initialized': ingredient_analyzer is not None,
        'has_api_keys': bool(api_keys)
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
