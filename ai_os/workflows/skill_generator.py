"""
Skill Generator - Create SKILL.md from Voice

Generates complete skill packages from voice input, including
SKILL.md documentation, workflow YAML, and folder structure.
Handles name sanitization, template management, and skill organization.
"""

import asyncio
import json
import logging
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import yaml
import shutil

# Import local LM agent for workflow generation
from ..agents.local_lm_agent import LocalLMAgent, GeneratedWorkflow

logger = logging.getLogger(__name__)


@dataclass
class SkillMetadata:
    """Metadata for generated skill."""
    name: str
    description: str
    category: str
    tags: List[str]
    author: str
    created_at: str
    version: str
    dependencies: List[str]
    estimated_time: int
    difficulty: str


@dataclass
class GeneratedSkill:
    """Complete generated skill package."""
    metadata: SkillMetadata
    workflow: GeneratedWorkflow
    skill_markdown: str
    workflow_yaml: str
    folder_structure: Dict[str, Any]
    examples: List[str]


class SkillGenerator:
    """
    Generate complete skill packages from voice input.
    
    Creates SKILL.md documentation, workflow YAML, and folder structure
    from natural language descriptions.
    """
    
    def __init__(
        self,
        local_lm_agent: Optional[LocalLMAgent] = None,
        skills_dir: Optional[Path] = None,
        template_dir: Optional[Path] = None
    ):
        """
        Initialize skill generator.
        
        Args:
            local_lm_agent: Local LM agent for workflow generation
            skills_dir: Directory to store generated skills
            template_dir: Directory containing skill templates
        """
        self.local_lm_agent = local_lm_agent or LocalLMAgent()
        self.skills_dir = skills_dir or Path("./skills")
        self.template_dir = template_dir or Path("./templates")
        
        # Ensure directories exist
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Skill categories
        self.categories = [
            "automation", "productivity", "file-management",
            "development", "system", "communication", "media",
            "security", "monitoring", "backup", "integration"
        ]
        
        # Default templates
        self._ensure_default_templates()
    
    def _ensure_default_templates(self) -> None:
        """Ensure default skill templates exist."""
        templates = {
            "basic_skill.md": """# {name}

## Description
{description}

## Category
{category}

## Tags
{tags}

## Author
{author}

## Version
{version}

## Created
{created_at}

## Dependencies
{dependencies}

## Estimated Time
{estimated_time} minutes

## Difficulty
{difficulty}

## Usage

```bash
# Run the skill
aios run {name}
```

## Workflow

```yaml
{workflow_yaml}
```

## Examples

{examples}

## Notes

This skill was automatically generated from voice input.
""",
            
            "workflow.yaml": """name: {name}
description: {description}
version: {version}
author: {author}
created_at: {created_at}
category: {category}
tags: {tags}
estimated_time: {estimated_time}
difficulty: {difficulty}
dependencies: {dependencies}

steps:
{steps}
"""
        }
        
        for template_name, template_content in templates.items():
            template_file = self.template_dir / template_name
            if not template_file.exists():
                with open(template_file, 'w') as f:
                    f.write(template_content)
                logger.info(f"Created default template: {template_name}")
    
    async def generate_skill(
        self,
        voice_input: str,
        context: Optional[Dict[str, Any]] = None,
        author: str = "AI-OS User",
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> GeneratedSkill:
        """
        Generate complete skill package from voice input.
        
        Args:
            voice_input: Natural language description of desired skill
            context: Additional context for skill generation
            author: Author of the skill
            category: Skill category (auto-detected if not provided)
            tags: Skill tags (auto-generated if not provided)
            
        Returns:
            Complete generated skill package
        """
        logger.info(f"Generating skill from: {voice_input}")
        
        # Generate workflow using local LM
        workflow = await self.local_lm_agent.generate_workflow(
            voice_input,
            context
        )
        
        # Create metadata
        metadata = self._create_metadata(
            workflow.name,
            workflow.description,
            author,
            category,
            tags,
            workflow.estimated_time or 30
        )
        
        # Generate skill markdown
        skill_markdown = self._generate_skill_markdown(metadata, workflow)
        
        # Generate workflow YAML
        workflow_yaml = self._generate_workflow_yaml(metadata, workflow)
        
        # Create folder structure
        folder_structure = self._create_folder_structure(metadata)
        
        # Generate examples
        examples = self._generate_examples(workflow)
        
        return GeneratedSkill(
            metadata=metadata,
            workflow=workflow,
            skill_markdown=skill_markdown,
            workflow_yaml=workflow_yaml,
            folder_structure=folder_structure,
            examples=examples
        )
    
    def _create_metadata(
        self,
        name: str,
        description: str,
        author: str,
        category: Optional[str],
        tags: Optional[List[str]],
        estimated_time: int
    ) -> SkillMetadata:
        """Create skill metadata."""
        # Sanitize name
        sanitized_name = self._sanitize_name(name)
        
        # Auto-detect category if not provided
        if not category:
            category = self._detect_category(description)
        
        # Auto-generate tags if not provided
        if not tags:
            tags = self._generate_tags(description)
        
        # Determine difficulty based on complexity
        difficulty = self._determine_difficulty(description, estimated_time)
        
        # Auto-detect dependencies
        dependencies = self._detect_dependencies(description)
        
        return SkillMetadata(
            name=sanitized_name,
            description=description,
            category=category,
            tags=tags,
            author=author,
            created_at=datetime.now().isoformat(),
            version="1.0.0",
            dependencies=dependencies,
            estimated_time=estimated_time,
            difficulty=difficulty
        )
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize skill name for file system compatibility."""
        # Remove special characters, replace spaces with hyphens
        sanitized = re.sub(r'[^\w\s-]', '', name)
        sanitized = re.sub(r'[-\s]+', '-', sanitized)
        sanitized = sanitized.strip('-').lower()
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed-skill"
        
        # Ensure it doesn't start with number
        if sanitized[0].isdigit():
            sanitized = "skill-" + sanitized
        
        return sanitized
    
    def _detect_category(self, description: str) -> str:
        """Auto-detect skill category from description."""
        description_lower = description.lower()
        
        category_keywords = {
            "automation": ["automate", "automation", "script", "macro", "batch"],
            "productivity": ["productivity", "organize", "manage", "schedule", "task"],
            "file-management": ["file", "folder", "directory", "organize", "move", "copy"],
            "development": ["code", "develop", "program", "build", "compile", "test"],
            "system": ["system", "admin", "monitor", "service", "process"],
            "communication": ["email", "message", "notify", "alert", "chat"],
            "media": ["image", "video", "audio", "media", "convert", "edit"],
            "security": ["security", "encrypt", "backup", "protect", "secure"],
            "monitoring": ["monitor", "watch", "track", "log", "report"],
            "backup": ["backup", "save", "archive", "restore"],
            "integration": ["integrate", "connect", "sync", "api", "webhook"]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in description_lower)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or default
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return "automation"  # Default category
    
    def _generate_tags(self, description: str) -> List[str]:
        """Generate tags from description."""
        description_lower = description.lower()
        
        # Common keywords to extract as tags
        tag_keywords = [
            "file", "folder", "directory", "backup", "sync", "organize",
            "automate", "script", "terminal", "command", "process",
            "monitor", "log", "report", "email", "notify", "alert",
            "convert", "edit", "image", "video", "audio", "media",
            "security", "encrypt", "protect", "api", "web", "integration"
        ]
        
        tags = []
        for keyword in tag_keywords:
            if keyword in description_lower:
                tags.append(keyword)
        
        # Limit to 5 tags
        return tags[:5]
    
    def _determine_difficulty(self, description: str, estimated_time: int) -> str:
        """Determine skill difficulty."""
        description_lower = description.lower()
        
        # Complexity indicators
        complex_indicators = [
            "multiple", "several", "complex", "advanced", "integration",
            "api", "database", "service", "system", "admin"
        ]
        
        simple_indicators = [
            "simple", "basic", "single", "quick", "easy", "straightforward"
        ]
        
        complexity_score = 0
        for indicator in complex_indicators:
            if indicator in description_lower:
                complexity_score += 2
        
        for indicator in simple_indicators:
            if indicator in description_lower:
                complexity_score -= 1
        
        # Time-based difficulty
        if estimated_time < 5:
            time_difficulty = -1
        elif estimated_time < 15:
            time_difficulty = 0
        elif estimated_time < 30:
            time_difficulty = 1
        else:
            time_difficulty = 2
        
        total_score = complexity_score + time_difficulty
        
        if total_score <= -1:
            return "beginner"
        elif total_score <= 1:
            return "intermediate"
        else:
            return "advanced"
    
    def _detect_dependencies(self, description: str) -> List[str]:
        """Detect required dependencies from description."""
        description_lower = description.lower()
        
        dependencies = []
        
        # Common tools and dependencies
        dependency_map = {
            "ffmpeg": ["ffmpeg", "video", "audio", "convert", "encode"],
            "imagemagick": ["image", "convert", "resize", "magick"],
            "git": ["git", "repository", "commit", "push"],
            "docker": ["docker", "container", "image"],
            "node": ["node", "npm", "javascript", "package"],
            "python": ["python", "pip", "package"],
            "curl": ["curl", "download", "http", "api"],
            "wget": ["wget", "download", "http"],
            "rsync": ["rsync", "sync", "backup"],
            "tar": ["tar", "archive", "compress"]
        }
        
        for dependency, keywords in dependency_map.items():
            if any(keyword in description_lower for keyword in keywords):
                dependencies.append(dependency)
        
        return list(set(dependencies))  # Remove duplicates
    
    def _generate_skill_markdown(self, metadata: SkillMetadata, workflow: GeneratedWorkflow) -> str:
        """Generate SKILL.md content."""
        # Load template
        template_file = self.template_dir / "basic_skill.md"
        with open(template_file, 'r') as f:
            template = f.read()
        
        # Format workflow steps for YAML
        workflow_yaml = self._generate_workflow_yaml(metadata, workflow)
        
        # Format examples
        examples_text = "\n\n".join(f"- {example}" for example in self._generate_examples(workflow))
        
        # Format dependencies
        dependencies_text = ", ".join(metadata.dependencies) if metadata.dependencies else "None"
        
        # Format tags
        tags_text = ", ".join(metadata.tags) if metadata.tags else "None"
        
        # Fill template
        content = template.format(
            name=metadata.name.title(),
            description=metadata.description,
            category=metadata.category,
            tags=tags_text,
            author=metadata.author,
            version=metadata.version,
            created_at=metadata.created_at,
            dependencies=dependencies_text,
            estimated_time=metadata.estimated_time,
            difficulty=metadata.difficulty,
            workflow_yaml=workflow_yaml,
            examples=examples_text
        )
        
        return content
    
    def _generate_workflow_yaml(self, metadata: SkillMetadata, workflow: GeneratedWorkflow) -> str:
        """Generate workflow YAML content."""
        # Format steps
        steps_yaml = []
        for step in workflow.steps:
            step_yaml = f"""  - step_id: {step.step_id}
    action: {step.action}
    command: {step.command}
    parameters: {step.parameters}
    description: {step.description}"""
            if step.expected_result:
                step_yaml += f"\n    expected_result: {step.expected_result}"
            steps_yaml.append(step_yaml)
        
        steps_text = "\n".join(steps_yaml)
        
        # Load template
        template_file = self.template_dir / "workflow.yaml"
        with open(template_file, 'r') as f:
            template = f.read()
        
        # Format dependencies
        dependencies_yaml = "\n  ".join(f"- {dep}" for dep in metadata.dependencies) if metadata.dependencies else "[]"
        
        # Format tags
        tags_yaml = "\n  ".join(f"- {tag}" for tag in metadata.tags) if metadata.tags else "[]"
        
        # Fill template
        content = template.format(
            name=metadata.name,
            description=metadata.description,
            version=metadata.version,
            author=metadata.author,
            created_at=metadata.created_at,
            category=metadata.category,
            tags=tags_yaml,
            estimated_time=metadata.estimated_time,
            difficulty=metadata.difficulty,
            dependencies=dependencies_yaml,
            steps=steps_text
        )
        
        return content
    
    def _create_folder_structure(self, metadata: SkillMetadata) -> Dict[str, Any]:
        """Create folder structure for skill."""
        return {
            "skill_folder": {
                "name": metadata.name,
                "files": [
                    "SKILL.md",
                    "workflow.yaml",
                    "README.md",
                    "examples/"
                ],
                "subdirectories": {
                    "examples": {
                        "files": [
                            "basic_usage.md",
                            "advanced_usage.md"
                        ]
                    }
                }
            }
        }
    
    def _generate_examples(self, workflow: GeneratedWorkflow) -> List[str]:
        """Generate usage examples from workflow."""
        examples = []
        
        # Basic usage example
        basic_example = f"Run {workflow.name} to {workflow.description.lower()}"
        examples.append(basic_example)
        
        # Step-specific examples
        for step in workflow.steps[:2]:  # Limit to first 2 steps
            if step.description:
                examples.append(f"Step: {step.description}")
        
        return examples
    
    async def save_skill(
        self,
        skill: GeneratedSkill,
        overwrite: bool = False
    ) -> Path:
        """
        Save complete skill package to filesystem.
        
        Args:
            skill: Generated skill package
            overwrite: Whether to overwrite existing skill
            
        Returns:
            Path to skill directory
        """
        skill_dir = self.skills_dir / skill.metadata.name
        
        # Check if skill exists
        if skill_dir.exists() and not overwrite:
            raise FileExistsError(f"Skill already exists: {skill_dir}")
        
        # Create skill directory
        skill_dir.mkdir(parents=True, exist_ok=True)
        
        # Save SKILL.md
        skill_file = skill_dir / "SKILL.md"
        with open(skill_file, 'w') as f:
            f.write(skill.skill_markdown)
        
        # Save workflow.yaml
        workflow_file = skill_dir / "workflow.yaml"
        with open(workflow_file, 'w') as f:
            f.write(skill.workflow_yaml)
        
        # Create examples directory
        examples_dir = skill_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        # Save basic usage example
        basic_example_file = examples_dir / "basic_usage.md"
        basic_example_content = f"""# Basic Usage

This example shows how to use the {skill.metadata.name} skill.

## Command

```bash
aios run {skill.metadata.name}
```

## Expected Output

{skill.metadata.description}

## Notes

- Estimated time: {skill.metadata.estimated_time} minutes
- Difficulty: {skill.metadata.difficulty}
- Category: {skill.metadata.category}
"""
        
        with open(basic_example_file, 'w') as f:
            f.write(basic_example_content)
        
        # Save advanced usage example
        advanced_example_file = examples_dir / "advanced_usage.md"
        advanced_example_content = f"""# Advanced Usage

This example shows advanced usage of the {skill.metadata.name} skill.

## Custom Parameters

You can customize the skill execution by modifying the workflow.yaml file.

## Integration

This skill can be integrated with other skills for complex automation workflows.

## Troubleshooting

Common issues and solutions for {skill.metadata.name}.

## Tips

- {skill.metadata.description}
- Estimated time: {skill.metadata.estimated_time} minutes
"""
        
        with open(advanced_example_file, 'w') as f:
            f.write(advanced_example_content)
        
        # Create README.md
        readme_file = skill_dir / "README.md"
        readme_content = f"""# {skill.metadata.name.title()}

{skill.metadata.description}

## Quick Start

```bash
aios run {skill.metadata.name}
```

## Details

- **Category**: {skill.metadata.category}
- **Difficulty**: {skill.metadata.difficulty}
- **Estimated Time**: {skill.metadata.estimated_time} minutes
- **Author**: {skill.metadata.author}
- **Version**: {skill.metadata.version}
- **Created**: {skill.metadata.created_at}

## Dependencies

{', '.join(skill.metadata.dependencies) if skill.metadata.dependencies else 'None'}

## Tags

{', '.join(skill.metadata.tags) if skill.metadata.tags else 'None'}

## Files

- `SKILL.md` - Complete skill documentation
- `workflow.yaml` - Workflow definition
- `examples/` - Usage examples

## Usage Examples

See the `examples/` directory for detailed usage examples.

## Support

For issues or questions about this skill, please check the documentation or create an issue.
"""
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        logger.info(f"Saved skill to: {skill_dir}")
        return skill_dir
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """List all available skills."""
        skills = []
        
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    # Try to read metadata from SKILL.md
                    try:
                        with open(skill_file, 'r') as f:
                            content = f.read()
                        
                        # Extract basic info
                        name = skill_dir.name
                        description = self._extract_field(content, "Description")
                        category = self._extract_field(content, "Category")
                        
                        skills.append({
                            "name": name,
                            "description": description,
                            "category": category,
                            "path": str(skill_dir),
                            "created_at": skill_dir.stat().st_mtime
                        })
                    except Exception as e:
                        logger.warning(f"Failed to read skill {skill_dir}: {e}")
        
        return sorted(skills, key=lambda x: x["created_at"], reverse=True)
    
    def _extract_field(self, content: str, field: str) -> str:
        """Extract field value from markdown content."""
        pattern = f"## {field}\\s*\\n(.+?)(?=\\n## |\\n$|$)"
        match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return "Unknown"
    
    def delete_skill(self, skill_name: str) -> bool:
        """Delete a skill."""
        skill_dir = self.skills_dir / skill_name
        
        if not skill_dir.exists():
            return False
        
        try:
            shutil.rmtree(skill_dir)
            logger.info(f"Deleted skill: {skill_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete skill {skill_name}: {e}")
            return False
    
    def get_skill_stats(self) -> Dict[str, Any]:
        """Get statistics about generated skills."""
        skills = self.list_skills()
        
        if not skills:
            return {
                "total_skills": 0,
                "categories": {},
                "average_difficulty": None,
                "most_recent": None
            }
        
        # Count by category
        categories = {}
        for skill in skills:
            cat = skill.get("category", "unknown")
            categories[cat] = categories.get(cat, 0) + 1
        
        # Find most recent
        most_recent = max(skills, key=lambda x: x["created_at"]) if skills else None
        
        return {
            "total_skills": len(skills),
            "categories": categories,
            "most_recent": most_recent["name"] if most_recent else None,
            "skills_directory": str(self.skills_dir)
        }
