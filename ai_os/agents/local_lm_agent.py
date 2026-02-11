"""
Local LM Agent - Offline Workflow Design

Provides offline workflow generation using local LLM models (Ollama, LM Studio).
Handles model communication, workflow generation, and context management
for offline-first processing.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import subprocess
import requests
from enum import Enum
import aiohttp
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class LocalLMProvider(Enum):
    """Supported local LLM providers."""
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"
    CUSTOM = "custom"


@dataclass
class WorkflowStep:
    """Single step in a generated workflow."""
    step_id: str
    action: str
    command: str
    parameters: Dict[str, Any]
    description: str
    expected_result: Optional[str] = None


@dataclass
class GeneratedWorkflow:
    """Complete generated workflow."""
    name: str
    description: str
    steps: List[WorkflowStep]
    context: Dict[str, Any]
    estimated_time: Optional[int] = None
    confidence_score: Optional[float] = None


class LocalLMAgent:
    """
    Local LLM agent for offline workflow generation.
    
    Connects to local LLM providers (Ollama, LM Studio) to generate
    workflows from natural language input.
    """
    
    def __init__(
        self,
        provider: LocalLMProvider = LocalLMProvider.OLLAMA,
        model_name: str = "llama2",
        base_url: str = "http://localhost:11434",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize local LM agent.
        
        Args:
            provider: Local LLM provider
            model_name: Name of the model to use
            base_url: Base URL for the provider API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Provider-specific configuration
        self.api_endpoint = self._get_api_endpoint()
        self.headers = {"Content-Type": "application/json"}
        
        # Test connection on initialization
        self._is_available = False
        self._test_connection()
    
    def _get_api_endpoint(self) -> str:
        """Get API endpoint for the provider."""
        if self.provider == LocalLMProvider.OLLAMA:
            return f"{self.base_url}/api/generate"
        elif self.provider == LocalLMProvider.LM_STUDIO:
            return f"{self.base_url}/v1/chat/completions"
        else:
            return f"{self.base_url}/chat/completions"
    
    def _test_connection(self) -> bool:
        """Test connection to local LLM provider."""
        try:
            if self.provider == LocalLMProvider.OLLAMA:
                # Test Ollama connection with proper URL handling
                parsed_url = urlparse(self.base_url)
                test_url = f"{self.base_url}/api/tags"
                logger.info(f"Testing Ollama connection to: {test_url}")
                logger.info(f"Parsed URL - host: '{parsed_url.hostname}', port: {parsed_url.port}")
                
                # Use session with no proxy for local connections
                session = requests.Session()
                session.trust_env = False  # Don't use proxy settings from environment
                response = session.get(test_url, timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    if self.model_name in model_names:
                        self._is_available = True
                        logger.info(f"Connected to Ollama with model: {self.model_name}")
                        return True
                    else:
                        logger.warning(f"Model {self.model_name} not found. Available: {model_names}")
                        return False
                else:
                    logger.error(f"Ollama connection failed: {response.status_code}")
                    return False
            
            elif self.provider == LocalLMProvider.LM_STUDIO:
                # Test LM Studio connection
                response = requests.get(f"{self.base_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    self._is_available = True
                    logger.info(f"Connected to LM Studio")
                    return True
                else:
                    logger.error(f"LM Studio connection failed: {response.status_code}")
                    return False
            
            else:
                # Test custom endpoint
                response = requests.get(f"{self.base_url}/health", timeout=5)
                self._is_available = response.status_code == 200
                return self._is_available
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            self._is_available = False
            return False
    
    @property
    def is_available(self) -> bool:
        """Check if local LLM is available."""
        return self._is_available
    
    async def generate_workflow(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        examples: Optional[List[str]] = None
    ) -> GeneratedWorkflow:
        """
        Generate workflow from natural language input.
        
        Args:
            user_input: Natural language description of desired workflow
            context: Additional context for workflow generation
            examples: Example workflows for few-shot learning
            
        Returns:
            Generated workflow with steps and metadata
        """
        if not self.is_available:
            raise RuntimeError("Local LLM not available")
        
        # Build prompt
        prompt = self._build_workflow_prompt(user_input, context, examples)
        
        # Generate response
        response = await self._generate_response(prompt)
        
        # Parse workflow from response
        workflow = self._parse_workflow_response(response, user_input)
        
        logger.info(f"Generated workflow: {workflow.name} with {len(workflow.steps)} steps")
        return workflow
    
    def _build_workflow_prompt(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        examples: Optional[List[str]] = None
    ) -> str:
        """Build prompt for workflow generation."""
        prompt = """You are an AI workflow automation assistant. Generate executable workflows from natural language descriptions.

