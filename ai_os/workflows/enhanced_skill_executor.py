"""
Enhanced Skill Executor - The Runtime Engine
============================================
Executes production-grade skills with strict architectural enforcement.
1. Enforces Execution Mode (Local vs Cloud)
2. Manages Progressive Loading of Context
3. Handles Intrinsic Step Execution
"""

import asyncio
import yaml
import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

# Import existing agents
from ..agents.local_lm_agent import LocalLMAgent
from ..agents.offline_online_context_switcher import ContextSwitcher, ProcessingMode

logger = logging.getLogger(__name__)

class SecurityViolationError(Exception):
    """Raised when a skill attempts an action forbidden by its execution mode."""
    pass

class EnhancedSkillExecutor:
    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.context_switcher = ContextSwitcher()
        
    async def execute_skill(self, skill_name: str, parameters: Dict[str, Any] = None):
        """
        Main entry point to run a skill.
        """
        skill_path = Path(f"./skills/{skill_name}")
        workflow_file = skill_path / "workflow.yaml"
        
        if not workflow_file.exists():
            raise FileNotFoundError(f"Skill '{skill_name}' not found at {skill_path}")
            
        # 1. Load Workflow Definition
        with open(workflow_file, 'r') as f:
            workflow_config = yaml.safe_load(f)
            
        logger.info(f"⚡ Executing Skill: {workflow_config['skill_id']} (Version: {workflow_config['version']})")
        
        # 2. Enforce Architecture / Initialize Engine
        engine_config = workflow_config.get('execution_engine', {})
        await self._configure_runtime_environment(engine_config)
        
        # 3. Progressive Context Loading
        context = await self._load_progressive_context(skill_path, workflow_config.get('context_references', []))
        if parameters:
            context.update(parameters)
            
        # 4. Execute Steps
        steps = workflow_config['workflow']['steps']
        results = []
        
        for step in steps:
            step_result = await self._execute_step(step, context, engine_config)
            results.append(step_result)
            
            # Update context with result for subsequent steps
            context[f"step_{step.get('step_id', 'unknown')}_output"] = step_result
            
        return {
            "status": "success",
            "skill": skill_name,
            "steps_completed": len(results),
            "final_context": context
        }

    async def _configure_runtime_environment(self, config: Dict[str, Any]):
        """
        Sets up the AI agent based on the 'Model Research' decision.
        """
        mode_str = config.get('mode', 'hybrid')
        internet_allowed = config.get('internet_access', True)
        
        # Set Context Switcher Mode
        if mode_str == "local_only":
            self.context_switcher.switch_mode(ProcessingMode.LOCAL_ONLY)
            if internet_allowed:
                logger.warning("⚠️ Configuration Conflict: 'local_only' mode should not have internet access. Disabling internet.")
                config['internet_access'] = False
        
        elif mode_str == "cloud_first":
            self.context_switcher.switch_mode(ProcessingMode.CLOUD_FIRST)
            
        logger.info(f"⚙️ Runtime Configured: {mode_str.upper()} (Internet: {config.get('internet_access')})")

    async def _load_progressive_context(self, skill_root: Path, references: List[str]) -> Dict[str, Any]:
        """
        Loads heavy context files only when needed (Progressive Loading).
        """
        context = {}
        for ref in references:
            ref_path = skill_root / ref
            if ref_path.exists():
                logger.debug(f"📥 Loading Reference: {ref}")
                if ref.endswith('.json'):
                    import json
                    context.update(json.loads(ref_path.read_text()))
                elif ref.endswith('.md'):
                    key = ref_path.stem
                    context[key] = ref_path.read_text()
        return context

    async def _execute_step(self, step: Dict[str, Any], context: Dict[str, Any], config: Dict[str, Any]):
        """
        Executes a single workflow step with security checks.
        """
        action = step.get('action')
        command = step.get('command')
        
        logger.info(f"▶️ Step: {step.get('description', action)}")
        
        # Security Enforcement
        if action == "terminal" and not config.get('internet_access'):
            # Simple heuristic: block curl/wget/ssh in local_only mode
            if any(cmd in command for cmd in ['curl', 'wget', 'ssh', 'git clone']):
                raise SecurityViolationError(f"Network command '{command}' blocked in LOCAL_ONLY mode.")

        # Execution Logic
        if action == "terminal":
            return await self._run_terminal_command(command)
        elif action == "call_agent":
            # Nested Agent Call (Recursive capability)
            prompt = command  # Assuming command holds the prompt
            return await self.context_switcher.generate_workflow(prompt, context)
        elif action == "execute_python":
            # Python script execution
            return await self._execute_python_script(command, context)
        elif action == "interactive_input":
            # Interactive user input
            return input(f"🔸 {command}: ")
        else:
            logger.warning(f"Unknown action: {action}")
            return None

    async def _run_terminal_command(self, command: str) -> str:
        """Runs a shell command in the workspace."""
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.workspace_dir
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode != 0:
            raise RuntimeError(f"Command failed: {stderr.decode()}")
            
        return stdout.decode().strip()

    async def _execute_python_script(self, script_content: str, context: Dict[str, Any]) -> Any:
        """Executes Python code in a controlled environment."""
        # Create a safe execution environment
        exec_globals = {
            '__builtins__': {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sum': sum,
                'max': max,
                'min': min,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
            },
            'context': context
        }
        
        try:
            exec(script_content, exec_globals)
            return exec_globals.get('result', None)
        except Exception as e:
            raise RuntimeError(f"Python execution failed: {str(e)}")

    def find_and_execute(self, command: str) -> Dict[str, Any]:
        """
        Finds a skill matching the command triggers and executes it.
        """
        skill_path = self._find_matching_skill(command)
        
        if not skill_path:
            print(f"❌ No matching skill found for: {command}")
            return {"status": "not_found"}
            
        print(f"⚡ Executing skill: {skill_path.parent.name}")
        # In the next step, we will implement the actual execution engine
        # that parses the SKILL.md steps (terminal, python, applescript)
        # and runs them.
        
        return {"status": "executed_mock", "skill": skill_path.parent.name}

    def _find_matching_skill(self, command: str) -> Path:
        """Scans all SKILL.md files for matching triggers"""
        command_lower = command.lower()
        
        skills_dir = Path.cwd() / "skills"
        if not skills_dir.exists():
            return None
            
        for skill_folder in skills_dir.iterdir():
            if skill_folder.is_dir():
                skill_file = skill_folder / "SKILL.md"
                if skill_file.exists():
                    triggers = self._parse_triggers(skill_file)
                    for trigger in triggers:
                        if trigger in command_lower:
                            return skill_file
        return None

    def _parse_triggers(self, file_path: Path) -> list:
        """Extracts triggers from YAML frontmatter manually"""
        triggers = []
        try:
            with open(file_path, "r") as f:
                content = f.read()
                if content.startswith("---"):
                    # Quick and dirty YAML extraction to avoid parsing whole file
                    frontmatter = content.split("---")[1]
                    data = yaml.safe_load(frontmatter)
                    triggers = [t.lower() for t in data.get("triggers", [])]
        except Exception as e:
            print(f"Error parsing triggers for {file_path}: {e}")
        return triggers

# --- Testing Block ---
if __name__ == "__main__":
    async def test_executor():
        executor = EnhancedSkillExecutor()
        print("Enhanced Skill Executor initialized successfully!")
        print("Ready to execute skills with architectural enforcement.")
    
    asyncio.run(test_executor())
