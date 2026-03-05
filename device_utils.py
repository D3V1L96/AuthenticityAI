# device_utils.py
import torch


def get_device(hide_gpu_name=True):
    """
    Detects device and optionally hides the exact GPU model name.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    if device == "cuda":
        full_name = torch.cuda.get_device_name(0)
        display_name = "GPU" if hide_gpu_name else full_name
    else:
        display_name = "CPU"

    print(f"[AuthenticityAI] Using device: {device.upper()} ({display_name})")
    return device, display_name