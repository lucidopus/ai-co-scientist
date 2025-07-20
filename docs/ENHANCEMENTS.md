# AI Co-Scientist Enhancement Implementation Plan

## Current State Assessment

### ✅ Completed Components
- **Multi-agent architecture**: 6 specialized agents (Generation, Proximity, Reflection, Ranking, Evolution, Meta-review)
- **Structured prompts**: Comprehensive prompts with scientific rigor and JSON output formats
- **Scientific methodology**: Built-in validation criteria (validity, novelty, feasibility, impact)
- **Agent orchestration**: Basic workflow_orchestrator.py implementation
- **Memory infrastructure**: Existing memory_service.py foundation

### 🚧 Enhancement Areas
Based on Google's AI Co-Scientist research, we need to implement:
1. **Tool Integration** (Web search, memory, additional tools)
2. **Elo Rating System** (Tournament-style automated ranking)
3. **Supervisor Agent** (Enhanced orchestration layer)

---

## 1. Tool Integration Implementation

### 1.1 Tavily Search Integration

#### Step 1: Install Dependencies
```bash
pip install tavily-python
```

#### Step 2: Create Search Service (`utils/search_service.py`)
```python
import os
import logging
from typing import List, Dict, Optional
from tavily import TavilyClient
from dataclasses import dataclass

@dataclass
class SearchResult:
    title: str
    content: str
    url: str
    score: float

class TavilySearchService:
    """Scientific literature and web search service using Tavily API"""
    
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY environment variable not set")
        self.client = TavilyClient(self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def scientific_search(
        self, 
        query: str, 
        max_results: int = 10,
        include_academic: bool = True
    ) -> List[SearchResult]:
        """
        Perform scientific literature search with academic focus
        """
        try:
            # Enhance query for scientific relevance
            enhanced_query = self._enhance_scientific_query(query, include_academic)
            
            response = self.client.search(
                enhanced_query, 
                max_results=max_results,
                include_images=False  # Focus on textual content for scientific research
            )
            
            results = []
            for result in response.get('results', []):
                search_result = SearchResult(
                    title=result.get('title', ''),
                    content=result.get('content', ''),
                    url=result.get('url', ''),
                    score=result.get('score', 0.0)
                )
                results.append(search_result)
            
            self.logger.info(f"Found {len(results)} search results for query: {query}")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {str(e)}")
            return []
    
    def hypothesis_literature_search(self, hypothesis: Dict) -> Dict:
        """
        Search for literature relevant to a specific hypothesis
        """
        # Extract key concepts from hypothesis
        search_terms = self._extract_search_terms(hypothesis)
        
        all_results = {}
        for term in search_terms:
            results = self.scientific_search(
                term, 
                max_results=5,
                include_academic=True
            )
            all_results[term] = results
        
        return {
            "hypothesis_id": hypothesis.get("id", "unknown"),
            "search_results": all_results,
            "literature_summary": self._summarize_literature(all_results)
        }
    
    def _enhance_scientific_query(self, query: str, include_academic: bool) -> str:
        """Add scientific context to search queries"""
        if include_academic:
            academic_terms = ["research", "study", "scientific", "peer-reviewed"]
            query = f"{query} {' '.join(academic_terms)}"
        return query
    
    def _extract_search_terms(self, hypothesis: Dict) -> List[str]:
        """Extract key search terms from hypothesis"""
        terms = []
        
        # Extract from title and description
        if "title" in hypothesis:
            terms.append(hypothesis["title"])
        
        if "description" in hypothesis:
            # Simple keyword extraction (can be enhanced with NLP)
            description = hypothesis["description"]
            terms.append(description[:100])  # First 100 chars as search term
        
        # Add reasoning-based terms
        if "reasoning" in hypothesis:
            terms.append(hypothesis["reasoning"][:100])
        
        return terms
    
    def _summarize_literature(self, results: Dict) -> str:
        """Summarize literature findings"""
        total_results = sum(len(results_list) for results_list in results.values())
        return f"Found {total_results} relevant papers across {len(results)} search terms"
```

