import os
import threading
import queue
import time
from pathlib import Path
from ai_os.voice.audio_recorder import AudioRecorder
from ai_os.voice.transcriber import LocalTranscriber
from ai_os.voice.overlay_ui import VoiceOverlay
from ai_os.workflows.enhanced_skill_executor import EnhancedSkillExecutor
from ai_os.workflows.enhanced_skill_generator import EnhancedSkillGenerator

class VoiceManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.recorder = AudioRecorder(base_path / "tmp")
        self.transcriber = LocalTranscriber(model_size="base") # "tiny" or "base" for speed
        self.ui = VoiceOverlay()
        
        # Skill Engines
        self.executor = EnhancedSkillExecutor()
        self.generator = EnhancedSkillGenerator()
        
        self.is_processing = False
        
    def start_listening_loop(self):
        """Starts the UI event loop and hotkey listener"""
        print("🎙️ Voice System Online. Press Cmd+Shift+V to speak.")
        
        # Define the hotkey action
        def on_hotkey_trigger():
            if not self.is_processing:
                self.activate_voice_session()
        
        # Start Global Hotkey Listener (runs in background)
        # Note: We use pynput or keyboard depending on OS. 
        # For Mac (your setup), pynput is reliable.
        try:
            from pynput import keyboard
            
            # Hotkey: Cmd+Shift+V (Mac) or Ctrl+Shift+V (Win/Linux)
            # Adjust combination as needed
            with keyboard.GlobalHotKeys({
                '<cmd>+<shift>+v': on_hotkey_trigger
            }) as h:
                self.ui.run() # This blocks until UI closes
        except ImportError:
            print("❌ pynput not installed. Install with: pip install pynput")
            print("🔄 Falling back to manual input mode...")
            self.manual_fallback()
            
    def manual_fallback(self):
        """Fallback mode when hotkey library is not available"""
        print("🎙️ Manual voice activation mode")
        print("Press Enter to start recording, type 'quit' to exit")
        
        while True:
            user_input = input("\n> ").strip().lower()
            if user_input == 'quit':
                break
            elif user_input == '':
                if not self.is_processing:
                    self.activate_voice_session()
                    
    def activate_voice_session(self):
        """The core workflow when hotkey is pressed"""
        self.is_processing = True
        self.ui.show_state("listening")
        
        # 1. Record Audio
        audio_file = self.recorder.start_recording()
        
        # Wait for silence or stop trigger (simulated here with duration or key up)
        # For this v1, we record for fixed time or until silence is detected
        # In production, we'd wait for the hotkey release
        time.sleep(0.5) # Debounce
        
        # 2. Stop Recording (triggered by user action in real impl)
        # Here we simulate a "Push-to-Talk" release or Silence detection
        self.recorder.stop_recording()
        self.ui.show_state("processing")
        
        # 3. Transcribe (Offline)
        text = self.transcriber.transcribe(audio_file)
        print(f"🗣️ User said: {text}")
        
        if not text.strip():
            self.ui.show_state("error", "No speech detected")
            self.is_processing = False
            return

        # 4. Route to Engine
        self.route_command(text)
        
    def route_command(self, text: str):
        """Decides if this is a creation request or execution request"""
        text_lower = text.lower()
        
        # Check against Skill Creator triggers
        creation_triggers = ["create a skill", "build a skill", "new skill", "automate"]
        
        if any(trigger in text_lower for trigger in creation_triggers):
            self.ui.show_state("generating")
            # Call Generator
            result = self.generator.generate_skill_from_voice(text)
            self.ui.show_state("success", f"Created: {result.get('name')}")
        else:
            self.ui.show_state("executing")
            # Call Executor (Search for existing skill)
            result = self.executor.find_and_execute(text)
            self.ui.show_state("success", "Done")
            
        self.is_processing = False
        # UI will hide after a delay handled internally
