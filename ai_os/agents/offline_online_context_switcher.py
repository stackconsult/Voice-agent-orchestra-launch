"""
Offline/Online Context Switcher - Cloud Fallback

Manages seamless switching between local and cloud AI providers.
Implements local-first logic with intelligent cloud fallback when
local processing is insufficient or unavailable.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import os
from pathlib import Path

# Import local LM agent
from .local_lm_agent import LocalLMAgent, LocalLMProvider, GeneratedWorkflow

# Try to import cloud providers (make them optional)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

logger = logging.getLogger(__name__)


class CloudProvider(Enum):
    """Supported cloud AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"


class ProcessingMode(Enum):
    """Processing modes."""
    LOCAL_ONLY = "local_only"
    LOCAL_FIRST = "local_first"
    CLOUD_FIRST = "cloud_first"
    CLOUD_ONLY = "cloud_only"


@dataclass
class ProcessingResult:
    """Result from AI processing."""
    content: str
    provider: str
    model: str
    processing_time: float
    cost_estimate: float
    confidence: float
    metadata: Dict[str, Any]


@dataclass
class CostTracking:
    """Cost tracking information."""
    total_cost: float
    local_cost: float
    cloud_cost: float
    request_count: int
    fallback_count: int


class ContextSwitcher:
    """
    Offline/Online context switcher for AI processing.
    
    Manages local-first processing with intelligent cloud fallback.
    Tracks costs, performance, and provides seamless switching.
    """
    
    def __init__(
        self,
        processing_mode: ProcessingMode = ProcessingMode.LOCAL_FIRST,
        local_provider: LocalLMProvider = LocalLMProvider.OLLAMA,
        local_model: str = "llama2",
        cloud_providers: Optional[List[CloudProvider]] = None,
        cost_budget: Optional[float] = None,
        fallback_threshold: float = 0.7,
        timeout: int = 30
    ):
        """
        Initialize context switcher.
        
        Args:
            processing_mode: Preferred processing mode
            local_provider: Local LLM provider
            local_model: Local model name
            cloud_providers: Preferred cloud providers
            cost_budget: Monthly cost budget in USD
            fallback_threshold: Confidence threshold for cloud fallback
            timeout: Request timeout in seconds
        """
        self.processing_mode = processing_mode
        self.fallback_threshold = fallback_threshold
        self.timeout = timeout
        self.cost_budget = cost_budget
        
        # Initialize local agent
        self.local_agent = LocalLMAgent(
            provider=local_provider,
            model_name=local_model,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        )
        
        # Cloud provider configuration
        self.cloud_providers = cloud_providers or [CloudProvider.OPENAI, CloudProvider.ANTHROPIC]
        self.cloud_configs = self._load_cloud_configs()
        
        # Cost tracking
        self.cost_tracking = CostTracking(
            total_cost=0.0,
            local_cost=0.0,
            cloud_cost=0.0,
            request_count=0,
            fallback_count=0
        )
        
        # Performance tracking
        self.performance_stats = {
            "local_requests": 0,
            "cloud_requests": 0,
            "local_success_rate": 0.0,
            "cloud_success_rate": 0.0,
            "avg_local_time": 0.0,
            "avg_cloud_time": 0.0
        }
        
        # Initialize cloud clients
        self._init_cloud_clients()
    
    def _load_cloud_configs(self) -> Dict[str, Dict[str, Any]]:
        """Load cloud provider configurations."""
        configs = {}
        
        # OpenAI config
        if CloudProvider.OPENAI in self.cloud_providers and OPENAI_AVAILABLE:
            configs["openai"] = {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4"),
                "base_url": os.getenv("OPENAI_BASE_URL"),
                "cost_per_1k_tokens": {
                    "gpt-4": 0.03,
                    "gpt-4-turbo": 0.01,
                    "gpt-3.5-turbo": 0.002
                }
            }
        
        # Anthropic config
        if CloudProvider.ANTHROPIC in self.cloud_providers and ANTHROPIC_AVAILABLE:
            configs["anthropic"] = {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
                "cost_per_1k_tokens": {
                    "claude-3-sonnet-20240229": 0.015,
                    "claude-3-haiku-20240307": 0.00125
                }
            }
        
        # Gemini config (placeholder for future implementation)
        if CloudProvider.GEMINI in self.cloud_providers:
            configs["gemini"] = {
                "api_key": os.getenv("GEMINI_API_KEY"),
                "model": os.getenv("GEMINI_MODEL", "gemini-pro"),
                "cost_per_1k_tokens": {
                    "gemini-pro": 0.0005
                }
            }
        
        return configs
    
    def _init_cloud_clients(self) -> None:
        """Initialize cloud provider clients."""
        self.cloud_clients = {}
        
        # Initialize OpenAI client
        if "openai" in self.cloud_configs and self.cloud_configs["openai"]["api_key"]:
            try:
                client_kwargs = {"api_key": self.cloud_configs["openai"]["api_key"]}
                if self.cloud_configs["openai"]["base_url"]:
                    client_kwargs["base_url"] = self.cloud_configs["openai"]["base_url"]
                
                self.cloud_clients["openai"] = openai.OpenAI(**client_kwargs)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        
        # Initialize Anthropic client
        if "anthropic" in self.cloud_configs and self.cloud_configs["anthropic"]["api_key"]:
            try:
                self.cloud_clients["anthropic"] = anthropic.Anthropic(
                    api_key=self.cloud_configs["anthropic"]["api_key"]
                )
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
    
    async def generate_workflow(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        force_cloud: bool = False
    ) -> ProcessingResult:
        """
        Generate workflow with automatic provider switching.
        
        Args:
            user_input: Natural language description
            context: Additional context
            force_cloud: Force cloud processing
            
        Returns:
            Processing result with workflow and metadata
        """
        start_time = time.time()
        self.cost_tracking.request_count += 1
        
        # Determine processing strategy
        if force_cloud or self.processing_mode == ProcessingMode.CLOUD_ONLY:
            return await self._process_cloud(user_input, context, start_time)
        
        if self.processing_mode == ProcessingMode.LOCAL_ONLY:
            return await self._process_local(user_input, context, start_time)
        
        if self.processing_mode == ProcessingMode.CLOUD_FIRST:
            cloud_result = await self._process_cloud(user_input, context, start_time)
            if cloud_result.confidence >= self.fallback_threshold:
                return cloud_result
            else:
                # Fallback to local
                return await self._process_local(user_input, context, start_time)
        
        # Default: LOCAL_FIRST
        try:
            local_result = await self._process_local(user_input, context, start_time)
            
            # Check if local result is good enough
            if local_result.confidence >= self.fallback_threshold:
                return local_result
            else:
                logger.info(f"Local confidence {local_result.confidence} below threshold, falling back to cloud")
                self.cost_tracking.fallback_count += 1
                return await self._process_cloud(user_input, context, start_time)
                
        except Exception as e:
            logger.warning(f"Local processing failed: {e}, falling back to cloud")
            self.cost_tracking.fallback_count += 1
            return await self._process_cloud(user_input, context, start_time)
    
    async def _process_local(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Process using local LLM."""
        try:
            if not self.local_agent.is_available:
                raise RuntimeError("Local LLM not available")
            
            workflow = await self.local_agent.generate_workflow(user_input, context)
            
            processing_time = time.time() - start_time
            
            # Validate workflow
            validation = self.local_agent.validate_workflow(workflow)
            confidence = validation["confidence"]
            
            result = ProcessingResult(
                content=json.dumps({
                    "name": workflow.name,
                    "description": workflow.description,
                    "steps": [
                        {
                            "step_id": step.step_id,
                            "action": step.action,
                            "command": step.command,
                            "parameters": step.parameters,
                            "description": step.description,
                            "expected_result": step.expected_result
                        }
                        for step in workflow.steps
                    ],
                    "estimated_time": workflow.estimated_time,
                    "validation": validation
                }, indent=2),
                provider="local",
                model=self.local_agent.model_name,
                processing_time=processing_time,
                cost_estimate=0.0,  # Local processing is free
                confidence=confidence,
                metadata={
                    "provider_type": "local",
                    "validation": validation,
                    "step_count": len(workflow.steps)
                }
            )
            
            # Update stats
            self.performance_stats["local_requests"] += 1
            self.performance_stats["avg_local_time"] = (
                (self.performance_stats["avg_local_time"] * (self.performance_stats["local_requests"] - 1) + processing_time) /
                self.performance_stats["local_requests"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Local processing failed: {e}")
            raise
    
    async def _process_cloud(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Process using cloud AI."""
        # Check budget
        if self.cost_budget and self.cost_tracking.total_cost >= self.cost_budget:
            raise RuntimeError(f"Cost budget exceeded: ${self.cost_tracking.total_cost:.2f}")
        
        # Try cloud providers in order
        for provider in self.cloud_providers:
            if provider.value in self.cloud_clients:
                try:
                    result = await self._call_cloud_provider(provider.value, user_input, context, start_time)
                    
                    # Update cost tracking
                    self.cost_tracking.cloud_cost += result.cost_estimate
                    self.cost_tracking.total_cost += result.cost_estimate
                    
                    # Update stats
                    self.performance_stats["cloud_requests"] += 1
                    self.performance_stats["avg_cloud_time"] = (
                        (self.performance_stats["avg_cloud_time"] * (self.performance_stats["cloud_requests"] - 1) + result.processing_time) /
                        self.performance_stats["cloud_requests"]
                    )
                    
                    return result
                    
                except Exception as e:
                    logger.warning(f"Cloud provider {provider.value} failed: {e}")
                    continue
        
        raise RuntimeError("All cloud providers failed")
    
    async def _call_cloud_provider(
        self,
        provider: str,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Call specific cloud provider."""
        if provider == "openai":
            return await self._call_openai(user_input, context, start_time)
        elif provider == "anthropic":
            return await self._call_anthropic(user_input, context, start_time)
        elif provider == "gemini":
            return await self._call_gemini(user_input, context, start_time)
        else:
            raise ValueError(f"Unknown cloud provider: {provider}")
    
    async def _call_openai(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Call OpenAI API."""
        config = self.cloud_configs["openai"]
        client = self.cloud_clients["openai"]
        
        # Build prompt
        prompt = self._build_cloud_prompt(user_input, context)
        
        response = client.chat.completions.create(
            model=config["model"],
            messages=[
                {"role": "system", "content": "You are a workflow automation assistant. Generate JSON workflows."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        processing_time = time.time() - start_time
        
        # Estimate cost
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        cost_per_1k = config["cost_per_1k_tokens"].get(config["model"], 0.01)
        cost_estimate = (input_tokens + output_tokens) / 1000 * cost_per_1k
        
        return ProcessingResult(
            content=content,
            provider="openai",
            model=config["model"],
            processing_time=processing_time,
            cost_estimate=cost_estimate,
            confidence=0.9,  # Cloud models typically have high confidence
            metadata={
                "provider_type": "cloud",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "usage": response.usage.dict() if response.usage else {}
            }
        )
    
    async def _call_anthropic(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Call Anthropic API."""
        config = self.cloud_configs["anthropic"]
        client = self.cloud_clients["anthropic"]
        
        # Build prompt
        prompt = self._build_cloud_prompt(user_input, context)
        
        response = client.messages.create(
            model=config["model"],
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        processing_time = time.time() - start_time
        
        # Estimate cost
        input_tokens = response.usage.input_tokens if response.usage else 0
        output_tokens = response.usage.output_tokens if response.usage else 0
        cost_per_1k = config["cost_per_1k_tokens"].get(config["model"], 0.015)
        cost_estimate = (input_tokens + output_tokens) / 1000 * cost_per_1k
        
        return ProcessingResult(
            content=content,
            provider="anthropic",
            model=config["model"],
            processing_time=processing_time,
            cost_estimate=cost_estimate,
            confidence=0.9,
            metadata={
                "provider_type": "cloud",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "usage": response.usage.dict() if response.usage else {}
            }
        )
    
    async def _call_gemini(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]],
        start_time: float
    ) -> ProcessingResult:
        """Call Gemini API (placeholder implementation)."""
        # This is a placeholder for Gemini integration
        # In a real implementation, you would use the Gemini API
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            content='{"name": "Gemini Workflow", "description": "Generated by Gemini", "steps": []}',
            provider="gemini",
            model="gemini-pro",
            processing_time=processing_time,
            cost_estimate=0.001,
            confidence=0.8,
            metadata={
                "provider_type": "cloud",
                "note": "Placeholder implementation"
            }
        )
    
    def _build_cloud_prompt(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build prompt for cloud providers."""
        prompt = f"""Generate a workflow automation plan for: {user_input}

Return a JSON response with:
- name: Workflow name
- description: Brief description  
- steps: Array of steps with action, command, parameters, description
- estimated_time: Time in minutes
- confidence: How confident you are this will work (0-1)

Example format:
{{
    "name": "Organize Desktop",
    "description": "Clean up desktop files",
    "steps": [
        {{
            "action": "terminal",
            "command": "mkdir -p ~/Desktop/Organized",
            "parameters": {{}},
            "description": "Create organized folder"
        }}
    ],
    "estimated_time": 5,
    "confidence": 0.8
}}"""
        
        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
        
        return prompt
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "processing_mode": self.processing_mode.value,
            "local_available": self.local_agent.is_available,
            "cloud_providers": list(self.cloud_clients.keys()),
            "cost_tracking": {
                "total_cost": self.cost_tracking.total_cost,
                "local_cost": self.cost_tracking.local_cost,
                "cloud_cost": self.cost_tracking.cloud_cost,
                "request_count": self.cost_tracking.request_count,
                "fallback_count": self.cost_tracking.fallback_count,
                "fallback_rate": self.cost_tracking.fallback_count / max(1, self.cost_tracking.request_count)
            },
            "performance_stats": self.performance_stats,
            "budget_status": {
                "budget": self.cost_budget,
                "spent": self.cost_tracking.total_cost,
                "remaining": (self.cost_budget - self.cost_tracking.total_cost) if self.cost_budget else None
            }
        }
    
    def switch_mode(self, new_mode: ProcessingMode) -> None:
        """Switch processing mode."""
        old_mode = self.processing_mode
        self.processing_mode = new_mode
        logger.info(f"Switched processing mode from {old_mode.value} to {new_mode.value}")
    
    def update_budget(self, new_budget: Optional[float]) -> None:
        """Update cost budget."""
        self.cost_budget = new_budget
        logger.info(f"Updated cost budget to: ${new_budget}")
    
    def reset_cost_tracking(self) -> None:
        """Reset cost tracking statistics."""
        self.cost_tracking = CostTracking(
            total_cost=0.0,
            local_cost=0.0,
            cloud_cost=0.0,
            request_count=0,
            fallback_count=0
        )
        logger.info("Reset cost tracking")
    
    def export_usage_data(self, output_file: Path) -> None:
        """Export usage data to file."""
        data = {
            "timestamp": time.time(),
            "status": self.get_status(),
            "local_agent_info": self.local_agent.get_provider_info() if self.local_agent.is_available else None
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported usage data to {output_file}")
