import requests
import os

class ImageProvider:
    def __init__(self):
        # Hardcoded API credentials — replace with your actual keys here:
        self.api_key = "AIzaSyBli2Z_-cVa3v2hi9JzXKnByBTfZX1Hqow"
        self.cse_id = "c531c53ab8e3a4348"

        if not self.api_key or not self.cse_id:
            raise ValueError("Google API key and CSE ID must be set.")

    def analyze(self, input_path: str) -> dict:
        """
        Uses Google Custom Search API to find similar images on the web.
        Uses the filename (without extension) as search query as a basic heuristic.

        Returns a dictionary with:
          - sources: list of URLs where similar images were found
          - match_confidence: float 0-1 estimate of confidence based on results count
          - credibility_score: placeholder value 0.5 (can be improved with source analysis)
        """

        # Basic query: use the filename without extension
        query = os.path.splitext(os.path.basename(input_path))[0]

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "cx": self.cse_id,
            "key": self.api_key,
            "searchType": "image",
            "num": 5
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            sources = []
            if "items" in data:
                for item in data["items"]:
                    sources.append(item["link"])  # image URL

            match_confidence = min(1.0, len(sources) / 5.0)  # simple heuristic
            credibility_score = 0.5  # placeholder, can be improved

            return {
                "sources": sources,
                "match_confidence": match_confidence,
                "credibility_score": credibility_score
            }

        except Exception as e:
            print(f"[ImageProvider] API error: {e}")
            return {
                "sources": [],
                "match_confidence": 0.0,
                "credibility_score": 0.0
            }
