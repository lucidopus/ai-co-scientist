from typing import Dict, Any, List, Optional
import json
import requests

from agents.base_agent import BaseCoScientistAgent
from utils.adk_tools import retrieve_knowledge_tool
from utils.search_service import TavilySearchService

# Import prompts with fallback for testing
try:
    from prompts import AgentPrompts, PromptTemplates
except ImportError:
    from test_prompts import MockAgentPrompts as AgentPrompts, MockPromptTemplates as PromptTemplates

class ProximityAgent(BaseCoScientistAgent):
    """Agent responsible for retrieving related knowledge and grounding hypotheses using GROQ Llama scout"""
    
    def __init__(self, search_service=None):
        super().__init__(
            name="proximity_agent",
            description="Retrieves related knowledge and grounds hypotheses in existing research",
            model="meta-llama/llama-4-scout-17b-16e-instruct",  # Use GROQ Llama Scout for fast search and retrieval
            tools=[retrieve_knowledge_tool]
        )
        # Store search service in a way that's compatible with ADK Agent
        self._search_service = search_service or self._initialize_search_service()
    
    @property
    def search_service(self):
        """Get the search service"""
        return self._search_service
    
    def _initialize_search_service(self):
        """Initialize Tavily search service with error handling"""
        try:
            return TavilySearchService()
        except ValueError as e:
            # If Tavily API key is not set, return None and use fallback
            print(f"Warning: {e}. Using fallback search implementation.")
            return None
    
    def get_system_prompt(self) -> str:
        return AgentPrompts.PROXIMITY_AGENT

    def retrieve_knowledge(
        self, 
        hypotheses: List[Dict[str, Any]],
        perform_web_search: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve related knowledge and ground hypotheses
        
        Args:
            hypotheses: List of hypothesis dictionaries
            perform_web_search: Whether to perform actual web searches
            
        Returns:
            List of knowledge analysis dictionaries
        """
        # Format hypotheses for knowledge retrieval
        knowledge_input = self._format_knowledge_input(hypotheses)
        
        knowledge_query = PromptTemplates.knowledge_retrieval_template(knowledge_input)

        result = self.run(knowledge_query)
        
        try:
            # Parse JSON response
            output = result["output"]
            
            # Extract JSON from the response
            if "```json" in output:
                json_start = output.find("```json") + 7
                json_end = output.find("```", json_start)
                json_content = output[json_start:json_end].strip()
            else:
                start_idx = output.find("{")
                end_idx = output.rfind("}")
                json_content = output[start_idx:end_idx + 1]
            
            parsed_output = json.loads(json_content)
            
            # Extract knowledge analysis
            if "knowledge_analysis" in parsed_output:
                analyses = parsed_output["knowledge_analysis"]
            elif isinstance(parsed_output, list):
                analyses = parsed_output
            else:
                analyses = [parsed_output]
            
            # Process knowledge analyses
            processed_analyses = []
            for i, analysis in enumerate(analyses):
                processed_analysis = {
                    "hypothesis_id": analysis.get("hypothesis_id", hypotheses[i]["id"] if i < len(hypotheses) else f"unknown_{i}"),
                    "key_concepts": analysis.get("key_concepts", []),
                    "related_fields": analysis.get("related_fields", []),
                    "existing_research": analysis.get("existing_research", "Research landscape analysis pending"),
                    "knowledge_gaps": analysis.get("knowledge_gaps", "Knowledge gap analysis pending"),
                    "methodological_connections": analysis.get("methodological_connections", []),
                    "expert_communities": analysis.get("expert_communities", []),
                    "literature_recommendations": analysis.get("literature_recommendations", []),
                    "search_queries": analysis.get("search_queries", []),
                    "agent_metadata": result["metadata"]
                }
                
                # Perform web search if requested and search queries available
                if perform_web_search and processed_analysis["search_queries"]:
                    search_results = self._perform_web_search(processed_analysis["search_queries"][:3])
                    processed_analysis["web_search_results"] = search_results
                
                processed_analyses.append(processed_analysis)
            
            return processed_analyses
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback: create basic knowledge analyses
            fallback_analyses = []
            for hyp in hypotheses:
                # Extract key terms from hypothesis for basic analysis
                title = hyp.get("title", "")
                description = hyp.get("description", "")
                
                fallback_analysis = {
                    "hypothesis_id": hyp.get("id", "unknown"),
                    "key_concepts": self._extract_key_concepts(title + " " + description),
                    "related_fields": ["Interdisciplinary research", "Applied sciences"],
                    "existing_research": "Comprehensive literature review recommended",
                    "knowledge_gaps": "Novel approach requiring further investigation",
                    "methodological_connections": ["Experimental validation", "Computational modeling"],
                    "expert_communities": ["Academic research institutions", "Industry R&D"],
                    "literature_recommendations": ["Recent peer-reviewed literature"],
                    "search_queries": [title[:50], f"research methodology {title[:30]}"],
                    "agent_metadata": result["metadata"]
                }
                
                # Perform web search if requested and search queries available
                if perform_web_search and fallback_analysis["search_queries"]:
                    search_results = self._perform_web_search(fallback_analysis["search_queries"][:3])
                    fallback_analysis["web_search_results"] = search_results
                
                fallback_analyses.append(fallback_analysis)
            
            return fallback_analyses
    
    def _format_knowledge_input(self, hypotheses: List[Dict[str, Any]]) -> str:
        """Format hypotheses for knowledge retrieval"""
        
        knowledge_input = "HYPOTHESES FOR KNOWLEDGE GROUNDING:\n\n"
        
        for i, hyp in enumerate(hypotheses, 1):
            knowledge_input += f"Hypothesis {i} (ID: {hyp.get('id', 'unknown')}):\n"
            knowledge_input += f"Title: {hyp.get('title', 'N/A')}\n"
            knowledge_input += f"Description: {hyp.get('description', 'N/A')}\n"
            knowledge_input += f"Reasoning: {hyp.get('reasoning', 'N/A')}\n"
            
            # Add any research approach information
            if "research_approach" in hyp:
                knowledge_input += f"Research Approach: {hyp.get('research_approach', 'N/A')}\n"
            
            knowledge_input += "-" * 60 + "\n"
        
        return knowledge_input
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key scientific concepts from text (simple implementation)"""
        # Simple keyword extraction - in production, use NLP libraries
        scientific_keywords = [
            "machine learning", "artificial intelligence", "quantum", "biomarker", 
            "genetic", "protein", "algorithm", "neural network", "optimization",
            "modeling", "simulation", "experimental", "computational", "analysis"
        ]
        
        text_lower = text.lower()
        found_concepts = []
        
        for keyword in scientific_keywords:
            if keyword in text_lower:
                found_concepts.append(keyword)
        
        # Add basic concepts from text (simple word extraction)
        words = text.split()
        important_words = [w.strip(".,!?") for w in words if len(w) > 6 and w.isalpha()]
        found_concepts.extend(important_words[:3])
        
        return found_concepts[:5]  # Return top 5 concepts
    
    def _perform_web_search(self, queries: List[str]) -> List[Dict[str, str]]:
        """Perform web search for queries using Tavily or fallback implementation"""
        if self.search_service:
            # Use Tavily search service
            return self.search_service.search_for_hypothesis_queries(queries)
        else:
            # Fallback to placeholder implementation
            search_results = []
            
            for query in queries:
                # Simulated search result
                search_results.append({
                    "query": query,
                    "title": f"Research on {query}",
                    "summary": f"Recent developments in {query} show promising advances in the field.",
                    "source": "academic-search-engine.com",
                    "relevance": "high"
                })
            
            return search_results