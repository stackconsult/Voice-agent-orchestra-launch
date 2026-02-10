#!/usr/bin/env python3
"""
Enhanced AI-OS System Test Suite
================================
Comprehensive tests for the enhanced skill generation and execution system.
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add project to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
from ai_os.workflows.enhanced_skill_generator import (
    EnhancedSkillGenerator,
    ModelSelector,
    ExecutionMode,
    ModelConfig,
    SkillMetadata,
    GeneratedSkill
)
from ai_os.workflows.enhanced_skill_executor import EnhancedSkillExecutor, SecurityViolationError


class TestModelSelector(unittest.TestCase):
    """Test the ModelSelector decision tree logic."""
    
    def setUp(self):
        self.selector = ModelSelector()
    
    def test_sensitive_data_forces_local(self):
        """Test that sensitive data forces local execution."""
        config = self.selector.analyze_requirements("Analyze financial reports with passwords", {})
        self.assertEqual(config.mode, ExecutionMode.LOCAL_ONLY)
        self.assertEqual(config.recommended_model, "llama3-local")
        self.assertFalse(config.requires_internet)
    
    def test_medical_data_forces_local(self):
        """Test that medical data forces local execution."""
        config = self.selector.analyze_requirements("Process medical patient records", {})
        self.assertEqual(config.mode, ExecutionMode.LOCAL_ONLY)
        self.assertFalse(config.requires_internet)
    
    def test_coding_requires_cloud(self):
        """Test that coding tasks prefer cloud models."""
        config = self.selector.analyze_requirements("Write a Python script for API integration", {})
        self.assertEqual(config.mode, ExecutionMode.CLOUD_PREFERRED)
        self.assertEqual(config.recommended_model, "claude-3-5-sonnet")
        self.assertTrue(config.requires_internet)
    
    def test_vision_requires_cloud(self):
        """Test that vision tasks prefer cloud models."""
        config = self.selector.analyze_requirements("Analyze screenshots and PDF charts", {})
        self.assertEqual(config.mode, ExecutionMode.CLOUD_PREFERRED)
        self.assertEqual(config.recommended_model, "gpt-4o")
        self.assertTrue(config.requires_internet)
    
    def test_complex_reasoning_requires_cloud(self):
        """Test that complex reasoning prefers cloud models."""
        config = self.selector.analyze_requirements("Create a strategic business analysis report", {})
        self.assertEqual(config.mode, ExecutionMode.CLOUD_PREFERRED)
        self.assertEqual(config.recommended_model, "claude-3-opus")
        self.assertTrue(config.requires_internet)
    
    def test_default_automation_uses_hybrid(self):
        """Test that basic automation uses hybrid mode."""
        config = self.selector.analyze_requirements("Automate file organization", {})
        self.assertEqual(config.mode, ExecutionMode.HYBRID)
        self.assertEqual(config.recommended_model, "llama3-local")
        self.assertTrue(config.requires_internet)


class TestEnhancedSkillGenerator(unittest.TestCase):
    """Test the EnhancedSkillGenerator functionality."""
    
    def setUp(self):
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        self.skills_dir = self.temp_dir / "skills"
        self.templates_dir = self.temp_dir / "templates"
        
        # Mock local LM agent
        self.mock_lm_agent = Mock()
        self.mock_lm_agent.generate_workflow = AsyncMock()
        
        # Create generator
        self.generator = EnhancedSkillGenerator(
            local_lm_agent=self.mock_lm_agent,
            skills_dir=self.skills_dir,
            template_dir=self.templates_dir
        )
    
    def tearDown(self):
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test generator initialization."""
        self.assertTrue(self.skills_dir.exists())
        self.assertTrue(self.templates_dir.exists())
        self.assertIsInstance(self.generator.model_selector, ModelSelector)
    
    def test_name_sanitization(self):
        """Test name sanitization."""
        test_cases = [
            ("Hello World!", "hello-world"),
            ("Test@#$%^&*()", "test"),
            ("  Multiple   Spaces  ", "multiple-spaces"),
            ("", "unnamed-skill")
        ]
        
        for input_name, expected in test_cases:
            result = self.generator._sanitize_name(input_name)
            self.assertEqual(result, expected)
    
    def test_category_detection(self):
        """Test category detection logic."""
        test_cases = [
            ("Automate file scripts", "automation"),
            ("Generate analysis report", "analysis"),
            "Write code for API",
            ("Create blog post", "creative"),
            ("Generic task", "automation")
        ]
        
        for description, expected in test_cases:
            result = self.generator._detect_category(description)
            self.assertEqual(result, expected)
    
    def test_dependency_detection(self):
        """Test dependency detection."""
        test_cases = [
            ("Use git to clone repository", ["git"]),
            ("Make HTTP requests with curl", ["curl", "git"]),
            ("Simple file operation", [])
        ]
        
        for description, expected in test_cases:
            result = self.generator._detect_dependencies(description)
            self.assertEqual(sorted(result), sorted(expected))
    
    def test_frontmatter_generation(self):
        """Test YAML frontmatter generation."""
        # Create test metadata
        model_config = ModelConfig(
            mode=ExecutionMode.HYBRID,
            recommended_model="llama3-local",
            requires_internet=True
        )
        
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill for automation",
            category="automation",
            tags=["test", "automation"],
            author="Test User",
            version="1.0.0",
            created_at="2024-01-01T00:00:00",
            dependencies=["git"],
            estimated_time=15,
            difficulty="beginner",
            execution_config=model_config,
            triggers=["run test-skill"],
            output_artifacts=["report.md"]
        )
        
        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.steps = [
            Mock(action="terminal", command="echo 'hello'", description="Print hello")
        ]
        
        # Generate frontmatter
        frontmatter = self.generator._generate_frontmatter_markdown(metadata, mock_workflow)
        
        # Verify YAML frontmatter exists
        self.assertIn("---", frontmatter)
        self.assertIn("name: test-skill", frontmatter)
        self.assertIn("execution:", frontmatter)
        self.assertIn("mode: hybrid", frontmatter)
        self.assertIn("model: llama3-local", frontmatter)
        
        # Verify content exists
        self.assertIn("# Test Skill", frontmatter)
        self.assertIn("## 📋 Overview", frontmatter)
    
    def test_workflow_yaml_generation(self):
        """Test workflow YAML generation."""
        # Create test metadata
        model_config = ModelConfig(
            mode=ExecutionMode.LOCAL_ONLY,
            recommended_model="llama3-local",
            requires_internet=False
        )
        
        metadata = SkillMetadata(
            name="test-skill",
            description="Test skill",
            category="automation",
            tags=["test"],
            author="Test",
            version="1.0.0",
            created_at="2024-01-01T00:00:00",
            dependencies=[],
            estimated_time=10,
            difficulty="beginner",
            execution_config=model_config
        )
        
        # Create mock workflow
        mock_workflow = Mock()
        mock_workflow.steps = [
            Mock(step_id="1", action="terminal", command="echo test", description="Test command")
        ]
        
        # Generate YAML
        yaml_content = self.generator._generate_workflow_yaml(metadata, mock_workflow)
        
        # Verify structure
        self.assertIn("skill_id: test-skill", yaml_content)
        self.assertIn("execution_engine:", yaml_content)
        self.assertIn("provider: ai_os.context_switcher", yaml_content)
        self.assertIn("mode: local_only", yaml_content)
        self.assertIn("environment:", yaml_content)
        self.assertIn("workflow:", yaml_content)
    
    @patch.object(EnhancedSkillGenerator, '_generate_frontmatter_markdown')
    @patch.object(EnhancedSkillGenerator, '_generate_workflow_yaml')
    async def test_skill_generation(self, mock_yaml, mock_markdown):
        """Test complete skill generation."""
        # Setup mocks
        mock_markdown.return_value = "# Test Skill\nContent here"
        mock_yaml.return_value = "skill_id: test"
        
        # Setup mock workflow
        mock_workflow = Mock()
        mock_workflow.name = "Test Skill"
        mock_workflow.description = "Test description"
        mock_workflow.estimated_time = 15
        mock_workflow.steps = []
        
        self.mock_lm_agent.generate_workflow.return_value = mock_workflow
        
        # Generate skill
        skill = await self.generator.generate_skill("Create a test automation", author="Test Author")
        
        # Verify results
        self.assertIsInstance(skill, GeneratedSkill)
        self.assertEqual(skill.metadata.name, "test-skill")
        self.assertEqual(skill.metadata.author, "Test Author")
        self.assertEqual(skill.metadata.execution_config.mode, ExecutionMode.HYBRID)
        
        # Verify LM agent was called
        self.mock_lm_agent.generate_workflow.assert_called_once()
    
    async def test_skill_saving(self):
        """Test skill saving to disk."""
        # Create test skill
        model_config = ModelConfig(
            mode=ExecutionMode.LOCAL_ONLY,
            recommended_model="llama3-local"
        )
        
        metadata = SkillMetadata(
            name="test-skill",
            description="Test",
            category="automation",
            tags=["test"],
            author="Test",
            version="1.0.0",
            created_at="2024-01-01T00:00:00",
            dependencies=[],
            estimated_time=10,
            difficulty="beginner",
            execution_config=model_config
        )
        
        mock_workflow = Mock()
        mock_workflow.name = "Test Skill"
        mock_workflow.description = "Test description"
        
        skill = GeneratedSkill(
            metadata=metadata,
            workflow=mock_workflow,
            skill_markdown="# Test Skill",
            workflow_yaml="skill_id: test",
            folder_structure={},
            examples=["Test example"]
        )
        
        # Save skill
        path = await self.generator.save_skill(skill)
        
        # Verify files created
        self.assertTrue(path.exists())
        self.assertTrue((path / "SKILL.md").exists())
        self.assertTrue((path / "workflow.yaml").exists())
        self.assertTrue((path / "examples").exists())
        self.assertTrue((path / "references").exists())
        self.assertTrue((path / "logs").exists())
        
        # Verify content
        skill_md_content = (path / "SKILL.md").read_text()
        self.assertIn("# Test Skill", skill_md_content)
        
        workflow_yaml_content = (path / "workflow.yaml").read_text()
        self.assertIn("skill_id: test", workflow_yaml_content)


