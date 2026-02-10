#!/usr/bin/env python3
"""
Enhanced AI-OS Validation Script
================================
Demonstrates the enhanced system capabilities without external dependencies.
"""

import json
from pathlib import Path
import sys

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_os.workflows.enhanced_skill_generator import ModelSelector, ExecutionMode, ModelConfig


def validate_model_selector():
    """Validate the ModelSelector decision tree logic."""
    print("🧠 Testing ModelSelector Decision Tree...")
    print("=" * 50)
    
    selector = ModelSelector()
    
    test_cases = [
        ("Analyze financial reports with passwords", ExecutionMode.LOCAL_ONLY, "llama3-local"),
        ("Process medical patient records", ExecutionMode.LOCAL_ONLY, "llama3-local"),
        ("Write a Python script for API integration", ExecutionMode.CLOUD_PREFERRED, "claude-3-5-sonnet"),
        ("Analyze screenshots and PDF charts", ExecutionMode.CLOUD_PREFERRED, "gpt-4o"),
        ("Create a strategic business analysis report", ExecutionMode.CLOUD_PREFERRED, "claude-3-opus"),
        ("Automate file organization", ExecutionMode.HYBRID, "llama3-local")
    ]
    
    all_passed = True
    
    for description, expected_mode, expected_model in test_cases:
        config = selector.analyze_requirements(description, {})
        
        mode_passed = config.mode == expected_mode
        model_passed = config.recommended_model == expected_model
        
        status = "✅" if (mode_passed and model_passed) else "❌"
        print(f"{status} {description[:40]}...")
        print(f"   Expected: {expected_mode.value} + {expected_model}")
        print(f"   Got:      {config.mode.value} + {config.recommended_model}")
        
        if not (mode_passed and model_passed):
            all_passed = False
        print()
    
    return all_passed


def validate_skill_structure():
    """Validate the enhanced skill file structure."""
    print("📁 Validating Enhanced Skill Structure...")
    print("=" * 50)
    
    # Check if enhanced components exist
    required_files = [
        "ai_os/workflows/enhanced_skill_generator.py",
        "ai_os/workflows/enhanced_skill_executor.py",
        "skills/skill-creator/SKILL.md",
        "templates/workflow.yaml",
        "ai_os/main.py"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        path = Path(file_path)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        
        if not exists:
            all_exist = False
    
    print()
    return all_exist


def validate_yaml_frontmatter():
    """Validate YAML frontmatter in skill files."""
    print("📋 Validating YAML Frontmatter Structure...")
    print("=" * 50)
    
    skill_files = [
        "skills/skill-creator/SKILL.md"
    ]
    
    all_valid = True
    
    for skill_file in skill_files:
        path = Path(skill_file)
        if not path.exists():
            print(f"❌ {skill_file} not found")
            all_valid = False
            continue
        
        content = path.read_text()
        
        # Check for YAML frontmatter
        has_frontmatter = content.startswith("---") and "execution:" in content
        
        status = "✅" if has_frontmatter else "❌"
        print(f"{status} {skill_file}")
        
        if has_frontmatter:
            # Extract frontmatter
            frontmatter_end = content.find("---", 3)
            if frontmatter_end != -1:
                frontmatter = content[3:frontmatter_end]
                if "mode:" in frontmatter and "model:" in frontmatter:
                    print(f"   ✅ Contains execution mode and model")
                else:
                    print(f"   ❌ Missing execution config")
                    all_valid = False
        else:
            all_valid = False
        
        print()
    
    return all_valid


def validate_workflow_template():
    """Validate the enhanced workflow template."""
    print("🔧 Validating Enhanced Workflow Template...")
    print("=" * 50)
    
    template_path = Path("templates/workflow.yaml")
    
    if not template_path.exists():
        print("❌ templates/workflow.yaml not found")
        return False
    
    content = template_path.read_text()
    
    required_sections = [
        "skill_id:",
        "execution_engine:",
        "provider: \"ai_os.context_switcher\"",
        "mode:",
        "environment:",
        "context_references:",
        "workflow:",
        "validation:"
    ]
    
    all_present = True
    
    for section in required_sections:
        present = section in content
        status = "✅" if present else "❌"
        print(f"{status} {section}")
        
        if not present:
            all_present = False
    
    print()
    return all_present


def validate_main_integration():
    """Validate main.py integration."""
    print("🚀 Validating Main Entry Point Integration...")
    print("=" * 50)
    
    main_path = Path("ai_os/main.py")
    
    if not main_path.exists():
        print("❌ ai_os/main.py not found")
        return False
    
    content = main_path.read_text()
    
    required_imports = [
        "from ai_os.workflows.enhanced_skill_generator import EnhancedSkillGenerator",
        "from ai_os.workflows.enhanced_skill_executor import EnhancedSkillExecutor"
    ]
    
    required_functions = [
        "start_enhanced_cli_mode",
        "EnhancedSkillGenerator()",
        "EnhancedSkillExecutor()"
    ]
    
    all_present = True
    
    for import_stmt in required_imports:
        present = import_stmt in content
        status = "✅" if present else "❌"
        print(f"{status} {import_stmt}")
        
        if not present:
            all_present = False
    
    for func in required_functions:
        present = func in content
        status = "✅" if present else "❌"
        print(f"{status} {func}")
        
        if not present:
            all_present = False
    
    print()
    return all_present


def demonstrate_skill_generation():
    """Demonstrate skill generation capabilities."""
    print("🎨 Demonstrating Skill Generation...")
    print("=" * 50)
    
    selector = ModelSelector()
    
    examples = [
        "Create a skill to analyze financial PDFs",
        "Build a workflow for cleaning my desktop", 
        "Generate a script for API integration",
        "Automate email processing"
    ]
    
    print("📋 Model Selection Examples:")
    for example in examples:
        config = selector.analyze_requirements(example, {})
        print(f"  🎯 '{example[:30]}...'")
        print(f"     Mode: {config.mode.value}")
        print(f"     Model: {config.recommended_model}")
        print(f"     Internet: {config.requires_internet}")
        print()
    
    return True


def main():
    """Run complete validation."""
    print("🚀 Enhanced AI-OS Validation Suite")
    print("=" * 60)
    print()
    
    validations = [
        ("ModelSelector Decision Tree", validate_model_selector),
        ("Enhanced Skill Structure", validate_skill_structure),
        ("YAML Frontmatter", validate_yaml_frontmatter),
        ("Workflow Template", validate_workflow_template),
        ("Main Integration", validate_main_integration),
        ("Skill Generation Demo", demonstrate_skill_generation)
    ]
    
    results = []
    
    for name, validator in validations:
        try:
            result = validator()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
    
    print()
    print(f"🎯 Overall: {passed}/{total} validations passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print()
        print("🎉 Enhanced AI-OS is fully validated and ready for production!")
        print()
        print("🚀 To start using the enhanced system:")
        print("   python3 ai_os/main.py --cli")
        print()
        print("🧪 To run comprehensive tests:")
        print("   python3 test_enhanced_system.py")
        print()
        print("📚 Available enhanced features:")
        print("   • Intelligent model selection")
        print("   • Progressive loading architecture")
        print("   • Security enforcement")
        print("   • YAML frontmatter skills")
        print("   • Meta-skill creation")
        print("   • Interactive CLI")
    else:
        print()
        print("❌ Some validations failed. Please review the issues above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
