"""
Real-Time Audio Deepfake Analyzer (2026 Optimized)
-------------------------------------------------
Uses fine-tuned Wav2Vec2 for live microphone deepfake detection.
Integrates with webcam live mode via threading.
Detects synthetic/cloned voices in 1-3 sec chunks.
"""

import threading
import queue
import time
import numpy as np
import pyaudio
import soundfile as sf
import librosa
from transformers import pipeline
import torch

# Global audio result queue (shared with main loop)
audio_result_queue = queue.Queue(maxsize=1)

# Audio capture params (16kHz for model)
CHUNK_SIZE = 1024
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_DURATION_SEC = 2  # Analyze every 2 seconds

# Model (Hugging Face fine-tuned for deepfake audio)
_detector = None
_device = "cuda" if torch.cuda.is_available() else "cpu"

def load_detector():
    """Lazy load the audio deepfake model"""
    global _detector
    if _detector is None:
        print("[Audio Analyzer] Loading Wav2Vec2 deepfake model (first time: 1-2 min)...")
        try:
            _detector = pipeline(
                "audio-classification",
                model="garystafford/wav2vec2-deepfake-voice-detector",
                device=_device
            )
            print("[Audio Analyzer] Model loaded on", _device.upper())
        except Exception as e:
            print(f"[Audio Analyzer] Load failed: {e}")
            _detector = None
    return _detector

def live_audio_thread(stop_event):
    """Thread for real-time mic capture & deepfake analysis"""
    detector = load_detector()
    if detector is None:
        audio_result_queue.put({"verdict": "ERROR", "confidence": 0.0, "details": "Model not loaded"})
        return

    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paFloat32,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    print("[Audio Analyzer] Live mic detection started...")

    frames = []
    start_time = time.time()

    while not stop_event.is_set():
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(np.frombuffer(data, dtype=np.float32))

        # Analyze every CHUNK_DURATION_SEC
        if time.time() - start_time >= CHUNK_DURATION_SEC:
            # Save temp wav (model needs file or array)
            temp_path = "temp_mic_chunk.wav"
            with sf.SoundFile(temp_path, mode='w', samplerate=SAMPLE_RATE, channels=CHANNELS) as f:
                f.write(np.concatenate(frames))

            # Resample if needed (though already 16kHz)
            audio, sr = librosa.load(temp_path, sr=SAMPLE_RATE, mono=True)

            try:
                # Inference
                results = detector(audio)
                top = max(results, key=lambda x: x['score'])
                label = top["label"].upper()  # "bonafide" (real) or "spoof" (fake)
                confidence = top["score"]

                if "BONAFIDE" in label or "REAL" in label:
                    verdict = "REAL"
                    ai_score = confidence
                else:
                    verdict = "DEEPFAKE"
                    ai_score = 1 - confidence

                audio_result_queue.put({
                    "verdict": verdict,
                    "confidence": round(confidence, 4),
                    "ai_score": round(ai_score, 4),
                    "details": f"Model: {top['label']} ({confidence:.1%})"
                })
            except Exception as e:
                audio_result_queue.put({
                    "verdict": "ERROR",
                    "confidence": 0.0,
                    "details": str(e)
                })

            # Reset for next chunk
            frames = []
            start_time = time.time()

    stream.stop_stream()
    stream.close()
    p.terminate()
    print("[Audio Analyzer] Live mic stopped.")