#### Step 3: Update Environment Configuration
Add to `.env` file:
```
TAVILY_API_KEY=your_tavily_api_key_here
```

#### Step 4: Integrate Search into Proximity Agent (`agents/proximity_agent.py`)
```python
# Add to proximity_agent.py imports
from utils.search_service import TavilySearchService

class ProximityAgent(BaseAgent):
    def __init__(self, llm_client, search_service=None):
        super().__init__(llm_client)
        self.search_service = search_service or TavilySearchService()
    
    def process_hypotheses(self, hypotheses: List[Dict]) -> Dict:
        """Enhanced with literature search"""
        enriched_hypotheses = []
        
        for hypothesis in hypotheses:
            # Perform literature search
            literature_data = self.search_service.hypothesis_literature_search(hypothesis)
            
            # Create enhanced prompt with search results
            enhanced_prompt = self._create_enhanced_prompt(hypothesis, literature_data)
            
            # Process with LLM
            response = self.llm_client.generate_response(enhanced_prompt)
            enriched_hypotheses.append(response)
        
        return {"enriched_hypotheses": enriched_hypotheses}
```

### 1.2 Enhanced Memory System

#### Step 1: Upgrade Memory Service (`utils/memory_service.py`)
```python
import json
from typing import Dict, List, Optional
from datetime import datetime
import os
from pymongo import MongoClient
from bson import ObjectId

class EnhancedMemoryService:
    """Enhanced memory system for AI Co-Scientist using MongoDB"""
    
    def __init__(self, mongo_uri: str = None, database_name: str = "ai_coscientist"):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        self.database_name = database_name
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        self._init_collections()
    
    def _init_collections(self):
        """Initialize MongoDB collections with indexes"""
        # Create indexes for better performance
        self.db.hypotheses.create_index("id", unique=True)
        self.db.hypotheses.create_index("created_at")
        self.db.evaluations.create_index("hypothesis_id")
        self.db.evaluations.create_index("agent_type")
        self.db.evolution_history.create_index("original_hypothesis_id")
        self.db.research_sessions.create_index("created_at")
    
    def store_hypothesis(self, hypothesis: Dict) -> str:
        """Store hypothesis with versioning"""
        hypothesis_id = hypothesis.get("id", self._generate_id())
        now = datetime.now()
        
        hypothesis_doc = {
            "id": hypothesis_id,
            "title": hypothesis.get("title", ""),
            "description": hypothesis.get("description", ""),
            "reasoning": hypothesis.get("reasoning", ""),
            "novelty_assessment": hypothesis.get("novelty_assessment", ""),
            "research_approach": hypothesis.get("research_approach", ""),
            "created_at": now,
            "updated_at": now,
            "version": 1
        }
        
        # Use upsert to handle updates
        self.db.hypotheses.update_one(
            {"id": hypothesis_id},
            {"$set": hypothesis_doc, "$inc": {"version": 1}},
            upsert=True
        )
        
        return hypothesis_id
    
    def store_evaluation(self, hypothesis_id: str, evaluation: Dict, agent_type: str):
        """Store agent evaluation results"""
        evaluation_doc = {
            "hypothesis_id": hypothesis_id,
            "agent_type": agent_type,
            "validity_score": evaluation.get("validity_score", 0.0),
            "novelty_score": evaluation.get("novelty_score", 0.0),
            "feasibility_score": evaluation.get("feasibility_score", 0.0),
            "impact_score": evaluation.get("impact_score", 0.0),
            "final_score": evaluation.get("final_score", 0.0),
            "feedback": evaluation.get("feedback", {}),
            "created_at": datetime.now()
        }
        
        self.db.evaluations.insert_one(evaluation_doc)
    
    def get_hypothesis_history(self, hypothesis_id: str) -> Dict:
        """Retrieve full history of a hypothesis"""
        # Get hypothesis data
        hypothesis_data = self.db.hypotheses.find_one({"id": hypothesis_id})
        
        # Get evaluations
        evaluations = list(self.db.evaluations.find({"hypothesis_id": hypothesis_id}))
        
        # Get evolution history
        evolution_data = list(self.db.evolution_history.find({
            "$or": [
                {"original_hypothesis_id": hypothesis_id},
                {"evolved_hypothesis_id": hypothesis_id}
            ]
        }))
        
        return {
            "hypothesis": hypothesis_data,
            "evaluations": evaluations,
            "evolution_history": evolution_data
        }
    
    def store_research_session(self, session):
        """Store research session data"""
        session_doc = {
            "id": session.session_id,
            "research_query": session.research_query,
            "status": session.status,
            "created_at": session.created_at,
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "hypotheses_count": len(session.hypotheses),
            "session_data": {
                "hypotheses": session.hypotheses
            }
        }
        
        self.db.research_sessions.update_one(
            {"id": session.session_id},
            {"$set": session_doc},
            upsert=True
        )
    
    def _generate_id(self) -> str:
        """Generate unique ID for hypothesis"""
        return f"hyp_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
```