class TestEnhancedSkillExecutor(unittest.TestCase):
    """Test the EnhancedSkillExecutor functionality."""
    
    def setUp(self):
        # Create temporary workspace
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_dir = self.temp_dir / "workspace"
        self.skills_dir = self.temp_dir / "skills"
        
        # Create executor
        self.executor = EnhancedSkillExecutor(workspace_dir=str(self.workspace_dir))
        
        # Create test skill
        self.test_skill_dir = self.skills_dir / "test-skill"
        self.test_skill_dir.mkdir(parents=True)
        
        # Create test workflow file
        self.workflow_content = """
skill_id: test-skill
version: 1.0.0
execution_engine:
  provider: ai_os.context_switcher
  mode: local_only
  recommended_model: llama3-local
  internet_access: false
environment:
  dependencies: []
  required_vars: []
  working_directory: "./workspace"
context_references: []
workflow:
  steps:
    - step_id: 1
      action: terminal
      command: echo "Hello World"
      description: Print hello message
validation:
  pre_flight: check_dependencies
  post_flight: verify_artifacts
"""
        
        (self.test_skill_dir / "workflow.yaml").write_text(self.workflow_content)
    
    def tearDown(self):
        # Clean up
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test executor initialization."""
        self.assertTrue(self.workspace_dir.exists())
        self.assertIsNotNone(self.executor.context_switcher)
    
    async def test_skill_execution(self):
        """Test skill execution."""
        # Execute skill
        result = await self.executor.execute_skill("test-skill")
        
        # Verify results
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["skill"], "test-skill")
        self.assertEqual(result["steps_completed"], 1)
        self.assertIn("final_context", result)
    
    async def test_security_enforcement(self):
        """Test security enforcement in local_only mode."""
        # Create skill with network command
        network_workflow = """
