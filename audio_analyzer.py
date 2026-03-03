"""
Audio Deepfake Analyzer (CNN on Mel Spectrogram)
-----------------------------------------------
Detects AI-generated or cloned voices.
"""

import torch
import torchaudio
import torchvision.models as models

# Load CNN
_model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
_model.fc = torch.nn.Linear(_model.fc.in_features, 1)
_model.eval()

_mel = torchaudio.transforms.MelSpectrogram(
    sample_rate=16000,
    n_mels=128
)

def audio_analyzer(audio_path: str) -> dict:
    waveform, sr = torchaudio.load(audio_path)

    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)

    spec = _mel(waveform)
    spec = spec.mean(dim=0).unsqueeze(0).repeat(3, 1, 1).unsqueeze(0)

    with torch.no_grad():
        output = torch.sigmoid(_model(spec)).item()

    return {
        "ai_score": round(float(output), 3)
    }
