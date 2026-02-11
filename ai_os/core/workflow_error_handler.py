"""
Workflow Error Handler
Specialized error handling for AI-OS workflow execution
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from .error_handler import (
    ErrorSeverity, ErrorCategory, ErrorContext, ErrorReport,
    SkillErrorHandler, get_error_handler
)


class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class StepStatus(Enum):
    """Individual step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    description: str
    step_type: str  # terminal, python, applescript, etc.
    command: str
    dependencies: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    timeout: Optional[int] = None
    status: StepStatus = StepStatus.PENDING
    error_report: Optional[ErrorReport] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if not self.step_id:
            self.step_id = f"step_{hash(self.command) % 10000:04d}"


@dataclass
class WorkflowContext:
    """Workflow execution context"""
    workflow_id: str
    workflow_name: str
    user_command: str
    skill_name: str
    steps: List[WorkflowStep] = field(default_factory=list)
    current_step_index: int = 0
    state: WorkflowState = WorkflowState.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    error_reports: List[ErrorReport] = field(default_factory=list)
    rollback_available: bool = True
    snapshots_taken: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.workflow_id:
            self.workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.user_command) % 10000:04d}"
        if self.start_time is None:
            self.start_time = datetime.now()


class WorkflowErrorHandler:
    """Specialized error handler for workflow execution"""
    
    def __init__(self, error_handler: Optional[SkillErrorHandler] = None):
        self.error_handler = error_handler or get_error_handler()
        self.logger = logging.getLogger("workflow_error_handler")
        
        # Workflow recovery strategies
        self.recovery_strategies = {
            ErrorCategory.PERMISSION: self._handle_permission_error,
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.DEPENDENCY: self._handle_dependency_error,
            ErrorCategory.RESOURCE: self._handle_resource_error,
            ErrorCategory.TIMEOUT: self._handle_timeout_error,
            ErrorCategory.EXECUTION: self._handle_execution_error,
            ErrorCategory.VALIDATION: self._handle_validation_error
        }
        
        # Active workflows
        self.active_workflows: Dict[str, WorkflowContext] = {}
    
    async def execute_workflow(
        self,
        workflow_context: WorkflowContext,
        step_executor: Callable[[WorkflowStep, WorkflowContext], Any]
    ) -> WorkflowContext:
        """
        Execute a workflow with comprehensive error handling
        
        Args:
            workflow_context: The workflow to execute
            step_executor: Function to execute individual steps
            
        Returns:
            Updated workflow context with execution results
        """
        workflow_context.state = WorkflowState.RUNNING
        self.active_workflows[workflow_context.workflow_id] = workflow_context
        
        try:
            # Create initial snapshot
            await self._create_snapshot(workflow_context, "workflow_start")
            
            # Execute steps in order
            for i, step in enumerate(workflow_context.steps):
                workflow_context.current_step_index = i
                
                try:
                    # Execute step with error handling
                    await self._execute_step_with_error_handling(
                        step, workflow_context, step_executor
                    )
                    
                    # Step completed successfully
                    step.status = StepStatus.COMPLETED
                    
                except Exception as e:
                    # Handle step failure
                    step.status = StepStatus.FAILED
                    await self._handle_step_failure(step, workflow_context, e)
                    
                    # Decide whether to continue or abort
                    if not await self._should_continue_workflow(step, workflow_context):
                        workflow_context.state = WorkflowState.FAILED
                        break
            
            # Finalize workflow
            if workflow_context.state == WorkflowState.RUNNING:
                workflow_context.state = WorkflowState.COMPLETED
            
        except Exception as e:
            # Handle workflow-level failure
            workflow_context.state = WorkflowState.FAILED
            await self._handle_workflow_failure(workflow_context, e)
        
        finally:
            # Cleanup
            workflow_context.end_time = datetime.now()
            if workflow_context.start_time:
                workflow_context.total_execution_time = (
                    workflow_context.end_time - workflow_context.start_time
                ).total_seconds()
            
            # Remove from active workflows
            self.active_workflows.pop(workflow_context.workflow_id, None)
        
        return workflow_context
    
    async def _execute_step_with_error_handling(
        self,
        step: WorkflowStep,
        workflow_context: WorkflowContext,
        step_executor: Callable[[WorkflowStep, WorkflowContext], Any]
    ):
        """Execute a single step with comprehensive error handling"""
        step.status = StepStatus.RUNNING
        start_time = datetime.now()
        
        try:
            # Check dependencies
            await self._check_step_dependencies(step, workflow_context)
            
            # Execute step with timeout
            if step.timeout:
                result = await asyncio.wait_for(
                    step_executor(step, workflow_context),
                    timeout=step.timeout
                )
            else:
                result = await step_executor(step, workflow_context)
            
            # Record execution time
            step.execution_time = (datetime.now() - start_time).total_seconds()
            
            return result
            
        except asyncio.TimeoutError:
            step.execution_time = (datetime.now() - start_time).total_seconds()
            raise TimeoutError(f"Step '{step.name}' timed out after {step.timeout} seconds")
    
    async def _check_step_dependencies(self, step: WorkflowStep, workflow_context: WorkflowContext):
        """Check if step dependencies are satisfied"""
        for dep_id in step.dependencies:
            dep_step = next((s for s in workflow_context.steps if s.step_id == dep_id), None)
            if not dep_step:
                raise ValueError(f"Dependency step '{dep_id}' not found")
            if dep_step.status != StepStatus.COMPLETED:
                raise RuntimeError(f"Dependency step '{dep_step.name}' not completed")
    
    async def _handle_step_failure(
        self,
        step: WorkflowStep,
        workflow_context: WorkflowContext,
        error: Exception
    ):
        """Handle individual step failure"""
        # Create error context
        error_context = ErrorContext(
            skill_name=workflow_context.skill_name,
            workflow_step=step.name,
            user_command=workflow_context.user_command,
            execution_environment="workflow"
        )
        
        # Handle error with specialized error handler
        error_report = await self.error_handler.handle_error(error, error_context)
        step.error_report = error_report
        workflow_context.error_reports.append(error_report)
        
        # Log step failure
        self.logger.error(f"Step '{step.name}' failed: {error_report.message}")
        
        # Attempt recovery based on error category
        recovery_strategy = self.recovery_strategies.get(error_report.category)
        if recovery_strategy:
            try:
                await recovery_strategy(step, workflow_context, error_report)
            except Exception as recovery_error:
                self.logger.error(f"Recovery strategy failed: {recovery_error}")
        
        # Retry logic
        if step.retry_count < step.max_retries:
            step.retry_count += 1
            step.status = StepStatus.RETRYING
            self.logger.info(f"Retrying step '{step.name}' (attempt {step.retry_count}/{step.max_retries})")
            
            # Wait before retry
            await asyncio.sleep(2 ** step.retry_count)  # Exponential backoff
            
            # Retry the step
            await self._execute_step_with_error_handling(step, workflow_context, None)
    
    async def _should_continue_workflow(
        self,
        step: WorkflowStep,
        workflow_context: WorkflowContext
    ) -> bool:
        """Determine if workflow should continue after step failure"""
        if step.error_report is None:
            return True
        
        # Continue for low/medium severity errors
        if step.error_report.severity in [ErrorSeverity.LOW, ErrorSeverity.MEDIUM]:
            return True
        
        # Stop for critical errors
        if step.error_report.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Check if step is critical (has dependent steps)
        has_dependents = any(
            step.step_id in other_step.dependencies
            for other_step in workflow_context.steps
        )
        
        return not has_dependents
    
    async def _handle_workflow_failure(self, workflow_context: WorkflowContext, error: Exception):
        """Handle workflow-level failure"""
        # Create error context
        error_context = ErrorContext(
            skill_name=workflow_context.skill_name,
            user_command=workflow_context.user_command,
            execution_environment="workflow"
        )
        
        # Handle error
        error_report = await self.error_handler.handle_error(error, error_context)
        workflow_context.error_reports.append(error_report)
        
        # Attempt rollback if available
        if workflow_context.rollback_available:
            await self._rollback_workflow(workflow_context)
    
    async def _rollback_workflow(self, workflow_context: WorkflowContext):
        """Rollback workflow execution"""
        self.logger.info(f"Rolling back workflow '{workflow_context.workflow_name}'")
        
        try:
            # Restore from last snapshot
            if workflow_context.snapshots_taken:
                last_snapshot = workflow_context.snapshots_taken[-1]
                await self._restore_snapshot(workflow_context, last_snapshot)
            
            workflow_context.state = WorkflowState.ROLLED_BACK
            
        except Exception as rollback_error:
            self.logger.error(f"Rollback failed: {rollback_error}")
            workflow_context.state = WorkflowState.FAILED
    
    async def _create_snapshot(self, workflow_context: WorkflowContext, snapshot_name: str):
        """Create workflow snapshot"""
        snapshot_id = f"{workflow_context.workflow_id}_{snapshot_name}_{datetime.now().strftime('%H%M%S')}"
        workflow_context.snapshots_taken.append(snapshot_id)
        
        self.logger.info(f"Created snapshot '{snapshot_id}' for workflow '{workflow_context.workflow_name}'")
        
        # Implementation would integrate with RestoreManager
        # For now, just record the snapshot
    
    async def _restore_snapshot(self, workflow_context: WorkflowContext, snapshot_id: str):
        """Restore workflow from snapshot"""
        self.logger.info(f"Restoring snapshot '{snapshot_id}' for workflow '{workflow_context.workflow_name}'")
        
        # Implementation would integrate with RestoreManager
        # For now, just log the restore
    
    # Recovery strategy implementations
    async def _handle_permission_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle permission errors"""
        self.logger.info("Attempting to resolve permission issues...")
        # Implementation would try to fix permissions
    
    async def _handle_network_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle network errors"""
        self.logger.info("Attempting to resolve network issues...")
        # Implementation would try to fix network connectivity
    
    async def _handle_dependency_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle dependency errors"""
        self.logger.info("Attempting to resolve dependency issues...")
        # Implementation would try to install missing dependencies
    
    async def _handle_resource_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle resource errors"""
        self.logger.info("Attempting to resolve resource issues...")
        # Implementation would try to free up resources
    
    async def _handle_timeout_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle timeout errors"""
        self.logger.info("Attempting to resolve timeout issues...")
        # Implementation would try to increase timeout or optimize step
    
    async def _handle_execution_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle execution errors"""
        self.logger.info("Attempting to resolve execution issues...")
        # Implementation would try to fix command syntax or environment
    
    async def _handle_validation_error(self, step: WorkflowStep, workflow_context: WorkflowContext, error_report: ErrorReport):
        """Handle validation errors"""
        self.logger.info("Attempting to resolve validation issues...")
        # Implementation would try to fix input validation
    
    def get_workflow_status(self, workflow_id: str) -> Optional[WorkflowContext]:
        """Get status of active workflow"""
        return self.active_workflows.get(workflow_id)
    
    def get_active_workflows(self) -> Dict[str, WorkflowContext]:
        """Get all active workflows"""
        return self.active_workflows.copy()
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            workflow.state = WorkflowState.FAILED
            await self._rollback_workflow(workflow)
            return True
        return False


