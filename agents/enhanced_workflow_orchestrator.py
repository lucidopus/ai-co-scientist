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
from agents.smart_orchestrator import SmartOrchestrator

from utils.models import (
    QueryRequest,
    QueryResponse,
    Hypothesis,
    ProcessingStep,
    AgentOutput,
)
from utils.memory_service import enhanced_memory_service

class EnhancedAICoScientistWorkflow:
    """
    Enhanced ADK-based workflow orchestrator with intelligent model assignment
    using Claude Opus 4 for optimal task-to-model matching
    """
    
    def __init__(self, memory_service=None):
        # Initialize enhanced memory service
        self.memory_service = memory_service or enhanced_memory_service
        
        # Initialize smart orchestrator for model assignment
        self.smart_orchestrator = SmartOrchestrator()
        
        # Initialize all agents (models will be assigned dynamically)
        self.generation_agent = GenerationAgent()
        self.reflection_agent = ReflectionAgent()
        self.ranking_agent = RankingAgent()
        self.evolution_agent = EvolutionAgent()
        self.proximity_agent = ProximityAgent()
        self.meta_review_agent = MetaReviewAgent()
        
        # Workflow configuration
        self.evolution_rounds = 1
        self.enable_knowledge_retrieval = True
        
        # Track model assignments and performance
        self.model_assignments = {}
        self.step_performance = {}
    
    def process_scientific_query(self, request: QueryRequest) -> QueryResponse:
        """
        Main workflow with intelligent model assignment for processing scientific queries
        
        Args:
            request: QueryRequest with research query and parameters
            
        Returns:
            QueryResponse with generated hypotheses and processing details
        """
        start_time = time.time()
        query_id = str(uuid.uuid4())
        processing_steps = []
        
        # Analyze the entire workflow and get model recommendations
        workflow_steps = self._define_workflow_steps(request)
        workflow_analysis = self.smart_orchestrator.batch_analyze_workflow(workflow_steps)
        
        # Create research session in memory
        session_data = {
            "session_id": query_id,
            "research_query": request.query,
            "status": "active",
            "created_at": datetime.now(),
            "hypotheses": [],
            "processing_steps": [],
            "current_round": 1,
            "max_rounds": 1,
            "total_processing_time": 0.0,
            "quality_score": 0.0,
            "workflow_analysis": workflow_analysis,
            "model_assignments": {}
        }
        
        # Step 1: Hypothesis Generation (with intelligent model assignment)
        step_recommendation = workflow_analysis["step_recommendations"][0]["recommendation"]
        generation_step = self._run_generation_step(
            request.query, 
            request.max_hypotheses, 
            query_id,
            assigned_model=step_recommendation["recommended_model"],
            model_reasoning=step_recommendation["reasoning"]
        )
        processing_steps.append(generation_step)
        hypotheses_data = generation_step.agent_outputs[0].metadata.get("hypotheses", [])
        
        # Store hypotheses in enhanced memory
        for hypothesis in hypotheses_data:
            hypothesis["research_query"] = request.query
            hypothesis["source_session"] = query_id
            stored_id = self.memory_service.store_hypothesis(hypothesis)
            hypothesis["stored_id"] = stored_id
        
        # Step 2: Knowledge Retrieval (Proximity Agent)
        if self.enable_knowledge_retrieval:
            step_recommendation = workflow_analysis["step_recommendations"][1]["recommendation"]
            proximity_step = self._run_proximity_step(
                hypotheses_data,
                assigned_model=step_recommendation["recommended_model"],
                model_reasoning=step_recommendation["reasoning"]
            )
            processing_steps.append(proximity_step)
            knowledge_data = proximity_step.agent_outputs[0].metadata.get("knowledge_analyses", [])
        else:
            knowledge_data = []
        
        # Step 3: Hypothesis Critique (Reflection Agent)
        step_recommendation = workflow_analysis["step_recommendations"][2]["recommendation"]
        reflection_step = self._run_reflection_step(
            hypotheses_data,
            assigned_model=step_recommendation["recommended_model"],
            model_reasoning=step_recommendation["reasoning"]
        )
        processing_steps.append(reflection_step)
        critiques_data = reflection_step.agent_outputs[0].metadata.get("critiques", [])
        
        # Store evaluations in memory
        for critique in critiques_data:
            hypothesis_id = critique.get("hypothesis_id")
            if hypothesis_id:
                evaluation_data = {
                    "validity_score": critique.get("validity_score", 0.0),
                    "novelty_score": critique.get("novelty_score", 0.0),
                    "feasibility_score": critique.get("feasibility_score", 0.0),
                    "impact_score": critique.get("impact_score", 0.0),
                    "final_score": critique.get("final_score", 0.0),
                    "feedback": critique.get("feedback", {}),
                    "detailed_analysis": critique.get("detailed_analysis", ""),
                    "recommendations": critique.get("recommendations", []),
                    "model_used": step_recommendation["recommended_model"],
                    "processing_time": reflection_step.duration_seconds,
                    "confidence": critique.get("confidence", 0.0)
                }
                self.memory_service.store_evaluation(hypothesis_id, evaluation_data, "reflection_agent")
        
        # Step 4: Hypothesis Ranking
        step_recommendation = workflow_analysis["step_recommendations"][3]["recommendation"]
        ranking_step = self._run_ranking_step(
            hypotheses_data, 
            critiques_data,
            assigned_model=step_recommendation["recommended_model"],
            model_reasoning=step_recommendation["reasoning"]
        )
        processing_steps.append(ranking_step)
        ranked_hypotheses = ranking_step.agent_outputs[0].metadata.get("ranked_hypotheses", hypotheses_data)
        
        # Step 5: Hypothesis Evolution (optional)
        if self.evolution_rounds > 0:
            step_recommendation = workflow_analysis["step_recommendations"][4]["recommendation"]
            evolution_step = self._run_evolution_step(
                ranked_hypotheses[:3], 
                critiques_data,
                assigned_model=step_recommendation["recommended_model"],
                model_reasoning=step_recommendation["reasoning"]
            )
            processing_steps.append(evolution_step)
            evolved_hypotheses = evolution_step.agent_outputs[0].metadata.get("evolved_hypotheses", ranked_hypotheses)
            
            # Re-rank evolved hypotheses
            final_ranking_step = self._run_ranking_step(evolved_hypotheses, critiques_data)
            processing_steps.append(final_ranking_step)
            final_hypotheses = final_ranking_step.agent_outputs[0].metadata.get("ranked_hypotheses", evolved_hypotheses)
        else:
            final_hypotheses = ranked_hypotheses
        
        # Step 6: Meta-Review and Experimental Planning
        step_recommendation = workflow_analysis["step_recommendations"][-1]["recommendation"]
        meta_review_step = self._run_meta_review_step(
            final_hypotheses, 
            critiques_data, 
            ranked_hypotheses,
            assigned_model=step_recommendation["recommended_model"],
            model_reasoning=step_recommendation["reasoning"]
        )
        processing_steps.append(meta_review_step)
        final_reviews = meta_review_step.agent_outputs[0].metadata.get("final_reviews", [])
        
        # Convert to Hypothesis objects for response
        final_hypothesis_objects = self._convert_to_hypothesis_objects(
            final_hypotheses, critiques_data, knowledge_data, final_reviews
        )
        
        total_time = time.time() - start_time
        
        # Update session data with final results
        session_data.update({
            "status": "completed",
            "hypotheses": [h.dict() if hasattr(h, 'dict') else h for h in final_hypothesis_objects],
            "processing_steps": [step.dict() if hasattr(step, 'dict') else step for step in processing_steps],
            "total_processing_time": total_time,
            "quality_score": sum(h.confidence_score for h in final_hypothesis_objects) / len(final_hypothesis_objects) if final_hypothesis_objects else 0.0,
            "model_assignments": self.model_assignments
        })
        
        # Store final session in memory
        self.memory_service.store_research_session(session_data)
        
        # Generate summary and recommendations
        summary = self._generate_enhanced_summary(request.query, final_hypothesis_objects, final_reviews, workflow_analysis)
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
    
    def _define_workflow_steps(self, request: QueryRequest) -> List[Dict[str, Any]]:
        """Define the workflow steps for orchestrator analysis"""
        return [
            {
                "name": "hypothesis_generation",
                "type": "hypothesis_generation",
                "description": f"Generate {request.max_hypotheses} novel scientific hypotheses for: {request.query}",
                "context": {"max_hypotheses": request.max_hypotheses, "query_complexity": len(request.query.split())}
            },
            {
                "name": "knowledge_retrieval", 
                "type": "knowledge_retrieval",
                "description": "Retrieve and analyze relevant scientific knowledge and literature",
                "context": {"retrieval_scope": "comprehensive"}
            },
            {
                "name": "hypothesis_critique",
                "type": "hypothesis_critique", 
                "description": "Critically evaluate hypotheses for validity, novelty, feasibility, and impact",
                "context": {"evaluation_depth": "comprehensive"}
            },
            {
                "name": "hypothesis_ranking",
                "type": "hypothesis_ranking",
                "description": "Rank hypotheses using multi-criteria assessment",
                "context": {"ranking_criteria": ["novelty", "feasibility", "impact", "validity"]}
            },
            {
                "name": "hypothesis_evolution", 
                "type": "hypothesis_evolution",
                "description": "Evolve and refine top-ranked hypotheses",
                "context": {"evolution_rounds": self.evolution_rounds}
            },
            {
                "name": "meta_review",
                "type": "meta_review",
                "description": "Comprehensive final review and experimental planning",
                "context": {"review_scope": "comprehensive"}
            }
        ]
    
    def _run_generation_step(self, query: str, max_hypotheses: int, session_id: str = None, 
                           assigned_model: str = None, model_reasoning: str = None) -> ProcessingStep:
        """Run hypothesis generation step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to generation agent if provided
        if assigned_model:
            self.generation_agent._actual_model = assigned_model
            self.model_assignments["generation_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "hypothesis_generation"
            }
        
        hypotheses = self.generation_agent.generate_hypotheses(query, max_hypotheses)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["generation"] = duration
        
        return ProcessingStep(
            step_name="hypothesis_generation",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="generation_agent",
                    output=f"Generated {len(hypotheses)} novel hypotheses using {assigned_model or 'default model'}",
                    metadata={
                        "hypotheses": hypotheses, 
                        "model": assigned_model or "gemma3:12b",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _run_proximity_step(self, hypotheses: List[Dict[str, Any]], 
                          assigned_model: str = None, model_reasoning: str = None) -> ProcessingStep:
        """Run knowledge retrieval step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to proximity agent if provided
        if assigned_model:
            self.proximity_agent._actual_model = assigned_model
            self.model_assignments["proximity_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "knowledge_retrieval"
            }
        
        knowledge_analyses = self.proximity_agent.retrieve_knowledge(hypotheses)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["proximity"] = duration
        
        return ProcessingStep(
            step_name="knowledge_retrieval",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="proximity_agent",
                    output=f"Retrieved knowledge context for {len(hypotheses)} hypotheses using {assigned_model or 'default model'}",
                    metadata={
                        "knowledge_analyses": knowledge_analyses, 
                        "model": assigned_model or "meta-llama/llama-4-scout-17b-16e-instruct",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _run_reflection_step(self, hypotheses: List[Dict[str, Any]], 
                           assigned_model: str = None, model_reasoning: str = None) -> ProcessingStep:
        """Run hypothesis critique step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to reflection agent if provided
        if assigned_model:
            self.reflection_agent._actual_model = assigned_model
            self.model_assignments["reflection_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "hypothesis_critique"
            }
        
        critiques = self.reflection_agent.critique_hypotheses(hypotheses)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["reflection"] = duration
        
        return ProcessingStep(
            step_name="hypothesis_critique",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="reflection_agent",
                    output=f"Critiqued {len(hypotheses)} hypotheses using {assigned_model or 'default model'}",
                    metadata={
                        "critiques": critiques, 
                        "model": assigned_model or "llama-3.3-70b-versatile",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _run_ranking_step(self, hypotheses: List[Dict[str, Any]], critiques: List[Dict[str, Any]],
                         assigned_model: str = None, model_reasoning: str = None) -> ProcessingStep:
        """Run hypothesis ranking step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to ranking agent if provided
        if assigned_model:
            self.ranking_agent._actual_model = assigned_model
            self.model_assignments["ranking_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "hypothesis_ranking"
            }
        
        ranked_hypotheses = self.ranking_agent.rank_hypotheses(hypotheses, critiques)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["ranking"] = duration
        
        return ProcessingStep(
            step_name="hypothesis_ranking",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="ranking_agent",
                    output=f"Ranked {len(hypotheses)} hypotheses using {assigned_model or 'default model'}",
                    metadata={
                        "ranked_hypotheses": ranked_hypotheses, 
                        "model": assigned_model or "qwen/qwen3-32b",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _run_evolution_step(self, hypotheses: List[Dict[str, Any]], critiques: List[Dict[str, Any]],
                          assigned_model: str = None, model_reasoning: str = None) -> ProcessingStep:
        """Run hypothesis evolution step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to evolution agent if provided
        if assigned_model:
            self.evolution_agent._actual_model = assigned_model
            self.model_assignments["evolution_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "hypothesis_evolution"
            }
        
        evolved_hypotheses = self.evolution_agent.evolve_hypotheses(hypotheses, critiques, self.evolution_rounds)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["evolution"] = duration
        
        return ProcessingStep(
            step_name="hypothesis_evolution",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="evolution_agent",
                    output=f"Evolved {len(hypotheses)} hypotheses using {assigned_model or 'default model'}",
                    metadata={
                        "evolved_hypotheses": evolved_hypotheses, 
                        "model": assigned_model or "llama-3.3-70b-versatile",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _run_meta_review_step(self, hypotheses: List[Dict[str, Any]], critiques: List[Dict[str, Any]], 
                            rankings: List[Dict[str, Any]], assigned_model: str = None, 
                            model_reasoning: str = None) -> ProcessingStep:
        """Run meta-review and experimental planning step with intelligent model assignment"""
        start_time = time.time()
        
        # Assign model to meta review agent if provided
        if assigned_model:
            self.meta_review_agent._actual_model = assigned_model
            self.model_assignments["meta_review_agent"] = {
                "assigned_model": assigned_model,
                "reasoning": model_reasoning,
                "step": "meta_review"
            }
        
        meta_review_result = self.meta_review_agent.final_review(hypotheses, critiques, rankings)
        
        end_time = time.time()
        duration = end_time - start_time
        self.step_performance["meta_review"] = duration
        
        return ProcessingStep(
            step_name="meta_review_and_planning",
            status="completed",
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            duration_seconds=duration,
            agent_outputs=[
                AgentOutput(
                    agent_name="meta_review_agent",
                    output=f"Completed final review using {assigned_model or 'default model'}",
                    metadata={
                        "final_reviews": meta_review_result["final_reviews"], 
                        "model": assigned_model or "claude-opus-4",
                        "model_reasoning": model_reasoning,
                        "orchestrator_assignment": assigned_model is not None
                    }
                )
            ]
        )
    
    def _convert_to_hypothesis_objects(self, hypotheses_data: List[Dict[str, Any]], critiques_data: List[Dict[str, Any]], 
                                     knowledge_data: List[Dict[str, Any]], reviews_data: List[Dict[str, Any]]) -> List[Hypothesis]:
        """Convert processed data to Hypothesis objects"""
        hypothesis_objects = []
        
        for hyp_data in hypotheses_data:
            # Find corresponding critique
            critique = next((c for c in critiques_data if c.get("hypothesis_id") == hyp_data.get("id")), {})
            
            # Find corresponding review
            review = next((r for r in reviews_data if r.get("hypothesis_id") == hyp_data.get("id")), {})
            
            # Find corresponding knowledge analysis
            knowledge = next((k for k in knowledge_data if k.get("hypothesis_id") == hyp_data.get("id")), {})
            
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
    
    def _generate_enhanced_summary(self, query: str, hypotheses: List[Hypothesis], 
                                 reviews: List[Dict[str, Any]], workflow_analysis: Dict[str, Any]) -> str:
        """Generate enhanced summary with orchestrator insights"""
        model_usage = workflow_analysis.get("model_distribution", {})
        model_names = ", ".join([f"{model} ({count}x)" for model, count in model_usage.items()])
        
        return f"Generated {len(hypotheses)} novel hypotheses for: {query}. " \
               f"Intelligent orchestration using Claude Opus 4 assigned optimal models: {model_names}. " \
               f"Average confidence: {sum(h.confidence_score for h in hypotheses) / len(hypotheses):.2f}. " \
               f"Workflow completed with {len(workflow_analysis['step_recommendations'])} optimized steps."
    
    def _generate_recommendations(self, hypotheses: List[Hypothesis], reviews: List[Dict[str, Any]]) -> List[str]:
        """Generate research recommendations"""
        recommendations = [
            "Conduct comprehensive literature review for each hypothesis",
            "Prioritize hypotheses based on confidence scores and feasibility", 
            "Seek domain expert validation and feedback",
            "Design pilot studies for highest-ranked hypotheses",
            "Consider interdisciplinary collaboration opportunities",
            "Plan iterative hypothesis refinement based on initial results",
            "Leverage intelligent model assignment for future analyses"
        ]
        
        # Add specific recommendations from reviews
        for review in reviews:
            collab_recs = review.get("collaboration_recommendations", [])
            for rec in collab_recs[:2]:  # Add top 2 collaboration recommendations
                recommendations.append(f"Consider collaboration: {rec}")
        
        return recommendations[:8]  # Return top 8 recommendations