skill_id: network-test
version: 1.0.0
execution_engine:
  provider: ai_os.context_switcher
  mode: local_only
  recommended_model: llama3-local
  internet_access: false
environment:
  dependencies: []
  required_vars: []
  working_directory: "./workspace"
context_references: []
workflow:
  steps:
    - step_id: 1
      action: terminal
      command: curl http://example.com
      description: Try to access network
validation:
  pre_flight: check_dependencies
  post_flight: verify_artifacts
"""
        
        network_skill_dir = self.skills_dir / "network-test"
        network_skill_dir.mkdir(parents=True)
        (network_skill_dir / "workflow.yaml").write_text(network_workflow)
        
        # Should raise security violation
        with self.assertRaises(SecurityViolationError) as context:
            await self.executor.execute_skill("network-test")
        
        self.assertIn("blocked in LOCAL_ONLY mode", str(context.exception))
    
    async def test_missing_skill_error(self):
        """Test error handling for missing skills."""
        with self.assertRaises(FileNotFoundError) as context:
            await self.executor.execute_skill("nonexistent-skill")
        
        self.assertIn("not found", str(context.exception))


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete enhanced system."""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.skills_dir = self.temp_dir / "skills"
        self.templates_dir = self.temp_dir / "templates"
        
        # Mock LM agent
        self.mock_lm_agent = Mock()
        self.mock_lm_agent.generate_workflow = AsyncMock()
        
        # Setup mock workflow
        self.mock_workflow = Mock()
        self.mock_workflow.name = "Integration Test Skill"
        self.mock_workflow.description = "Test integration"
        self.mock_workflow.estimated_time = 10
        self.mock_workflow.steps = [
            Mock(step_id="1", action="terminal", command="echo 'Integration Test'", description="Test integration")
        ]
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    async def test_complete_skill_workflow(self):
        """Test complete workflow from generation to execution."""
        # Create generator
        generator = EnhancedSkillGenerator(
            local_lm_agent=self.mock_lm_agent,
            skills_dir=self.skills_dir,
            template_dir=self.templates_dir
        )
        
        self.mock_lm_agent.generate_workflow.return_value = self.mock_workflow
        
        # Generate skill
        skill = await generator.generate_skill("Create integration test skill", author="Test")
        
        # Save skill
        skill_path = await generator.save_skill(skill)
        
        # Create executor
        executor = EnhancedSkillExecutor()
        
        # Execute skill
        result = await executor.execute_skill(skill.metadata.name)
        
        # Verify complete workflow
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["steps_completed"], 1)
        self.assertTrue(skill_path.exists())
        self.assertTrue((skill_path / "SKILL.md").exists())
        self.assertTrue((skill_path / "workflow.yaml").exists())


