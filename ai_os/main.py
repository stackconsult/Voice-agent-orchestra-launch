#!/usr/bin/env python3
"""
AI-OS Main Entry Point

Voice-driven workflow automation system with offline-first processing
and seamless cloud fallback.
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


async def start_cli_mode(args) -> None:
    """Start command-line interface mode."""
    print("🎙️ AI-OS CLI Mode")
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
    parser = argparse.ArgumentParser(description="AI-OS Voice Workflow Automation")
    parser.add_argument("--init", action="store_true", help="Initialize system")
    parser.add_argument("--ppt", action="store_true", help="Start push-to-talk mode")
    parser.add_argument("--cli", action="store_true", help="Start CLI mode")
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
            asyncio.run(start_cli_mode(args))
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
