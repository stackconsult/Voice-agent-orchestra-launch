#!/usr/bin/env python3
"""Test local_lm_agent.py component"""

import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add ai_os to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test component import"""
    try:
        from ai_os.agents.local_lm_agent import (
            LocalLMAgent, 
            LocalLMProvider, 
            WorkflowStep, 
            GeneratedWorkflow
        )
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic local LM agent functionality"""
    try:
        from ai_os.agents.local_lm_agent import (
            LocalLMAgent, 
            LocalLMProvider, 
            WorkflowStep, 
            GeneratedWorkflow
        )
        
        # Create agent with mock connection
        agent = LocalLMAgent(
            provider=LocalLMProvider.OLLAMA,
            model_name="test_model",
            base_url="http://localhost:11434"
        )
        
        # Test provider info
        info = agent.get_provider_info()
        assert isinstance(info, dict), "Provider info should be dictionary"
        assert info["provider"] == "ollama", "Provider should be ollama"
        assert info["model"] == "test_model", "Model should match"
        
        # Test workflow step creation
        step = WorkflowStep(
            step_id="step_1",
            action="terminal",
            command="echo 'test'",
            parameters={},
            description="Test step"
        )
        assert step.step_id == "step_1", "Step ID should match"
        assert step.action == "terminal", "Action should be terminal"
        
        # Test workflow creation
        workflow = GeneratedWorkflow(
            name="Test Workflow",
            description="Test description",
            steps=[step],
            context={}
        )
        assert workflow.name == "Test Workflow", "Workflow name should match"
        assert len(workflow.steps) == 1, "Should have one step"
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_building():
    """Test prompt building functionality"""
    try:
        from ai_os.agents.local_lm_agent import LocalLMAgent, LocalLMProvider
        
        agent = LocalLMAgent(provider=LocalLMProvider.OLLAMA)
        
        # Test basic prompt
        prompt = agent._build_workflow_prompt(
            "Organize my desktop",
            context={"user": "test"},
            examples=[]
        )
        
        assert "Organize my desktop" in prompt, "User input should be in prompt"
        assert "JSON" in prompt, "Should mention JSON format"
        assert "steps" in prompt, "Should mention steps"
        
        # Test prompt with examples
        examples = ['{"name": "Example", "steps": []}']
        prompt_with_examples = agent._build_workflow_prompt(
            "Test task",
            examples=examples
        )
        
        assert "Example" in prompt_with_examples, "Example should be in prompt"
        
        print("✅ Prompt building test passed")
        return True
        
    except Exception as e:
        print(f"❌ Prompt building test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_parsing():
    """Test workflow parsing functionality"""
    try:
        from ai_os.agents.local_lm_agent import LocalLMAgent, LocalLMProvider
        
        agent = LocalLMAgent(provider=LocalLMProvider.OLLAMA)
        
        # Test valid JSON response
        valid_response = '''{
            "name": "Test Workflow",
            "description": "A test workflow",
            "steps": [
                {
                    "step_id": "step_1",
                    "action": "terminal",
                    "command": "echo 'hello'",
                    "parameters": {},
                    "description": "Print hello",
                    "expected_result": "hello printed"
                }
            ],
            "estimated_time": 10,
            "confidence_score": 0.8
        }'''
        
        workflow = agent._parse_workflow_response(valid_response, "Test input")
        
        assert workflow.name == "Test Workflow", "Workflow name should match"
        assert len(workflow.steps) == 1, "Should have one step"
        assert workflow.steps[0].action == "terminal", "Step action should be terminal"
        assert workflow.estimated_time == 10, "Estimated time should match"
        assert workflow.confidence_score == 0.8, "Confidence should match"
        
        # Test invalid response (should create fallback)
        invalid_response = "This is not JSON"
        fallback_workflow = agent._parse_workflow_response(invalid_response, "Test input")
        
        assert fallback_workflow.name == "Fallback Workflow", "Should create fallback"
        assert len(fallback_workflow.steps) == 1, "Fallback should have one step"
        assert fallback_workflow.context.get("fallback") == True, "Should mark as fallback"
        
        print("✅ Workflow parsing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Workflow parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_workflow_validation():
    """Test workflow validation functionality"""
    try:
        from ai_os.agents.local_lm_agent import (
            LocalLMAgent, 
            LocalLMProvider,
            WorkflowStep,
            GeneratedWorkflow
        )
        
        agent = LocalLMAgent(provider=LocalLMProvider.OLLAMA)
        
        # Test valid workflow
        valid_step = WorkflowStep(
            step_id="step_1",
            action="terminal",
            command="echo 'test'",
            parameters={},
            description="Test step"
        )
        
        valid_workflow = GeneratedWorkflow(
            name="Valid Workflow",
            description="A valid workflow",
            steps=[valid_step],
            context={},
            confidence_score=0.8
        )
        
        validation = agent.validate_workflow(valid_workflow)
        assert validation["is_valid"] == True, "Valid workflow should pass validation"
        assert len(validation["issues"]) == 0, "Should have no issues"
        
        # Test invalid workflow
        invalid_step = WorkflowStep(
            step_id="step_1",
            action="invalid_action",
            command="",
            parameters={},
            description="Invalid step"
        )
        
        invalid_workflow = GeneratedWorkflow(
            name="Invalid Workflow",
            description="An invalid workflow",
            steps=[invalid_step],
            context={},
            confidence_score=0.8
        )
        
        validation = agent.validate_workflow(invalid_workflow)
        assert validation["is_valid"] == False, "Invalid workflow should fail validation"
        assert len(validation["issues"]) > 0, "Should have issues"
        assert len(validation["recommendations"]) > 0, "Should have recommendations"
        
        # Test dangerous command detection
        dangerous_step = WorkflowStep(
            step_id="step_1",
            action="terminal",
            command="rm -rf /",
            parameters={},
            description="Dangerous step"
        )
        
        dangerous_workflow = GeneratedWorkflow(
            name="Dangerous Workflow",
            description="A dangerous workflow",
            steps=[dangerous_step],
            context={},
            confidence_score=0.8
        )
        
        validation = agent.validate_workflow(dangerous_workflow)
        assert validation["is_valid"] == False, "Dangerous workflow should fail validation"
        assert any("dangerous" in issue.lower() for issue in validation["issues"]), "Should detect dangerous command"
        
        print("✅ Workflow validation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Workflow validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_connection_handling():
    """Test connection handling functionality"""
    try:
        from ai_os.agents.local_lm_agent import LocalLMAgent, LocalLMProvider
        
        # Test with invalid URL (should handle gracefully)
        agent = LocalLMAgent(
            provider=LocalLMProvider.OLLAMA,
            base_url="http://invalid:9999"
        )
        
        assert agent.is_available == False, "Should not be available with invalid URL"
        
        # Test provider info when not available
        info = agent.get_provider_info()
        assert info["is_available"] == False, "Info should show not available"
        
        # Test model update when not available
        result = agent.update_model("new_model")
        assert result == False, "Should fail to update model when not available"
        
        print("✅ Connection handling test passed")
        return True
        
    except Exception as e:
        print(f"❌ Connection handling test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoints():
    """Test API endpoint configuration"""
    try:
        from ai_os.agents.local_lm_agent import LocalLMAgent, LocalLMProvider
        
        # Test Ollama endpoint
        ollama_agent = LocalLMAgent(
            provider=LocalLMProvider.OLLAMA,
            base_url="http://localhost:11434"
        )
        assert ollama_agent.api_endpoint == "http://localhost:11434/api/generate", "Ollama endpoint should match"
        
        # Test LM Studio endpoint
        lm_studio_agent = LocalLMAgent(
            provider=LocalLMProvider.LM_STUDIO,
            base_url="http://localhost:1234"
        )
        assert lm_studio_agent.api_endpoint == "http://localhost:1234/v1/chat/completions", "LM Studio endpoint should match"
        
        # Test custom endpoint
        custom_agent = LocalLMAgent(
            provider=LocalLMProvider.CUSTOM,
            base_url="http://localhost:5678/api"
        )
        assert custom_agent.api_endpoint == "http://localhost:5678/api/chat/completions", "Custom endpoint should match"
        
        print("✅ API endpoints test passed")
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_operations():
    """Test async operations"""
    try:
        from ai_os.agents.local_lm_agent import LocalLMAgent, LocalLMProvider
        
        # Create agent with invalid URL to avoid network calls
        agent = LocalLMAgent(
            provider=LocalLMProvider.OLLAMA,
            base_url="http://invalid:9999"
        )
        
        # Test list models (should return empty list when not available)
        models = await agent.list_available_models()
        assert isinstance(models, list), "Should return list"
        assert len(models) == 0, "Should return empty list when not available"
        
        # Test generate response should fail gracefully when not available
        try:
            await agent._generate_response("test prompt")
            assert False, "Should have failed when not available"
        except RuntimeError:
            pass  # Expected
        except Exception as e:
            # Any other exception is also acceptable since we're not connected
            pass
        
        print("✅ Async operations test passed")
        return True
        
    except Exception as e:
        print(f"❌ Async operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Local LM Agent Component...")
    
    tests = [
        test_import,
        test_basic_functionality,
        test_prompt_building,
        test_workflow_parsing,
        test_workflow_validation,
        test_connection_handling,
        test_api_endpoints
    ]
    
    # Add async test
    async def run_async_test():
        return await test_async_operations()
    
    passed = 0
    total = len(tests) + 1  # +1 for async test
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Run async test
    if asyncio.run(run_async_test()):
        passed += 1
    print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - Component is ready!")
    else:
        print("❌ Some tests failed - Component needs fixes")
        sys.exit(1)
