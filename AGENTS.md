# AGENTS - Environment & Forbidden States

## Product Vision

AI-OS is a voice-driven workflow automation system that enables users to:
- Speak natural language commands to automate repetitive tasks
- Generate complete workflows automatically using local AI
- Execute workflows safely with automatic rollback on errors
- Monitor all actions in real-time with complete audit trails
- Work offline-first with seamless cloud fallback when needed

## Environment Configuration

### Target Environment
- **Hardware**: MacBook Pro 2015+ (Intel i5, 8GB+ RAM, 121GB+ storage)
- **OS**: macOS Monterey 12.7.6+
- **Python**: 3.9+
- **IDE**: Windsurf Cascade, Google IDX, or similar

### Development Environment
- **Local Development**: All development happens on target hardware
- **Git Repository**: Version control with comprehensive documentation
- **Testing**: pytest with >90% code coverage requirement
- **Documentation**: Complete API docs and user guides

### Production Environment
- **Single User**: Designed for individual productivity
- **Local Processing**: Voice, transcription, and workflow design happen locally
- **Cloud Fallback**: Optional cloud AI for complex tasks
- **Security First**: All data processed locally unless explicitly sent to cloud

## Forbidden States (Never Allowed)

### System States
- **NO Autonomous Execution**: System never acts without user initiation
- **NO System Modification**: Never modifies OS files or settings without explicit approval
- **NO Data Exfiltration**: Never sends user data to cloud without consent
- **NO Credential Exposure**: Never logs or exposes API keys or passwords
- **NO Surveillance**: Never monitors user activity outside of explicit commands

### Data States
- **NO Training Data Usage**: User data never used to train AI models
- **NO Persistent Cloud Storage**: User data not stored permanently in cloud
- **NO Cross-User Data**: No data sharing between different users
- **NO Sensitive Data Upload**: Financial, legal, or health data processed locally only
- **NO Unencrypted Storage**: Sensitive data encrypted at rest when stored

### Execution States
- **NO Unmonitored Execution**: All actions logged and monitored in real-time
- **NO Irreversible Actions**: Critical actions require snapshots and rollback capability
- **NO Background Processing**: No background tasks without user knowledge
- **NO Network Operations**: No external network calls without explicit user approval
- **NO Resource Exhaustion**: No operations that consume excessive system resources

## Allowed States (With Safeguards)

### Safe System States
- **Voice Input**: User-initiated voice recording with explicit start/stop
- **Local Processing**: All transcription and workflow design happens locally
- **User Commands**: Explicit user commands executed in controlled environment
- **Snapshot Creation**: System state captured before potentially dangerous operations
- **Real-time Monitoring**: All actions logged and displayed to user

### Controlled Cloud States
- **Context Switching**: Switch to cloud AI only when local processing insufficient
- **Minimal Data Transfer**: Only necessary context sent to cloud providers
- **Cost Tracking**: Real-time cost monitoring and budget enforcement
- **User Approval**: Cloud operations above threshold require explicit consent
- **Immediate Fallback**: Return to local processing as soon as possible

### Safe Execution States
- **Sandbox Commands**: Terminal commands run in user context with monitoring
- **File Operations**: File operations limited to user-specified directories
- **Application Integration**: Integration through standard APIs and interfaces
- **Error Recovery**: Automatic rollback to previous state on critical errors
- **Audit Logging**: Complete audit trail of all system actions

## Agent Capabilities

### Core Capabilities
- **Voice Recognition**: Convert speech to text using local whisper.cpp
- **Natural Language Understanding**: Parse user intent from voice commands
- **Workflow Generation**: Create complete workflows from natural language
- **Skill Creation**: Generate executable skills with proper documentation
- **Safe Execution**: Execute workflows with monitoring and rollback capability

### Integration Capabilities
- **Terminal Commands**: Execute shell commands safely
- **AppleScript**: Automate macOS applications
- **Python Scripts**: Run custom Python code for data processing
- **API Integration**: Connect to external services with user credentials
- **File System**: Organize and manipulate files safely

### Learning Capabilities
- **Pattern Recognition**: Learn from successful workflow patterns
- **Optimization**: Improve workflow efficiency over time
- **Error Prevention**: Learn from failures to prevent future issues
- **User Adaptation**: Adapt to user preferences and work patterns
- **Cost Optimization**: Minimize cloud usage to reduce costs

## Agent Limitations

### Technical Limitations
- **macOS Only**: Designed specifically for macOS environment
- **Single User**: Not designed for multi-user environments
- **Local Resources**: Limited by available hardware resources
- **Network Dependency**: Cloud features require internet connection
- **Application Dependencies**: Requires specific applications for some tasks

### Ethical Limitations
- **No Autonomous Decisions**: Cannot make decisions without user input
- **No Legal Advice**: Cannot provide legal or financial advice
- **No Medical Diagnosis**: Cannot provide medical information or diagnosis
- **No Critical Decisions**: Cannot make life-critical or safety-critical decisions
- **No Manipulation**: Cannot influence user decisions or behavior

