"""
Input Router
------------
Determines whether input is audio, image, or video.
"""

import os

AUDIO_EXT = [".wav", ".mp3", ".flac"]
IMAGE_EXT = [".jpg", ".jpeg", ".png"]
VIDEO_EXT = [".mp4", ".avi", ".mov"]


def route_input(file_path: str) -> dict:
    if not os.path.isfile(file_path):
        raise FileNotFoundError("Input file does not exist")

    ext = os.path.splitext(file_path)[1].lower()

    if ext in AUDIO_EXT:
        return {"type": "audio"}
    elif ext in IMAGE_EXT:
        return {"type": "image"}
    elif ext in VIDEO_EXT:
        return {"type": "video"}
    else:
        raise ValueError(f"Unsupported file format: {ext}")
