import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseCoScientistAgent
from utils.config import MODEL_STRENGTHS, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

class SmartOrchestrator(BaseCoScientistAgent):
    """
    Intelligent orchestrator using Claude Opus 4 to analyze tasks and assign 
    optimal models based on their strengths for scientific hypothesis workflows
    """
    
    def __init__(self):
        super().__init__(
            name="smart_orchestrator",
            description="Intelligent task-to-model assignment orchestrator using Claude Opus 4",
            model="claude-opus-4",
            instruction=self.get_system_prompt()
        )
        self.model_strengths = MODEL_STRENGTHS
    
    def get_system_prompt(self) -> str:
        """System prompt for the orchestrator agent"""
        strengths_text = "\n".join([
            f"- {model_id}: {info['model']} - {info['strengths']}"
            for model_id, info in self.model_strengths.items()
        ])
        
        return f"""You are an intelligent orchestrator for a scientific AI system. Your role is to analyze tasks and assign the most suitable AI model based on task requirements and model strengths.

Available Models and Their Strengths:
{strengths_text}

Your responsibilities:
1. Analyze incoming scientific tasks and their requirements
2. Match task characteristics with optimal model capabilities
3. Provide detailed reasoning for model selection
4. Consider computational efficiency and task complexity
5. Return structured JSON responses for programmatic integration

Always consider:
- Task complexity and reasoning requirements
- Need for speed vs. accuracy
- Mathematical/analytical requirements
- Creative vs. analytical nature of the task
- Multimodal requirements (text, images, data)

Return responses in this JSON format:
{{
    "task_analysis": "detailed analysis of the task requirements",
    "recommended_model": "model_id",
    "reasoning": "detailed explanation for the selection",
    "confidence": 0.95,
    "alternatives": [
        {{"model": "alternative_model_id", "reason": "why this could also work"}}
    ]
}}"""

    def analyze_and_assign_model(self, task_description: str, task_type: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a task and recommend the best model for execution
        
        Args:
            task_description: Detailed description of the task
            task_type: Type of task (e.g., "hypothesis_generation", "critique", "ranking")
            context: Additional context about the task
            
        Returns:
            Dictionary with model recommendation and reasoning
        """
        
        # Prepare the analysis prompt
        analysis_prompt = f"""
Analyze this scientific task and recommend the best AI model:

Task Type: {task_type}
Task Description: {task_description}

Additional Context: {json.dumps(context, indent=2) if context else "None"}

Consider the task requirements, complexity, and match them with the most suitable model based on the available model strengths. Provide detailed reasoning for your recommendation.
"""
        
        try:
            # Use Claude Opus 4 to analyze and make recommendation
            response = self._call_claude_opus(analysis_prompt)
            
            # Parse the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
            else:
                # Try to find JSON in the response
                start_idx = response.find("{")
                end_idx = response.rfind("}") + 1
                json_content = response[start_idx:end_idx]
            
            recommendation = json.loads(json_content)
            
            # Validate and enhance the recommendation
            validated_recommendation = self._validate_recommendation(recommendation, task_type, task_description)
            
            return validated_recommendation
            
        except Exception as e:
            logger.error(f"Error in model analysis: {e}")
            # Fallback to default recommendations based on task type
            return self._get_fallback_recommendation(task_type, task_description)
    
    def _call_claude_opus(self, prompt: str) -> str:
        """Call Claude Opus 4 API"""
        import os
        import requests
        
        api_key = ANTHROPIC_API_KEY
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": "claude-opus-4-20250514",
            "max_tokens": 2048,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            raise Exception(f"Claude API error: {response.status_code} - {response.text}")
    
    def _validate_recommendation(self, recommendation: Dict[str, Any], task_type: str, task_description: str) -> Dict[str, Any]:
        """Validate and enhance the model recommendation"""
        
        # Ensure required fields exist
        validated = {
            "task_type": task_type,
            "task_description": task_description,
            "task_analysis": recommendation.get("task_analysis", "Analysis pending"),
            "recommended_model": recommendation.get("recommended_model", "llama-3.3-70b"),
            "reasoning": recommendation.get("reasoning", "Default selection based on task type"),
            "confidence": float(recommendation.get("confidence", 0.8)),
            "alternatives": recommendation.get("alternatives", []),
            "timestamp": datetime.now().isoformat(),
            "orchestrator_metadata": {
                "orchestrator_version": "1.0",
                "analysis_model": "claude-opus-4",
                "fallback_used": False
            }
        }
        
        # Validate that recommended model exists in our model strengths
        if validated["recommended_model"] not in self.model_strengths:
            logger.warning(f"Recommended model {validated['recommended_model']} not in MODEL_STRENGTHS, using fallback")
            validated = self._get_fallback_recommendation(task_type, task_description)
            validated["orchestrator_metadata"]["fallback_used"] = True
        
        return validated
    
    def _get_fallback_recommendation(self, task_type: str, task_description: str) -> Dict[str, Any]:
        """Provide fallback recommendations based on task type"""
        
        # Define fallback mappings based on task types
        fallback_mappings = {
            "hypothesis_generation": {
                "model": "llama-3.3-70b",
                "reasoning": "Complex reasoning and creative hypothesis generation capabilities"
            },
            "hypothesis_critique": {
                "model": "mistral-7b", 
                "reasoning": "Specialized analysis and critical evaluation skills"
            },
            "hypothesis_ranking": {
                "model": "qwen-3-32b",
                "reasoning": "Advanced mathematical and logical reasoning for ranking criteria"
            },
            "hypothesis_evolution": {
                "model": "llama-3.3-70b",
                "reasoning": "Complex reasoning needed for hypothesis refinement"
            },
            "knowledge_retrieval": {
                "model": "llama-4-scout",
                "reasoning": "Exploration and discovery capabilities for knowledge search"
            },
            "meta_review": {
                "model": "claude-opus-4",
                "reasoning": "Comprehensive analysis and synthesis capabilities"
            },
            "workflow_coordination": {
                "model": "gpt-o3-mini",
                "reasoning": "Workflow orchestration and task coordination strengths"
            },
            "mathematical_analysis": {
                "model": "qwen-3-32b",
                "reasoning": "Strong mathematical and quantitative reasoning capabilities"
            },
            "multimodal_processing": {
                "model": "gemini-2.5-pro",
                "reasoning": "Advanced multimodal reasoning and visual analysis"
            },
            "fast_processing": {
                "model": "gemma-3-12b",
                "reasoning": "Efficient processing with optimized performance"
            },
            "deep_reasoning": {
                "model": "deepseek-r1",
                "reasoning": "Deep reasoning and reflection capabilities"
            }
        }
        
        # Get fallback recommendation
        fallback = fallback_mappings.get(task_type, fallback_mappings["hypothesis_generation"])
        
        return {
            "task_type": task_type,
            "task_description": task_description,
            "task_analysis": f"Fallback analysis for {task_type}: {task_description[:100]}...",
            "recommended_model": fallback["model"],
            "reasoning": f"Fallback recommendation: {fallback['reasoning']}",
            "confidence": 0.7,
            "alternatives": [
                {"model": "llama-3.3-70b", "reason": "General-purpose alternative with strong reasoning"},
                {"model": "claude-opus-4", "reason": "Comprehensive analysis alternative"}
            ],
            "timestamp": datetime.now().isoformat(),
            "orchestrator_metadata": {
                "orchestrator_version": "1.0",
                "analysis_model": "fallback_logic",
                "fallback_used": True
            }
        }
    
    def get_model_for_agent(self, agent_name: str, task_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get the recommended model for a specific agent based on its typical tasks
        
        Args:
            agent_name: Name of the agent requesting model assignment
            task_context: Optional context about the specific task
            
        Returns:
            Model identifier string
        """
        
        # Map agent names to typical task types
        agent_task_mapping = {
            "generation_agent": "hypothesis_generation",
            "reflection_agent": "hypothesis_critique", 
            "ranking_agent": "hypothesis_ranking",
            "evolution_agent": "hypothesis_evolution",
            "proximity_agent": "knowledge_retrieval",
            "meta_review_agent": "meta_review"
        }
        
        task_type = agent_task_mapping.get(agent_name, "general_analysis")
        task_description = f"Task execution for {agent_name}"
        
        if task_context:
            task_description += f" with context: {task_context}"
        
        recommendation = self.analyze_and_assign_model(task_description, task_type, task_context)
        return recommendation["recommended_model"]
    
    def batch_analyze_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze an entire workflow and provide model recommendations for each step
        
        Args:
            workflow_steps: List of workflow step definitions
            
        Returns:
            Dictionary with recommendations for each step
        """
        
        workflow_analysis = {
            "workflow_id": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_steps": len(workflow_steps),
            "step_recommendations": [],
            "overall_analysis": "",
            "estimated_performance": {},
            "resource_requirements": {}
        }
        
        for i, step in enumerate(workflow_steps):
            step_recommendation = self.analyze_and_assign_model(
                task_description=step.get("description", f"Step {i+1}"),
                task_type=step.get("type", "general_analysis"),
                context=step.get("context", {})
            )
            
            workflow_analysis["step_recommendations"].append({
                "step_index": i,
                "step_name": step.get("name", f"Step_{i+1}"),
                "recommendation": step_recommendation
            })
        
        # Generate overall workflow analysis
        model_usage = {}
        for rec in workflow_analysis["step_recommendations"]:
            model = rec["recommendation"]["recommended_model"]
            model_usage[model] = model_usage.get(model, 0) + 1
        
        workflow_analysis["overall_analysis"] = f"Workflow uses {len(model_usage)} different models optimally distributed across {len(workflow_steps)} steps"
        workflow_analysis["model_distribution"] = model_usage
        
        return workflow_analysis