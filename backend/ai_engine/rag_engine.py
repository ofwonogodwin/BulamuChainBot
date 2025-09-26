"""
RAG (Retrieval-Augmented Generation) Engine
Combines vector search with language generation for intelligent medical responses
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import asyncio
from datetime import datetime
import json

# LangChain imports
from langchain.schema import Document
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.llms.base import BaseLLM

# Local imports
from .vector_store import VectorStoreManager
from .knowledge_base import MedicalKnowledgeBase

# Django imports
from django.conf import settings

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Advanced RAG engine for medical question answering
    Combines retrieval with generation for context-aware responses
    """
    
    def __init__(self, llm: Optional[BaseLLM] = None):
        """
        Initialize RAG Engine
        
        Args:
            llm: Language model instance (Gemini)
        """
        self.llm = llm
        self.vector_store = VectorStoreManager()
        self.knowledge_base = MedicalKnowledgeBase()
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            memory_key="chat_history",
            output_key="answer",
            return_messages=True
        )
        
        # Initialize knowledge base in vector store
        self._initialize_knowledge_base()
        
        # Setup prompts
        self.qa_prompt = self._create_qa_prompt()
        self.conversation_prompt = self._create_conversation_prompt()
        
        # Performance metrics
        self.metrics = {
            'total_queries': 0,
            'successful_retrievals': 0,
            'failed_retrievals': 0,
            'avg_response_time': 0.0
        }
    
    def _initialize_knowledge_base(self):
        """Initialize vector store with medical knowledge"""
        try:
            # Check if knowledge base is already loaded
            stats = self.vector_store.get_store_statistics()
            
            if not stats.get('chroma_has_documents', False):
                logger.info("Loading medical knowledge base into vector store...")
                
                # Get all knowledge as documents
                knowledge_docs = self.knowledge_base.get_all_knowledge_as_documents()
                
                # Convert to LangChain Document format
                documents = []
                for doc in knowledge_docs:
                    langchain_doc = Document(
                        page_content=doc['content'],
                        metadata=doc['metadata']
                    )
                    documents.append(langchain_doc)
                
                # Add to vector store
                success = self.vector_store.add_documents(documents, store_type="both")
                
                if success:
                    logger.info(f"Successfully loaded {len(documents)} medical documents")
                else:
                    logger.error("Failed to load medical knowledge base")
            else:
                logger.info("Medical knowledge base already loaded")
                
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
    
    def _create_qa_prompt(self) -> PromptTemplate:
        """Create prompt template for Q&A"""
        template = """You are a knowledgeable medical assistant helping patients in Uganda. 
Use the following medical context to answer the question accurately and compassionately.

Medical Context:
{context}

Question: {question}

Instructions:
1. Provide accurate medical information based on the context
2. Be empathetic and culturally sensitive
3. Always recommend consulting healthcare providers for serious symptoms
4. If emergency symptoms are mentioned, emphasize immediate medical attention
5. Include relevant local context for Uganda when appropriate
6. Mention both English and local language terms when helpful
7. If unsure, say so and recommend professional consultation

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _create_conversation_prompt(self) -> PromptTemplate:
        """Create prompt template for conversational responses"""
        template = """You are a caring medical assistant helping patients in Uganda. 
Continue this conversation naturally while providing helpful medical information.

Previous conversation:
{chat_history}

Current medical context:
{context}

Current question: {question}

Guidelines:
1. Maintain conversation continuity and remember previous context
2. Provide medically accurate information
3. Be empathetic and supportive
4. Adapt to the patient's language level and cultural background
5. Always prioritize patient safety
6. Encourage professional medical consultation when appropriate
7. Respect cultural practices while promoting evidence-based care

