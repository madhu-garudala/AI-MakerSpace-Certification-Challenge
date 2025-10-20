"""
Advanced Retrieval Strategies for KidSafe Food Analyzer.

Implements multiple retrieval strategies that can be used individually or combined:
- Naive Vector Search (baseline)
- BM25 (sparse keyword search)
- Multi-Query (LLM-generated query expansion)
- Compression with Cohere Rerank
- Ensemble (combines multiple strategies)
"""

from typing import List, Optional
from langchain.retrievers import EnsembleRetriever, ParentDocumentRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain_cohere import CohereRerank
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_qdrant import QdrantVectorStore


class AdvancedRetrievalManager:
    """Manages advanced retrieval strategies."""
    
    def __init__(
        self, 
        vectorstore: QdrantVectorStore,
        documents: List[Document],
        openai_api_key: str,
        cohere_api_key: Optional[str] = None
    ):
        """
        Initialize the advanced retrieval manager.
        
        Args:
            vectorstore: Qdrant vector store
            documents: Original documents for BM25
            openai_api_key: OpenAI API key
            cohere_api_key: Cohere API key (optional, for reranking)
        """
        self.vectorstore = vectorstore
        self.documents = documents
        self.openai_api_key = openai_api_key
        self.cohere_api_key = cohere_api_key
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_api_key)
        
    def get_naive_retriever(self, k: int = 5):
        """
        Get naive vector search retriever (baseline).
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever instance
        """
        return self.vectorstore.as_retriever(search_kwargs={"k": k})
    
    def get_bm25_retriever(self, k: int = 5):
        """
        Get BM25 retriever for sparse keyword-based search.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            BM25Retriever instance
        """
        return BM25Retriever.from_documents(self.documents, k=k)
    
    def get_multi_query_retriever(self, k: int = 5):
        """
        Get multi-query retriever that generates multiple query variants.
        
        Uses LLM to generate different perspectives of the query
        for better recall.
        
        Args:
            k: Number of documents to retrieve per query
            
        Returns:
            MultiQueryRetriever instance
        """
        base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        return MultiQueryRetriever.from_llm(
            retriever=base_retriever,
            llm=self.llm
        )
    
    def get_compression_retriever(self, k: int = 10, top_n: int = 5):
        """
        Get compression retriever with Cohere reranking.
        
        Retrieves more documents (k) then reranks and compresses to top_n.
        Requires Cohere API key.
        
        Args:
            k: Number of documents to retrieve initially
            top_n: Number of documents after reranking
            
        Returns:
            ContextualCompressionRetriever instance or None if no Cohere key
        """
        if not self.cohere_api_key:
            print("Warning: Cohere API key not provided. Compression retriever unavailable.")
            return None
        
        base_retriever = self.vectorstore.as_retriever(search_kwargs={"k": k})
        
        # Cohere Rerank for compression
        compressor = CohereRerank(
            model="rerank-english-v3.0",
            cohere_api_key=self.cohere_api_key,
            top_n=top_n
        )
        
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
    
    def get_parent_document_retriever(
        self, 
        child_chunk_size: int = 400,
        parent_chunk_size: int = 1000,
        k: int = 5
    ):
        """
        Get parent document retriever (small-to-big retrieval).
        
        Searches with small chunks but returns larger parent chunks
        for better context.
        
        Args:
            child_chunk_size: Size of child chunks for search
            parent_chunk_size: Size of parent chunks to return
            k: Number of documents to retrieve
            
        Returns:
            ParentDocumentRetriever instance
        """
        # Child splitter for search
        child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=50
        )
        
        # Parent splitter for retrieval
        parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=200
        )
        
        # In-memory store for parent documents
        store = InMemoryStore()
        
        retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=store,
            child_splitter=child_splitter,
            parent_splitter=parent_splitter,
            search_kwargs={"k": k}
        )
        
        # Add documents
        retriever.add_documents(self.documents)
        
        return retriever
    
    def get_ensemble_retriever(
        self, 
        k: int = 5,
        use_compression: bool = True,
        weights: Optional[List[float]] = None
    ):
        """
        Get ensemble retriever that combines multiple strategies.
        
        Combines naive vector search, BM25, and optionally compression
        using Reciprocal Rank Fusion (RRF).
        
        Args:
            k: Number of documents to retrieve per retriever
            use_compression: Whether to include compression retriever
            weights: Custom weights for each retriever (must sum to 1.0)
            
        Returns:
            EnsembleRetriever instance
        """
        # Build list of retrievers
        retrievers = []
        
        # 1. Naive vector search
        naive_retriever = self.get_naive_retriever(k=k)
        retrievers.append(naive_retriever)
        
        # 2. BM25 keyword search
        bm25_retriever = self.get_bm25_retriever(k=k)
        retrievers.append(bm25_retriever)
        
        # 3. Multi-query expansion (optional - adds latency)
        # multi_query_retriever = self.get_multi_query_retriever(k=k)
        # retrievers.append(multi_query_retriever)
        
        # 4. Compression with Cohere (if available)
        if use_compression and self.cohere_api_key:
            compression_retriever = self.get_compression_retriever(k=k*2, top_n=k)
            if compression_retriever:
                retrievers.append(compression_retriever)
        
        # Set default weights if not provided
        if weights is None:
            # Equal weights for all retrievers
            weights = [1.0 / len(retrievers)] * len(retrievers)
        
        if len(weights) != len(retrievers):
            raise ValueError(f"Number of weights ({len(weights)}) must match number of retrievers ({len(retrievers)})")
        
        print(f"Creating ensemble with {len(retrievers)} retrievers:")
        print(f"  1. Naive Vector Search (weight: {weights[0]:.2f})")
        print(f"  2. BM25 Keyword Search (weight: {weights[1]:.2f})")
        if len(retrievers) > 2:
            print(f"  3. Cohere Rerank (weight: {weights[2]:.2f})")
        
        return EnsembleRetriever(
            retrievers=retrievers,
            weights=weights
        )
    
    def compare_retrievers(self, query: str, k: int = 5):
        """
        Compare different retrieval strategies for a given query.
        
        Useful for debugging and understanding retrieval performance.
        
        Args:
            query: Query to test
            k: Number of documents to retrieve
            
        Returns:
            Dictionary with results from each retriever
        """
        results = {}
        
        print(f"\n{'='*80}")
        print(f"RETRIEVAL COMPARISON FOR QUERY: {query[:100]}...")
        print(f"{'='*80}\n")
        
        # Test naive retriever
        print("1. Testing Naive Vector Search...")
        naive = self.get_naive_retriever(k=k)
        results['naive'] = naive.invoke(query)
        print(f"   Retrieved {len(results['naive'])} documents")
        
        # Test BM25
        print("\n2. Testing BM25 Keyword Search...")
        bm25 = self.get_bm25_retriever(k=k)
        results['bm25'] = bm25.invoke(query)
        print(f"   Retrieved {len(results['bm25'])} documents")
        
        # Test compression if available
        if self.cohere_api_key:
            print("\n3. Testing Compression with Cohere Rerank...")
            compression = self.get_compression_retriever(k=k*2, top_n=k)
            if compression:
                results['compression'] = compression.invoke(query)
                print(f"   Retrieved {len(results['compression'])} documents")
        
        # Test ensemble
        print("\n4. Testing Ensemble Retriever...")
        ensemble = self.get_ensemble_retriever(k=k, use_compression=bool(self.cohere_api_key))
        results['ensemble'] = ensemble.invoke(query)
        print(f"   Retrieved {len(results['ensemble'])} documents")
        
        print(f"\n{'='*80}\n")
        
        return results

