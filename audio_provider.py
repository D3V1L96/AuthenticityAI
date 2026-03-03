"""
AudioProvider - Speaker recognition based audio analysis for deepfake detection
Uses speechbrain ECAPA-TDNN model trained on VoxCeleb
"""

import warnings
from typing import Dict, Any

# Modern import path (SpeechBrain ≥ 1.0)
from speechbrain.inference.speaker import SpeakerRecognition

# Optional fallback for very old installations
try:
    from speechbrain.pretrained.interfaces import SpeakerRecognition as OldSpeakerRecognition
except ImportError:
    OldSpeakerRecognition = None


class AudioProvider:
    """
    Provides speaker recognition based analysis for audio files.
    Currently uses self-similarity (verify file against itself) as a simple
    deepfake consistency check.
    """

    def __init__(self):
        self.model: SpeakerRecognition | None = None
        self._load_model()

    def _load_model(self) -> None:
        """Lazy load the pretrained ECAPA-TDNN speaker recognition model"""
        if self.model is not None:
            return

        try:
            print("[AudioProvider] Loading ECAPA-TDNN model from speechbrain...")
            self.model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="pretrained_models/spkrec-ecapa-voxceleb",
                run_opts={"device": "cuda"}  # Automatically uses GPU if available
            )
            print("[AudioProvider] Model loaded successfully")
        except Exception as e:
            print(f"[AudioProvider] Failed to load model: {e}")
            self.model = None

    def analyze(self, input_path: str) -> Dict[str, Any]:
        """
        Analyze audio file for potential deepfake characteristics.

        Simple method: self-verification score
        (genuine audio usually has very high similarity to itself)

        Args:
            input_path: path to audio file (.wav, .mp3, .flac, etc.)

        Returns:
            dict with verdict, confidence and details
        """
        if self.model is None:
            self._load_model()
            if self.model is None:
                return {
                    "confidence": 0.0,
                    "verdict": "ERROR",
                    "details": "Failed to initialize SpeakerRecognition model"
                }

        try:
            # Self-verification: compare file against itself
            # Real audio → score close to 1.0
            # Many deepfakes/spliced audio → noticeably lower
            score, prediction = self.model.verify_files(input_path, input_path)

            confidence: float = float(score.item())  # cosine similarity in [0, 1]

            # Suggested thresholds (tune based on your dataset):
            # > 0.88  → almost certainly same speaker / real recording
            # 0.65–0.88 → suspicious / possible manipulation or compression artifacts
            # < 0.65  → likely fake, different speaker, or heavy synthesis
            if confidence > 0.88:
                verdict = "REAL"
            elif confidence > 0.65:
                verdict = "SUSPICIOUS"
            else:
                verdict = "FAKE"

            return {
                "confidence": round(confidence, 4),
                "verdict": verdict,
                "score_raw": confidence,
                "details": (
                    f"Self-similarity cosine score: {confidence:.4f} "
                    f"(>0.88 = REAL, >0.65 = SUSPICIOUS, ≤0.65 = FAKE)"
                ),
                "prediction": bool(prediction.item())
            }

        except Exception as e:
            return {
                "confidence": 0.0,
                "verdict": "ERROR",
                "details": f"Analysis failed: {str(e)}",
                "error_type": type(e).__name__
            }


# Quick test when run directly
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        provider = AudioProvider()
        result = provider.analyze(sys.argv[1])
        print(result)
    else:
        print("Usage: python audio_provider.py <audio_file_path>")