Response:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["chat_history", "context", "question"]
        )
    
    async def ask_question(
        self, 
        question: str, 
        conversation_id: Optional[str] = None,
        language: str = "english",
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a medical question with RAG enhancement
        
        Args:
            question: User's medical question
            conversation_id: Optional conversation ID for context
            language: Preferred language for response
            include_sources: Whether to include source information
            
        Returns:
            Response with answer and metadata
        """
        start_time = datetime.now()
        
        try:
            self.metrics['total_queries'] += 1
            
            # Step 1: Retrieve relevant context
            relevant_context = await self._retrieve_context(question)
            
            if not relevant_context:
                self.metrics['failed_retrievals'] += 1
                return await self._handle_no_context(question, language)
            
            self.metrics['successful_retrievals'] += 1
            
            # Step 2: Analyze question type
            question_analysis = self._analyze_question(question)
            
            # Step 3: Generate response
            response = await self._generate_response(
                question=question,
                context=relevant_context,
                question_type=question_analysis['type'],
                language=language,
                conversation_id=conversation_id
            )
            
            # Step 4: Post-process response
            final_response = self._post_process_response(
                response=response,
                question_analysis=question_analysis,
                include_sources=include_sources,
                relevant_docs=relevant_context.get('documents', [])
            )
            
            # Update metrics
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_metrics(response_time)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in RAG question answering: {e}")
            return {
                'success': False,
                'answer': f"I apologize, but I encountered an error processing your question. Please try again or consult a healthcare provider directly.",
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _retrieve_context(self, question: str) -> Dict[str, Any]:
        """Retrieve relevant context for the question"""
        try:
            # Multi-strategy retrieval
            context_results = {}
            
            # 1. Semantic similarity search
            semantic_docs = self.vector_store.similarity_search(
                query=question,
                k=5,
                store_type="ensemble" if self.vector_store.ensemble_retriever else "chroma"
            )
            
            # 2. Get context with scores
            scored_docs = self.vector_store.semantic_search_with_score(
                query=question,
                k=8,
                score_threshold=0.1
            )
            
            # 3. Direct knowledge base search
            kb_results = self.knowledge_base.search_knowledge(question)
            
            # 4. Symptom analysis if applicable
            symptom_analysis = None
            if self._is_symptom_question(question):
                symptoms = self._extract_symptoms(question)
                if symptoms:
                    symptom_analysis = self.knowledge_base.get_symptoms_analysis(symptoms)
            
            # Combine results
            context_results = {
                'semantic_documents': semantic_docs,
                'scored_documents': scored_docs,
                'knowledge_base_results': kb_results,
                'symptom_analysis': symptom_analysis,
                'formatted_context': self.vector_store.get_relevant_context(question, max_tokens=2000)
            }
            
            return context_results
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return {}
    
    def _analyze_question(self, question: str) -> Dict[str, Any]:
        """Analyze the type and characteristics of the question"""
        question_lower = question.lower()
        
        analysis = {
            'type': 'general',
            'urgency': 'normal',
            'categories': [],
            'requires_disclaimer': True
        }
        
        # Determine question type
        if any(word in question_lower for word in ['emergency', 'urgent', 'chest pain', 'can\'t breathe', 'unconscious']):
            analysis['type'] = 'emergency'
            analysis['urgency'] = 'high'
        elif any(word in question_lower for word in ['symptoms', 'feel', 'hurts', 'pain']):
            analysis['type'] = 'symptoms'
        elif any(word in question_lower for word in ['treatment', 'cure', 'medicine', 'medication']):
            analysis['type'] = 'treatment'
        elif any(word in question_lower for word in ['prevent', 'avoid', 'stop']):
            analysis['type'] = 'prevention'
        elif any(word in question_lower for word in ['pregnancy', 'pregnant', 'baby']):
            analysis['type'] = 'maternal_child'
            analysis['categories'].append('maternal_child_health')
        
        # Determine medical categories
        if any(word in question_lower for word in ['malaria', 'fever', 'typhoid']):
            analysis['categories'].append('infectious_diseases')
        elif any(word in question_lower for word in ['blood pressure', 'diabetes', 'heart']):
            analysis['categories'].append('non_communicable_diseases')
        elif any(word in question_lower for word in ['depression', 'anxiety', 'mental']):
            analysis['categories'].append('mental_health')
        
        return analysis
    
    def _is_symptom_question(self, question: str) -> bool:
        """Check if question is about symptoms"""
        symptom_indicators = [
            'symptoms', 'feel', 'feeling', 'hurts', 'pain', 'ache',
            'experiencing', 'having', 'suffering', 'problem with'
        ]
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in symptom_indicators)
    
    def _extract_symptoms(self, question: str) -> List[str]:
        """Extract symptoms from question text"""
        # Simple keyword extraction - can be enhanced with NLP
        common_symptoms = [
            'fever', 'headache', 'cough', 'pain', 'nausea', 'vomiting',
            'diarrhea', 'constipation', 'fatigue', 'dizziness', 'rash',
            'shortness of breath', 'chest pain', 'abdominal pain'
        ]
        
        question_lower = question.lower()
        found_symptoms = []
        
        for symptom in common_symptoms:
            if symptom in question_lower:
                found_symptoms.append(symptom)
        
        return found_symptoms
    
    async def _generate_response(
        self,
        question: str,
        context: Dict[str, Any],
        question_type: str,
        language: str,
        conversation_id: Optional[str] = None
    ) -> str:
        """Generate response using LLM with context"""
        try:
            if not self.llm:
                return self._generate_fallback_response(question, context, question_type)
            
            # Prepare context string
            context_text = context.get('formatted_context', '')
            
            # Add symptom analysis if available
            if context.get('symptom_analysis'):
                symptom_info = context['symptom_analysis']
                context_text += f"\n\nSymptom Analysis: {json.dumps(symptom_info, indent=2)}"
            
            # Choose appropriate prompt
            if conversation_id and self.memory:
                # Use conversational prompt
                prompt_input = {
                    'chat_history': self.memory.chat_memory.messages,
                    'context': context_text,
                    'question': question
                }
                prompt = self.conversation_prompt.format(**prompt_input)
            else:
                # Use Q&A prompt
                prompt_input = {
                    'context': context_text,
                    'question': question
                }
                prompt = self.qa_prompt.format(**prompt_input)
            
            # Generate response
            response = await self.llm.agenerate([prompt])
            answer = response.generations[0][0].text.strip()
            
            # Save to memory if conversation ID provided
            if conversation_id and self.memory:
                self.memory.save_context(
                    {'question': question},
                    {'answer': answer}
                )
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return self._generate_fallback_response(question, context, question_type)
    
    def _generate_fallback_response(
        self, 
        question: str, 
        context: Dict[str, Any], 
        question_type: str
    ) -> str:
        """Generate fallback response when LLM is not available"""
        
        # Emergency response
        if question_type == 'emergency':
            return ("This appears to be an emergency situation. Please seek immediate medical attention "
                   "by calling emergency services or going to the nearest hospital immediately. "
                   "Do not delay treatment for serious symptoms.")
        
        # Use knowledge base results
        kb_results = context.get('knowledge_base_results', {})
        
        response_parts = []
        
        if kb_results.get('conditions'):
            response_parts.append("Based on your question, here's some relevant medical information:")
            for condition in kb_results['conditions'][:2]:  # Top 2 conditions
                if 'condition' in condition:
                    response_parts.append(f"\n**{condition['condition']}:**")
                    if 'symptoms' in condition:
                        symptoms = condition['symptoms']
                        if isinstance(symptoms, list):
                            response_parts.append(f"Symptoms: {', '.join(symptoms[:3])}")
                    if 'treatment' in condition:
                        response_parts.append(f"Treatment: {condition['treatment']}")
        
        if kb_results.get('emergency_info'):
            response_parts.append("\n**Emergency Information:**")
            for emergency in kb_results['emergency_info'][:1]:
                response_parts.append(str(emergency))
        
        if not response_parts:
            response_parts = [
                "I understand you have a medical question. While I can provide general health information, "
                "I recommend consulting with a qualified healthcare provider for personalized medical advice."
            ]
        
        # Add disclaimer
        response_parts.append(
            "\n\n*Please note: This information is for educational purposes only and should not replace "
            "professional medical advice. Always consult with a healthcare provider for proper diagnosis "
            "and treatment.*"
        )
        
        return " ".join(response_parts)
    
    def _post_process_response(
        self,
        response: str,
        question_analysis: Dict[str, Any],
        include_sources: bool,
        relevant_docs: List[Document]
    ) -> Dict[str, Any]:
        """Post-process the generated response"""
        
        # Add emergency warning if needed
        if question_analysis.get('urgency') == 'high':
            emergency_warning = ("⚠️ **EMERGENCY ALERT**: If this is a medical emergency, "
                               "call emergency services immediately or go to the nearest hospital.")
            response = f"{emergency_warning}\n\n{response}"
        
        # Add medical disclaimer
        if question_analysis.get('requires_disclaimer', True):
            disclaimer = ("\n\n---\n*Medical Disclaimer: This information is for educational purposes only "
                         "and should not replace professional medical advice. Always consult with a "
                         "qualified healthcare provider for proper diagnosis and treatment.*")
            response += disclaimer
        
        result = {
            'success': True,
            'answer': response,
            'question_type': question_analysis.get('type', 'general'),
            'urgency': question_analysis.get('urgency', 'normal'),
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'categories': question_analysis.get('categories', []),
                'sources_available': len(relevant_docs) > 0,
                'rag_enhanced': True
            }
        }
        
        # Add source information if requested
        if include_sources and relevant_docs:
            sources = []
            for doc in relevant_docs[:3]:  # Top 3 sources
                source_info = {
                    'type': doc.metadata.get('type', 'unknown'),
                    'category': doc.metadata.get('category', 'general')
                }
                if 'condition_name' in doc.metadata:
                    source_info['condition'] = doc.metadata['condition_name']
                sources.append(source_info)
            
            result['sources'] = sources
        
        return result
    
    async def _handle_no_context(self, question: str, language: str) -> Dict[str, Any]:
        """Handle cases where no relevant context is found"""
        return {
            'success': True,
            'answer': ("I understand you have a medical question, but I don't have specific information "
                      "about this topic in my knowledge base. I recommend consulting with a qualified "
                      "healthcare provider who can give you personalized medical advice based on your "
                      "specific situation.\n\n"
                      "If this is an emergency, please seek immediate medical attention."),
            'question_type': 'general',
            'urgency': 'normal',
            'timestamp': datetime.now().isoformat(),
            'metadata': {
                'no_context_found': True,
                'recommendation': 'consult_healthcare_provider'
            }
        }
    
    def _update_metrics(self, response_time: float):
        """Update performance metrics"""
        # Update average response time
        total_queries = self.metrics['total_queries']
        current_avg = self.metrics['avg_response_time']
        
        self.metrics['avg_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history for a specific conversation"""
        if self.memory and hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            history = []
            
            for i in range(0, len(messages), 2):
                if i + 1 < len(messages):
                    history.append({
                        'question': messages[i].content,
                        'answer': messages[i + 1].content,
                        'timestamp': datetime.now().isoformat()
                    })
            
            return history
        return []
    
    def clear_conversation_history(self, conversation_id: Optional[str] = None):
        """Clear conversation history"""
        if self.memory:
            self.memory.clear()
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get RAG engine performance metrics"""
        success_rate = 0.0
        if self.metrics['total_queries'] > 0:
            success_rate = (
                self.metrics['successful_retrievals'] / self.metrics['total_queries']
            ) * 100
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'vector_store_stats': self.vector_store.get_store_statistics()
        }
    
    async def add_new_knowledge(self, knowledge_data: Dict[str, Any]) -> bool:
        """Add new medical knowledge to the system"""
        try:
            # Add to vector store
            success = self.vector_store.add_medical_knowledge(knowledge_data)
            
            if success:
                logger.info("Successfully added new medical knowledge")
                return True
            else:
                logger.error("Failed to add new medical knowledge")
                return False
                
        except Exception as e:
            logger.error(f"Error adding new knowledge: {e}")
            return False
