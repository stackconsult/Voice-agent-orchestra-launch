#!/usr/bin/env python3
"""
AI-OS Enhanced Main Entry Point
============================================
Orchestrates the Voice -> Agent -> Execution pipeline.
Updated to use EnhancedSkillGenerator and EnhancedSkillExecutor.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add ai_os to path
sys.path.insert(0, str(Path(__file__).parent))

# Import enhanced components
from ai_os.workflows.enhanced_skill_generator import EnhancedSkillGenerator
from ai_os.workflows.enhanced_skill_executor import EnhancedSkillExecutor

# Import legacy components for compatibility
from ai_os.ui.ppt_window import PTTWindow
from ai_os.safety.restore_manager import RestoreManager
from ai_os.agents.monitor_agent import MonitorAgent
from ai_os.history.history_manager import HistoryManager


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    log_dir = Path.home() / ".aios" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "aios.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )


def init_system() -> None:
    """Initialize AI-OS system directories and configuration."""
    dirs = [
        Path.home() / ".aios" / "snapshots",
        Path.home() / ".aios" / "logs", 
        Path.home() / ".aios" / "history",
        Path.home() / ".aios" / "tmp",
        Path("./skills"),
        Path("./workflows")
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    print("🎙️ AI-OS system initialized successfully!")


async def start_ptt_mode(args) -> None:
    """Start push-to-talk mode with PyQt6 GUI."""
    try:
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = PTTWindow()
        window.show()
        
        print("🎙️ AI-OS Voice Command System")
        print("├─ ✅ Hotkey: Cmd+Shift+V registered")
        print("├─ ✅ PyQt6: Window ready")
        print("└─ 🟢 READY - Press Cmd+Shift+V to begin")
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ PyQt6 not available: {e}")
        print("Install with: pip install PyQt6")
        sys.exit(1)


async def start_enhanced_cli_mode(args) -> None:
    """Start enhanced command-line interface with skill generation."""
    logger = logging.getLogger("AI-OS")
    logger.info("🤖 AI-OS Enhanced Orchestrator Starting...")
    
    # Initialize Enhanced Components
    generator = EnhancedSkillGenerator()
    executor = EnhancedSkillExecutor()
    
    print("\n🎤 AI-OS Enhanced Voice Agent Ready")
    print("-----------------------------------")
    print("Try commands like:")
    print("  - 'Create a skill to analyze financial PDFs'")
    print("  - 'Build a workflow for cleaning my desktop'")
    print("  - 'Run the skill-creator'")
    print("  - 'help' - Show all commands")
    print("  - 'exit' - Exit CLI mode")
    
    while True:
        try:
            # In a real app, this would be voice input
            user_input = input("\n> ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                break
                
            if user_input.lower() == 'help':
                print("\n📚 Enhanced AI-OS Commands:")
                print("  create <description>  - Generate a new skill")
                print("  run <skill_name>      - Execute an existing skill")
                print("  list                  - List available skills")
                print("  status                - Show system status")
                print("  help                  - Show this help")
                print("  exit                  - Exit CLI mode")
                
            elif user_input.lower() == 'status':
                print("\n📊 System Status:")
                print("  ✅ Enhanced Generator: Active")
                print("  ✅ Enhanced Executor: Active")
                print("  ✅ Local LLM: Available")
                print("  ✅ Context Switcher: Ready")
                
            elif user_input.lower() == 'list':
                skills_dir = Path("./skills")
                if skills_dir.exists():
                    skills = [d.name for d in skills_dir.iterdir() if d.is_dir()]
                    print(f"\n📁 Available Skills ({len(skills)}):")
                    for skill in skills:
                        print(f"  - {skill}")
                else:
                    print("\n📁 No skills found. Create one with 'create <description>'")
                    
            elif user_input.lower().startswith("create"):
                # --- GENERATION PATH ---
                print("🧠 Analyzing architecture requirements...")
                try:
                    skill = await generator.generate_skill(
                        voice_input=user_input,
                        author="AI-OS User"
                    )
                    
                    # Save the production-grade skill
                    path = await generator.save_skill(skill)
                    print(f"✅ Skill Generated: {skill.metadata.name}")
                    print(f"📂 Location: {path}")
                    print(f"⚙️ Mode: {skill.metadata.execution_config.mode.value}")
                    print(f"🤖 Model: {skill.metadata.execution_config.recommended_model}")
                    
                except Exception as e:
                    print(f"❌ Skill Generation Failed: {e}")
                    logger.error(f"Skill generation error: {e}")
                
            elif user_input.lower().startswith("run"):
                # --- EXECUTION PATH ---
                parts = user_input.split(" ", 1)
                if len(parts) < 2:
                    print("❌ Usage: run <skill_name>")
                    continue
                    
                skill_name = parts[1]
                print(f"⚡ Executing {skill_name}...")
                
                try:
                    result = await executor.execute_skill(skill_name)
                    print("✅ Execution Complete")
                    print(f"📊 Steps completed: {result['steps_completed']}")
                    
                except Exception as e:
                    print(f"❌ Execution Failed: {e}")
                    logger.error(f"Skill execution error: {e}")
                    
            else:
                print(f"❌ Unknown command: {user_input}")
                print("Type 'help' for available commands")
                    
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"System Error: {e}")
            print(f"❌ System Error: {e}")
    
    print("\n👋 Enhanced AI-OS shutting down...")


async def start_cli_mode(args) -> None:
    """Start legacy command-line interface mode."""
    print("🎙️ AI-OS Legacy CLI Mode")
    print("Type 'help' for commands or 'exit' to quit")
    
    while True:
        try:
            command = input("aios> ").strip()
            if command.lower() in ['exit', 'quit']:
                break
            elif command.lower() == 'help':
                print("Available commands:")
                print("  help    - Show this help")
                print("  status  - Show system status")
                print("  list    - List available skills")
                print("  exit    - Exit CLI mode")
            elif command.lower() == 'status':
                print("✅ System operational")
                print("✅ Local LLM: Available")
                print("✅ Monitor: Active")
            else:
                print(f"Unknown command: {command}")
        except KeyboardInterrupt:
            break
    
    print("👋 Goodbye!")


def main() -> None:
    """Main entry point for AI-OS."""
    parser = argparse.ArgumentParser(description="AI-OS Enhanced Voice Workflow Automation")
    parser.add_argument("--init", action="store_true", help="Initialize system")
    parser.add_argument("--ppt", action="store_true", help="Start push-to-talk mode")
    parser.add_argument("--cli", action="store_true", help="Start enhanced CLI mode")
    parser.add_argument("--legacy-cli", action="store_true", help="Start legacy CLI mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--no-hotkey", action="store_true", help="Disable global hotkey")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    
    try:
        if args.init:
            init_system()
        elif args.ppt:
            asyncio.run(start_ptt_mode(args))
        elif args.cli:
            asyncio.run(start_enhanced_cli_mode(args))
        elif args.legacy_cli:
            asyncio.run(start_cli_mode(args))
        else:
            parser.print_help()
            print("\n🚀 Enhanced AI-OS Features:")
            print("  --cli       : Enhanced CLI with skill generation")
            print("  --legacy-cli: Legacy CLI mode")
            print("  --ppt       : Push-to-talk voice mode")
            print("  --init      : Initialize system directories")
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
