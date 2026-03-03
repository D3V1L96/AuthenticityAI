# intel_providers/video_provider.py

import requests


class VideoProvider:
    API_URL = "https://your-video-api.com/analyze"  # Replace with real API

    def analyze(self, input_path):
        with open(input_path, "rb") as f:
            files = {"file": f}
            response = requests.post(self.API_URL, files=files)

        if response.status_code != 200:
            raise RuntimeError(f"API error: {response.text}")

        data = response.json()
        return {
            "match_confidence": data.get("match_confidence", 0.0),
            "credibility_score": data.get("credibility_score", 0.5),
            "timeline_anomaly": data.get("timeline_anomaly", False),
        }
