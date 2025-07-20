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
    
    def search_for_hypothesis_queries(self, queries: List[str]) -> List[Dict[str, str]]:
        """
        Perform web search for multiple queries and return structured results
        """
        search_results = []
        
        for query in queries:
            try:
                # Use Tavily to search for the query
                results = self.scientific_search(query, max_results=3, include_academic=True)
                
                for result in results:
                    search_results.append({
                        "query": query,
                        "title": result.title,
                        "summary": result.content[:300] + "..." if len(result.content) > 300 else result.content,
                        "source": result.url,
                        "relevance": "high" if result.score > 0.7 else "medium"
                    })
                    
            except Exception as e:
                self.logger.error(f"Failed to search for query '{query}': {str(e)}")
                # Fallback to basic result
                search_results.append({
                    "query": query,
                    "title": f"Research on {query}",
                    "summary": f"Literature search for {query} - comprehensive analysis needed.",
                    "source": "tavily-search-api",
                    "relevance": "medium"
                })
        
        return search_results
    
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