---

## 2. Elo Rating System Implementation

### Step 1: Create Elo Rating Service (`utils/elo_rating_service.py`)
```python
import math
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
import random
from datetime import datetime
from pymongo import MongoClient

@dataclass
class EloMatch:
    hypothesis_a_id: str
    hypothesis_b_id: str
    winner_id: str
    criteria: str
    confidence: float

class EloRatingService:
    """Tournament-style Elo rating system for hypothesis evaluation using MongoDB"""
    
    def __init__(self, mongo_uri: str = None, database_name: str = "ai_coscientist", k_factor: int = 32):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI")
        self.database_name = database_name
        self.k_factor = k_factor
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        self._init_elo_collections()
    
    def _init_elo_collections(self):
        """Initialize Elo rating collections with indexes"""
        # Create indexes for better performance
        self.db.elo_ratings.create_index("hypothesis_id", unique=True)
        self.db.elo_ratings.create_index("overall_rating")
        self.db.elo_matches.create_index("hypothesis_a_id")
        self.db.elo_matches.create_index("hypothesis_b_id")
        self.db.elo_matches.create_index("created_at")
    
    def conduct_tournament(self, hypotheses: List[Dict], num_rounds: int = 5) -> Dict:
        """Conduct tournament-style comparisons"""
        tournament_results = []
        
        for round_num in range(num_rounds):
            # Create random pairings
            pairs = self._create_tournament_pairs(hypotheses)
            
            for pair in pairs:
                # Run comparison for each criteria
                criteria_list = ["validity", "novelty", "feasibility", "impact"]
                
                for criteria in criteria_list:
                    match_result = self._compare_hypotheses(pair[0], pair[1], criteria)
                    tournament_results.append(match_result)
                    self._update_elo_ratings(match_result)
        
        # Calculate final rankings
        final_rankings = self._get_current_rankings()
        
        return {
            "tournament_results": tournament_results,
            "final_rankings": final_rankings,
            "total_matches": len(tournament_results)
        }
    
    def _create_tournament_pairs(self, hypotheses: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """Create random pairs for tournament matches"""
        shuffled = hypotheses.copy()
        random.shuffle(shuffled)
        
        pairs = []
        for i in range(0, len(shuffled) - 1, 2):
            pairs.append((shuffled[i], shuffled[i + 1]))
        
        return pairs
    
    def _compare_hypotheses(self, hyp_a: Dict, hyp_b: Dict, criteria: str) -> EloMatch:
        """Use LLM to compare two hypotheses on specific criteria"""
        # This would integrate with your LLM client
        comparison_prompt = f"""
        Compare these two hypotheses on {criteria}:
        
        Hypothesis A: {hyp_a.get('title', '')} - {hyp_a.get('description', '')}
        Hypothesis B: {hyp_b.get('title', '')} - {hyp_b.get('description', '')}
        
        Which hypothesis is better in terms of {criteria}? Return:
        - winner: "A" or "B"
        - confidence: 0.0-1.0 (how confident you are in this judgment)
        - reasoning: brief explanation
        
        Response format: {{"winner": "A", "confidence": 0.85, "reasoning": "..."}}
        """
        
        # Placeholder for LLM call - you'd implement this with your LLM client
        # For now, random winner for demonstration
        winner = random.choice(["A", "B"])
        confidence = random.uniform(0.6, 0.95)
        
        winner_id = hyp_a["id"] if winner == "A" else hyp_b["id"]
        
        return EloMatch(
            hypothesis_a_id=hyp_a["id"],
            hypothesis_b_id=hyp_b["id"],
            winner_id=winner_id,
            criteria=criteria,
            confidence=confidence
        )
    
    def _update_elo_ratings(self, match: EloMatch):
        """Update Elo ratings based on match result"""
        # Get current ratings
        rating_a_doc = self.db.elo_ratings.find_one({"hypothesis_id": match.hypothesis_a_id})
        rating_a = rating_a_doc["overall_rating"] if rating_a_doc else 1200
        
        rating_b_doc = self.db.elo_ratings.find_one({"hypothesis_id": match.hypothesis_b_id})
        rating_b = rating_b_doc["overall_rating"] if rating_b_doc else 1200
        
        # Calculate expected scores
        expected_a = 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
        expected_b = 1 - expected_a
        
        # Actual scores (1 for winner, 0 for loser)
        actual_a = 1.0 if match.winner_id == match.hypothesis_a_id else 0.0
        actual_b = 1.0 - actual_a
        
        # Calculate rating changes
        change_a = self.k_factor * (actual_a - expected_a)
        change_b = self.k_factor * (actual_b - expected_b)
        
        # Update ratings
        new_rating_a = rating_a + change_a
        new_rating_b = rating_b + change_b
        
        # Store updated ratings for hypothesis A
        current_matches_a = rating_a_doc["matches_played"] if rating_a_doc else 0
        self.db.elo_ratings.update_one(
            {"hypothesis_id": match.hypothesis_a_id},
            {
                "$set": {
                    "overall_rating": new_rating_a,
                    "matches_played": current_matches_a + 1,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
        
        # Store updated ratings for hypothesis B
        current_matches_b = rating_b_doc["matches_played"] if rating_b_doc else 0
        self.db.elo_ratings.update_one(
            {"hypothesis_id": match.hypothesis_b_id},
            {
                "$set": {
                    "overall_rating": new_rating_b,
                    "matches_played": current_matches_b + 1,
                    "last_updated": datetime.now()
                }
            },
            upsert=True
        )
        
        # Store match record
        match_doc = {
            "hypothesis_a_id": match.hypothesis_a_id,
            "hypothesis_b_id": match.hypothesis_b_id,
            "winner_id": match.winner_id,
            "criteria": match.criteria,
            "confidence": match.confidence,
            "rating_change_a": change_a,
            "rating_change_b": change_b,
            "created_at": datetime.now()
        }
        self.db.elo_matches.insert_one(match_doc)
    
    def _get_current_rankings(self) -> List[Dict]:
        """Get current Elo rankings"""
        ratings_cursor = self.db.elo_ratings.find().sort("overall_rating", -1)
        
        rankings = []
        for rank, rating_doc in enumerate(ratings_cursor, 1):
            rankings.append({
                "rank": rank,
                "hypothesis_id": rating_doc["hypothesis_id"],
                "elo_rating": rating_doc["overall_rating"],
                "matches_played": rating_doc.get("matches_played", 0)
            })
        
        return rankings
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
```

