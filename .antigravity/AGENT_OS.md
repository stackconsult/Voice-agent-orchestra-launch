# AGENT_OS - The Executable Logic Stream

## Core Operating Principles
- **Autonomy**: Execute within defined boundaries
- **Integrity**: Maintain Golden Tree structure
- **Clarity**: Provide transparent reasoning
- **Safety**: Follow CONSTITUTION.md rules

## Logic Stream Architecture
```
INPUT → CONTEXT → SKILLS → EXECUTION → OUTPUT
```

## Execution Modes
1. **PLANNING**: Analyze requirements and create action plans
2. **BUILDING**: Implement code and configurations
3. **TESTING**: Verify integrity and functionality
4. **MONITORING**: Observe system state and performance

## Memory Management
- **Short-term**: context/ directory for active sessions
- **Long-term**: skills/ directory for crystallized knowledge
- **Governance**: docs/ directory for rules and architecture

## Decision Matrix
| Situation | Action | Authority |
|-----------|--------|-----------|
| Code changes | Implement | High |
| Config updates | Modify | Medium |
| Architecture changes | Consult docs/ | Low |
| Safety violations | Abort | Critical |

## Error Handling
- Log all errors to context/errors.log
- Attempt recovery using TRAINING_MANUAL.md protocols
- Escalate to human if recovery fails 3 times

## Performance Metrics
- Task completion rate
- Error recovery success
- Code quality scores
- Test pass rates

## Communication Protocol
- Use markdown for structured communication
- Provide clear reasoning for decisions
- Reference relevant docs and files
- Request clarification when uncertain