# Global workflow error handler
_global_workflow_error_handler: Optional[WorkflowErrorHandler] = None


def get_workflow_error_handler() -> WorkflowErrorHandler:
    """Get global workflow error handler"""
    global _global_workflow_error_handler
    if _global_workflow_error_handler is None:
        _global_workflow_error_handler = WorkflowErrorHandler()
    return _global_workflow_error_handler


# Decorator for workflow functions
def workflow_error_handler(workflow_name: str, skill_name: str):
    """
    Decorator for automatic workflow error handling
    
    Usage:
        @workflow_error_handler("my_workflow", "my_skill")
        async def my_workflow_function(user_command: str):
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Create workflow context
            user_command = args[0] if args else kwargs.get('user_command', '')
            
            workflow_context = WorkflowContext(
                workflow_name=workflow_name,
                user_command=user_command,
                skill_name=skill_name
            )
            
            # Get workflow error handler
            handler = get_workflow_error_handler()
            
            try:
                # Execute workflow with error handling
                result = await handler.execute_workflow(workflow_context, func)
                return result
                
            except Exception as e:
                # Handle unhandled exceptions
                error_context = ErrorContext(
                    skill_name=skill_name,
                    user_command=user_command,
                    execution_environment="workflow"
                )
                
                error_report = await handler.error_handler.handle_error(e, error_context)
                raise Exception(f"Workflow '{workflow_name}' failed: {error_report.user_friendly_message}") from e
        
        return wrapper
    return decorator