---

## 3. Enhanced Supervisor Agent Implementation

### Step 1: Create Advanced Supervisor Agent (`agents/supervisor_agent.py`)
```python
import logging
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from dataclasses import dataclass

from agents.generation_agent import GenerationAgent
from agents.proximity_agent import ProximityAgent
from agents.reflection_agent import ReflectionAgent
from agents.ranking_agent import RankingAgent
from agents.evolution_agent import EvolutionAgent
from agents.meta_review_agent import MetaReviewAgent
from utils.memory_service import EnhancedMemoryService
from utils.elo_rating_service import EloRatingService
from utils.search_service import TavilySearchService

@dataclass
class ResearchSession:
    session_id: str
    research_query: str
    status: str
    created_at: datetime
    hypotheses: List[Dict]
    current_round: int
    max_rounds: int

class SupervisorAgent:
    """Enhanced orchestration agent with test-time compute scaling"""
    
    def __init__(self, llm_client, config: Dict = None):
        self.llm_client = llm_client
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize services
        self.memory_service = EnhancedMemoryService()
        self.elo_service = EloRatingService()
        self.search_service = TavilySearchService()
        
        # Initialize agents
        self.agents = {
            "generation": GenerationAgent(llm_client),
            "proximity": ProximityAgent(llm_client, self.search_service),
            "reflection": ReflectionAgent(llm_client),
            "ranking": RankingAgent(llm_client),
            "evolution": EvolutionAgent(llm_client),
            "meta_review": MetaReviewAgent(llm_client)
        }
        
        # Research session tracking
        self.current_sessions: Dict[str, ResearchSession] = {}
    
    async def conduct_research(
        self, 
        research_query: str, 
        max_rounds: int = 3,
        quality_threshold: float = 0.85
    ) -> Dict:
        """
        Main research orchestration with test-time compute scaling
        """
        session_id = self._generate_session_id()
        self.logger.info(f"Starting research session {session_id}: {research_query}")
        
        # Initialize session
        session = ResearchSession(
            session_id=session_id,
            research_query=research_query,
            status="active",
            created_at=datetime.now(),
            hypotheses=[],
            current_round=0,
            max_rounds=max_rounds
        )
        self.current_sessions[session_id] = session
        
        try:
            # Phase 1: Initial hypothesis generation
            initial_hypotheses = await self._generate_initial_hypotheses(session)
            session.hypotheses.extend(initial_hypotheses)
            
            # Phase 2: Iterative improvement rounds
            for round_num in range(max_rounds):
                session.current_round = round_num + 1
                self.logger.info(f"Round {session.current_round}/{max_rounds}")
                
                # Run full pipeline for current round
                round_results = await self._run_improvement_round(session)
                
                # Check quality threshold
                best_score = max(h.get("final_score", 0) for h in session.hypotheses)
                if best_score >= quality_threshold:
                    self.logger.info(f"Quality threshold reached: {best_score}")
                    break
            
            # Phase 3: Final evaluation and ranking
            final_results = await self._finalize_research(session)
            
            session.status = "completed"
            return final_results
            
        except Exception as e:
            session.status = "failed"
            self.logger.error(f"Research session failed: {str(e)}")
            raise
        
        finally:
            # Store session in memory
            self.memory_service.store_research_session(session)
    
    async def _generate_initial_hypotheses(self, session: ResearchSession) -> List[Dict]:
        """Generate initial set of hypotheses"""
        self.logger.info("Generating initial hypotheses")
        
        # Use generation agent
        generation_result = self.agents["generation"].generate_hypotheses(
            session.research_query,
            num_hypotheses=self.config.get("initial_hypotheses", 5)
        )
        
        hypotheses = generation_result.get("hypotheses", [])
        
        # Store in memory
        for hypothesis in hypotheses:
            hypothesis["id"] = self.memory_service.store_hypothesis(hypothesis)
        
        return hypotheses
    
    async def _run_improvement_round(self, session: ResearchSession) -> Dict:
        """Run one complete improvement round"""
        self.logger.info(f"Running improvement round {session.current_round}")
        
        current_hypotheses = session.hypotheses
        round_results = {}
        
        # Step 1: Literature search and knowledge grounding
        proximity_results = self.agents["proximity"].process_hypotheses(current_hypotheses)
        round_results["proximity"] = proximity_results
        
        # Step 2: Critical evaluation
        reflection_results = self.agents["reflection"].evaluate_hypotheses(current_hypotheses)
        round_results["reflection"] = reflection_results
        
        # Step 3: Tournament-style ranking
        tournament_results = self.elo_service.conduct_tournament(
            current_hypotheses, 
            num_rounds=self.config.get("tournament_rounds", 3)
        )
        round_results["tournament"] = tournament_results
        
        # Step 4: Traditional ranking
        ranking_results = self.agents["ranking"].rank_hypotheses(
            current_hypotheses,
            reflection_results
        )
        round_results["ranking"] = ranking_results
        
        # Step 5: Evolution of top hypotheses
        top_hypotheses = self._select_top_hypotheses(
            current_hypotheses, 
            ranking_results,
            top_k=self.config.get("evolution_candidates", 3)
        )
        
        evolution_results = self.agents["evolution"].evolve_hypotheses(top_hypotheses)
        round_results["evolution"] = evolution_results
        
        # Step 6: Add evolved hypotheses to session
        evolved_hypotheses = evolution_results.get("evolved_hypotheses", [])
        for hypothesis in evolved_hypotheses:
            hypothesis["id"] = self.memory_service.store_hypothesis(hypothesis)
            hypothesis["generation"] = session.current_round
        
        session.hypotheses.extend(evolved_hypotheses)
        
        # Store round results in memory
        for hypothesis in current_hypotheses:
            if "reflection_score" in hypothesis:
                self.memory_service.store_evaluation(
                    hypothesis["id"],
                    hypothesis,
                    f"round_{session.current_round}_reflection"
                )
        
        return round_results
    
    async def _finalize_research(self, session: ResearchSession) -> Dict:
        """Final evaluation and research plan generation"""
        self.logger.info("Finalizing research results")
        
        # Get final rankings
        final_rankings = self.elo_service._get_current_rankings()
        
        # Get top hypotheses for meta-review
        top_hypotheses = self._get_top_hypotheses_by_elo(session.hypotheses, final_rankings, top_k=5)
        
        # Generate final research plans
        meta_review_results = self.agents["meta_review"].generate_research_plans(top_hypotheses)
        
        return {
            "session_id": session.session_id,
            "research_query": session.research_query,
            "total_rounds": session.current_round,
            "total_hypotheses": len(session.hypotheses),
            "elo_rankings": final_rankings,
            "top_hypotheses": top_hypotheses,
            "research_plans": meta_review_results,
            "session_summary": self._generate_session_summary(session)
        }
    
    def _select_top_hypotheses(self, hypotheses: List[Dict], ranking_results: Dict, top_k: int) -> List[Dict]:
        """Select top hypotheses for evolution"""
        ranked_hypotheses = ranking_results.get("rankings", [])
        top_ids = [h["hypothesis_id"] for h in ranked_hypotheses[:top_k]]
        
        return [h for h in hypotheses if h.get("id") in top_ids]
    
    def _get_top_hypotheses_by_elo(self, hypotheses: List[Dict], elo_rankings: List[Dict], top_k: int) -> List[Dict]:
        """Get top hypotheses based on Elo ratings"""
        top_ids = [r["hypothesis_id"] for r in elo_rankings[:top_k]]
        return [h for h in hypotheses if h.get("id") in top_ids]
    
    def _generate_session_summary(self, session: ResearchSession) -> str:
        """Generate summary of research session"""
        return f"""
        Research Session Summary:
        - Query: {session.research_query}
        - Duration: {session.current_round} rounds
        - Hypotheses Generated: {len(session.hypotheses)}
        - Status: {session.status}
        - Started: {session.created_at}
        """
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """Get current status of a research session"""
        session = self.current_sessions.get(session_id)
        if not session:
            return None
        
        return {
            "session_id": session_id,
            "status": session.status,
            "current_round": session.current_round,
            "max_rounds": session.max_rounds,
            "hypotheses_count": len(session.hypotheses),
            "progress": session.current_round / session.max_rounds
        }
```

