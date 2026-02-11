---
description: Global error handling patterns for AI-OS skills and workflows
---

# AI-OS Error Handling Patterns

## Overview

This document defines comprehensive error handling patterns for AI-OS skills, workflows, and IDE operations. These patterns ensure consistent error reporting, recovery strategies, and user experience across the entire system.

## Core Error Handling Principles

### 1. **Fail Fast, Fail Gracefully**
- Detect errors early in the execution pipeline
- Provide clear, actionable error messages
- Maintain system stability during failures

### 2. **Contextual Error Reporting**
- Always include execution context (skill name, workflow step, user command)
- Provide user-friendly messages alongside technical details
- Log comprehensive error information for debugging

### 3. **Recovery-Oriented Design**
- Implement automatic retry mechanisms for transient failures
- Provide rollback capabilities for destructive operations
- Offer multiple recovery strategies based on error categories

### 4. **Structured Error Classification**
- Use standardized error categories and severity levels
- Implement pattern-based error analysis
- Enable automated error routing and handling

## Error Categories and Handling Strategies

### **SYSTEM Errors**
- **Description**: Operating system, filesystem, or hardware issues
- **Severity**: HIGH
- **Recovery**: System checks, resource cleanup, user intervention
- **Example**: Disk full, memory exhausted, permissions denied

### **NETWORK Errors**
- **Description**: Connectivity, timeout, or service availability issues
- **Severity**: MEDIUM
- **Recovery**: Retry with backoff, offline mode, alternative endpoints
- **Example**: Connection timeout, DNS resolution failure

### **DEPENDENCY Errors**
- **Description**: Missing packages, incompatible versions, import failures
- **Severity**: HIGH
- **Recovery**: Automatic installation, version checks, fallback implementations
- **Example**: Module not found, incompatible library version

### **VALIDATION Errors**
- **Description**: Input validation, schema compliance, parameter errors
- **Severity**: LOW
- **Recovery**: Input correction, parameter defaults, user guidance
- **Example**: Invalid JSON, missing required fields

### **EXECUTION Errors**
- **Description**: Command execution, script runtime, process failures
- **Severity**: MEDIUM
- **Recovery**: Command correction, environment setup, alternative approaches
- **Example**: Command not found, script syntax error

### **TIMEOUT Errors**
- **Description**: Operation timeouts, performance issues
- **Severity**: MEDIUM
- **Recovery**: Timeout adjustment, operation optimization, progress reporting
- **Example**: Long-running operation timeout

### **PERMISSION Errors**
- **Description**: Access rights, privilege issues, security restrictions
- **Severity**: HIGH
- **Recovery**: Permission fixes, privilege escalation, alternative paths
- **Example**: File access denied, insufficient privileges

### **RESOURCE Errors**
- **Description**: Memory, CPU, disk space, file handle exhaustion
- **Severity**: HIGH
- **Recovery**: Resource cleanup, usage optimization, capacity planning
- **Example**: Out of memory, disk space full

## Implementation Patterns

### **Skill-Level Error Handling**

```python
from ai_os.core import skill_error_handler, ErrorContext

@skill_error_handler("my_skill", "step_1", "user command")
async def my_skill_function():
    # Skill implementation
    pass
```

### **Workflow-Level Error Handling**

```python
from ai_os.core import workflow_error_handler, WorkflowContext

@workflow_error_handler("my_workflow", "my_skill")
async def my_workflow_function(user_command: str):
    # Workflow implementation
    pass
```

### **Manual Error Handling**

```python
from ai_os.core import get_error_handler, ErrorContext

async def my_function():
    try:
        # Operation that might fail
        pass
    except Exception as e:
        error_context = ErrorContext(
            skill_name="my_skill",
            workflow_step="current_step",
            user_command="original_command"
        )
        error_report = await get_error_handler().handle_error(e, error_context)
        # Handle error or re-raise with enhanced information
```

## IDE Integration Patterns

### **File Operation Errors**
```python
# Pattern for file operations
async def safe_file_operation(file_path: Path, operation: str):
    try:
        # File operation
        pass
    except PermissionError as e:
        await handle_file_permission_error(e, file_path, operation)
    except FileNotFoundError as e:
        await handle_file_not_found_error(e, file_path, operation)
    except OSError as e:
        await handle_system_error(e, file_path, operation)
```

