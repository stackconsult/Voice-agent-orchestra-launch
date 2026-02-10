"""
Monitor Agent - Real-time Execution Monitoring

Provides real-time monitoring of skill execution, error detection,
and comprehensive logging. Tracks all system actions and provides
audit trails for safety and debugging.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# Try to import psutil, but make it optional
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events to monitor."""
    START = "start"
    STOP = "stop"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    RESOURCE_USAGE = "resource_usage"
    SKILL_EXECUTION = "skill_execution"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"


class Severity(Enum):
    """Event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    INFO = "info"


@dataclass
class MonitorEvent:
    """Single monitoring event."""
    timestamp: str
    event_type: EventType
    severity: Severity
    component: str
    message: str
    details: Dict[str, Any]
    execution_id: Optional[str] = None
    user_id: Optional[str] = None


class ResourceMonitor:
    """Monitor system resource usage."""
    
    def __init__(self):
        self.start_time = time.time()
        self.psutil_available = PSUTIL_AVAILABLE
        
        if self.psutil_available:
            try:
                self.process = psutil.Process()
            except Exception as e:
                logger.warning(f"Failed to initialize psutil Process: {e}")
                self.psutil_available = False
    
    def get_current_usage(self) -> Dict[str, Any]:
        """Get current resource usage."""
        if not self.psutil_available:
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
                "memory_percent": 0,
                "disk_usage": {},
                "network_io": {"bytes_sent": 0, "bytes_recv": 0},
                "uptime_seconds": time.time() - self.start_time,
                "note": "psutil not available - resource monitoring disabled"
            }
        
        try:
            return {
                "cpu_percent": self.process.cpu_percent(),
                "memory_mb": self.process.memory_info().rss / 1024 / 1024,
                "memory_percent": self.process.memory_percent(),
                "disk_usage": {
                    path: psutil.disk_usage(path).percent
                    for path in ["/", Path.home()]
                },
                "network_io": {
                    "bytes_sent": self.process.io_counters().write_bytes,
                    "bytes_recv": self.process.io_counters().read_bytes
                },
                "uptime_seconds": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Failed to get resource usage: {e}")
            return {
                "cpu_percent": 0,
                "memory_mb": 0,
                "memory_percent": 0,
                "disk_usage": {},
                "network_io": {"bytes_sent": 0, "bytes_recv": 0},
                "uptime_seconds": time.time() - self.start_time,
                "error": str(e)
            }


class MonitorAgent:
    """
    Real-time execution monitoring agent.
    
    Tracks all system actions, detects errors, and provides comprehensive
    audit trails for safety and debugging.
    """
    
    def __init__(
        self, 
        log_dir: Optional[Path] = None,
        max_events: int = 10000,
        resource_check_interval: float = 5.0
    ):
        """
        Initialize monitor agent.
        
        Args:
            log_dir: Directory to store logs (default: ~/.aios/logs)
            max_events: Maximum events to keep in memory
            resource_check_interval: Interval for resource monitoring (seconds)
        """
        self.log_dir = log_dir or Path.home() / ".aios" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_events = max_events
        self.resource_check_interval = resource_check_interval
        
        # Event storage
        self.events: List[MonitorEvent] = []
        self.event_queue = queue.Queue()
        self.current_execution_id: Optional[str] = None
        
        # Resource monitoring
        self.resource_monitor = ResourceMonitor()
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Log files
        self.jsonl_file = self.log_dir / "events.jsonl"
        self.error_file = self.log_dir / "errors.log"
        
        # Initialize log files
        self._init_log_files()
    
    def _init_log_files(self) -> None:
        """Initialize log files with headers."""
        try:
            # Create JSONL file if it doesn't exist
            if not self.jsonl_file.exists():
                with open(self.jsonl_file, 'w') as f:
                    f.write("# AI-OS Event Log\n")
            
            # Create error log file if it doesn't exist
            if not self.error_file.exists():
                with open(self.error_file, 'w') as f:
                    f.write("# AI-OS Error Log\n")
                    f.write(f"# Started: {datetime.now().isoformat()}\n\n")
                    
        except Exception as e:
            logger.error(f"Failed to initialize log files: {e}")
    
    def start_monitoring(self, execution_id: Optional[str] = None) -> None:
        """
        Start active monitoring.
        
        Args:
            execution_id: Unique execution identifier
        """
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return
        
        self.current_execution_id = execution_id or f"exec_{int(time.time())}"
        self.monitoring_active = True
        
        # Start resource monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._resource_monitor_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
        # Log start event
        self.log_event(
            EventType.START,
            Severity.INFO,
            "monitor_agent",
            f"Started monitoring for execution: {self.current_execution_id}",
            {"execution_id": self.current_execution_id}
        )
        
        logger.info(f"Monitoring started: {self.current_execution_id}")
    
    def stop_monitoring(self) -> None:
        """Stop active monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        # Log stop event
        self.log_event(
            EventType.STOP,
            Severity.INFO,
            "monitor_agent",
            f"Stopped monitoring for execution: {self.current_execution_id}",
            {"execution_id": self.current_execution_id}
        )
        
        logger.info(f"Monitoring stopped: {self.current_execution_id}")
        self.current_execution_id = None
    
    def _resource_monitor_loop(self) -> None:
        """Background thread for resource monitoring."""
        while self.monitoring_active:
            try:
                usage = self.resource_monitor.get_current_usage()
                self.log_event(
                    EventType.RESOURCE_USAGE,
                    Severity.INFO,
                    "resource_monitor",
                    "System resource usage",
                    usage
                )
                
                # Check for resource warnings
                if usage.get("memory_percent", 0) > 80:
                    self.log_event(
                        EventType.WARNING,
                        Severity.HIGH,
                        "resource_monitor",
                        "High memory usage detected",
                        usage
                    )
                
                if usage.get("cpu_percent", 0) > 90:
                    self.log_event(
                        EventType.WARNING,
                        Severity.HIGH,
                        "resource_monitor",
                        "High CPU usage detected",
                        usage
                    )
                
                time.sleep(self.resource_check_interval)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(self.resource_check_interval)
    
    def log_event(
        self,
        event_type: EventType,
        severity: Severity,
        component: str,
        message: str,
        details: Dict[str, Any],
        execution_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """
        Log a monitoring event.
        
        Args:
            event_type: Type of event
            severity: Event severity
            component: Component generating the event
            message: Event message
            details: Additional event details
            execution_id: Execution identifier
            user_id: User identifier
        """
        event = MonitorEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            severity=severity,
            component=component,
            message=message,
            details=details,
            execution_id=execution_id or self.current_execution_id,
            user_id=user_id
        )
        
        # Add to memory storage
        self.events.append(event)
        
        # Trim events if exceeding max
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Write to JSONL file
        self._write_event_to_file(event)
        
        # Log errors to error file
        if event_type == EventType.ERROR:
            self._write_error_to_file(event)
        
        # Log to standard logger
        log_level = {
            Severity.LOW: logging.DEBUG,
            Severity.MEDIUM: logging.INFO,
            Severity.HIGH: logging.WARNING,
            Severity.CRITICAL: logging.ERROR
        }.get(severity, logging.INFO)
        
        logger.log(log_level, f"[{component}] {message}")
    
    def _write_event_to_file(self, event: MonitorEvent) -> None:
        """Write event to JSONL file."""
        try:
            with open(self.jsonl_file, 'a') as f:
                event_dict = asdict(event)
                event_dict['event_type'] = event.event_type.value
                event_dict['severity'] = event.severity.value
                f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            logger.error(f"Failed to write event to file: {e}")
    
    def _write_error_to_file(self, event: MonitorEvent) -> None:
        """Write error event to error log file."""
        try:
            with open(self.error_file, 'a') as f:
                f.write(f"[{event.timestamp}] {event.severity.value.upper()}: ")
                f.write(f"[{event.component}] {event.message}\n")
                if event.details:
                    f.write(f"Details: {json.dumps(event.details, indent=2)}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            logger.error(f"Failed to write error to file: {e}")
    
    def log_skill_execution(
        self,
        skill_name: str,
        action: str,
        details: Dict[str, Any],
        success: bool = True
    ) -> None:
        """
        Log skill execution event.
        
        Args:
            skill_name: Name of the skill
            action: Action being performed
            details: Execution details
            success: Whether execution was successful
        """
        severity = Severity.INFO if success else Severity.HIGH
        event_type = EventType.SKILL_EXECUTION if success else EventType.ERROR
        
        self.log_event(
            event_type,
            severity,
            "skill_executor",
            f"Skill {action}: {skill_name}",
            {
                "skill_name": skill_name,
                "action": action,
                "success": success,
                **details
            }
        )
    
    def log_api_call(
        self,
        provider: str,
        endpoint: str,
        request_details: Dict[str, Any],
        response_details: Dict[str, Any],
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log API call event.
        
        Args:
            provider: API provider (e.g., 'openai', 'anthropic')
            endpoint: API endpoint
            request_details: Request details
            response_details: Response details
            success: Whether call was successful
            error: Error message if failed
        """
        details = {
            "provider": provider,
            "endpoint": endpoint,
            "request": request_details,
            "response": response_details,
            "success": success
        }
        
        if error:
            details["error"] = error
        
        severity = Severity.INFO if success else Severity.HIGH
        event_type = EventType.API_CALL if success else EventType.ERROR
        
        self.log_event(
            event_type,
            severity,
            "api_client",
            f"API call to {provider}: {endpoint}",
            details
        )
    
    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        success: bool = True,
        error: Optional[str] = None
    ) -> None:
        """
        Log file operation event.
        
        Args:
            operation: Type of operation (read, write, delete)
            file_path: Path to file
            success: Whether operation was successful
            error: Error message if failed
        """
        details = {
            "operation": operation,
            "file_path": file_path,
            "success": success
        }
        
        if error:
            details["error"] = error
        
        severity = Severity.INFO if success else Severity.MEDIUM
        event_type = EventType.FILE_OPERATION if success else EventType.ERROR
        
        self.log_event(
            event_type,
            severity,
            "file_manager",
            f"File {operation}: {file_path}",
            details
        )
    
    def detect_critical_failure(self, error: Exception, context: Dict[str, Any]) -> bool:
        """
        Detect if error represents a critical failure.
        
        Args:
            error: Exception that occurred
            context: Execution context
            
        Returns:
            True if critical failure detected
        """
        # Check for critical error patterns
        critical_patterns = [
            "system corruption",
            "data loss",
            "security breach",
            "resource exhaustion",
            "permission denied"
        ]
        
        error_str = str(error).lower()
        context_str = str(context).lower()
        
        for pattern in critical_patterns:
            if pattern in error_str or pattern in context_str:
                self.log_event(
                    EventType.ERROR,
                    Severity.CRITICAL,
                    "failure_detector",
                    f"Critical failure detected: {pattern}",
                    {
                        "error": str(error),
                        "context": context,
                        "pattern": pattern
                    }
                )
                return True
        
        return False
    
    def get_events(
        self,
        event_type: Optional[EventType] = None,
        severity: Optional[Severity] = None,
        component: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[MonitorEvent]:
        """
        Get filtered events.
        
        Args:
            event_type: Filter by event type
            severity: Filter by severity
            component: Filter by component
            execution_id: Filter by execution ID
            limit: Maximum number of events to return
            
        Returns:
            Filtered list of events
        """
        filtered_events = self.events
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
        
        if component:
            filtered_events = [e for e in filtered_events if e.component == component]
        
        if execution_id:
            filtered_events = [e for e in filtered_events if e.execution_id == execution_id]
        
        # Sort by timestamp (newest first)
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        if limit:
            filtered_events = filtered_events[:limit]
        
        return filtered_events
    
    def get_error_summary(self, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary of errors for analysis.
        
        Args:
            execution_id: Filter by execution ID
            
        Returns:
            Error summary statistics
        """
        error_events = self.get_events(
            event_type=EventType.ERROR,
            execution_id=execution_id
        )
        
        # Group errors by component
        errors_by_component = {}
        for event in error_events:
            component = event.component
            if component not in errors_by_component:
                errors_by_component[component] = []
            errors_by_component[component].append(event)
        
        # Calculate statistics
        summary = {
            "total_errors": len(error_events),
            "errors_by_component": {
                comp: len(events) for comp, events in errors_by_component.items()
            },
            "severity_distribution": {
                sev.value: len([e for e in error_events if e.severity == sev])
                for sev in Severity
            },
            "recent_errors": [
                {
                    "timestamp": e.timestamp,
                    "component": e.component,
                    "message": e.message
                }
                for e in error_events[:10]
            ]
        }
        
        return summary
    
    async def stream_events(
        self,
        event_type: Optional[EventType] = None,
        execution_id: Optional[str] = None
    ) -> AsyncGenerator[MonitorEvent, None]:
        """
        Stream events in real-time.
        
        Args:
            event_type: Filter by event type
            execution_id: Filter by execution ID
            
        Yields:
            MonitorEvent objects as they occur
        """
        last_event_count = len(self.events)
        
        while self.monitoring_active:
            # Check for new events
            if len(self.events) > last_event_count:
                new_events = self.events[last_event_count:]
                
                for event in new_events:
                    if event_type and event.event_type != event_type:
                        continue
                    if execution_id and event.execution_id != execution_id:
                        continue
                    
                    yield event
                
                last_event_count = len(self.events)
            
            await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
    
    def export_events(
        self,
        output_file: Path,
        format: str = "json",
        filters: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Export events to file.
        
        Args:
            output_file: Output file path
            format: Export format ('json', 'csv', 'jsonl')
            filters: Event filters
        """
        # Apply filters
        events = self.events
        if filters:
            events = self.get_events(**filters)
        
        try:
            if format == "json":
                with open(output_file, 'w') as f:
                    events_data = [asdict(event) for event in events]
                    for event in events_data:
                        event['event_type'] = event['event_type'].value
                        event['severity'] = event['severity'].value
                    json.dump(events_data, f, indent=2)
            
            elif format == "jsonl":
                with open(output_file, 'w') as f:
                    for event in events:
                        event_dict = asdict(event)
                        event_dict['event_type'] = event.event_type.value
                        event_dict['severity'] = event.severity.value
                        f.write(json.dumps(event_dict) + '\n')
            
            elif format == "csv":
                import csv
                with open(output_file, 'w', newline='') as f:
                    if events:
                        writer = csv.DictWriter(f, fieldnames=asdict(events[0]).keys())
                        writer.writeheader()
                        for event in events:
                            event_dict = asdict(event)
                            event_dict['event_type'] = event.event_type.value
                            event_dict['severity'] = event.severity.value
                            writer.writerow(event_dict)
            
            logger.info(f"Exported {len(events)} events to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export events: {e}")
            raise
