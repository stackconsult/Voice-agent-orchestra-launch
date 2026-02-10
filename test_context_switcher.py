#!/usr/bin/env python3
"""Test offline_online_context_switcher.py component"""

import sys
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add ai_os to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test component import"""
    try:
        from ai_os.agents.offline_online_context_switcher import (
            ContextSwitcher,
            ProcessingMode,
            CloudProvider,
            ProcessingResult,
            CostTracking
        )
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic context switcher functionality"""
    try:
        from ai_os.agents.offline_online_context_switcher import (
            ContextSwitcher,
            ProcessingMode,
            CloudProvider
        )
        
        # Create switcher with default settings
        switcher = ContextSwitcher(
            processing_mode=ProcessingMode.LOCAL_FIRST,
            cost_budget=10.0
        )
        
        # Test initial status
        status = switcher.get_status()
        assert isinstance(status, dict), "Status should be dictionary"
        assert status["processing_mode"] == "local_first", "Processing mode should match"
        assert status["budget_status"]["budget"] == 10.0, "Budget should match"
        assert isinstance(status["local_available"], bool), "Local availability should be boolean"
        
        # Test mode switching
        switcher.switch_mode(ProcessingMode.CLOUD_ONLY)
        new_status = switcher.get_status()
        assert new_status["processing_mode"] == "cloud_only", "Mode should have switched"
        
        # Test budget update
        switcher.update_budget(20.0)
        updated_status = switcher.get_status()
        assert updated_status["budget_status"]["budget"] == 20.0, "Budget should have updated"
        
        # Test cost tracking reset
        switcher.reset_cost_tracking()
        reset_status = switcher.get_status()
        assert reset_status["cost_tracking"]["request_count"] == 0, "Request count should reset"
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cloud_config_loading():
    """Test cloud configuration loading"""
    try:
        from ai_os.agents.offline_online_context_switcher import ContextSwitcher, CloudProvider
        
        # Test with no environment variables
        with patch.dict(os.environ, {}, clear=True):
            switcher = ContextSwitcher(cloud_providers=[CloudProvider.OPENAI])
            configs = switcher.cloud_configs
            
            # Should have config structure but no API keys
            assert "openai" in configs, "Should have OpenAI config structure"
            assert configs["openai"]["api_key"] is None, "API key should be None when not set"
        
        # Test with environment variables
        with patch.dict(os.environ, {
            "OPENAI_API_KEY": "test-key",
            "ANTHROPIC_API_KEY": "test-key",
            "OPENAI_MODEL": "gpt-4-turbo"
        }):
            switcher = ContextSwitcher(
                cloud_providers=[CloudProvider.OPENAI, CloudProvider.ANTHROPIC]
            )
            configs = switcher.cloud_configs
            
            assert configs["openai"]["api_key"] == "test-key", "Should load OpenAI API key"
            assert configs["anthropic"]["api_key"] == "test-key", "Should load Anthropic API key"
            assert configs["openai"]["model"] == "gpt-4-turbo", "Should load custom model"
        
        print("✅ Cloud config loading test passed")
        return True
        
    except Exception as e:
        print(f"❌ Cloud config loading test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_processing_result():
    """Test processing result dataclass"""
    try:
        from ai_os.agents.offline_online_context_switcher import ProcessingResult
        
        result = ProcessingResult(
            content="test content",
            provider="local",
            model="test-model",
            processing_time=1.5,
            cost_estimate=0.0,
            confidence=0.8,
            metadata={"test": "data"}
        )
        
        assert result.content == "test content", "Content should match"
        assert result.provider == "local", "Provider should match"
        assert result.processing_time == 1.5, "Processing time should match"
        assert result.cost_estimate == 0.0, "Cost estimate should match"
        assert result.confidence == 0.8, "Confidence should match"
        assert result.metadata["test"] == "data", "Metadata should match"
        
        print("✅ Processing result test passed")
        return True
        
    except Exception as e:
        print(f"❌ Processing result test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cost_tracking():
    """Test cost tracking functionality"""
    try:
        from ai_os.agents.offline_online_context_switcher import CostTracking
        
        tracking = CostTracking(
            total_cost=5.0,
            local_cost=0.0,
            cloud_cost=5.0,
            request_count=10,
            fallback_count=2
        )
        
        assert tracking.total_cost == 5.0, "Total cost should match"
        assert tracking.cloud_cost == 5.0, "Cloud cost should match"
        assert tracking.local_cost == 0.0, "Local cost should match"
        assert tracking.request_count == 10, "Request count should match"
        assert tracking.fallback_count == 2, "Fallback count should match"
        
        # Test fallback rate calculation
        fallback_rate = tracking.fallback_count / max(1, tracking.request_count)
        assert fallback_rate == 0.2, "Fallback rate should be 0.2"
        
        print("✅ Cost tracking test passed")
        return True
        
    except Exception as e:
        print(f"❌ Cost tracking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_local_processing():
    """Test local processing functionality"""
    try:
        from ai_os.agents.offline_online_context_switcher import (
            ContextSwitcher,
            ProcessingMode
        )
        
        # Create switcher with invalid local URL to force failure
        switcher = ContextSwitcher(
            processing_mode=ProcessingMode.LOCAL_ONLY,
            cost_budget=10.0
        )
        
        # Test local processing when not available (should fail gracefully)
        try:
            result = await switcher.generate_workflow("test input")
            # If it succeeds, that's fine too (maybe local is available)
            assert isinstance(result, ProcessingResult), "Should return ProcessingResult"
        except RuntimeError as e:
            # Expected when local is not available
            assert "not available" in str(e) or "failed" in str(e).lower(), "Should fail gracefully"
        
        print("✅ Local processing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Local processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cloud_fallback():
    """Test cloud fallback functionality"""
    try:
        from ai_os.agents.offline_online_context_switcher import (
            ContextSwitcher,
            ProcessingMode
        )
        
        # Create switcher with no cloud credentials
        with patch.dict(os.environ, {}, clear=True):
            switcher = ContextSwitcher(
                processing_mode=ProcessingMode.LOCAL_FIRST,
                cost_budget=10.0
            )
        
        # Test workflow generation with no providers available
        try:
            result = await switcher.generate_workflow("test input")
            # If it succeeds, that's fine
            assert isinstance(result, ProcessingResult), "Should return ProcessingResult"
        except RuntimeError as e:
            # Expected when no providers are available
            assert "failed" in str(e).lower() or "exceeded" in str(e).lower(), "Should fail gracefully"
        
        print("✅ Cloud fallback test passed")
        return True
        
    except Exception as e:
        print(f"❌ Cloud fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_building():
    """Test cloud prompt building"""
    try:
        from ai_os.agents.offline_online_context_switcher import ContextSwitcher
        
        switcher = ContextSwitcher()
        
        # Test basic prompt
        prompt = switcher._build_cloud_prompt("Organize files", {"user": "test"})
        
        assert "Organize files" in prompt, "User input should be in prompt"
        assert "JSON" in prompt, "Should mention JSON format"
        assert "steps" in prompt, "Should mention steps"
        assert "test" in prompt, "Context should be in prompt"
        
        # Test prompt without context
        prompt_no_context = switcher._build_cloud_prompt("Test task", None)
        assert "Test task" in prompt_no_context, "User input should be in prompt"
        assert "Context:" not in prompt_no_context, "Should not mention context when None"
        
        print("✅ Prompt building test passed")
        return True
        
    except Exception as e:
        print(f"❌ Prompt building test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_budget_enforcement():
    """Test budget enforcement"""
    try:
        from ai_os.agents.offline_online_context_switcher import (
            ContextSwitcher,
            ProcessingMode
        )
        
        # Create switcher with zero budget
        switcher = ContextSwitcher(
            processing_mode=ProcessingMode.CLOUD_ONLY,
            cost_budget=0.0
        )
        
        # Manually set cost to exceed budget
        switcher.cost_tracking.total_cost = 1.0
        
        status = switcher.get_status()
        assert status["budget_status"]["remaining"] is None, "Should show None remaining when budget is 0"
        assert status["budget_status"]["spent"] == 1.0, "Should show amount spent"
        
        print("✅ Budget enforcement test passed")
        return True
        
    except Exception as e:
        print(f"❌ Budget enforcement test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_export():
    """Test usage data export"""
    try:
        from ai_os.agents.offline_online_context_switcher import ContextSwitcher
        
        switcher = ContextSwitcher()
        
        # Test export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            switcher.export_usage_data(temp_file)
            
            # Verify file was created and contains valid JSON
            assert temp_file.exists(), "Export file should exist"
            
            with open(temp_file, 'r') as f:
                data = f.read()
                import json
                parsed_data = json.loads(data)
                
                assert "timestamp" in parsed_data, "Should contain timestamp"
                assert "status" in parsed_data, "Should contain status"
                
        finally:
            # Clean up
            if temp_file.exists():
                temp_file.unlink()
        
        print("✅ Data export test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all tests including async ones"""
    tests = [
        test_import,
        test_basic_functionality,
        test_cloud_config_loading,
        test_processing_result,
        test_cost_tracking,
        test_prompt_building,
        test_budget_enforcement,
        test_data_export
    ]
    
    async_tests = [
        test_local_processing,
        test_cloud_fallback
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Run async tests
    for test in async_tests:
        if await test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - Component is ready!")
    else:
        print("❌ Some tests failed - Component needs fixes")
    
    return passed == total

if __name__ == "__main__":
    print("Testing Offline/Online Context Switcher Component...")
    
    success = asyncio.run(run_all_tests())
    
    if not success:
        sys.exit(1)
