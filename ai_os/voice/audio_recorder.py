import sounddevice as sd
import soundfile as sf
import numpy as np
import uuid
from pathlib import Path

class AudioRecorder:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.sample_rate = 16000 # Standard for Whisper
        self.channels = 1
        self.recording = False
        self.audio_data = []

    def start_recording(self):
        """Starts capturing audio stream"""
        self.recording = True
        self.audio_data = []
        
        # Define callback
        def callback(indata, frames, time, status):
            if self.recording:
                self.audio_data.append(indata.copy())
                
        # Start stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, 
            channels=self.channels, 
            callback=callback
        )
        self.stream.start()
        return self._get_current_filepath()

    def stop_recording(self):
        """Stops stream and saves file"""
        self.recording = False
        self.stream.stop()
        self.stream.close()
        
        # Save to file
        if not self.audio_data:
            return None
            
        file_path = self._get_current_filepath()
        audio_concatenated = np.concatenate(self.audio_data, axis=0)
        sf.write(file_path, audio_concatenated, self.sample_rate)
        return file_path

    def _get_current_filepath(self):
        return self.output_dir / "current_command.wav"