Rules:
1. Break down the task into clear, sequential steps
2. Each step should have a specific action and command
3. Use standard commands (terminal, python, applescript)
4. Include parameters and expected results
5. Be specific and actionable

Output format (JSON):
{
    "name": "Workflow Name",
    "description": "Brief description of what the workflow does",
    "steps": [
        {
            "step_id": "step_1",
            "action": "terminal|python|applescript",
            "command": "Command to execute",
            "parameters": {"key": "value"},
            "description": "What this step does",
            "expected_result": "Expected outcome"
        }
    ],
    "estimated_time": 30,
    "confidence_score": 0.8
}

Example workflows:
"""
        
        # Add examples if provided
        if examples:
            for example in examples:
                prompt += f"\n{example}\n"
        else:
            # Add default examples
            prompt += """
{
    "name": "Organize Downloads Folder",
    "description": "Organize files in Downloads folder by type",
    "steps": [
        {
            "step_id": "step_1",
            "action": "terminal",
            "command": "mkdir -p ~/Downloads/{images,documents,videos,others}",
            "parameters": {},
            "description": "Create organized directories",
            "expected_result": "Directories created"
        },
        {
            "step_id": "step_2", 
            "action": "terminal",
            "command": "mv ~/Downloads/*.jpg ~/Downloads/images/ 2>/dev/null",
            "parameters": {},
            "description": "Move image files",
            "expected_result": "Images moved to images folder"
        }
    ],
    "estimated_time": 15,
    "confidence_score": 0.9
}
"""
        
        # Add user input
        prompt += f"\n\nGenerate a workflow for: {user_input}\n\n"
        
        # Add context if provided
        if context:
            prompt += f"Additional context: {json.dumps(context, indent=2)}\n\n"
        
        prompt += "Generate only the JSON workflow response:"
        
        return prompt
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response from local LLM."""
        for attempt in range(self.max_retries):
            try:
                if self.provider == LocalLMProvider.OLLAMA:
                    response = await self._ollama_generate(prompt)
                elif self.provider == LocalLMProvider.LM_STUDIO:
                    response = await self._lm_studio_generate(prompt)
                else:
                    response = await self._custom_generate(prompt)
                
                return response
                
            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(1)
        
        raise RuntimeError("Failed to generate response after all retries")
    
    async def _ollama_generate(self, prompt: str) -> str:
        """Generate using Ollama API."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        response = requests.post(
            self.api_endpoint,
            json=payload,
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Ollama API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result.get("response", "")
    
    async def _lm_studio_generate(self, prompt: str) -> str:
        """Generate using LM Studio API."""
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful workflow generation assistant."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.api_endpoint,
            json=payload,
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"LM Studio API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    async def _custom_generate(self, prompt: str) -> str:
        """Generate using custom API endpoint."""
        payload = {
            "prompt": prompt,
            "model": self.model_name,
            "max_tokens": 2000
        }
        
        response = requests.post(
            self.api_endpoint,
            json=payload,
            headers=self.headers,
            timeout=self.timeout
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"Custom API error: {response.status_code} - {response.text}")
        
        result = response.json()
        return result.get("text", result.get("response", ""))
    
    def _parse_workflow_response(self, response: str, user_input: str) -> GeneratedWorkflow:
        """Parse workflow from LLM response."""
        try:
            # Try to extract JSON from response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            workflow_data = json.loads(json_str)
            
            # Validate required fields
            if not all(key in workflow_data for key in ["name", "description", "steps"]):
                raise ValueError("Missing required fields in workflow")
            
            # Parse steps
            steps = []
            for step_data in workflow_data["steps"]:
                step = WorkflowStep(
                    step_id=step_data.get("step_id", f"step_{len(steps) + 1}"),
                    action=step_data.get("action", "terminal"),
                    command=step_data.get("command", ""),
                    parameters=step_data.get("parameters", {}),
                    description=step_data.get("description", ""),
                    expected_result=step_data.get("expected_result")
                )
                steps.append(step)
            
            return GeneratedWorkflow(
                name=workflow_data["name"],
                description=workflow_data["description"],
                steps=steps,
                context={"user_input": user_input},
                estimated_time=workflow_data.get("estimated_time"),
                confidence_score=workflow_data.get("confidence_score")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse workflow response: {e}")
            # Return fallback workflow
            return self._create_fallback_workflow(user_input)
    
    def _create_fallback_workflow(self, user_input: str) -> GeneratedWorkflow:
        """Create a simple fallback workflow when parsing fails."""
        return GeneratedWorkflow(
            name="Fallback Workflow",
            description=f"Generated for: {user_input}",
            steps=[
                WorkflowStep(
                    step_id="step_1",
                    action="terminal",
                    command="echo 'Workflow execution started'",
                    parameters={},
                    description="Initialize workflow",
                    expected_result="Workflow started"
                )
            ],
            context={"user_input": user_input, "fallback": True},
            estimated_time=5,
            confidence_score=0.3
        )
    
    async def list_available_models(self) -> List[str]:
        """List available models from the provider."""
        if not self.is_available:
            return []
        
        try:
            if self.provider == LocalLMProvider.OLLAMA:
                response = requests.get(f"{self.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return [model["name"] for model in models]
            
            elif self.provider == LocalLMProvider.LM_STUDIO:
                response = requests.get(f"{self.base_url}/v1/models", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    return [model["id"] for model in models]
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def update_model(self, model_name: str) -> bool:
        """Update the model being used."""
        old_model = self.model_name
        self.model_name = model_name
        
        # Test connection with new model
        if self._test_connection():
            logger.info(f"Updated model to: {model_name}")
            return True
        else:
            # Revert to old model
            self.model_name = old_model
            logger.error(f"Failed to use model {model_name}, reverted to {old_model}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider."""
        return {
            "provider": self.provider.value,
            "model": self.model_name,
            "base_url": self.base_url,
            "api_endpoint": self.api_endpoint,
            "is_available": self.is_available,
            "timeout": self.timeout,
            "max_retries": self.max_retries
        }
    
    async def generate_response(self, prompt: str, system_context: str = "") -> str:
        """
        Generates a text response from the local LLM.
        """
        full_prompt = f"{system_context}\n\nUser Request: {prompt}" if system_context else prompt
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.2, # Low temp for structured tasks
                "num_ctx": 4096     # Sufficient context window
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_endpoint, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        return f"Error: Local LLM returned status {response.status}"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    async def generate_structured_workflow(self, voice_command: str, templates: Dict[str, str]) -> Dict[str, Any]:
        """
        Specialized method to turn voice commands into JSON workflows.
        """
        system_prompt = f"""
        You are an AI Automation Architect. Your goal is to convert a voice command into a structured automation workflow.
        
        Use the following templates as a guide:
        {json.dumps(templates, indent=2)}
        
        You must return ONLY a valid JSON object representing the workflow. No conversational text.
        
        Structure required:
        {{
            "name": "skill-name-kebab-case",
            "description": "Short description of what it does",
            "triggers": ["trigger 1", "trigger 2"],
            "steps": [
                {{
                    "name": "Step Name",
                    "type": "terminal" | "python" | "applescript",
                    "command": "The actual code or command to run"
                }}
            ]
        }}
        """
        
        response_text = await self.generate_response(voice_command, system_prompt)
        
        # Clean up response (sometimes LLMs add markdown fences)
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(clean_json)
        except json.JSONDecodeError:
            # Fallback: Simple extraction or retry logic could go here
            print(f"⚠️ Failed to parse JSON from LLM: {response_text}")
            return {"error": "Invalid JSON generated", "raw": response_text}

    def validate_workflow(self, workflow: GeneratedWorkflow) -> Dict[str, Any]:
        """
        Validate a generated workflow.
        
        Args:
            workflow: Workflow to validate
            
        Returns:
            Validation result with issues and recommendations
        """
        issues = []
        recommendations = []
        
        # Check steps
        if not workflow.steps:
            issues.append("Workflow has no steps")
            recommendations.append("Add at least one executable step")
        
        for i, step in enumerate(workflow.steps):
            # Validate action
            if step.action not in ["terminal", "python", "applescript"]:
                issues.append(f"Step {i+1}: Invalid action '{step.action}'")
                recommendations.append(f"Step {i+1}: Use 'terminal', 'python', or 'applescript'")
            
            # Validate command
            if not step.command.strip():
                issues.append(f"Step {i+1}: Empty command")
                recommendations.append(f"Step {i+1}: Add a valid command")
            
            # Safety check for dangerous commands
            dangerous_commands = ["rm -rf", "sudo", "chmod 777", "dd if="]
            for dangerous in dangerous_commands:
                if dangerous in step.command:
                    issues.append(f"Step {i+1}: Potentially dangerous command '{dangerous}'")
                    recommendations.append(f"Step {i+1}: Review command safety")
        
        # Calculate confidence
        base_confidence = workflow.confidence_score or 0.5
        if issues:
            confidence = max(0.1, base_confidence - len(issues) * 0.1)
        else:
            confidence = min(1.0, base_confidence + 0.1)
        
        return {
            "is_valid": len(issues) == 0,
            "confidence": confidence,
            "issues": issues,
            "recommendations": recommendations,
            "step_count": len(workflow.steps)
        }