---

## 4. Integration Steps

### Step 1: Update Requirements (`requirements.txt`)
```txt
# Add to existing requirements
tavily-python>=0.3.0
pymongo>=4.0.0  # MongoDB driver for Python
numpy>=1.21.0
```

### Step 2: Update Main Orchestrator (`main.py`)
```python
# Add imports
from agents.supervisor_agent import SupervisorAgent
from utils.search_service import TavilySearchService
from utils.elo_rating_service import EloRatingService

# Update main function to use enhanced supervisor
async def main():
    # Initialize enhanced supervisor
    supervisor = SupervisorAgent(
        llm_client=unified_client,
        config={
            "initial_hypotheses": 5,
            "tournament_rounds": 3,
            "evolution_candidates": 3,
            "max_improvement_rounds": 3
        }
    )
    
    # Run research
    results = await supervisor.conduct_research(
        research_query=user_query,
        max_rounds=3,
        quality_threshold=0.85
    )
    
    return results
```

### Step 3: Environment Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
echo "TAVILY_API_KEY=your_key_here" >> .env
echo "MONGODB_URI=your_mongodb_connection_string" >> .env
echo "DATABASE=ai_coscientist" >> .env

# 3. Initialize MongoDB collections and indexes
python -c "from utils.memory_service import EnhancedMemoryService; EnhancedMemoryService()"
```

---

## 5. Testing and Validation

### Step 1: Create Test Suite (`tests/test_enhancements.py`)
```python
import pytest
import asyncio
from agents.supervisor_agent import SupervisorAgent
from utils.search_service import TavilySearchService
from utils.elo_rating_service import EloRatingService

