"""
image_analyzer.py - AuthenticityAI
Image & video frame deepfake detection module
Uses transformers pipeline (ViT or similar) with GPU/CPU support
"""

import cv2
from transformers import pipeline
from device_utils import get_device  # shared device detection

# Global detector (lazy load)
_detector = None

def image_analyzer(image_path: str) -> dict:
    """
    Analyze a single image for deepfake indicators.
    Returns: {"verdict": str, "confidence": float, "final_score": float}
    """
    global _detector

    # Load device once
    device, device_name = get_device()

    try:
        if _detector is None:
            print(f"[Image Analyzer] Loading deepfake detection model on {device.upper()} ({device_name})...")
            _detector = pipeline(
                "image-classification",
                model="your-image-deepfake-model",  # ← replace with actual model, e.g. "deepfake-detection-model"
                device=0 if device == "cuda" else -1
            )
            print(f"[Image Analyzer] Model loaded successfully on {device.upper()}")

        # Load and preprocess image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")

        # Convert BGR (OpenCV) to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Run inference
        results = _detector(img_rgb)

        # Assume model returns list of dicts: [{'label': 'REAL', 'score': 0.92}, ...]
        # Take top prediction
        top = results[0]
        verdict = top['label'].upper()
        confidence = top['score']

        # Map to your desired format
        final_score = confidence  # can be adjusted with logic

        return {
            "verdict": verdict,
            "confidence": confidence,
            "final_score": final_score,
            "details": results
        }

    except Exception as e:
        print(f"[Image Analyzer ERROR] {str(e)}")
        return {
            "verdict": "ERROR",
            "confidence": 0.0,
            "final_score": 0.0,
            "details": str(e)
        }
