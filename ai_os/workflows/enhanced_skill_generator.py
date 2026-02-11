"""
Enhanced Skill Generator - The "Skill Creator" Engine
=====================================================
Production-grade component for generating AI-OS skills with:
1. Intelligent Model Selection (Local vs. Cloud)
2. Progressive Loading Architecture (Frontmatter + References)
3. Intrinsic Execution Logic (Context-aware workflows)

Usage:
    generator = EnhancedSkillGenerator()
    skill = await generator.generate_skill("Build a financial report analyzer")
"""

import asyncio
import json
import logging
import re
import shutil
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import existing agent infrastructure
from ..agents.local_lm_agent import LocalLMAgent, GeneratedWorkflow

logger = logging.getLogger(__name__)

# --- Enums & Configuration Structures ---

class ExecutionMode(str, Enum):
    """Defines where the skill logic should execute."""
    LOCAL_ONLY = "local_only"       # Privacy critical, low latency
    CLOUD_PREFERRED = "cloud_first" # Complex reasoning, creative
    HYBRID = "hybrid"               # Local filtering -> Cloud reasoning

class ModelTier(str, Enum):
    """Defines the intelligence class required."""
    Basic = "basic"         # Mistral/Llama (Local)
    Reasoning = "reasoning" # Claude 3.5 Sonnet / GPT-4
    Coding = "coding"       # DeepSeek Coder / Claude 3.5
    Vision = "vision"       # GPT-4o / Claude 3.5

@dataclass
class ModelConfig:
    """Configuration for the AI model driving the skill."""
    mode: ExecutionMode
    recommended_model: str
    fallback_model: Optional[str] = None
    context_window_req: int = 4096
    requires_internet: bool = False

@dataclass
class SkillMetadata:
    """Enhanced metadata with execution configuration."""
    name: str
    description: str
    category: str
    tags: List[str]
    author: str
    version: str
    created_at: str
    dependencies: List[str]
    estimated_time: int
    difficulty: str
    # New fields for Enhanced Agent Workflow
    execution_config: ModelConfig
    triggers: List[str] = field(default_factory=list)
    output_artifacts: List[str] = field(default_factory=list)

@dataclass
class GeneratedSkill:
    """The complete skill package artifact."""
    metadata: SkillMetadata
    workflow: GeneratedWorkflow
    skill_markdown: str      # Contains YAML Frontmatter
    workflow_yaml: str       # Machine-readable logic
    folder_structure: Dict[str, Any]
    examples: List[str]

# --- Intelligence Layer: Model Research & Selection ---

class ModelSelector:
    """
    Implements the Decision Tree logic to select the best AI architecture
    based on task requirements.
    """
    
    def analyze_requirements(self, description: str, context: Dict) -> ModelConfig:
        """
        Determines execution mode and model based on the 'Skill Creator' guide logic.
        """
        desc_lower = description.lower()
        
        # 1. Privacy & Latency Check (Force Local)
        is_sensitive = any(w in desc_lower for w in ['financial', 'medical', 'password', 'key', 'private', 'personal'])
        needs_speed = any(w in desc_lower for w in ['real-time', 'immediate', 'latency', 'fast', 'quick'])
        
        if is_sensitive:
            return ModelConfig(
                mode=ExecutionMode.LOCAL_ONLY,
                recommended_model="llama3-local",
                requires_internet=False
            )

        # 2. Complexity Check (Reasoning vs Basic)
        needs_coding = any(w in desc_lower for w in ['code', 'script', 'python', 'api', 'debug', 'react', 'css'])
        needs_vision = any(w in desc_lower for w in ['image', 'screenshot', 'pdf', 'chart', 'diagram'])
        is_complex = any(w in desc_lower for w in ['analyze', 'strategy', 'plan', 'reason', 'complex', 'report'])

        if needs_coding:
            return ModelConfig(
                mode=ExecutionMode.CLOUD_PREFERRED,
                recommended_model="claude-3-5-sonnet",
                fallback_model="deepseek-coder-local",
                requires_internet=True
            )
            
        if needs_vision:
            return ModelConfig(
                mode=ExecutionMode.CLOUD_PREFERRED,
                recommended_model="gpt-4o",
                requires_internet=True
            )

        if is_complex:
            return ModelConfig(
                mode=ExecutionMode.CLOUD_PREFERRED,
                recommended_model="claude-3-opus",
                fallback_model="gpt-4",
                requires_internet=True
            )

        # 3. Default (Basic Automation)
        return ModelConfig(
            mode=ExecutionMode.HYBRID,
            recommended_model="llama3-local",
            fallback_model="gpt-3.5-turbo",
            requires_internet=True
        )

