#!/usr/bin/env python3
"""Test monitor_agent.py component"""

import sys
import asyncio
import tempfile
import shutil
from pathlib import Path

# Add ai_os to path
sys.path.insert(0, str(Path(__file__).parent))

def test_import():
    """Test component import"""
    try:
        from ai_os.agents.monitor_agent import MonitorAgent, EventType, Severity
        print("✅ Import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic monitor agent functionality"""
    try:
        from ai_os.agents.monitor_agent import MonitorAgent, EventType, Severity
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            
            # Initialize monitor agent
            monitor = MonitorAgent(log_dir=log_dir)
            
            # Test event logging
            monitor.log_event(
                EventType.INFO,
                Severity.INFO,
                "test_component",
                "Test message",
                {"test": "data"}
            )
            
            # Test skill execution logging
            monitor.log_skill_execution(
                "test_skill",
                "test_action",
                {"result": "success"},
                success=True
            )
            
            # Test API call logging
            monitor.log_api_call(
                "openai",
                "/chat/completions",
                {"model": "gpt-4"},
                {"response": "test"},
                success=True
            )
            
            # Test file operation logging
            monitor.log_file_operation(
                "write",
                "/tmp/test.txt",
                success=True
            )
            
            # Test event retrieval
            events = monitor.get_events()
            assert len(events) > 0, "No events found"
            
            # Test error detection
            test_error = Exception("test error")
            is_critical = monitor.detect_critical_failure(
                test_error,
                {"context": "test"}
            )
            assert isinstance(is_critical, bool), "Critical failure detection should return boolean"
            
            # Test error summary
            summary = monitor.get_error_summary()
            assert isinstance(summary, dict), "Error summary should be dictionary"
            
            print("✅ Basic functionality test passed")
            return True
            
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_monitoring_start_stop():
    """Test monitoring start/stop functionality"""
    try:
        from ai_os.agents.monitor_agent import MonitorAgent
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            monitor = MonitorAgent(log_dir=log_dir)
            
            # Test start monitoring
            monitor.start_monitoring("test_execution")
            assert monitor.monitoring_active == True, "Monitoring should be active"
            assert monitor.current_execution_id == "test_execution", "Execution ID should be set"
            
            # Test stop monitoring
            monitor.stop_monitoring()
            assert monitor.monitoring_active == False, "Monitoring should be stopped"
            
            print("✅ Monitoring start/stop test passed")
            return True
            
    except Exception as e:
        print(f"❌ Monitoring start/stop test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_resource_monitoring():
    """Test resource monitoring functionality"""
    try:
        from ai_os.agents.monitor_agent import ResourceMonitor
        
        # Test resource monitor
        resource_monitor = ResourceMonitor()
        usage = resource_monitor.get_current_usage()
        
        assert isinstance(usage, dict), "Resource usage should be dictionary"
        assert "cpu_percent" in usage, "CPU percent should be in usage"
        assert "memory_mb" in usage, "Memory usage should be in usage"
        
        print("✅ Resource monitoring test passed")
        return True
        
    except Exception as e:
        print(f"❌ Resource monitoring test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_event_filtering():
    """Test event filtering functionality"""
    try:
        from ai_os.agents.monitor_agent import MonitorAgent, EventType, Severity
        
        with tempfile.TemporaryDirectory() as temp_dir:
            log_dir = Path(temp_dir) / "logs"
            monitor = MonitorAgent(log_dir=log_dir)
            
            # Add test events
            monitor.log_event(EventType.INFO, Severity.INFO, "comp1", "msg1", {})
            monitor.log_event(EventType.ERROR, Severity.HIGH, "comp1", "msg2", {})
            monitor.log_event(EventType.INFO, Severity.LOW, "comp2", "msg3", {})
            
            # Test filtering by event type
            info_events = monitor.get_events(event_type=EventType.INFO)
            assert len(info_events) == 2, f"Expected 2 info events, got {len(info_events)}"
            
            # Test filtering by component
            comp1_events = monitor.get_events(component="comp1")
            assert len(comp1_events) == 2, f"Expected 2 comp1 events, got {len(comp1_events)}"
            
            # Test filtering by severity
            high_events = monitor.get_events(severity=Severity.HIGH)
            assert len(high_events) == 1, f"Expected 1 high severity event, got {len(high_events)}"
            
            print("✅ Event filtering test passed")
            return True
            
    except Exception as e:
        print(f"❌ Event filtering test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Monitor Agent Component...")
    
    tests = [
        test_import,
        test_basic_functionality,
        test_monitoring_start_stop,
        test_resource_monitoring,
        test_event_filtering
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - Component is ready!")
    else:
        print("❌ Some tests failed - Component needs fixes")
        sys.exit(1)
