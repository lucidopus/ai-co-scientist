import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid
import logging
from pymongo import MongoClient
from bson import ObjectId

class SimpleMemoryService:
    """Simple file-based memory service for session tracking and knowledge storage"""
    
    def __init__(self, storage_dir: str = "memory_storage"):
        self.storage_dir = storage_dir
        self.sessions_file = os.path.join(storage_dir, "sessions.json")
        self.knowledge_file = os.path.join(storage_dir, "knowledge_base.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize storage files
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage files if they don't exist"""
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump({}, f)
        
        if not os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'w') as f:
                json.dump({"hypotheses": [], "concepts": [], "experiments": []}, f)
    
    def create_session(self, query: str, user_id: str = None) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id or "anonymous",
            "query": query,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "hypotheses": [],
            "processing_steps": [],
            "metadata": {}
        }
        
        # Load existing sessions
        with open(self.sessions_file, 'r') as f:
            sessions = json.load(f)
        
        # Add new session
        sessions[session_id] = session_data
        
        # Save sessions
        with open(self.sessions_file, 'w') as f:
            json.dump(sessions, f, indent=2)
        
        return session_id
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session with new data"""
        # Load existing sessions
        with open(self.sessions_file, 'r') as f:
            sessions = json.load(f)
        
        if session_id in sessions:
            sessions[session_id].update(data)
            sessions[session_id]["last_updated"] = datetime.now().isoformat()
            
            # Save sessions
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        try:
            with open(self.sessions_file, 'r') as f:
                sessions = json.load(f)
            return sessions.get(session_id)
        except FileNotFoundError:
            return None
    
    def store_hypothesis(self, hypothesis_data: Dict[str, Any]):
        """Store hypothesis in knowledge base"""
        try:
            with open(self.knowledge_file, 'r') as f:
                knowledge = json.load(f)
            
            # Add metadata
            hypothesis_data["stored_at"] = datetime.now().isoformat()
            hypothesis_data["id"] = hypothesis_data.get("id", str(uuid.uuid4()))
            
            knowledge["hypotheses"].append(hypothesis_data)
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(knowledge, f, indent=2)
                
        except Exception as e:
            print(f"Error storing hypothesis: {e}")
    
    def store_concept(self, concept: str, related_data: Dict[str, Any] = None):
        """Store scientific concept in knowledge base"""
        try:
            with open(self.knowledge_file, 'r') as f:
                knowledge = json.load(f)
            
            concept_data = {
                "concept": concept,
                "stored_at": datetime.now().isoformat(),
                "related_data": related_data or {},
                "frequency": 1
            }
            
            # Check if concept already exists
            existing_concept = next(
                (c for c in knowledge["concepts"] if c["concept"].lower() == concept.lower()), 
                None
            )
            
            if existing_concept:
                existing_concept["frequency"] += 1
                existing_concept["last_seen"] = datetime.now().isoformat()
            else:
                knowledge["concepts"].append(concept_data)
            
            with open(self.knowledge_file, 'w') as f:
                json.dump(knowledge, f, indent=2)
                
        except Exception as e:
            print(f"Error storing concept: {e}")
    
    def get_related_hypotheses(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve related hypotheses based on query"""
        try:
            with open(self.knowledge_file, 'r') as f:
                knowledge = json.load(f)
            
            # Simple keyword matching for related hypotheses
            query_lower = query.lower()
            related = []
            
            for hypothesis in knowledge["hypotheses"]:
                title = hypothesis.get("title", "").lower()
                description = hypothesis.get("description", "").lower()
                
                # Simple relevance scoring based on keyword overlap
                relevance_score = 0
                query_words = set(query_lower.split())
                hypothesis_words = set(title.split()) | set(description.split())
                
                # Calculate overlap
                overlap = query_words & hypothesis_words
                if overlap:
                    relevance_score = len(overlap) / len(query_words)
                    hypothesis["relevance_score"] = relevance_score
                    related.append(hypothesis)
            
            # Sort by relevance and return top results
            related.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            return related[:limit]
            
        except Exception as e:
            print(f"Error retrieving related hypotheses: {e}")
            return []
    
    def get_frequent_concepts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most frequently used concepts"""
        try:
            with open(self.knowledge_file, 'r') as f:
                knowledge = json.load(f)
            
            concepts = knowledge.get("concepts", [])
            concepts.sort(key=lambda x: x.get("frequency", 0), reverse=True)
            
            return concepts[:limit]
            
        except Exception as e:
            print(f"Error retrieving frequent concepts: {e}")
            return []
    
    def cleanup_old_sessions(self, days_old: int = 30):
        """Remove sessions older than specified days"""
        try:
            with open(self.sessions_file, 'r') as f:
                sessions = json.load(f)
            
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Filter out old sessions
            active_sessions = {}
            for session_id, session_data in sessions.items():
                created_at = datetime.fromisoformat(session_data["created_at"])
                if created_at > cutoff_date:
                    active_sessions[session_id] = session_data
            
            # Save cleaned sessions
            with open(self.sessions_file, 'w') as f:
                json.dump(active_sessions, f, indent=2)
            
            print(f"Cleaned up {len(sessions) - len(active_sessions)} old sessions")
            
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")


class EnhancedMemoryService:
    """Enhanced memory system for AI Co-Scientist using MongoDB"""
    
    def __init__(self, mongo_uri: str = None, database_name: str = "ai_coscientist"):
        from utils.config import MONGODB_URI, DATABASE
        
        self.mongo_uri = mongo_uri or MONGODB_URI
        self.database_name = database_name or DATABASE
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        self.logger = logging.getLogger(__name__)
        self._init_collections()
    
    def _init_collections(self):
        """Initialize MongoDB collections with indexes"""
        try:
            # Create indexes for better performance
            self.db.hypotheses.create_index("id", unique=True)
            self.db.hypotheses.create_index("created_at")
            self.db.hypotheses.create_index("research_query")
            self.db.hypotheses.create_index("domain")
            
            self.db.evaluations.create_index("hypothesis_id")
            self.db.evaluations.create_index("agent_type")
            self.db.evaluations.create_index("created_at")
            
            self.db.evolution_history.create_index("original_hypothesis_id")
            self.db.evolution_history.create_index("evolved_hypothesis_id")
            self.db.evolution_history.create_index("evolution_generation")
            
            self.db.research_sessions.create_index("session_id", unique=True)
            self.db.research_sessions.create_index("created_at")
            self.db.research_sessions.create_index("research_query")
            self.db.research_sessions.create_index("status")
            
            self.db.knowledge_base.create_index("concept")
            self.db.knowledge_base.create_index("domain")
            self.db.knowledge_base.create_index("relevance_score")
            
            self.logger.info("MongoDB collections and indexes initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing collections: {str(e)}")
    
    def store_hypothesis(self, hypothesis: Dict) -> str:
        """Store hypothesis with versioning and metadata"""
        try:
            hypothesis_id = hypothesis.get("id", self._generate_id())
            now = datetime.now()
            
            # Create comprehensive hypothesis document
            hypothesis_doc = {
                "id": hypothesis_id,
                "title": hypothesis.get("title", ""),
                "description": hypothesis.get("description", ""),
                "reasoning": hypothesis.get("reasoning", ""),
                "novelty_assessment": hypothesis.get("novelty_assessment", ""),
                "research_approach": hypothesis.get("research_approach", ""),
                "domain": hypothesis.get("domain", "general"),
                "research_query": hypothesis.get("research_query", ""),
                "created_at": now,
                "updated_at": now,
                "version": 1,
                "metadata": {
                    "generation_method": hypothesis.get("generation_method", "unknown"),
                    "confidence_score": hypothesis.get("confidence_score", 0.0),
                    "tags": hypothesis.get("tags", []),
                    "source_session": hypothesis.get("source_session", ""),
                    "parent_hypotheses": hypothesis.get("parent_hypotheses", [])
                }
            }
            
            # Check if hypothesis already exists
            existing = self.db.hypotheses.find_one({"id": hypothesis_id})
            
            if existing:
                # Update existing hypothesis (remove version from set operation)
                hypothesis_doc_update = hypothesis_doc.copy()
                del hypothesis_doc_update["version"]  # Remove version from $set to avoid conflict
                
                result = self.db.hypotheses.update_one(
                    {"id": hypothesis_id},
                    {
                        "$set": hypothesis_doc_update,
                        "$inc": {"version": 1}
                    }
                )
            else:
                # Insert new hypothesis
                result = self.db.hypotheses.insert_one(hypothesis_doc)
            
            if existing:
                self.logger.info(f"Hypothesis updated: {hypothesis_id}")
            else:
                self.logger.info(f"New hypothesis stored: {hypothesis_id}")
            
            return hypothesis_id
            
        except Exception as e:
            self.logger.error(f"Error storing hypothesis: {str(e)}")
            return ""
    
    def store_evaluation(self, hypothesis_id: str, evaluation: Dict, agent_type: str):
        """Store agent evaluation results with detailed metrics"""
        try:
            evaluation_doc = {
                "hypothesis_id": hypothesis_id,
                "agent_type": agent_type,
                "validity_score": evaluation.get("validity_score", 0.0),
                "novelty_score": evaluation.get("novelty_score", 0.0),
                "feasibility_score": evaluation.get("feasibility_score", 0.0),
                "impact_score": evaluation.get("impact_score", 0.0),
                "final_score": evaluation.get("final_score", 0.0),
                "feedback": evaluation.get("feedback", {}),
                "detailed_analysis": evaluation.get("detailed_analysis", ""),
                "recommendations": evaluation.get("recommendations", []),
                "created_at": datetime.now(),
                "metadata": {
                    "model_used": evaluation.get("model_used", "unknown"),
                    "processing_time": evaluation.get("processing_time", 0.0),
                    "confidence": evaluation.get("confidence", 0.0)
                }
            }
            
            result = self.db.evaluations.insert_one(evaluation_doc)
            self.logger.info(f"Evaluation stored for hypothesis {hypothesis_id} by {agent_type}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error storing evaluation: {str(e)}")
            return ""
    
    def get_hypothesis_history(self, hypothesis_id: str) -> Dict:
        """Retrieve comprehensive history of a hypothesis"""
        try:
            # Get hypothesis data
            hypothesis_data = self.db.hypotheses.find_one({"id": hypothesis_id})
            
            # Get all evaluations
            evaluations = list(self.db.evaluations.find({"hypothesis_id": hypothesis_id}))
            
            # Get evolution history
            evolution_data = list(self.db.evolution_history.find({
                "$or": [
                    {"original_hypothesis_id": hypothesis_id},
                    {"evolved_hypothesis_id": hypothesis_id}
                ]
            }))
            
            # Get related knowledge
            related_knowledge = list(self.db.knowledge_base.find({
                "related_hypotheses": hypothesis_id
            }))
            
            return {
                "hypothesis": hypothesis_data,
                "evaluations": evaluations,
                "evolution_history": evolution_data,
                "related_knowledge": related_knowledge,
                "summary": self._generate_hypothesis_summary(hypothesis_data, evaluations)
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving hypothesis history: {str(e)}")
            return {}
    
    def store_research_session(self, session):
        """Store comprehensive research session data"""
        try:
            if hasattr(session, '__dict__'):
                session_data = session.__dict__
            else:
                session_data = session
            
            session_doc = {
                "session_id": session_data.get("session_id", self._generate_session_id()),
                "research_query": session_data.get("research_query", ""),
                "status": session_data.get("status", "active"),
                "created_at": session_data.get("created_at", datetime.now()),
                "updated_at": datetime.now(),
                "current_round": session_data.get("current_round", 0),
                "max_rounds": session_data.get("max_rounds", 3),
                "hypotheses_count": len(session_data.get("hypotheses", [])),
                "session_data": {
                    "hypotheses": session_data.get("hypotheses", []),
                    "processing_steps": session_data.get("processing_steps", []),
                    "metrics": session_data.get("metrics", {}),
                    "final_results": session_data.get("final_results", {})
                },
                "performance_metrics": {
                    "total_processing_time": session_data.get("total_processing_time", 0.0),
                    "agent_performance": session_data.get("agent_performance", {}),
                    "quality_score": session_data.get("quality_score", 0.0)
                }
            }
            
            result = self.db.research_sessions.update_one(
                {"session_id": session_doc["session_id"]},
                {"$set": session_doc},
                upsert=True
            )
            
            self.logger.info(f"Research session stored: {session_doc['session_id']}")
            return session_doc["session_id"]
            
        except Exception as e:
            self.logger.error(f"Error storing research session: {str(e)}")
            return ""
    
    def store_evolution_record(self, original_id: str, evolved_id: str, evolution_data: Dict):
        """Store hypothesis evolution tracking"""
        try:
            evolution_doc = {
                "original_hypothesis_id": original_id,
                "evolved_hypothesis_id": evolved_id,
                "evolution_generation": evolution_data.get("generation", 1),
                "evolution_method": evolution_data.get("method", "agent_evolution"),
                "evolution_reason": evolution_data.get("reason", ""),
                "improvements": evolution_data.get("improvements", []),
                "performance_delta": evolution_data.get("performance_delta", {}),
                "created_at": datetime.now(),
                "metadata": evolution_data.get("metadata", {})
            }
            
            result = self.db.evolution_history.insert_one(evolution_doc)
            self.logger.info(f"Evolution record stored: {original_id} -> {evolved_id}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error storing evolution record: {str(e)}")
            return ""
    
    def get_related_hypotheses(self, query: str, domain: str = None, limit: int = 5) -> List[Dict]:
        """Advanced hypothesis retrieval with semantic similarity"""
        try:
            # Build query filter
            filter_query = {}
            
            if domain:
                filter_query["domain"] = domain
            
            # Text search on multiple fields
            text_search = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"reasoning": {"$regex": query, "$options": "i"}},
                    {"research_query": {"$regex": query, "$options": "i"}}
                ]
            }
            
            if filter_query:
                combined_query = {"$and": [filter_query, text_search]}
            else:
                combined_query = text_search
            
            # Find related hypotheses with scoring
            hypotheses = list(self.db.hypotheses.find(combined_query).limit(limit))
            
            # Add relevance scoring (simplified)
            for hyp in hypotheses:
                hyp["relevance_score"] = self._calculate_relevance_score(query, hyp)
            
            # Sort by relevance
            hypotheses.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
            
            return hypotheses
            
        except Exception as e:
            self.logger.error(f"Error retrieving related hypotheses: {str(e)}")
            return []
    
    def get_session_analytics(self, session_id: str = None, days: int = 30) -> Dict:
        """Get comprehensive analytics for sessions"""
        try:
            # Build time filter
            time_filter = {"created_at": {"$gte": datetime.now() - timedelta(days=days)}}
            
            if session_id:
                time_filter["session_id"] = session_id
            
            # Aggregate session data
            pipeline = [
                {"$match": time_filter},
                {"$group": {
                    "_id": None,
                    "total_sessions": {"$sum": 1},
                    "avg_hypotheses": {"$avg": "$hypotheses_count"},
                    "avg_processing_time": {"$avg": "$performance_metrics.total_processing_time"},
                    "completed_sessions": {"$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}},
                    "failed_sessions": {"$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}}
                }}
            ]
            
            result = list(self.db.research_sessions.aggregate(pipeline))
            
            if result:
                analytics = result[0]
                analytics["success_rate"] = analytics["completed_sessions"] / analytics["total_sessions"] if analytics["total_sessions"] > 0 else 0
                del analytics["_id"]
                return analytics
            else:
                return {"total_sessions": 0}
                
        except Exception as e:
            self.logger.error(f"Error getting session analytics: {str(e)}")
            return {}
    
    def store_knowledge_item(self, knowledge_item: Dict):
        """Store knowledge base items with metadata"""
        try:
            knowledge_doc = {
                "concept": knowledge_item.get("concept", ""),
                "domain": knowledge_item.get("domain", "general"),
                "description": knowledge_item.get("description", ""),
                "source": knowledge_item.get("source", ""),
                "relevance_score": knowledge_item.get("relevance_score", 0.0),
                "related_hypotheses": knowledge_item.get("related_hypotheses", []),
                "metadata": knowledge_item.get("metadata", {}),
                "created_at": datetime.now(),
                "tags": knowledge_item.get("tags", [])
            }
            
            result = self.db.knowledge_base.insert_one(knowledge_doc)
            self.logger.info(f"Knowledge item stored: {knowledge_item.get('concept', 'Unknown')}")
            
            return str(result.inserted_id)
            
        except Exception as e:
            self.logger.error(f"Error storing knowledge item: {str(e)}")
            return ""
    
    def _generate_id(self) -> str:
        """Generate unique ID for hypothesis"""
        return f"hyp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def _calculate_relevance_score(self, query: str, hypothesis: Dict) -> float:
        """Calculate relevance score between query and hypothesis"""
        query_words = set(query.lower().split())
        
        # Combine text fields
        text_content = " ".join([
            hypothesis.get("title", ""),
            hypothesis.get("description", ""),
            hypothesis.get("reasoning", "")
        ]).lower()
        
        content_words = set(text_content.split())
        
        # Calculate overlap score
        if len(query_words) == 0:
            return 0.0
        
        overlap = query_words & content_words
        return len(overlap) / len(query_words)
    
    def _generate_hypothesis_summary(self, hypothesis: Dict, evaluations: List[Dict]) -> Dict:
        """Generate summary of hypothesis performance"""
        if not evaluations:
            return {"status": "no_evaluations"}
        
        # Calculate average scores
        scores = {
            "validity": sum(e.get("validity_score", 0) for e in evaluations) / len(evaluations),
            "novelty": sum(e.get("novelty_score", 0) for e in evaluations) / len(evaluations),
            "feasibility": sum(e.get("feasibility_score", 0) for e in evaluations) / len(evaluations),
            "impact": sum(e.get("impact_score", 0) for e in evaluations) / len(evaluations),
            "overall": sum(e.get("final_score", 0) for e in evaluations) / len(evaluations)
        }
        
        return {
            "average_scores": scores,
            "evaluation_count": len(evaluations),
            "agents_evaluated": list(set(e.get("agent_type", "") for e in evaluations)),
            "last_evaluation": max(e.get("created_at", datetime.min) for e in evaluations)
        }
    
    def close(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
            self.logger.info("MongoDB connection closed")
        except Exception as e:
            self.logger.error(f"Error closing MongoDB connection: {str(e)}")


# Global memory service instances
memory_service = SimpleMemoryService()
enhanced_memory_service = EnhancedMemoryService()