### **Command Execution Errors**
```python
# Pattern for command execution
async def safe_command_execution(command: str, context: str):
    try:
        # Command execution
        pass
    except subprocess.CalledProcessError as e:
        await handle_command_error(e, command, context)
    except TimeoutError as e:
        await handle_timeout_error(e, command, context)
```

### **API Request Errors**
```python
# Pattern for API requests
async def safe_api_request(endpoint: str, data: dict):
    try:
        # API request
        pass
    except aiohttp.ClientError as e:
        await handle_network_error(e, endpoint, data)
    except asyncio.TimeoutError as e:
        await handle_timeout_error(e, endpoint, data)
```

## Error Recovery Strategies

### **Automatic Retry**
- Implement exponential backoff
- Limit retry attempts
- Track retry history
- Provide progress feedback

### **Fallback Mechanisms**
- Alternative implementations
- Degraded functionality
- Offline mode capabilities
- Manual intervention prompts

### **Rollback Procedures**
- System state snapshots
- Transactional operations
- Undo capabilities
- State restoration

### **User Guidance**
- Clear error messages
- Actionable suggestions
- Step-by-step instructions
- Context-aware help

## Monitoring and Analytics

### **Error Metrics**
- Error frequency by category
- Recovery success rates
- User satisfaction scores
- System impact assessment

### **Error Trends**
- Recurring error patterns
- Performance degradation indicators
- Usage pattern correlations
- System health monitoring

### **Alerting**
- Critical error notifications
- Performance threshold breaches
- System capacity warnings
- User experience degradation

## Best Practices

### **1. Always Provide Context**
```python
# Good
error_context = ErrorContext(
    skill_name="file_organizer",
    workflow_step="move_files",
    user_command="organize downloads",
    system_state={"disk_space": "85%", "memory": "4GB"}
)

# Bad
# No context provided
```

### **2. Use Appropriate Severity Levels**
```python
# Low severity - user input issues
ErrorSeverity.LOW

# Medium severity - temporary failures
ErrorSeverity.MEDIUM

# High severity - system issues
ErrorSeverity.HIGH

# Critical severity - system stability
ErrorSeverity.CRITICAL
```

### **3. Implement Comprehensive Logging**
```python
# Log at appropriate levels
logger.debug("Detailed debugging information")
logger.info("Normal operation information")
logger.warning("Potential issues")
logger.error("Error conditions")
logger.critical("Critical system failures")
```

### **4. Provide Recovery Options**
```python
# Always suggest recovery actions
recovery_suggestions = [
    "Check file permissions",
    "Free up disk space",
    "Try running with administrator privileges",
    "Contact support if issue persists"
]
```

### **5. Handle Exceptions Gracefully**
```python
try:
    # Operation
    pass
except SpecificException as e:
    # Handle specific exception
    pass
except Exception as e:
    # Handle unexpected exceptions
    # Always log and provide context
    pass
finally:
    # Cleanup resources
    pass
```

## Testing Error Handling

### **Unit Tests**
- Test error detection logic
- Verify error classification
- Validate recovery strategies
- Check error message formatting

### **Integration Tests**
- Test error propagation
- Verify rollback mechanisms
- Test retry logic
- Validate system stability

### **User Experience Tests**
- Test error message clarity
- Verify recovery guidance
- Test user interaction flows
- Validate accessibility

## Configuration

### **Error Handling Settings**
```yaml
error_handling:
  max_retries: 3
  retry_backoff_factor: 2
  timeout_seconds: 30
  enable_rollback: true
  log_level: "INFO"
  error_reports_dir: "~/.aios/errors"
```

### **Category-Specific Settings**
```yaml
error_categories:
  network:
    max_retries: 5
    timeout_seconds: 60
  system:
    max_retries: 1
    enable_rollback: true
  user_input:
    max_retries: 0
    provide_guidance: true
```

## Maintenance and Updates

### **Regular Review**
- Update error patterns
- Refine recovery strategies
- Improve user messages
- Optimize performance

### **Pattern Evolution**
- Add new error categories
- Enhance detection logic
- Improve recovery mechanisms
- Extend monitoring capabilities

### **Documentation Updates**
- Keep patterns current
- Update examples
- Revise best practices
- Maintain change logs