### Security Limitations
- **User Permissions**: Limited by user's system permissions
- **API Rate Limits**: Subject to cloud provider rate limits
- **Network Security**: Dependent on network security for cloud operations
- **Credential Security**: Dependent on user securing their API keys
- **File System Access**: Limited to user-accessible files and directories

## Success Criteria

### Functional Success
- **Voice Recognition**: >95% accuracy for clear speech
- **Workflow Generation**: >90% success rate for common tasks
- **Execution Reliability**: >99% success rate for generated workflows
- **Error Recovery**: 100% successful rollback on critical errors
- **User Satisfaction**: >4.5/5 user satisfaction rating

### Performance Success
- **Response Time**: <200ms for local operations
- **Transcription Speed**: <3 seconds for voice-to-text
- **Workflow Generation**: <5 seconds for workflow creation
- **Execution Speed**: <30 seconds for typical workflows
- **System Resource Usage**: <500MB memory, <10% CPU

### Security Success
- **Zero Data Breaches**: No unauthorized data access
- **Complete Audit Trail**: 100% action logging and tracking
- **Cost Control**: No unexpected cost overruns
- **Privacy Compliance**: Full compliance with privacy regulations
- **User Control**: Complete user control over data and actions

## Failure Modes

### Critical Failures (Immediate Stop)
- **System Corruption**: Any modification to system files or settings
- **Security Breach**: Any unauthorized access or data exposure
- **Data Loss**: Any unexpected deletion or corruption of user data
- **Resource Exhaustion**: Any operation that crashes the system
- **Cost Overrun**: Any operation that exceeds budget limits

### Warning Failures (Continue with Monitoring)
- **Performance Degradation**: Slower than expected execution
- **Network Issues**: Temporary connectivity problems
- **API Rate Limits**: Cloud provider throttling
- **Minor Errors**: Non-critical execution errors
- **User Feedback**: Negative user feedback or complaints

### Recovery Procedures
- **Immediate Rollback**: Restore to last known good state
- **Error Analysis**: Log and analyze failure causes
- **User Notification**: Inform user of failure and recovery actions
- **System Reset**: Reset system to safe state if needed
- **Support Escalation**: Escalate to human support if needed

## Monitoring Requirements

### Real-time Monitoring
- **Execution Status**: Real-time display of workflow execution
- **Resource Usage**: Monitor CPU, memory, and disk usage
- **Network Activity**: Monitor all network requests and responses
- **Error Tracking**: Track all errors and failures
- **User Activity**: Monitor user interactions and commands

### Historical Monitoring
- **Usage Patterns**: Track system usage over time
- **Performance Trends**: Analyze performance changes
- **Cost Analysis**: Track and analyze costs
- **Error Patterns**: Identify recurring error patterns
- **User Behavior**: Analyze user behavior and preferences

### Alerting Requirements
- **Critical Alerts**: Immediate notification for critical failures
- **Performance Alerts**: Notification for performance degradation
- **Cost Alerts**: Notification for cost overruns
- **Security Alerts**: Notification for security issues
- **Maintenance Alerts**: Notification for maintenance needs

## Compliance Requirements

### Regulatory Compliance
- **GDPR**: Full compliance with EU data protection regulations
- **CCPA**: Compliance with California Consumer Privacy Act
- **HIPAA**: Optional compliance for healthcare data
- **SOX**: Compliance with financial reporting requirements
- **Industry Standards**: Compliance with industry-specific standards

### Security Compliance
- **SOC 2 Type II**: Security controls and procedures
- **ISO 27001**: Information security management
- **NIST Framework**: Cybersecurity framework compliance
- **OWASP**: Application security guidelines
- **Penetration Testing**: Regular security testing

### Audit Requirements
- **Complete Audit Trail**: All actions logged and auditable
- **Immutable Logs**: Logs cannot be modified or deleted
- **Regular Audits**: Regular security and compliance audits
- **Third-party Validation**: Independent validation of compliance
- **Transparent Reporting**: Clear reporting of compliance status

## Future Development

### Phase 2 Enhancements
- **Multi-user Support**: Support for multiple user profiles
- **Cloud Synchronization**: Sync skills and settings across devices
- **Mobile Applications**: Extend functionality to mobile devices
- **Advanced Analytics**: Enhanced data analysis and reporting
- **Enterprise Features**: Multi-tenant and enterprise features

### Phase 3 Capabilities
- **AI Model Improvements**: Advanced AI capabilities
- **Custom Integrations**: Support for custom third-party integrations
- **Advanced Security**: Enhanced security features
- **Performance Optimization**: System performance improvements
- **Global Expansion**: Support for multiple languages and regions

### Research Directions
- **New AI Technologies**: Evaluate and integrate new AI technologies
- **User Experience**: Improve user interface and experience
- **Performance Optimization**: Research performance optimization techniques
- **Security Research**: Research new security threats and mitigations
- **Usability Research**: Research user behavior and preferences

This AGENTS.md file serves as the kernel for the AI-OS system, defining the environment, capabilities, limitations, and success criteria for the voice-driven workflow automation system.
