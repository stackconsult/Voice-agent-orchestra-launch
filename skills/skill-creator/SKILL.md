---
name: skill-creator
version: 2.0.0
description: The meta-skill that interviews users and architects new AI skills with proper model selection.
author: AI-OS System
tags: ["meta", "system", "generator", "architect"]
category: system
triggers:
  - "create a new skill"
  - "build an automation"
  - "scaffold a workflow"
execution:
  mode: local_first
  model: llama3-local
  internet: false
---

# Skill Creator (Meta-Skill)

## 📋 Overview
This is the **Master Skill** responsible for spawning new agent capabilities. It uses an interactive interview process to determine the requirements, selects the appropriate AI architecture (Local vs Cloud), and generates a production-grade skill package.

## 🚀 Usage
```bash
aios run skill-creator
```

## 🔄 Workflow Steps

### 1. Requirement Interview
**Action**: `interactive_input`
**Prompt**: "What task would you like to automate? Please describe the inputs, desired outputs, and any sensitivity concerns."

### 2. Architecture Decision
**Action**: `execute_python`
**Logic**: Run `ModelSelector.analyze_requirements(input)`
**Output**: Returns `ModelConfig` (e.g., `{"mode": "local_only", "model": "llama3"}`)

### 3. Skill Generation
**Action**: `call_agent`
**Agent**: `EnhancedSkillGenerator`
**Parameters**:
- `voice_input`: [User Response from Step 1]
- `context`: [Architecture Decision from Step 2]

### 4. Validation & Deployment
**Action**: `terminal`
**Command**: `python -c "import yaml; yaml.safe_load(open('skills/{generated_skill_name}/workflow.yaml'))"`
**Description**: Verifies the generated skill folder structure and YAML syntax.

### 5. Test Execution
**Action**: `terminal`
**Command**: `python -m ai_os.workflows.enhanced_skill_executor --test {generated_skill_name}`
**Description**: Tests the skill execution in a safe environment.

## ⚙️ Configuration

This skill is configured to run in **local_first** mode using **llama3-local** for privacy and security during skill creation.

## 🔄 Detailed Implementation Logic

### Phase 1 (Discovery): User Interview
- Collect task requirements
- Identify sensitivity constraints
- Determine performance needs
- Gather context about data types

### Phase 2 (Architecture): Model Selection
- Analyze requirements for privacy concerns
- Evaluate complexity and coding needs
- Check for vision or specialized requirements
- Select optimal execution mode and model

### Phase 3 (Generation): Skill Creation
- Generate workflow steps based on requirements
- Create metadata with architectural decisions
- Build progressive loading folder structure
- Generate YAML frontmatter and templates

### Phase 4 (Validation): Quality Assurance
- Verify YAML syntax and structure
- Test skill execution in sandbox
- Validate security constraints
- Ensure proper file organization

## 📚 References

- **Generator Source**: `ai_os/workflows/enhanced_skill_generator.py`
- **Executor Source**: `ai_os/workflows/enhanced_skill_executor.py`
- **Templates**: `templates/workflow.yaml`
- **Architecture Docs**: `docs/ENHANCED_ARCHITECTURE.md`

## 🔧 Technical Implementation

### Model Selection Algorithm
```python
def analyze_requirements(description, context):
    # Privacy Check
    if sensitive_data or latency_critical:
        return LOCAL_ONLY
    
    # Complexity Check
    if coding or vision or complex_reasoning:
        return CLOUD_PREFERRED
    
    # Default
    return HYBRID
```

### Skill Structure Generation
```
generated_skill/
├── SKILL.md          # YAML frontmatter + content
├── workflow.yaml     # Execution logic
├── examples/         # Usage examples
├── references/       # Heavy context files
└── logs/            # Execution logs
```

## ✅ Success Criteria

1. **Requirements Gathered**: Complete user input collected
2. **Architecture Selected**: Optimal model and mode chosen
3. **Skill Generated**: Complete skill package created
4. **Validation Passed**: YAML syntax and structure verified
5. **Test Successful**: Skill executes without errors
6. **Documentation Complete**: All references and examples created

## 🚨 Error Handling

- **Input Validation**: Ensure user provides sufficient detail
- **Model Selection**: Handle edge cases in architecture decisions
- **File Creation**: Manage permission and path issues
- **YAML Validation**: Catch and report syntax errors
- **Execution Testing**: Handle test failures gracefully

## 🎯 Example Usage

```bash
# Start the skill creator
aios run skill-creator

# Example interaction:
> What task would you like to automate?
I need to analyze financial reports and generate summaries

> Architecture Decision: LOCAL_ONLY mode selected (financial data sensitivity)

> Skill Generated: financial-analyzer
> Location: ./skills/financial-analyzer/
> Validation: PASSED
> Test Execution: SUCCESS
```

---

**This meta-skill enables users to create production-grade AI skills with proper architectural decisions and security constraints.**
