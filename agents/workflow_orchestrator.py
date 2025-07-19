import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.generation_agent import GenerationAgent
from agents.reflection_agent import ReflectionAgent
from agents.ranking_agent import RankingAgent
from agents.evolution_agent import EvolutionAgent
from agents.proximity_agent import ProximityAgent
from agents.meta_review_agent import MetaReviewAgent

from utils.models import (
    QueryRequest,
    QueryResponse,
    Hypothesis,
    ProcessingStep,
    AgentOutput,
)

class AICoScientistWorkflow:
    """ADK-based workflow orchestrator for the AI Co-Scientist system"""
    
    def __init__(self):
        # Initialize all agents
        self.generation_agent = GenerationAgent()
        self.reflection_agent = ReflectionAgent()
        self.ranking_agent = RankingAgent()
        self.evolution_agent = EvolutionAgent()
        self.proximity_agent = ProximityAgent()
        self.meta_review_agent = MetaReviewAgent()
        
        # Workflow configuration
        self.evolution_rounds = 1
        self.enable_knowledge_retrieval = True
    
    def process_scientific_query(self, request: QueryRequest) -> QueryResponse:
        """
        Main workflow for processing scientific queries through multi-agent pipeline
        
        Args:
            request: QueryRequest with research query and parameters
            
        Returns:
            QueryResponse with generated hypotheses and processing details
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        processing_steps = []
        
        # Step 1: Hypothesis Generation
        generation_step = self._run_generation_step(request.query, request.max_hypotheses)
        processing_steps.append(generation_step)
        hypotheses_data = generation_step.agent_outputs[0].metadata.get("hypotheses", [])
        
        # Step 2: Knowledge Retrieval (Proximity Agent)
        if self.enable_knowledge_retrieval:
            proximity_step = self._run_proximity_step(hypotheses_data)
            processing_steps.append(proximity_step)
            knowledge_data = proximity_step.agent_outputs[0].metadata.get("knowledge_analyses", [])
        else:
            knowledge_data = []
        
        # Step 3: Hypothesis Critique (Reflection Agent)
        reflection_step = self._run_reflection_step(hypotheses_data)
        processing_steps.append(reflection_step)
        critiques_data = reflection_step.agent_outputs[0].metadata.get("critiques", [])
        
        # Step 4: Hypothesis Ranking
        ranking_step = self._run_ranking_step(hypotheses_data, critiques_data)
        processing_steps.append(ranking_step)
        ranked_hypotheses = ranking_step.agent_outputs[0].metadata.get("ranked_hypotheses", hypotheses_data)
        
        # Step 5: Hypothesis Evolution (optional)
        if self.evolution_rounds > 0:
            evolution_step = self._run_evolution_step(ranked_hypotheses[:3], critiques_data)  # Evolve top 3
            processing_steps.append(evolution_step)
            evolved_hypotheses = evolution_step.agent_outputs[0].metadata.get("evolved_hypotheses", ranked_hypotheses)
            
            # Re-rank evolved hypotheses
            final_ranking_step = self._run_ranking_step(evolved_hypotheses, critiques_data)
            processing_steps.append(final_ranking_step)
            final_hypotheses = final_ranking_step.agent_outputs[0].metadata.get("ranked_hypotheses", evolved_hypotheses)
        else:
            final_hypotheses = ranked_hypotheses
        
        # Step 6: Meta-Review and Experimental Planning
        meta_review_step = self._run_meta_review_step(final_hypotheses, critiques_data, ranked_hypotheses)
        processing_steps.append(meta_review_step)
        final_reviews = meta_review_step.agent_outputs[0].metadata.get("final_reviews", [])
        # Convert to Hypothesis objects for response
        final_hypothesis_objects = self._convert_to_hypothesis_objects(
            final_hypotheses, critiques_data, knowledge_data, final_reviews
        )
        
        total_time = time.time() - start_time
        
        # Generate summary and recommendations
        summary = self._generate_summary(request.query, final_hypothesis_objects, final_reviews)
        recommendations = self._generate_recommendations(final_hypothesis_objects, final_reviews)
        
        return QueryResponse(
            query_id=query_id,
            original_query=request.query,
            hypotheses=final_hypothesis_objects,
            processing_steps=processing_steps,
            total_processing_time=total_time,
            summary=summary,
            recommendations=recommendations
        )
    
    def _run_generation_step(self, query: str, max_hypotheses: int) -> ProcessingStep:
        """Run hypothesis generation step"""
        start_time = time.time()
        
        hypotheses = self.generation_agent.generate_hypotheses(query, max_hypotheses)
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="hypothesis_generation",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="generation_agent",
                    output=f"Generated {len(hypotheses)} novel hypotheses using Gemma 3 12B",
                    metadata={"hypotheses": hypotheses, "model": "gemma3:12b"}
                )
            ]
        )
    
    def _run_proximity_step(self, hypotheses: List[Dict[str, Any]]) -> ProcessingStep:
        """Run knowledge retrieval step"""
        start_time = time.time()
        
        knowledge_analyses = self.proximity_agent.retrieve_knowledge(hypotheses)
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="knowledge_retrieval",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="proximity_agent",
                    output=f"Retrieved knowledge context for {len(hypotheses)} hypotheses",
                    metadata={"knowledge_analyses": knowledge_analyses, "model": "gemma2-9b-it"}
                )
            ]
        )
    
    def _run_reflection_step(self, hypotheses: List[Dict[str, Any]]) -> ProcessingStep:
        """Run hypothesis critique step"""
        start_time = time.time()
        
        critiques = self.reflection_agent.critique_hypotheses(hypotheses)
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="hypothesis_critique",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="reflection_agent",
                    output=f"Critiqued {len(hypotheses)} hypotheses using OpenAI o3-mini",
                    metadata={"critiques": critiques, "model": "o3-mini"}
                )
            ]
        )
    
    def _run_ranking_step(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]]
    ) -> ProcessingStep:
        """Run hypothesis ranking step"""
        start_time = time.time()
        
        ranked_hypotheses = self.ranking_agent.rank_hypotheses(hypotheses, critiques)
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="hypothesis_ranking",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="ranking_agent",
                    output=f"Ranked {len(hypotheses)} hypotheses by novelty and feasibility",
                    metadata={"ranked_hypotheses": ranked_hypotheses, "model": "gemma2-9b-it"}
                )
            ]
        )
    
    def _run_evolution_step(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]]
    ) -> ProcessingStep:
        """Run hypothesis evolution step"""
        start_time = time.time()
        
        evolved_hypotheses = self.evolution_agent.evolve_hypotheses(
            hypotheses, critiques, self.evolution_rounds
        )
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="hypothesis_evolution",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="evolution_agent",
                    output=f"Evolved {len(hypotheses)} hypotheses through {self.evolution_rounds} rounds",
                    metadata={"evolved_hypotheses": evolved_hypotheses, "model": "llama-3.3-70b-versatile"}
                )
            ]
        )
    
    def _run_meta_review_step(
        self, 
        hypotheses: List[Dict[str, Any]], 
        critiques: List[Dict[str, Any]],
        rankings: List[Dict[str, Any]]
    ) -> ProcessingStep:
        """Run meta-review and experimental planning step"""
        start_time = time.time()
        
        meta_review_result = self.meta_review_agent.final_review(hypotheses, critiques, rankings)
        
        end_time = time.time()
        
        return ProcessingStep(
            step_name="meta_review_and_planning",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=end_time - start_time,
            agent_outputs=[
                AgentOutput(
                    agent_name="meta_review_agent",
                    output=f"Completed final review and experimental planning for {len(hypotheses)} hypotheses",
                    metadata={"final_reviews": meta_review_result["final_reviews"], "model": "o3-mini"}
                )
            ]
        )
    
    def _convert_to_hypothesis_objects(
        self,
        hypotheses_data: List[Dict[str, Any]],
        critiques_data: List[Dict[str, Any]],
        knowledge_data: List[Dict[str, Any]],
        reviews_data: List[Dict[str, Any]]
    ) -> List[Hypothesis]:
        """Convert processed data to Hypothesis objects"""
        
        hypothesis_objects = []
        
        for hyp_data in hypotheses_data:
            # Find corresponding critique
            critique = next(
                (c for c in critiques_data if c.get("hypothesis_id") == hyp_data.get("id")), 
                {}
            )
            
            # Find corresponding review
            review = next(
                (r for r in reviews_data if r.get("hypothesis_id") == hyp_data.get("id")), 
                {}
            )
            
            # Find corresponding knowledge analysis
            knowledge = next(
                (k for k in knowledge_data if k.get("hypothesis_id") == hyp_data.get("id")), 
                {}
            )
            
            # Create experimental plan from review or fallback
            experimental_plan = "Step-by-step experimental plan:\n"
            if "experimental_plan" in review:
                plan_dict = review["experimental_plan"]
                if isinstance(plan_dict, dict):
                    for phase, description in plan_dict.items():
                        experimental_plan += f"{phase}: {description}\n"
                else:
                    experimental_plan += str(plan_dict)
            else:
                experimental_plan += hyp_data.get("research_approach", "Experimental approach to be determined")
            
            # Create citations from knowledge data
            citations = knowledge.get("literature_recommendations", [])
            if not citations:
                citations = ["Literature review pending", "Domain-specific references needed"]
            
            hypothesis_obj = Hypothesis(
                id=hyp_data.get("id", str(uuid.uuid4())),
                title=hyp_data.get("title", "Untitled Hypothesis"),
                description=hyp_data.get("description", ""),
                reasoning=hyp_data.get("reasoning", ""),
                novelty_score=critique.get("novelty_score", 0.7),
                feasibility_score=critique.get("feasibility_score", 0.7),
                confidence_score=review.get("confidence_rating", 0.7),
                experimental_plan=experimental_plan,
                citations=citations
            )
            
            hypothesis_objects.append(hypothesis_obj)
        
        return hypothesis_objects
    
    def _generate_summary(
        self, 
        query: str, 
        hypotheses: List[Hypothesis], 
        reviews: List[Dict[str, Any]]
    ) -> str:
        """Generate summary of results"""
        return f"Generated {len(hypotheses)} novel hypotheses addressing: {query}. " \
               f"Hypotheses underwent multi-agent analysis including generation (Gemma 3 12B), " \
               f"critique (OpenAI o3-mini), ranking (Gemma 2 9B), evolution (Llama 3.3 70B), " \
               f"and final meta-review (o3-mini). Average confidence: " \
               f"{sum(h.confidence_score for h in hypotheses) / len(hypotheses):.2f}"
    
    def _generate_recommendations(
        self, 
        hypotheses: List[Hypothesis], 
        reviews: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate research recommendations"""
        recommendations = [
            "Conduct comprehensive literature review for each hypothesis",
            "Prioritize hypotheses based on confidence scores and feasibility",
            "Seek domain expert validation and feedback",
            "Design pilot studies for highest-ranked hypotheses",
            "Consider interdisciplinary collaboration opportunities",
            "Plan iterative hypothesis refinement based on initial results"
        ]
        
        # Add specific recommendations from reviews
        for review in reviews:
            collab_recs = review.get("collaboration_recommendations", [])
            for rec in collab_recs[:2]:  # Add top 2 collaboration recommendations
                recommendations.append(f"Consider collaboration: {rec}")
        
        return recommendations[:8]  # Return top 8 recommendations