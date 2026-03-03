"""
Image Deepfake Analyzer (using a real detection model)
------------------------------------------------------
Fixed version with proper imports and real verdict logic.
Uses a lightweight pre-trained model from Hugging Face.
"""

import torch
from PIL import Image
import cv2
import numpy as np
from transformers import pipeline

# Global model (loaded lazily – only once)
_detector = None


def get_detector():
    """Lazy-load the deepfake detection model (only downloads once)"""
    global _detector
    if _detector is None:
        print("[image_analyzer] Loading deepfake detection model (may take 1–2 min first time)...")
        try:
            _detector = pipeline(
                "image-classification",
                model="dima806/deepfake_vs_real_image_detection",
                device=0 if torch.cuda.is_available() else -1  # GPU if RTX 3050 is ready
            )
            print("[image_analyzer] Model loaded successfully")
        except Exception as e:
            print(f"[image_analyzer] Model load failed: {e}")
            _detector = None
    return _detector


def image_analyzer(input_data):
    """
    Analyze image for deepfake.

    Args:
        input_data: str (file path) or np.ndarray (webcam frame)

    Returns:
        dict with verdict, confidence, etc.
    """
    detector = get_detector()
    if detector is None:
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "ai_score": 0.0,
            "details": "Failed to load deepfake detection model"
        }

    try:
        # Handle both path and numpy array (from webcam)
        if isinstance(input_data, str):
            # File path
            img_rgb = cv2.imread(input_data)
            if img_rgb is None:
                raise ValueError("Could not read image file")
            img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
        else:
            # Already numpy array (BGR from OpenCV)
            img_rgb = cv2.cvtColor(input_data, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image (transformers expects PIL)
        img_pil = Image.fromarray(img_rgb)

        # Run inference
        results = detector(img_pil)

        # Take top prediction
        top = results[0]
        label = top["label"].upper()  # usually "Real" or "Fake"
        confidence = top["score"]  # 0.0–1.0

        # Convert to our format
        if "REAL" in label or "AUTHENTIC" in label:
            verdict = "REAL"
            ai_score = confidence
        else:
            verdict = "DEEPFAKE"
            ai_score = 1 - confidence

        return {
            "verdict": verdict,
            "confidence": round(confidence, 4),
            "ai_score": round(ai_score, 4),
            "details": f"Model: {top['label']} ({confidence:.1%})",
            "raw_results": results  # optional – for debugging
        }

    except Exception as e:
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "ai_score": 0.0,
            "details": f"Analysis failed: {str(e)}"
        }


# Optional: Quick test when run directly
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        result = image_analyzer(sys.argv[1])
        print(result)
    else:
        print("Usage: python image_analyzer.py <image_path.jpg>")