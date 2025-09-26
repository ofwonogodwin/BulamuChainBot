"""
Vector Store Manager for Medical Knowledge Base
Handles vector embeddings, similarity search, and document retrieval
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import numpy as np
from datetime import datetime

# LangChain imports
try:
    from langchain_community.vectorstores import Chroma, FAISS
    from langchain.embeddings import GoogleGenerativeAIEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.document_loaders import TextLoader, DirectoryLoader
    from langchain.schema import Document
    from langchain_community.retrievers import BM25Retriever
    try:
        from langchain.retrievers import EnsembleRetriever
    except ImportError:
        EnsembleRetriever = None
    VECTOR_STORES_AVAILABLE = True
except ImportError:
    # Fallback imports or stubs
    VECTOR_STORES_AVAILABLE = False
    Chroma = None
    FAISS = None
    GoogleGenerativeAIEmbeddings = None
    BM25Retriever = None
    EnsembleRetriever = None
    # Create a simple Document class for fallback
    class Document:
        def __init__(self, page_content: str, metadata: dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}
    
    # Create a simple text splitter for fallback
    class RecursiveCharacterTextSplitter:
        def __init__(self, chunk_size=1000, chunk_overlap=200, **kwargs):
            self.chunk_size = chunk_size
            self.chunk_overlap = chunk_overlap
        
        def split_documents(self, documents):
            return documents  # Simple fallback - return as is

# Django imports
from django.conf import settings

logger = logging.getLogger(__name__)

class VectorStoreManager:
    """
    Manages vector stores for medical knowledge retrieval
    Supports multiple embedding models and retrieval strategies
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize Vector Store Manager
        
        Args:
            persist_directory: Directory to persist vector store
        """
        self.persist_directory = persist_directory or os.path.join(
            settings.BASE_DIR, 'ai_engine', 'vector_stores'
        )
        
        # Create directories if they don't exist
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings
        self.embeddings = self._initialize_embeddings()
        
        # Initialize vector stores
        self.chroma_store = None
        self.faiss_store = None
        self.bm25_retriever = None
        self.ensemble_retriever = None
        
        # Text splitter for document processing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        self._load_or_create_stores()
    
    def _initialize_embeddings(self):
        """Initialize embedding model"""
        try:
            if not VECTOR_STORES_AVAILABLE:
                logger.warning("Vector stores not available. Using mock embeddings.")
                return MockEmbeddings()
                
            api_key = getattr(settings, 'GOOGLE_GEMINI_API_KEY', '')
            if api_key and GoogleGenerativeAIEmbeddings:
                return GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=api_key
                )
            else:
                logger.warning("No Gemini API key found or embeddings unavailable. Using mock embeddings.")
                return MockEmbeddings()
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            return MockEmbeddings()
    
    def _load_or_create_stores(self):
        """Load existing vector stores or create new ones"""
        try:
            if not VECTOR_STORES_AVAILABLE:
                logger.warning("Vector stores not available. Running in fallback mode.")
                return
                
            # Try to load existing Chroma store
            if Chroma:
                chroma_path = os.path.join(self.persist_directory, 'chroma')
                if os.path.exists(chroma_path):
                    self.chroma_store = Chroma(
                        persist_directory=chroma_path,
                        embedding_function=self.embeddings
                    )
                    logger.info("Loaded existing Chroma vector store")
                else:
                    # Create new Chroma store
                    self.chroma_store = Chroma(
                        persist_directory=chroma_path,
                        embedding_function=self.embeddings
                    )
                    logger.info("Created new Chroma vector store")
            
            # Try to load existing FAISS store
            if FAISS:
                faiss_path = os.path.join(self.persist_directory, 'faiss')
                if os.path.exists(faiss_path):
                    self.faiss_store = FAISS.load_local(
                        faiss_path, 
                        self.embeddings
                    )
                    logger.info("Loaded existing FAISS vector store")
            
        except Exception as e:
            logger.error(f"Error loading vector stores: {e}")
    
    def add_documents(self, documents: List[Document], store_type: str = "chroma") -> bool:
        """
        Add documents to vector store
        
        Args:
            documents: List of Document objects
            store_type: Type of store to use ("chroma", "faiss", or "both")
            
        Returns:
            Success status
        """
        try:
            if not VECTOR_STORES_AVAILABLE:
                logger.warning("Vector stores not available. Skipping document addition.")
                return True  # Return True to avoid breaking the flow
                
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            if store_type in ["chroma", "both"]:
                if self.chroma_store:
                    self.chroma_store.add_documents(chunks)
                    self.chroma_store.persist()
                    logger.info(f"Added {len(chunks)} chunks to Chroma store")
            
            if store_type in ["faiss", "both"]:
                if self.faiss_store:
                    self.faiss_store.add_documents(chunks)
                    faiss_path = os.path.join(self.persist_directory, 'faiss')
                    self.faiss_store.save_local(faiss_path)
                elif FAISS:
                    # Create new FAISS store
                    self.faiss_store = FAISS.from_documents(chunks, self.embeddings)
                    faiss_path = os.path.join(self.persist_directory, 'faiss')
                    self.faiss_store.save_local(faiss_path)
                    logger.info(f"Added {len(chunks)} chunks to FAISS store")
            
            # Update BM25 retriever
            self._update_bm25_retriever(chunks)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def add_medical_knowledge(self, knowledge_data: Dict[str, Any]) -> bool:
        """
        Add structured medical knowledge to vector store
        
        Args:
            knowledge_data: Dictionary containing medical information
            
        Returns:
            Success status
        """
        try:
            documents = []
            
            # Convert structured data to documents
            for category, items in knowledge_data.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            # Create document from structured data
                            content = self._format_medical_content(item, category)
                            doc = Document(
                                page_content=content,
                                metadata={
                                    'category': category,
                                    'source': 'medical_knowledge_base',
                                    'timestamp': datetime.now().isoformat(),
                                    **item
                                }
                            )
                            documents.append(doc)
                elif isinstance(items, str):
                    # Simple text content
                    doc = Document(
                        page_content=items,
                        metadata={
                            'category': category,
                            'source': 'medical_knowledge_base',
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                    documents.append(doc)
            
            return self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Error adding medical knowledge: {e}")
            return False
    
    def _format_medical_content(self, item: Dict[str, Any], category: str) -> str:
        """Format medical data into searchable content"""
        content_parts = [f"Category: {category}"]
        
        # Add common medical fields
        if 'condition' in item:
            content_parts.append(f"Condition: {item['condition']}")
        if 'symptoms' in item:
            if isinstance(item['symptoms'], list):
                content_parts.append(f"Symptoms: {', '.join(item['symptoms'])}")
            else:
                content_parts.append(f"Symptoms: {item['symptoms']}")
        if 'treatment' in item:
            content_parts.append(f"Treatment: {item['treatment']}")
        if 'prevention' in item:
            content_parts.append(f"Prevention: {item['prevention']}")
        if 'description' in item:
            content_parts.append(f"Description: {item['description']}")
        if 'emergency_signs' in item:
            if isinstance(item['emergency_signs'], list):
                content_parts.append(f"Emergency signs: {', '.join(item['emergency_signs'])}")
            else:
                content_parts.append(f"Emergency signs: {item['emergency_signs']}")
        
        return '\n'.join(content_parts)
    
    def _update_bm25_retriever(self, documents: List[Document]):
        """Update BM25 retriever with new documents"""
        try:
            if not VECTOR_STORES_AVAILABLE or not BM25Retriever:
                logger.warning("BM25 retriever not available.")
                return
                
            # Get all documents from Chroma store
            all_docs = []
            if self.chroma_store:
                # Get sample of documents for BM25
                results = self.chroma_store.similarity_search("medical health", k=1000)
                all_docs.extend(results)
            
            all_docs.extend(documents)
            
            if all_docs:
                self.bm25_retriever = BM25Retriever.from_documents(all_docs)
                self.bm25_retriever.k = 5
                
                # Create ensemble retriever combining vector and BM25
                if self.chroma_store and EnsembleRetriever:
                    vector_retriever = self.chroma_store.as_retriever(search_kwargs={"k": 5})
                    self.ensemble_retriever = EnsembleRetriever(
                        retrievers=[vector_retriever, self.bm25_retriever],
                        weights=[0.7, 0.3]  # Favor vector search slightly
                    )
                
        except Exception as e:
            logger.error(f"Error updating BM25 retriever: {e}")
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 5, 
        store_type: str = "chroma",
        filter_metadata: Optional[Dict] = None
    ) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return
            store_type: Which store to use ("chroma", "faiss", "ensemble")
            filter_metadata: Optional metadata filters
            
        Returns:
            List of relevant documents
        """
        try:
            if not VECTOR_STORES_AVAILABLE:
                logger.warning("Vector stores not available. Returning empty results.")
                return []
                
            if store_type == "chroma" and self.chroma_store:
                if filter_metadata:
                    return self.chroma_store.similarity_search(
                        query, k=k, filter=filter_metadata
                    )
                else:
                    return self.chroma_store.similarity_search(query, k=k)
            
            elif store_type == "faiss" and self.faiss_store:
                return self.faiss_store.similarity_search(query, k=k)
            
            elif store_type == "ensemble" and self.ensemble_retriever:
                return self.ensemble_retriever.get_relevant_documents(query)
            
            else:
                logger.warning(f"Store type '{store_type}' not available")
                return []
                
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def semantic_search_with_score(
        self, 
        query: str, 
        k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Tuple[Document, float]]:
        """
        Perform semantic search with similarity scores
        
        Args:
            query: Search query
            k: Number of results
            score_threshold: Minimum similarity score
            
        Returns:
            List of (document, score) tuples
        """
        try:
            if self.chroma_store:
                results = self.chroma_store.similarity_search_with_score(query, k=k)
                # Filter by score threshold
                return [(doc, score) for doc, score in results if score >= score_threshold]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error in semantic search with score: {e}")
            return []
    
    def get_relevant_context(
        self, 
        query: str, 
        max_tokens: int = 2000,
        relevance_threshold: float = 0.1
    ) -> str:
        """
        Get relevant context for RAG
        
        Args:
            query: User query
            max_tokens: Maximum tokens in context
            relevance_threshold: Minimum relevance score
            
        Returns:
            Formatted context string
        """
        try:
            # Get relevant documents with scores
            results = self.semantic_search_with_score(
                query, k=10, score_threshold=relevance_threshold
            )
            
            if not results:
                return ""
            
            # Sort by relevance score (lower is better for some distance metrics)
            results.sort(key=lambda x: x[1])
            
            # Build context within token limit
            context_parts = []
            current_tokens = 0
            
            for doc, score in results:
                content = doc.page_content
                # Rough token estimation (1 token ≈ 4 characters)
                content_tokens = len(content) // 4
                
                if current_tokens + content_tokens > max_tokens:
                    break
                
                # Add metadata for better context
                metadata_str = ""
                if doc.metadata.get('category'):
                    metadata_str = f"[{doc.metadata['category']}] "
                
                context_parts.append(f"{metadata_str}{content}")
                current_tokens += content_tokens
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting relevant context: {e}")
            return ""
    
    def update_knowledge_base(self, knowledge_file: str) -> bool:
        """
        Update knowledge base from file
        
        Args:
            knowledge_file: Path to knowledge file
            
        Returns:
            Success status
        """
        try:
            if knowledge_file.endswith('.json'):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_data = json.load(f)
                return self.add_medical_knowledge(knowledge_data)
            else:
                # Load as text documents
                loader = TextLoader(knowledge_file)
                documents = loader.load()
                return self.add_documents(documents)
                
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            return False
    
    def get_store_statistics(self) -> Dict[str, Any]:
        """Get statistics about vector stores"""
        stats = {
            'vector_stores_available': VECTOR_STORES_AVAILABLE,
            'chroma_available': self.chroma_store is not None,
            'faiss_available': self.faiss_store is not None,
            'bm25_available': self.bm25_retriever is not None,
            'ensemble_available': self.ensemble_retriever is not None,
            'persist_directory': self.persist_directory
        }
        
        try:
            if self.chroma_store:
                # Try to get document count
                sample = self.chroma_store.similarity_search("test", k=1)
                stats['chroma_has_documents'] = len(sample) > 0
        except:
            stats['chroma_has_documents'] = False
            
        return stats

class MockEmbeddings:
    """Mock embeddings for fallback when API is not available"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Return random embeddings for documents"""
        return [np.random.rand(384).tolist() for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Return random embedding for query"""
        return np.random.rand(384).tolist()
