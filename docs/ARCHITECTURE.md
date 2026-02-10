# ARCHITECTURE - System Design & Boundaries

## System Overview
AI-OS is a voice-driven workflow automation system that operates offline-first with seamless cloud fallback. The system enables users to speak natural language commands and automatically generate, execute, and monitor complete workflows.

## Core Architecture Tiers

### Tier 1: User Interface (PyQt6)
- **Global hotkey registration** (Cmd+Shift+V)
- **Push-to-talk voice recording window**
- **Real-time transcription display**
- **Execution history panel**
- **Status indicators**

### Tier 2: Audio & Voice Input
- **FFmpeg audio recording** (local, offline)
- **Device enumeration** (microphone selection)
- **whisper.cpp transcription** (offline, no API calls)
- **Voice prefix detection** (optional "aios" safety prefix)

### Tier 3: Orchestration & Decision
- **local_lm_agent** (Ollama/LM Studio integration)
- **offline_online_context_switcher** (cloud fallback logic)
- **skill_generator** (workflow to SKILL.md conversion)

### Tier 4: Execution & Action
- **restore_manager** (system snapshots + rollback)
- **skill_executor** (Terminal/AppleScript/Python execution)
- **monitor_agent** (real-time execution monitoring)

### Tier 5: Persistence & Learning
- **history_manager** (command logging and cost tracking)
- **Snapshots** (restore points for safety)
- **Logs** (detailed execution records)
- **Skills** (auto-generated workflows)

## Data Flow Architecture

```
VOICE INPUT → TRANSCRIPTION → WORKFLOW DESIGN → SKILL CREATION → SNAPSHOT → EXECUTION → MONITORING → HISTORY
```

### Phase Breakdown:
1. **Voice Input** (2s): User presses Cmd+Shift+V, speaks command
2. **Transcription** (2-3s): whisper.cpp processes audio offline
3. **Workflow Design** (3-4s): Local LM generates structured workflow
4. **Skill Creation** (instant): Convert workflow to executable SKILL.md
5. **Snapshot** (instant): Capture system state for safety
6. **Execution** (varies): Run Terminal/AppleScript/Python commands
7. **Monitoring** (real-time): Watch execution, log everything
8. **History** (instant): Record command, results, costs

## Component Interactions

### Core Components (6 Critical Files):
1. **restore_manager.py** - System snapshots and rollback
2. **monitor_agent.py** - Real-time execution monitoring  
3. **local_lm_agent.py** - Offline workflow design
4. **offline_online_context_switcher.py** - Cloud fallback
5. **skill_executor.py** - Execute SKILL.yaml workflows
6. **skill_generator.py** - Create SKILL.md from voice

### Integration Points:
- All components log to **monitor_agent**
- **restore_manager** creates snapshots before **skill_executor** runs
- **local_lm_agent** feeds **skill_generator** with workflow YAML
- **offline_online_context_switcher** enhances local results with cloud
- **history_manager** tracks everything for cost analysis

## Security Boundaries

### Offline-First Security:
- Voice data never leaves the Mac
- Transcription happens locally via whisper.cpp
- Workflow design uses local Ollama/LM Studio
- Skills execute locally (Terminal/AppleScript/Python)

### Cloud Fallback Security:
- Only switches when local can't handle task
- Context passed to cloud (no raw files unless <50KB)
- API keys stored in environment variables
- Cloud providers don't train on API data

### Data Protection:
- Snapshots encrypted (optional)
- API keys never logged
- Audit trail for all operations
- Cost tracking per client/project

## Performance Boundaries

### Target Hardware:
- MacBook Pro 2015: Intel i5, 8GB RAM, 121GB storage
- macOS Monterey 12.7.6+

### Performance Targets:
- Voice recording: Instant
- Transcription: 2-3 seconds
- Workflow design: 3-4 seconds (local)
- Skill creation: Instant
- Execution: Varies by task (typically 2-30 seconds)
- Cloud fallback: 2-5 seconds (when needed)

### Resource Limits:
- Memory usage: <500MB for AI-OS
- Storage: <1GB for models + snapshots
- Network: Only for cloud fallback (optional)
- CPU: Minimal during idle, moderate during execution

## Cost Boundaries

### Offline Operations: $0
- Voice input: Free
- Transcription: Free (whisper.cpp local)
- Workflow design: Free (Ollama local)
- Skill creation: Free
- Execution: Free (local commands)

### Cloud Fallback: $0.15-5
- Gemini 2.5 Flash: $0.10-0.50 per call
- Claude 3.5 Sonnet: $0.50-2.00 per call
- GPT-4: $0.50-3.00 per call

### Monthly Projections:
- Light usage (10 commands/day): $10-15
- Medium usage (50 commands/day): $40-60
- Heavy usage (100+ commands/day): $100-200

## Failure Boundaries & Recovery

### Critical Failures (Trigger Restore):
- File deletion/modification errors
- Permission violations
- System corruption
- Network failures during cloud operations

### Non-Critical Failures (Continue):
- Temporary command failures
- Network timeouts
- Rate limiting
- Minor syntax errors

### Recovery Strategies:
- **Automatic Restore**: Rollback to snapshot on critical errors
- **Retry Logic**: Up to 3 attempts for transient failures
- **Cloud Fallback**: Switch to cloud if local fails
- **Manual Intervention**: User approval for system changes

## Scalability Boundaries

### Single User Scale:
- Supports 1 user with multiple concurrent skills
- Up to 10 simultaneous skill executions
- History tracking for 10,000+ commands

### Multi-Client Scale (Future):
- Per-client cost tracking
- Client-specific skill directories
- Separate audit trails
- Role-based access control

## Technology Stack Boundaries

### Core Technologies:
- **Python 3.9+**: Main development language
- **PyQt6**: GUI framework
- **FFmpeg**: Audio recording
- **whisper.cpp**: Offline transcription
- **Ollama/LM Studio**: Local LLM hosting

### Integration Boundaries:
- **macOS only**: AppleScript, macOS-specific features
- **Intel Mac**: Primary target (ARM support planned)
- **Local filesystem**: No cloud storage dependencies
- **REST APIs**: For cloud provider integration

## Deployment Boundaries

### Development Environment:
- Local development on target hardware
- Git version control
- pytest for testing
- IDE integration (Windsurf Cascade)

### Production Deployment:
- One-command install via install.sh
- Automatic dependency management
- Configuration via .env file
- Health checks and monitoring

### Distribution:
- GitHub repository
- pip package (optional)
- Docker container (future)
- macOS app bundle (future)

## Compliance Boundaries

### Data Privacy:
- GDPR compliant (local processing)
- CCPA compliant (user data control)
- HIPAA compatible (with encryption)
- SOX compliant (audit trails)

### Industry Standards:
- SOC 2 Type II (cloud providers)
- ISO 27001 (security management)
- NIST Cybersecurity Framework
- OWASP security guidelines

## Future Architecture Evolution

### Phase 2 Enhancements:
- Multi-user support
- Cloud synchronization
- Mobile app interface
- Advanced AI models

### Phase 3 Capabilities:
- Enterprise features
- Advanced analytics
- Custom integrations
- White-label options

### Technical Debt Management:
- Regular refactoring
- Dependency updates
- Security patches
- Performance optimization
