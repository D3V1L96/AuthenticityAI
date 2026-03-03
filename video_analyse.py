"""
Video Deepfake Analyzer (CNN on Frames)
---------------------------------------
Extracts frames and averages CNN predictions.
"""

import cv2
import torch
import torchvision.transforms as T
import torchvision.models as models
from PIL import Image

_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
_model.fc = torch.nn.Linear(_model.fc.in_features, 1)
_model.eval()

_transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225])
])

def video_analyzer(video_path: str, frame_skip: int = 15) -> dict:
    cap = cv2.VideoCapture(video_path)
    scores = []
    frame_id = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % frame_skip == 0:
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            tensor = _transform(img).unsqueeze(0)

            with torch.no_grad():
                score = torch.sigmoid(_model(tensor)).item()
                scores.append(score)

        frame_id += 1

    cap.release()

    if not scores:
        return {"ai_score": 0.5}

    avg_score = sum(scores) / len(scores)

    return {
        "ai_score": round(float(avg_score), 3)
    }
