# intel_providers/registry.py

from .image_provider import ImageProvider
from .audio_provider import AudioProvider
from .video_provider import VideoProvider

def get_provider(file_type):
    providers = {
        "image": ImageProvider(),
        "audio": AudioProvider(),
        "video": VideoProvider(),
    }
    if file_type not in providers:
        raise ValueError(f"No provider available for file type: {file_type}")
    return providers[file_type]