# --- Core Generator Class ---

class EnhancedSkillGenerator:
    """
    Production-grade skill generator that creates 'Progressive Loading' 
    compliant skill packages.
    """
    
    def __init__(
        self, 
        local_lm_agent: Optional[LocalLMAgent] = None,
        skills_dir: Optional[Path] = None,
        template_dir: Optional[Path] = None
    ):
        self.local_lm_agent = local_lm_agent or LocalLMAgent()
        self.skills_dir = skills_dir or Path("./skills")
        self.template_dir = template_dir or Path("./templates")
        self.model_selector = ModelSelector()
        
        # Ensure base directories
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)

    async def generate_skill(
        self,
        voice_input: str,
        context: Optional[Dict[str, Any]] = None,
        author: str = "AI-OS User"
    ) -> GeneratedSkill:
        """
        Orchestrates the creation of a production-grade skill.
        """
        logger.info(f"🚀 Initiating Skill Creation: {voice_input}")
        
        # 1. Analyze Architecture Requirements
        model_config = self.model_selector.analyze_requirements(voice_input, context or {})
        
        # 2. Generate Workflow Logic (Using Local LM)
        # We inject the architectural decision into the prompt context
        gen_context = context or {}
        gen_context.update({"recommended_architecture": asdict(model_config)})
        
        workflow = await self.local_lm_agent.generate_workflow(voice_input, gen_context)
        
        # 3. Create Enhanced Metadata
        metadata = self._create_enhanced_metadata(workflow, author, model_config)
        
        # 4. Generate Content with Frontmatter
        skill_markdown = self._generate_frontmatter_markdown(metadata, workflow)
        workflow_yaml = self._generate_workflow_yaml(metadata, workflow)
        
        # 5. Define Progressive Folder Structure
        folder_structure = self._create_progressive_structure(metadata)
        examples = self._generate_examples(workflow)

        return GeneratedSkill(
            metadata=metadata,
            workflow=workflow,
            skill_markdown=skill_markdown,
            workflow_yaml=workflow_yaml,
            folder_structure=folder_structure,
            examples=examples
        )

    def _create_enhanced_metadata(
        self, 
        workflow: GeneratedWorkflow, 
        author: str, 
        model_config: ModelConfig
    ) -> SkillMetadata:
        """Creates metadata with architectural decisions."""
        sanitized_name = self._sanitize_name(workflow.name)
        
        return SkillMetadata(
            name=sanitized_name,
            description=workflow.description,
            category=self._detect_category(workflow.description),
            tags=self._generate_tags(workflow.description),
            author=author,
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            dependencies=self._detect_dependencies(workflow.description),
            estimated_time=workflow.estimated_time or 15,
            difficulty=self._determine_difficulty(workflow.estimated_time or 15),
            execution_config=model_config,
            triggers=[f"run {sanitized_name}", f"execute {sanitized_name}"],
            output_artifacts=["report.md", "data.json"] # Default artifacts
        )

    def _generate_frontmatter_markdown(self, metadata: SkillMetadata, workflow: GeneratedWorkflow) -> str:
        """
        Generates SKILL.md with YAML Frontmatter for generic context loaders.
        This follows the 'Skill Creator' best practice.
        """
        # Convert config to dict for YAML dump
        config_dict = asdict(metadata.execution_config)
        
        # Build triggers list
        triggers_yaml = "\n".join([f"  - {trigger}" for trigger in metadata.triggers])
        
        # Build workflow steps
        steps_text = ""
        for i, step in enumerate(workflow.steps, 1):
            steps_text += f"### {i}. {step.description or step.action}\n"
            steps_text += f"- Action: {step.action}\n"
            steps_text += f"- Command: {step.command}\n\n"
        
        frontmatter = f"""---
name: {metadata.name}
version: {metadata.version}
description: {metadata.description}
author: {metadata.author}
tags: {json.dumps(metadata.tags)}
category: {metadata.category}
triggers:
{triggers_yaml}
execution:
  mode: {metadata.execution_config.mode.value}
  model: {metadata.execution_config.recommended_model}
  internet: {str(metadata.execution_config.requires_internet).lower()}
---

# {metadata.name.replace('-', ' ').title()}

## 📋 Overview
{metadata.description}

## 🚀 Usage
```bash
aios run {metadata.name}
```

## ⚙️ Configuration
This skill is configured to run in {metadata.execution_config.mode.value} mode using {metadata.execution_config.recommended_model}.

## 🔄 Workflow Logic
The following steps are executed automatically:
{steps_text}
## 📚 References
See `references/` directory for API documentation and templates.
"""
        return frontmatter

    def _generate_workflow_yaml(self, metadata: SkillMetadata, workflow: GeneratedWorkflow) -> str:
        """Generates the intrinsic executable workflow file."""
        data = {
            "skill_id": metadata.name,
            "version": metadata.version,
            "execution_engine": {
                "provider": "ai_os.context_switcher",
                "mode": metadata.execution_config.mode.value,
                "model": metadata.execution_config.recommended_model
            },
            "environment": {
                "dependencies": metadata.dependencies,
                "env_vars": ["OPENAI_API_KEY"] if metadata.execution_config.requires_internet else []
            },
            "workflow": {
                "steps": [asdict(step) for step in workflow.steps]
            }
        }
        return yaml.dump(data, sort_keys=False)

    def _create_progressive_structure(self, metadata: SkillMetadata) -> Dict[str, Any]:
        """
        Creates a 'Progressive Loading' compatible folder structure.
        Context is split into 'references' to save tokens during initial load.
        """
        return {
            "skill_folder": {
                "name": metadata.name,
                "files": ["SKILL.md", "workflow.yaml", "README.md"],
                "subdirectories": {
                    "examples": {
                        "files": ["basic_usage.md"]
                    },
                    "references": { # Progressive loading storage
                        "files": ["context_definitions.json", "api_schema.md"]
                    },
                    "logs": {
                        "files": [".gitkeep"]
                    }
                }
            }
        }

    # --- Helper Utilities (Sanitization, Categories, etc.) ---
    
    def _sanitize_name(self, name: str) -> str:
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '-', sanitized).strip('-').lower()
        return sanitized if sanitized else "unnamed-skill"

    def _format_list_yaml(self, items: List[str]) -> str:
        return "\n".join([f"  - {item}" for item in items])

    def _detect_category(self, description: str) -> str:
        # Simplified detection logic
        keywords = {
            "automation": ["script", "macro"],
            "analysis": ["report", "analyze", "summary"],
            "dev": ["code", "git", "api"],
            "creative": ["write", "blog", "post"]
        }
        for cat, keys in keywords.items():
            if any(k in description.lower() for k in keys):
                return cat
        return "automation"

    def _generate_tags(self, description: str) -> List[str]:
        return [w for w in ["automation", "productivity", "ai"] if w in description.lower()]

    def _detect_dependencies(self, description: str) -> List[str]:
        deps = []
        if "git" in description.lower(): deps.append("git")
        if "http" in description.lower(): deps.append("curl")
        return deps

    def _determine_difficulty(self, time_est: int) -> str:
        return "advanced" if time_est > 30 else "beginner"

    def _generate_examples(self, workflow: GeneratedWorkflow) -> List[str]:
        return [f"Run {workflow.name} to {workflow.description}"]

    # --- Persistence Layer ---

    async def save_skill(self, skill: GeneratedSkill, overwrite: bool = False) -> Path:
        """Persists the skill to disk with the new structure."""
        skill_dir = self.skills_dir / skill.metadata.name
        
        if skill_dir.exists() and not overwrite:
            raise FileExistsError(f"Skill {skill.metadata.name} already exists")
            
        # Create Main & Sub Directories
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "examples").mkdir(exist_ok=True)
        (skill_dir / "references").mkdir(exist_ok=True)
        (skill_dir / "logs").mkdir(exist_ok=True)

        # Write Core Files
        (skill_dir / "SKILL.md").write_text(skill.skill_markdown)
        (skill_dir / "workflow.yaml").write_text(skill.workflow_yaml)
        
        # Write Examples
        (skill_dir / "examples" / "basic_usage.md").write_text(f"# Usage\n\n{skill.examples[0]}")
        
        # Write Placeholder Reference (Progressive Loading)
        ref_note = "# References\nStore large API docs or context files here to keep the main SKILL.md lightweight."
        (skill_dir / "references" / "README.md").write_text(ref_note)
        
        logger.info(f"✅ Skill '{skill.metadata.name}' created at {skill_dir}")
        return skill_dir

    def generate_skill_from_voice(self, voice_command: str) -> Dict[str, Any]:
        """
        Synchronous wrapper for the async generation process.
        Called by VoiceManager.
        """
        return asyncio.run(self._generate_async(voice_command))

    async def _generate_async(self, voice_command: str) -> Dict[str, Any]:
        print(f"⚙️ Generating skill from: '{voice_command}'")
        
        # 1. Load Context
        templates = self._load_templates()
        
        # 2. Consult Local Intelligence
        workflow_data = await self.agent.generate_structured_workflow(voice_command, templates)
        
        if "error" in workflow_data:
            return {"status": "error", "message": workflow_data["error"]}

        # 3. Construct Skill Directory
        skill_name = workflow_data.get("name", "unnamed_skill")
        new_skill_dir = self.skills_dir / skill_name
        new_skill_dir.mkdir(parents=True, exist_ok=True)
        (new_skill_dir / "references").mkdir(exist_ok=True)

        # 4. Generate SKILL.md Content
        skill_md_content = self._construct_skill_md(workflow_data)
        
        # 5. Write to Disk
        skill_file_path = new_skill_dir / "SKILL.md"
        with open(skill_file_path, "w") as f:
            f.write(skill_md_content)
            
        print(f"✅ Skill saved to: {skill_file_path}")
        return {"status": "success", "name": skill_name, "path": str(skill_file_path)}

    def _load_templates(self) -> Dict[str, str]:
        """Loads the reference templates we built in the previous step"""
        templates = {}
        
        # Load main SKILL.md template
        template_path = self.skills_dir / "skill-creator" / "SKILL.md"
        if template_path.exists():
            with open(template_path, "r") as f:
                templates["main"] = f.read()
                
        return templates

    def _construct_skill_md(self, data: Dict[str, Any]) -> str:
        """Builds the final markdown content from the JSON data"""
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        
        # Frontmatter
        md = "---\n"
        md += f"name: {data.get('name')}\n"
        md += f"description: {data.get('description')}\n"
        md += f"version: 1.0.0\n"
        md += f"created: {timestamp}\n"
        
        triggers = data.get("triggers", [])
        if triggers:
            md += "triggers:\n"
            for t in triggers:
                md += f"  - \"{t}\"\n"
        
        md += "model_requirements:\n  primary: \"local\"\n"
        md += "---\n\n"
        
        # Body
        md += f"# {data.get('name').replace('-', ' ').title()}\n\n"
        md += f"{data.get('description')}\n\n"
        
        md += "## Workflow\n\n"
        
        for idx, step in enumerate(data.get("steps", [])):
            md += f"### Step {idx + 1}: {step.get('name')}\n\n"
            
            cmd_type = step.get('type', 'terminal')
            cmd = step.get('command', '# No command provided')
            
            md += f"```{cmd_type}\n{cmd}\n```\n\n"
            
        return md

# --- Intrinsic Execution Block ---
if __name__ == "__main__":
    async def main():
        print("Initializing Enhanced Skill Generator...")
        gen = EnhancedSkillGenerator()
        
        # Mock generation for testing
        skill = await gen.generate_skill("Create a Python script to analyze daily stock prices and save to CSV")
        path = await gen.save_skill(skill, overwrite=True)
        print(f"Generated Production Skill at: {path}")

    asyncio.run(main())
