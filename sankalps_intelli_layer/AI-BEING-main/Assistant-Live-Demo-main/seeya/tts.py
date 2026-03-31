import pyttsx3
import threading
import time
import platform
import os

class TTSEngine:
    """Text-to-Speech engine with error handling and configuration options."""
    
    def __init__(self):
        self.engine = None
        self.is_speaking = False
        self._pause_ms = 120
        self._chunk_size = 180
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the TTS engine with error handling."""
        try:
            self.engine = pyttsx3.init()
            self._configure_engine()
            print("TTS Engine initialized successfully")
        except Exception as e:
            print(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _configure_engine(self):
        """Configure TTS engine properties."""
        if not self.engine:
            return
            
        try:
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 165)
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 1.0)
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Try to set a preferred voice (usually the first one is good)
                self.engine.setProperty('voice', voices[0].id)
                
        except Exception as e:
            print(f"Error configuring TTS engine: {e}")
    
    def get_available_voices(self):
        """Get list of available voices."""
        if not self.engine:
            return []
            
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            for voice in voices:
                voice_info = {
                    'id': voice.id,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                }
                voice_list.append(voice_info)
            return voice_list
        except Exception as e:
            print(f"Error getting voices: {e}")
            return []
    
    def set_voice(self, voice_id):
        """Set the voice by ID."""
        if not self.engine:
            return False
            
        try:
            self.engine.setProperty('voice', voice_id)
            return True
        except Exception as e:
            print(f"Error setting voice: {e}")
            return False
    
    def set_rate(self, rate):
        """Set speech rate (words per minute)."""
        if not self.engine:
            return False
            
        try:
            # Clamp rate between reasonable bounds
            rate = max(50, min(300, rate))
            self.engine.setProperty('rate', rate)
            return True
        except Exception as e:
            print(f"Error setting rate: {e}")
            return False
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)."""
        if not self.engine:
            return False
            
        try:
            # Clamp volume between 0.0 and 1.0
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            return True
        except Exception as e:
            print(f"Error setting volume: {e}")
            return False
    
    def speak(self, text, blocking=True):
        """
        Speak the given text.
        
        Args:
            text (str): Text to speak
            blocking (bool): If True, wait for speech to complete
            
        Returns:
            bool: True if speech started successfully
        """
        if not self.engine or not text:
            return False
            
        if self.is_speaking:
            print("TTS is already speaking. Please wait...")
            return False
            
        try:
            self.is_speaking = True
            
            clean_text = self._normalize_text_for_waveform(self._clean_text(text))
            # Gentle volume ramp to avoid pops
            try:
                base_vol = float(self.engine.getProperty('volume') or 0.9)
                for v in [0.6, 0.75, base_vol]:
                    self.engine.setProperty('volume', v)
                    time.sleep(0.02)
            except Exception:
                pass
            
            if blocking:
                for chunk in self._chunk_text(clean_text):
                    self.engine.say(chunk)
                    self.engine.runAndWait()
                    time.sleep(self._pause_ms / 1000.0)
                self.is_speaking = False
            else:
                # Run in separate thread for non-blocking
                def speak_async():
                    try:
                        for chunk in self._chunk_text(clean_text):
                            self.engine.say(chunk)
                            self.engine.runAndWait()
                            time.sleep(self._pause_ms / 1000.0)
                    finally:
                        self.is_speaking = False
                
                thread = threading.Thread(target=speak_async)
                thread.daemon = True
                thread.start()
            
            return True
            
        except Exception as e:
            print(f"Error during speech: {e}")
            self.is_speaking = False
            return False
    
    def _clean_text(self, text):
        """Clean text for better TTS pronunciation."""
        if not text:
            return ""
            
        # Remove or replace problematic characters
        clean_text = text.replace('\n', ' ')
        clean_text = clean_text.replace('\t', ' ')
        clean_text = clean_text.replace('  ', ' ')  # Remove double spaces
        # Normalize repeated punctuation and emojis for clearer speech
        clean_text = clean_text.replace('!!', '!')
        clean_text = clean_text.replace('??', '?')
        clean_text = clean_text.replace('...', '.')
        # Break overly long sentences slightly
        clean_text = ". ".join([seg.strip() for seg in clean_text.split(".") if seg.strip()])
        
        # Limit text length to prevent very long speeches
        if len(clean_text) > 1000:
            clean_text = clean_text[:1000] + "... (text truncated)"
            
        return clean_text.strip()
    
    def _normalize_text_for_waveform(self, text: str) -> str:
        """Inject soft pauses and normalize pacing for waveform consistency."""
        if not text:
            return ""
        # Add commas after conjunctions to slow down speech slightly
        text = text.replace(" and ", ", and ")
        text = text.replace(" but ", ", but ")
        # Ensure sentence endings have a pause marker character
        text = text.replace("! ", "!  ")
        text = text.replace("? ", "?  ")
        return text
    
    def _chunk_text(self, text: str) -> list[str]:
        """Split text into manageable chunks for consistent audio output."""
        if not text:
            return []
        chunks = []
        buf = ""
        for token in text.split(" "):
            if len(buf) + len(token) + 1 > self._chunk_size:
                chunks.append(buf.strip())
                buf = token
            else:
                buf = f"{buf} {token}".strip()
        if buf:
            chunks.append(buf)
        return chunks
    
    def stop(self):
        """Stop current speech."""
        if self.engine:
            try:
                self.engine.stop()
                self.is_speaking = False
                return True
            except Exception as e:
                print(f"Error stopping speech: {e}")
                return False
        return False
    
    def is_available(self):
        """Check if TTS engine is available."""
        return self.engine is not None


# Global TTS engine instance
_tts_engine = TTSEngine()


def read_text(text, rate=175, volume=0.9, blocking=True):
    """
    Reads the given text aloud using pyttsx3.
    
    Args:
        text (str): Text to read
        rate (int): Speech rate in words per minute
        volume (float): Volume level (0.0 to 1.0)
        blocking (bool): Whether to wait for speech to complete
        
    Returns:
        bool: True if speech started successfully, False otherwise
    """
    global _tts_engine
    
    if not text:
        print("No text provided for TTS")
        return False
    
    if not _tts_engine.is_available():
        print("TTS engine not available")
        return False
    
    # Set properties
    _tts_engine.set_rate(rate)
    _tts_engine.set_volume(volume)
    
    # Speak the text
    return _tts_engine.speak(text, blocking=blocking)


def stop_speech():
    """Stop current speech."""
    global _tts_engine
    return _tts_engine.stop()


def get_voices():
    """Get available voices."""
    global _tts_engine
    return _tts_engine.get_available_voices()


def set_voice(voice_id):
    """Set voice by ID."""
    global _tts_engine
    return _tts_engine.set_voice(voice_id)


def is_speaking():
    """Check if TTS is currently speaking."""
    global _tts_engine
    return _tts_engine.is_speaking


def test_tts():
    """Test TTS functionality."""
    print("Testing TTS functionality...")
    
    # Test basic speech
    test_text = "Hello, this is a test of the text to speech system."
    success = read_text(test_text)
    
    if success:
        print("✅ TTS test successful")
    else:
        print("❌ TTS test failed")
    
    # Show available voices
    voices = get_voices()
    print(f"Available voices: {len(voices)}")
    for i, voice in enumerate(voices[:3]):  # Show first 3 voices
        print(f"  {i+1}. {voice['name']} ({voice['id']})")


if __name__ == "__main__":
    test_tts()
