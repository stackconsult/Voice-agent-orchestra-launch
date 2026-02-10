"""
Skill Executor - Execute SKILL.yaml Workflows

Executes generated workflows by running terminal commands, AppleScript,
and Python scripts. Provides context substitution, error handling,
and comprehensive execution logging.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import yaml
import shlex

# Import monitoring agent
from ..agents.monitor_agent import MonitorAgent, EventType, Severity

# Import restore manager for safety
from ..safety.restore_manager import RestoreManager

logger = logging.getLogger(__name__)


class ExecutionAction(Enum):
    """Types of execution actions."""
    TERMINAL = "terminal"
    PYTHON = "python"
    APPLESCRIPT = "applescript"
    SHELL = "shell"


@dataclass
class ExecutionStep:
    """Single execution step."""
    step_id: str
    action: ExecutionAction
    command: str
    parameters: Dict[str, Any]
    description: str
    expected_result: Optional[str] = None
    timeout: int = 30
    working_directory: Optional[str] = None


@dataclass
class ExecutionResult:
    """Result of step execution."""
    step_id: str
    success: bool
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    output_files: List[str] = None


@dataclass
class WorkflowExecution:
    """Complete workflow execution result."""
    workflow_name: str
    success: bool
    total_steps: int
    completed_steps: int
    failed_steps: int
    total_time: float
    step_results: List[ExecutionResult]
    snapshot_id: Optional[str] = None
    rollback_performed: bool = False


class SkillExecutor:
    """
    Execute SKILL.yaml workflows safely.
    
    Runs terminal commands, AppleScript, and Python scripts with
    context substitution, error handling, and comprehensive logging.
    """
    
    def __init__(
        self,
        monitor_agent: Optional[MonitorAgent] = None,
        restore_manager: Optional[RestoreManager] = None,
        default_timeout: int = 30,
        max_execution_time: int = 300,
        safe_mode: bool = True
    ):
        """
        Initialize skill executor.
        
        Args:
            monitor_agent: Monitor agent for logging
            restore_manager: Restore manager for snapshots
            default_timeout: Default timeout for individual steps
            max_execution_time: Maximum total execution time
            safe_mode: Enable safety checks and restrictions
        """
        self.monitor_agent = monitor_agent
        self.restore_manager = restore_manager
        self.default_timeout = default_timeout
        self.max_execution_time = max_execution_time
        self.safe_mode = safe_mode
        
        # Execution context
        self.execution_context: Dict[str, Any] = {}
        self.current_execution_id: Optional[str] = None
        
        # Safety restrictions
        self.dangerous_commands = {
            "rm -rf /", "sudo rm", "chmod 777", "dd if=", "mkfs",
            "format", "fdisk", "reboot", "shutdown", "halt"
        }
        
        self.restricted_paths = [
            "/System", "/Library", "/usr/bin", "/bin", "/sbin"
        ]
        
        # Statistics
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_steps": 0,
            "average_execution_time": 0.0
        }
    
    async def execute_workflow(
        self,
        workflow_data: Union[str, Dict[str, Any], Path],
        context: Optional[Dict[str, Any]] = None,
        create_snapshot: bool = True
    ) -> WorkflowExecution:
        """
        Execute a complete workflow.
        
        Args:
            workflow_data: Workflow data (file path, dict, or JSON string)
            context: Execution context for variable substitution
            create_snapshot: Whether to create system snapshot
            
        Returns:
            Workflow execution result
        """
        start_time = time.time()
        self.current_execution_id = f"exec_{int(start_time)}"
        
        # Set execution context
        self.execution_context = context or {}
        self.execution_context["execution_id"] = self.current_execution_id
        self.execution_context["start_time"] = start_time
        
        # Parse workflow
        workflow = self._parse_workflow(workflow_data)
        
        # Create snapshot if requested
        snapshot_id = None
        if create_snapshot and self.restore_manager:
            try:
                snapshot_id = await self.restore_manager.create_snapshot(
                    workflow.get("name", "unnamed"),
                    self.execution_context,
                    directories=[str(Path.home())],
                    files=[]
                )
                logger.info(f"Created snapshot: {snapshot_id}")
            except Exception as e:
                logger.error(f"Failed to create snapshot: {e}")
        
        # Log workflow start
        if self.monitor_agent:
            self.monitor_agent.log_skill_execution(
                workflow.get("name", "unnamed"),
                "start",
                {
                    "steps": len(workflow.get("steps", [])),
                    "snapshot_id": snapshot_id,
                    "context": self.execution_context
                }
            )
        
        try:
            # Execute steps
            step_results = []
            completed_steps = 0
            failed_steps = 0
            
            for step_data in workflow.get("steps", []):
                step = self._parse_step(step_data)
                
                # Check execution time limit
                if time.time() - start_time > self.max_execution_time:
                    raise RuntimeError(f"Execution timeout exceeded ({self.max_execution_time}s)")
                
                # Execute step
                result = await self.execute_step(step)
                step_results.append(result)
                
                if result.success:
                    completed_steps += 1
                else:
                    failed_steps += 1
                    
                    # Stop on first failure in safe mode
                    if self.safe_mode:
                        logger.error(f"Step {step.step_id} failed, stopping execution")
                        break
            
            total_time = time.time() - start_time
            success = failed_steps == 0
            
            # Update statistics
            self.execution_stats["total_executions"] += 1
            self.execution_stats["total_steps"] += len(workflow.get("steps", []))
            self.execution_stats["average_execution_time"] = (
                (self.execution_stats["average_execution_time"] * (self.execution_stats["total_executions"] - 1) + total_time) /
                self.execution_stats["total_executions"]
            )
            
            if success:
                self.execution_stats["successful_executions"] += 1
            else:
                self.execution_stats["failed_executions"] += 1
            
            # Create execution result
            execution_result = WorkflowExecution(
                workflow_name=workflow.get("name", "unnamed"),
                success=success,
                total_steps=len(workflow.get("steps", [])),
                completed_steps=completed_steps,
                failed_steps=failed_steps,
                total_time=total_time,
                step_results=step_results,
                snapshot_id=snapshot_id
            )
            
            # Log workflow completion
            if self.monitor_agent:
                self.monitor_agent.log_skill_execution(
                    workflow.get("name", "unnamed"),
                    "complete",
                    {
                        "success": success,
                        "completed_steps": completed_steps,
                        "failed_steps": failed_steps,
                        "total_time": total_time
                    },
                    success=success
                )
            
            # Handle failure with rollback if needed
            if not success and snapshot_id and self.restore_manager:
                try:
                    await self.restore_manager.restore(snapshot_id)
                    execution_result.rollback_performed = True
                    logger.info(f"Performed rollback using snapshot: {snapshot_id}")
                except Exception as e:
                    logger.error(f"Failed to rollback: {e}")
            
            return execution_result
            
        except Exception as e:
            # Handle critical failure
            total_time = time.time() - start_time
            
            if self.monitor_agent:
                self.monitor_agent.log_event(
                    EventType.ERROR,
                    Severity.CRITICAL,
                    "skill_executor",
                    f"Workflow execution failed: {str(e)}",
                    {
                        "workflow_name": workflow.get("name", "unnamed"),
                        "execution_time": total_time,
                        "snapshot_id": snapshot_id
                    }
                )
            
            # Attempt rollback
            rollback_performed = False
            if snapshot_id and self.restore_manager:
                try:
                    await self.restore_manager.restore(snapshot_id)
                    rollback_performed = True
                except Exception as rollback_error:
                    logger.error(f"Failed to rollback: {rollback_error}")
            
            return WorkflowExecution(
                workflow_name=workflow.get("name", "unnamed"),
                success=False,
                total_steps=len(workflow.get("steps", [])),
                completed_steps=0,
                failed_steps=len(workflow.get("steps", [])),
                total_time=total_time,
                step_results=[],
                snapshot_id=snapshot_id,
                rollback_performed=rollback_performed
            )
        
        finally:
            self.current_execution_id = None
    
    def _parse_workflow(self, workflow_data: Union[str, Dict[str, Any], Path]) -> Dict[str, Any]:
        """Parse workflow from various input formats."""
        if isinstance(workflow_data, dict):
            return workflow_data
        elif isinstance(workflow_data, Path):
            # Load from file
            if workflow_data.suffix.lower() in ['.yaml', '.yml']:
                with open(workflow_data, 'r') as f:
                    return yaml.safe_load(f)
            elif workflow_data.suffix.lower() == '.json':
                with open(workflow_data, 'r') as f:
                    return json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {workflow_data.suffix}")
        elif isinstance(workflow_data, str):
            # Try to parse as JSON, then YAML
            try:
                return json.loads(workflow_data)
            except json.JSONDecodeError:
                try:
                    return yaml.safe_load(workflow_data)
                except yaml.YAMLError:
                    raise ValueError("Invalid workflow data format")
        else:
            raise ValueError(f"Unsupported workflow data type: {type(workflow_data)}")
    
    def _parse_step(self, step_data: Dict[str, Any]) -> ExecutionStep:
        """Parse execution step from data."""
        action_str = step_data.get("action", "terminal")
        try:
            action = ExecutionAction(action_str)
        except ValueError:
            logger.warning(f"Unknown action: {action_str}, defaulting to terminal")
            action = ExecutionAction.TERMINAL
        
        return ExecutionStep(
            step_id=step_data.get("step_id", f"step_{len(self.execution_context)}"),
            action=action,
            command=step_data.get("command", ""),
            parameters=step_data.get("parameters", {}),
            description=step_data.get("description", ""),
            expected_result=step_data.get("expected_result"),
            timeout=step_data.get("timeout", self.default_timeout),
            working_directory=step_data.get("working_directory")
        )
    
    async def execute_step(self, step: ExecutionStep) -> ExecutionResult:
        """
        Execute a single step.
        
        Args:
            step: Step to execute
            
        Returns:
            Execution result
        """
        start_time = time.time()
        
        # Log step start
        if self.monitor_agent:
            self.monitor_agent.log_event(
                EventType.START,
                Severity.INFO,
                "skill_executor",
                f"Executing step: {step.step_id}",
                {
                    "action": step.action.value,
                    "command": step.command,
                    "description": step.description
                }
            )
        
        try:
            # Safety checks
            if self.safe_mode:
                self._safety_check(step)
            
            # Substitute context variables
            command = self._substitute_context(step.command)
            
            # Execute based on action type
            if step.action == ExecutionAction.TERMINAL or step.action == ExecutionAction.SHELL:
                result = await self._execute_terminal_command(command, step)
            elif step.action == ExecutionAction.PYTHON:
                result = await self._execute_python_script(command, step)
            elif step.action == ExecutionAction.APPLESCRIPT:
                result = await self._execute_applescript(command, step)
            else:
                raise ValueError(f"Unsupported action: {step.action}")
            
            result.execution_time = time.time() - start_time
            
            # Log step completion
            if self.monitor_agent:
                self.monitor_agent.log_event(
                    EventType.STOP,
                    Severity.INFO if result.success else Severity.HIGH,
                    "skill_executor",
                    f"Step {step.step_id} {'completed' if result.success else 'failed'}",
                    {
                        "success": result.success,
                        "exit_code": result.exit_code,
                        "execution_time": result.execution_time
                    }
                )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Log step error
            if self.monitor_agent:
                self.monitor_agent.log_event(
                    EventType.ERROR,
                    Severity.HIGH,
                    "skill_executor",
                    f"Step {step.step_id} failed: {str(e)}",
                    {
                        "error": str(e),
                        "execution_time": execution_time
                    }
                )
            
            return ExecutionResult(
                step_id=step.step_id,
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _safety_check(self, step: ExecutionStep) -> None:
        """Perform safety checks on step."""
        command = step.command.lower()
        
        # Check for dangerous commands
        for dangerous in self.dangerous_commands:
            if dangerous in command:
                raise RuntimeError(f"Dangerous command detected: {dangerous}")
        
        # Check for restricted paths
        for restricted in self.restricted_paths:
            if restricted in command:
                raise RuntimeError(f"Restricted path detected: {restricted}")
        
        # Check for suspicious file operations
        if step.action in [ExecutionAction.TERMINAL, ExecutionAction.SHELL]:
            # Check for file deletion in sensitive areas
            if "rm" in command and any(path in command for path in ["/system", "/library", "/usr"]):
                raise RuntimeError("File deletion in restricted area detected")
    
    def _substitute_context(self, command: str) -> str:
        """Substitute context variables in command."""
        if not self.execution_context:
            return command
        
        # Simple variable substitution
        for key, value in self.execution_context.items():
            placeholder = f"${{{key}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(value))
        
        # Environment variable substitution
        for key, value in os.environ.items():
            placeholder = f"${{env.{key}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(value))
        
        return command
    
    async def _execute_terminal_command(self, command: str, step: ExecutionStep) -> ExecutionResult:
        """Execute terminal command."""
        try:
            # Prepare execution environment
            env = os.environ.copy()
            if step.parameters:
                env.update({k: str(v) for k, v in step.parameters.items()})
            
            # Determine working directory
            cwd = None
            if step.working_directory:
                cwd = Path(step.working_directory).expanduser().resolve()
                if not cwd.exists():
                    cwd = None
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=step.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Command timed out after {step.timeout} seconds")
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            return ExecutionResult(
                step_id=step.step_id,
                success=process.returncode == 0,
                exit_code=process.returncode,
                stdout=stdout_str,
                stderr=stderr_str
            )
            
        except Exception as e:
            return ExecutionResult(
                step_id=step.step_id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_python_script(self, script_content: str, step: ExecutionStep) -> ExecutionResult:
        """Execute Python script."""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                script_file = Path(f.name)
                f.write(script_content)
            
            try:
                # Execute Python script
                process = await asyncio.create_subprocess_exec(
                    sys.executable,
                    str(script_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=step.timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    raise RuntimeError(f"Python script timed out after {step.timeout} seconds")
                
                stdout_str = stdout.decode('utf-8') if stdout else ""
                stderr_str = stderr.decode('utf-8') if stderr else ""
                
                return ExecutionResult(
                    step_id=step.step_id,
                    success=process.returncode == 0,
                    exit_code=process.returncode,
                    stdout=stdout_str,
                    stderr=stderr_str
                )
                
            finally:
                # Clean up temporary file
                if script_file.exists():
                    script_file.unlink()
            
        except Exception as e:
            return ExecutionResult(
                step_id=step.step_id,
                success=False,
                error_message=str(e)
            )
    
    async def _execute_applescript(self, script_content: str, step: ExecutionStep) -> ExecutionResult:
        """Execute AppleScript."""
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.scpt', delete=False) as f:
                script_file = Path(f.name)
                f.write(script_content)
            
            try:
                # Execute AppleScript using osascript
                process = await asyncio.create_subprocess_exec(
                    'osascript',
                    str(script_file),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=step.timeout
                    )
                except asyncio.TimeoutError:
                    process.kill()
                    await process.wait()
                    raise RuntimeError(f"AppleScript timed out after {step.timeout} seconds")
                
                stdout_str = stdout.decode('utf-8') if stdout else ""
                stderr_str = stderr.decode('utf-8') if stderr else ""
                
                return ExecutionResult(
                    step_id=step.step_id,
                    success=process.returncode == 0,
                    exit_code=process.returncode,
                    stdout=stdout_str,
                    stderr=stderr_str
                )
                
            finally:
                # Clean up temporary file
                if script_file.exists():
                    script_file.unlink()
            
        except Exception as e:
            return ExecutionResult(
                step_id=step.step_id,
                success=False,
                error_message=str(e)
            )
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return self.execution_stats.copy()
    
    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self.execution_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "total_steps": 0,
            "average_execution_time": 0.0
        }
    
    def validate_workflow(self, workflow_data: Union[str, Dict[str, Any], Path]) -> Dict[str, Any]:
        """
        Validate workflow without executing.
        
        Args:
            workflow_data: Workflow to validate
            
        Returns:
            Validation result
        """
        try:
            workflow = self._parse_workflow(workflow_data)
            
            issues = []
            warnings = []
            
            # Check required fields
            if not workflow.get("name"):
                issues.append("Workflow missing name")
            
            if not workflow.get("steps"):
                issues.append("Workflow has no steps")
            
            # Validate each step
            for i, step_data in enumerate(workflow.get("steps", [])):
                step = self._parse_step(step_data)
                
                # Check step ID
                if not step.step_id:
                    issues.append(f"Step {i+1} missing step_id")
                
                # Check command
                if not step.command.strip():
                    issues.append(f"Step {step.step_id} has empty command")
                
                # Safety checks
                if self.safe_mode:
                    try:
                        self._safety_check(step)
                    except RuntimeError as e:
                        warnings.append(f"Step {step.step_id}: {str(e)}")
            
            # Calculate validation score
            total_checks = len(workflow.get("steps", [])) * 2 + 2  # 2 checks per step + name and steps check
            failed_checks = len(issues)
            validation_score = max(0, (total_checks - failed_checks) / total_checks)
            
            return {
                "is_valid": len(issues) == 0,
                "validation_score": validation_score,
                "issues": issues,
                "warnings": warnings,
                "step_count": len(workflow.get("steps", [])),
                "estimated_time": sum(step.get("timeout", self.default_timeout) for step in workflow.get("steps", []))
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "validation_score": 0.0,
                "issues": [f"Failed to parse workflow: {str(e)}"],
                "warnings": [],
                "step_count": 0,
                "estimated_time": 0
            }
