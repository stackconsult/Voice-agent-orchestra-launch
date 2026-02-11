import os
try:
    from faster_whisper import WhisperModel
except ImportError:
    print("⚠️ faster_whisper not found. Install with: pip install faster-whisper")
    WhisperModel = None

class LocalTranscriber:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        """
        device="cpu" is safe for Intel Macs. 
        compute_type="int8" is optimized for CPU inference.
        """
        self.model_size = model_size
        print(f"⏳ Loading Whisper model ({model_size})...")
        if WhisperModel:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            print("✅ Whisper model loaded.")
        else:
            self.model = None

    def transcribe(self, audio_path):
        if not self.model:
            return "Error: Transcriber not initialized"
            
        segments, info = self.model.transcribe(str(audio_path), beam_size=5)
        
        text = ""
        for segment in segments:
            text += segment.text + " "
            
        return text.strip()
