import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

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

# Global memory service instance
memory_service = SimpleMemoryService()