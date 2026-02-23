import webrtcvad
import collections

class VADDetector:
    """Voice Activity Detection - Tuned for INSTANT Response"""
    
    def __init__(self, aggressiveness=3, sample_rate=16000):
        """
        aggressiveness: 3 (Max level to filter out fans/background noise)
        """
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = sample_rate
        
        # SPEED OPTIMIZATION: Ultra-fast silence detection
        # Reduced from 200ms to 100ms for instant response (2x faster!)
        # This makes Jarvis realize you stopped talking 100ms faster.
        self.frame_duration = 20  # ms (20ms frames for fine granularity)
        self.padding_duration = 100  # ms (HALVED from 200ms!)
        self.num_padding_frames = int(self.padding_duration / self.frame_duration)
        
    def is_speech(self, frame):
        """Check if frame contains speech"""
        try:
            # Resizing logic to match frame_duration
            frame_size = int(self.sample_rate * self.frame_duration / 1000) * 2
            
            if len(frame) < frame_size:
                frame = frame + b'\x00' * (frame_size - len(frame))
            elif len(frame) > frame_size:
                frame = frame[:frame_size]
            
            return self.vad.is_speech(frame, self.sample_rate)
        except Exception:
            return False # Default to silence on error
    
    def should_stop_listening(self, ring_buffer):
        """Determine if we should stop listening"""
        num_voiced = len([f for f, speech in ring_buffer if speech])
        
        # SPEED TWEAK 2: The "Snap" Factor
        # Old: < 0.3 (Required 70% silence to stop)
        # New: < 0.75 (Stops if > 25% silence)
        # This cuts the mic immediately even if there is slight background noise.
        return num_voiced < 0.75 * len(ring_buffer)
    
    def process_audio_stream(self, audio_generator):
        triggered = False
        ring_buffer = collections.deque(maxlen=self.num_padding_frames)
        
        for frame in audio_generator:
            is_speech = self.is_speech(frame)
            
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # Start trigger: > 60% speech in buffer (slightly harder to start = fewer false starts)
                if num_voiced > 0.6 * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield (f, True)
                    ring_buffer.clear()
            else:
                yield (frame, True)
                ring_buffer.append((frame, is_speech))
                
                if self.should_stop_listening(ring_buffer):
                    for f, s in ring_buffer:
                        yield (f, False)
                    break
    
    def get_frame_size(self):
        return int(self.sample_rate * self.frame_duration / 1000) * 2