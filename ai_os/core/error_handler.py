"""
Enhanced AI-OS Error Handler
Comprehensive error handling patterns for skills and workflows
"""

import asyncio
import logging
import traceback
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, asdict
import sys


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    SYSTEM = "system"
    NETWORK = "network"
    PERMISSION = "permission"
    VALIDATION = "validation"
    EXECUTION = "execution"
    TIMEOUT = "timeout"
    RESOURCE = "resource"
    DEPENDENCY = "dependency"
    USER_INPUT = "user_input"
    CONFIGURATION = "configuration"


@dataclass
class ErrorContext:
    """Context information for errors"""
    skill_name: Optional[str] = None
    workflow_step: Optional[str] = None
    user_command: Optional[str] = None
    system_state: Optional[Dict[str, Any]] = None
    execution_environment: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ErrorReport:
    """Comprehensive error report"""
    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    details: Optional[str] = None
    traceback_info: Optional[str] = None
    context: Optional[ErrorContext] = None
    recovery_suggestions: Optional[List[str]] = None
    rollback_available: bool = False
    user_friendly_message: Optional[str] = None
    
    def __post_init__(self):
        if not self.error_id:
            self.error_id = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(self.message) % 10000:04d}"


class SkillErrorHandler:
    """Enhanced error handler for AI-OS skills and workflows"""
    
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path.home() / ".aios" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logger()
        
        # Error patterns and recovery strategies
        self.error_patterns = self._load_error_patterns()
        
        # Error history for analysis
        self.error_history: List[ErrorReport] = []
        
    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive logging"""
        logger = logging.getLogger("aios_error_handler")
        logger.setLevel(logging.DEBUG)
        
        # File handler for all errors
        error_file = self.log_dir / "errors.log"
        file_handler = logging.FileHandler(error_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler for critical errors
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.ERROR)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load error patterns and recovery strategies"""
        return {
            "permission_denied": {
                "category": ErrorCategory.PERMISSION,
                "severity": ErrorSeverity.HIGH,
                "recovery": [
                    "Check file permissions",
                    "Run with appropriate privileges",
                    "Verify file ownership"
                ],
                "user_message": "Permission denied. Check file access rights."
            },
            "file_not_found": {
                "category": ErrorCategory.SYSTEM,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": [
                    "Verify file path exists",
                    "Check file name spelling",
                    "Ensure file is accessible"
                ],
                "user_message": "File not found. Please check the file path."
            },
            "network_timeout": {
                "category": ErrorCategory.NETWORK,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": [
                    "Check internet connection",
                    "Try again later",
                    "Use offline mode if available"
                ],
                "user_message": "Network timeout. Please check your connection."
            },
            "dependency_missing": {
                "category": ErrorCategory.DEPENDENCY,
                "severity": ErrorSeverity.HIGH,
                "recovery": [
                    "Install missing dependencies",
                    "Update package versions",
                    "Check system requirements"
                ],
                "user_message": "Missing dependency. Please install required packages."
            },
            "invalid_input": {
                "category": ErrorCategory.USER_INPUT,
                "severity": ErrorSeverity.LOW,
                "recovery": [
                    "Check input format",
                    "Verify required parameters",
                    "Review input examples"
                ],
                "user_message": "Invalid input format. Please check your parameters."
            },
            "resource_exhausted": {
                "category": ErrorCategory.RESOURCE,
                "severity": ErrorSeverity.HIGH,
                "recovery": [
                    "Free up system resources",
                    "Close unnecessary applications",
                    "Increase resource limits"
                ],
                "user_message": "System resources exhausted. Please free up memory/disk space."
            },
            "execution_failed": {
                "category": ErrorCategory.EXECUTION,
                "severity": ErrorSeverity.MEDIUM,
                "recovery": [
                    "Check command syntax",
                    "Verify executable permissions",
                    "Review execution environment"
                ],
                "user_message": "Command execution failed. Please check syntax and permissions."
            }
        }
    
    async def handle_error(
        self,
        error: Exception,
        context: Optional[ErrorContext] = None,
        severity: Optional[ErrorSeverity] = None,
        category: Optional[ErrorCategory] = None
    ) -> ErrorReport:
        """
        Handle an error with comprehensive analysis and recovery suggestions
        
        Args:
            error: The exception that occurred
            context: Error context information
            severity: Override severity level
            category: Override error category
            
        Returns:
            ErrorReport with comprehensive error information
        """
        # Analyze error
        error_analysis = self._analyze_error(error, context)
        
        # Create error report
        report = ErrorReport(
            error_id="",
            severity=severity or error_analysis["severity"],
            category=category or error_analysis["category"],
            message=str(error),
            details=error_analysis.get("details"),
            traceback_info=traceback.format_exc(),
            context=context,
            recovery_suggestions=error_analysis.get("recovery", []),
            rollback_available=error_analysis.get("rollback_available", False),
            user_friendly_message=error_analysis.get("user_message", str(error))
        )
        
        # Log error
        self._log_error(report)
        
        # Store in history
        self.error_history.append(report)
        
        # Trigger recovery actions if needed
        if report.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            await self._trigger_recovery_actions(report)
        
        return report
    
    def _analyze_error(self, error: Exception, context: Optional[ErrorContext] = None) -> Dict[str, Any]:
        """Analyze error and determine category, severity, and recovery options"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        # Pattern matching for common errors
        for pattern_name, pattern_info in self.error_patterns.items():
            if any(keyword in error_str for keyword in [
                "permission", "denied", "access", "unauthorized"
            ]) and pattern_name == "permission_denied":
                return pattern_info
            
            if any(keyword in error_str for keyword in [
                "not found", "no such file", "does not exist"
            ]) and pattern_name == "file_not_found":
                return pattern_info
            
            if any(keyword in error_str for keyword in [
                "timeout", "connection", "network", "unreachable"
            ]) and pattern_name == "network_timeout":
                return pattern_info
            
            if any(keyword in error_str for keyword in [
                "module", "import", "dependency", "package"
            ]) and pattern_name == "dependency_missing":
                return pattern_info
            
            if any(keyword in error_str for keyword in [
                "invalid", "malformed", "syntax", "parse"
            ]) and pattern_name == "invalid_input":
                return pattern_info
            
            if any(keyword in error_str for keyword in [
                "memory", "disk", "resource", "space"
            ]) and pattern_name == "resource_exhausted":
                return pattern_info
        
        # Default analysis
        return {
            "category": ErrorCategory.SYSTEM,
            "severity": ErrorSeverity.MEDIUM,
            "recovery": ["Check system logs", "Retry the operation", "Contact support"],
            "user_message": "An unexpected error occurred. Please try again.",
            "rollback_available": context is not None
        }
    
    def _log_error(self, report: ErrorReport):
        """Log error with comprehensive information"""
        log_data = {
            "error_id": report.error_id,
            "severity": report.severity.value,
            "category": report.category.value,
            "message": report.message,
            "details": report.details,
            "context": asdict(report.context) if report.context else None,
            "recovery_suggestions": report.recovery_suggestions,
            "rollback_available": report.rollback_available,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log to file
        self.logger.error(json.dumps(log_data, indent=2, default=str))
        
        # Log to dedicated error file
        error_file = self.log_dir / f"error_{report.error_id}.json"
        with open(error_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
    
    async def _trigger_recovery_actions(self, report: ErrorReport):
        """Trigger automatic recovery actions for critical errors"""
        if report.category == ErrorCategory.RESOURCE:
            # Trigger resource cleanup
            await self._cleanup_resources()
        
        if report.category == ErrorCategory.DEPENDENCY:
            # Trigger dependency check
            await self._check_dependencies()
        
        if report.rollback_available and report.context:
            # Trigger rollback if available
            await self._trigger_rollback(report.context)
    
    async def _cleanup_resources(self):
        """Cleanup system resources"""
        self.logger.info("Triggering resource cleanup...")
        # Implementation would go here
        pass
    
    async def _check_dependencies(self):
        """Check system dependencies"""
        self.logger.info("Checking system dependencies...")
        # Implementation would go here
        pass
    
    async def _trigger_rollback(self, context: ErrorContext):
        """Trigger system rollback"""
        self.logger.info(f"Triggering rollback for skill: {context.skill_name}")
        # Implementation would go here
        pass
    
    def get_error_summary(self, limit: int = 50) -> Dict[str, Any]:
        """Get summary of recent errors"""
        recent_errors = self.error_history[-limit:]
        
        summary = {
            "total_errors": len(self.error_history),
            "recent_errors": len(recent_errors),
            "by_severity": {},
            "by_category": {},
            "most_common": {}
        }
        
        # Count by severity
        for error in recent_errors:
            severity = error.severity.value
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
        
        # Count by category
        for error in recent_errors:
            category = error.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        # Most common errors
        error_messages = [error.message for error in recent_errors]
        for message in set(error_messages):
            count = error_messages.count(message)
            if count > 1:
                summary["most_common"][message] = count
        
        return summary
    
    def export_error_reports(self, filepath: Path) -> bool:
        """Export all error reports to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump([asdict(report) for report in self.error_history], f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export error reports: {e}")
            return False


# Global error handler instance
_global_error_handler: Optional[SkillErrorHandler] = None


def get_error_handler() -> SkillErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = SkillErrorHandler()
    return _global_error_handler


async def handle_skill_error(
    error: Exception,
    skill_name: str,
    workflow_step: Optional[str] = None,
    user_command: Optional[str] = None
) -> ErrorReport:
    """
    Convenience function to handle skill errors
    
    Args:
        error: The exception that occurred
        skill_name: Name of the skill that failed
        workflow_step: Current workflow step
        user_command: Original user command
        
    Returns:
        ErrorReport with comprehensive information
    """
    context = ErrorContext(
        skill_name=skill_name,
        workflow_step=workflow_step,
        user_command=user_command
    )
    
    handler = get_error_handler()
    return await handler.handle_error(error, context)


def skill_error_handler(
    skill_name: str,
    workflow_step: Optional[str] = None,
    user_command: Optional[str] = None
):
    """
    Decorator for automatic skill error handling
    
    Usage:
        @skill_error_handler("my_skill", "step_1", "user command")
        async def my_skill_function():
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                report = await handle_skill_error(e, skill_name, workflow_step, user_command)
                # Re-raise with enhanced information
                raise Exception(f"Skill '{skill_name}' failed: {report.user_friendly_message}") from e
        return wrapper
    return decorator