def run_tests():
    """Run all tests."""
    print("🧪 Running Enhanced AI-OS Test Suite")
    print("=" * 50)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestModelSelector,
        TestEnhancedSkillGenerator,
        TestEnhancedSkillExecutor,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100)
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    # Run async tests
    async def run_async_tests():
        # Create test instances for async tests
        generator_test = TestEnhancedSkillGenerator()
        generator_test.setUp()
        
        executor_test = TestEnhancedSkillExecutor()
        executor_test.setUp()
        
        integration_test = TestIntegration()
        integration_test.setUp()
        
        try:
            # Run async tests
            await generator_test.test_skill_generation()
            await generator_test.test_skill_saving()
            await executor_test.test_skill_execution()
            await executor_test.test_security_enforcement()
            await integration_test.test_complete_skill_workflow()
            
            print("✅ All async tests passed!")
            
        finally:
            # Cleanup
            generator_test.tearDown()
            executor_test.tearDown()
            integration_test.tearDown()
    
    # Run all tests
    print("🚀 Starting Enhanced AI-OS Test Suite")
    
    # Run async tests first
    asyncio.run(run_async_tests())
    
    # Run synchronous tests
    success = run_tests()
    
    if success:
        print("\n🎉 All tests passed! Enhanced AI-OS is ready for deployment.")
    else:
        print("\n❌ Some tests failed. Please review and fix issues.")
    
    exit(0 if success else 1)