class TestEnhancements:
    def test_search_service(self):
        # Test Tavily integration
        pass
    
    def test_elo_rating_system(self):
        # Test tournament ranking
        pass
    
    async def test_supervisor_agent(self):
        # Test full pipeline
        pass
```

### Step 2: Performance Benchmarks
```python
# Add performance monitoring
def benchmark_search_performance():
    # Measure search response times
    pass

def benchmark_elo_convergence():
    # Test rating convergence
    pass
```

---

## 6. Deployment Considerations

### Production Readiness Checklist:
- [ ] API key management and rotation
- [ ] Database connection pooling
- [ ] Error handling and retry logic
- [ ] Rate limiting for external APIs
- [ ] Logging and monitoring
- [ ] Caching for expensive operations
- [ ] Async processing for long-running tasks
- [ ] Resource management and cleanup

### Monitoring and Observability:
- [ ] Search API usage tracking
- [ ] Elo rating distribution analysis
- [ ] Research session success rates
- [ ] Performance metrics dashboard

---

## 7. Future Enhancements

### Advanced Features to Consider:
1. **Multi-modal inputs**: Image and document analysis
2. **Active learning**: Adaptive hypothesis generation
3. **Collaborative filtering**: Cross-researcher insights
4. **Domain-specific specialization**: Biology, physics, chemistry agents
5. **Real-time collaboration**: Multiple researchers working together
6. **Automated experimentation**: Integration with lab equipment APIs

This implementation plan provides a comprehensive roadmap to achieve Google-level AI co-scientist capabilities while building on your existing solid foundation.