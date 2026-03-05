"""
live_audio_analyzer.py - AuthenticityAI
Real-time microphone audio deepfake detection
Uses transformers pipeline (Wav2Vec2) with GPU/CPU support
"""

import time
import threading
import queue
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
import tempfile
import os
from transformers import pipeline
from device_utils import get_device  # shared device detection

# Global variables
_detector = None
audio_result_queue = queue.Queue()
stop_event = threading.Event()
CHUNK_DURATION_SEC = 2.0  # analyze every 2 seconds of audio

def load_detector():
    global _detector
    if _detector is None:
        device, device_name = get_device()
        print(f"[Audio Analyzer] Loading Wav2Vec2 model on {device.upper()} ({device_name})...")
        try:
            _detector = pipeline(
                "audio-classification",
                model="garystafford/wav2vec2-deepfake-voice-detector",  # or your preferred model
                device=0 if device == "cuda" else -1
            )
            print(f"[Audio Analyzer] Model loaded successfully on {device.upper()}")
        except Exception as e:
            print(f"[Audio Analyzer] Model load failed: {e}")
            _detector = None
    return _detector

def audio_callback(indata, frames, time_info, status):
    """Called by sounddevice for each audio block"""
    if status:
        print(f"[Audio Callback] Status: {status}")
    # Put audio data into a queue or process directly
    # For simplicity, we'll collect in a buffer in live_audio_thread

def live_audio_thread(stop_event):
    """Background thread for continuous mic capture & analysis"""
    load_detector()  # ensure model is loaded

    fs = 16000  # sample rate
    channels = 1
    chunk_size = int(fs * CHUNK_DURATION_SEC)

    print("[Audio Thread] Starting microphone capture...")

    def stream_gen():
        with sd.InputStream(samplerate=fs, channels=channels, dtype='float32', blocksize=chunk_size,
                            callback=audio_callback):
            while not stop_event.is_set():
                time.sleep(0.1)

    # Use a buffer to collect audio
    audio_buffer = []

    def process_audio():
        while not stop_event.is_set():
            # Wait for enough data (simplified)
            time.sleep(CHUNK_DURATION_SEC)
            if len(audio_buffer) >= chunk_size:
                chunk = np.array(audio_buffer[:chunk_size], dtype=np.float32)
                audio_buffer[:] = audio_buffer[chunk_size:]

                # Save to temp wav
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    wavfile.write(tmp.name, fs, chunk)
                    tmp_path = tmp.name

                # Analyze
                detector = load_detector()
                if detector is None:
                    audio_result_queue.put({"verdict": "ERROR", "confidence": 0.0})
                else:
                    try:
                        results = detector(tmp_path)
                        top = results[0]
                        verdict = top['label'].upper()
                        confidence = top['score']
                        audio_result_queue.put({"verdict": verdict, "confidence": confidence})
                    except Exception as e:
                        print(f"[Audio Analysis ERROR] {e}")
                        audio_result_queue.put({"verdict": "ERROR", "confidence": 0.0})

                os.unlink(tmp_path)

    # Start audio stream in background
    stream_thread = threading.Thread(target=stream_gen, daemon=True)
    stream_thread.start()

    # Start processing thread
    process_thread = threading.Thread(target=process_audio, daemon=True)
    process_thread.start()

    stop_event.wait()
    print("[Audio Thread] Stopped.")
