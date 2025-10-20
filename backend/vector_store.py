"""
Vector store setup and management using Qdrant.
"""

from typing import Optional
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from backend.config import (
    FOOD_LABELING_PDF,
    QDRANT_COLLECTION_NAME,
    QDRANT_LOCATION,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    EMBEDDING_MODEL
)


class VectorStoreManager:
    """Manages the Qdrant vector store for food safety knowledge."""
    
    def __init__(self, openai_api_key: str):
        """
        Initialize the vector store manager.
        
        Args:
            openai_api_key: OpenAI API key for embeddings
        """
        self.openai_api_key = openai_api_key
        self.embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=openai_api_key
        )
        self.vectorstore: Optional[QdrantVectorStore] = None
        self.client: Optional[QdrantClient] = None
        self.chunks = []  # Store chunks for advanced retrieval
        
    def load_and_index_documents(self) -> QdrantVectorStore:
        """
        Load PDF documents, split into chunks, and create vector store.
        
        Returns:
            QdrantVectorStore instance
        """
        # Load PDF
        print(f"Loading PDF from {FOOD_LABELING_PDF}...")
        loader = PyMuPDFLoader(str(FOOD_LABELING_PDF))
        documents = loader.load()
        print(f"Loaded {len(documents)} pages from PDF")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DEFAULT_CHUNK_SIZE,
            chunk_overlap=DEFAULT_CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )
        self.chunks = text_splitter.split_documents(documents)
        print(f"Split into {len(self.chunks)} chunks")
        
        # Create Qdrant client
        self.client = QdrantClient(location=QDRANT_LOCATION)
        
        # Create vector store
        print("Creating vector store and generating embeddings...")
        self.vectorstore = QdrantVectorStore.from_documents(
            self.chunks,
            self.embeddings,
            location=QDRANT_LOCATION,
            collection_name=QDRANT_COLLECTION_NAME,
        )
        print("Vector store created successfully!")
        
        return self.vectorstore
    
    def get_chunks(self):
        """
        Get the document chunks for advanced retrieval strategies.
        
        Returns:
            List of document chunks
        """
        return self.chunks
    
    def get_retriever(self, k: int = 5):
        """
        Get a retriever from the vector store.
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever instance
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call load_and_index_documents() first.")
        
        return self.vectorstore.as_retriever(search_kwargs={"k": k})

