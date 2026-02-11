"""
Voice Activator Components
==========================

This package contains the voice-activated components for the Enhanced AI-OS:
- VoiceManager: Central coordinator for voice interactions
- AudioRecorder: Handles microphone recording
- LocalTranscriber: Offline speech-to-text processing
- VoiceOverlay: Visual feedback interface
"""

from .voice_manager import VoiceManager
from .audio_recorder import AudioRecorder
from .transcriber import LocalTranscriber
from .overlay_ui import VoiceOverlay

__all__ = ['VoiceManager', 'AudioRecorder', 'LocalTranscriber', 'VoiceOverlay']
