"""
AuthenticityAI - Advanced Deepfake Detection & Forensic Verification System
-------------------------
Real-time webcam + audio analysis | Multi-modal AI verification | Detailed audit reports

Author : D4RKD3V1L
Motive : Trust nothing. Verify everything.
"""

import os
import sys
import time
import cv2
import argparse
import tempfile
import json
import gc
import torch
from threading import Thread, Event, Lock
from queue import Queue
from datetime import datetime
from collections import Counter, deque

# ---- Your modules ----
from fusion import fuse_results
from image_analyzer import image_analyzer
from video_analyse import video_analyzer
from reverse_search import reverse_image_search
from time_check import check_timeline
from audio_provider import AudioProvider

# Live audio analyzer
from live_audio_analyzer import live_audio_thread, audio_result_queue

audio_provider = AudioProvider()

def audio_analyzer(file_path):
    return audio_provider.analyze(file_path)

# ---- GPU/CPU Detection ----
device = "cuda" if torch.cuda.is_available() else "cpu"
device_name = torch.cuda.get_device_name(0) if device == "cuda" else "CPU"
print(f"[AuthenticityAI] Using device: {device.upper()} ({device_name})")

# ---- CLI Visuals ----
def type_print(text, delay=0.002):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_logo():
    os.system("cls" if os.name == "nt" else "clear")
    banner = r"""
 █████╗ ██╗   ██╗████████╗██╗  ██╗███████╗███╗   ██╗████████╗██╗ ██████╗██╗████████╗██╗   ██╗ █████╗ ██╗
██╔══██╗██║   ██║╚══██╔══╝██║  ██║██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝██║╚══██╔══╝╚██╗ ██╔╝██╔══██╗██║
███████║██║   ██║   ██║   ███████║█████╗  ██╔██╗ ██║   ██║   ██║██║     ██║   ██║    ╚████╔╝ ███████║██║
██╔══██║╚██╗ ██╔╝   ██║   ██╔══██║██╔══╝  ██║╚██╗██║   ██║   ██║██║     ██║   ██║     ╚██╔╝  ██╔══██║██║
██║  ██║ ╚████╔╝    ██║   ██║  ██║███████╗██║ ╚████║   ██║   ██║╚██████╗██║   ██║      ██║   ██║  ██║██║
╚═╝  ╚═╝  ╚═══╝     ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝
                  AuthenticityAI
         Advanced Deepfake Detection & Verification
"""
    type_print(banner, 0.0005)
    type_print(" AI POWERED DIGITAL AUTHENTICITY PLATFORM\n")
    type_print(" Author : D4RKD3V1L")
    type_print(" Motive : Trust nothing. Verify everything.\n")
    type_print(f" [ Zero Trust | Real-Time Multimodal Analysis | GPU/CPU Support | Forensic Audit ]")
    print("\n" + "=" * 70 + "\n")
    time.sleep(0.5)

# ---- File Type Detection ----
def detect_file_type(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".jpg", ".jpeg", ".png", ".webp"]: return "image"
    if ext in [".wav", ".mp3", ".flac"]: return "audio"
    if ext in [".mp4", ".avi", ".mkv", ".mov"]: return "video"
    raise ValueError(f"Unsupported file format: {ext}")

# ---- File Detection Pipeline ----
def run_detection(input_path: str) -> dict:
    if not os.path.exists(input_path):
        raise FileNotFoundError("Input file does not exist")

    file_type = detect_file_type(input_path)
    results = []
    internet_data = None

    try:
        if file_type == "image":
            results.append(image_analyzer(input_path))
        elif file_type == "audio":
            results.append(audio_analyzer(input_path))
        elif file_type == "video":
            results.append(video_analyzer(input_path))
    except Exception as e:
        print(f"[ERROR] Analyzer failed for {file_type}: {str(e)}")
        results.append({"verdict": "ERROR", "confidence": 0.0})

    if not results:
        raise RuntimeError("No analyzers executed")

    if file_type == "image":
        try:
            reverse_result = reverse_image_search(input_path)
            source_result = reverse_image_search(input_path)
            source_credibility = 0.5
            if source_result and "credibility_score" in source_result:
                source_credibility = source_result["credibility_score"]
            timeline_flag = check_timeline(reverse_result.get("sources", [])) if reverse_result else False

            internet_data = {
                "match_confidence": reverse_result.get("match_confidence", 0.0) if reverse_result else 0.0,
                "credibility_score": source_credibility,
                "timeline_anomaly": timeline_flag
            }
        except Exception as e:
            print(f"[WARNING] Internet verification failed: {str(e)}")
            internet_data = None

    final_result = fuse_results(results, internet_data)

    final_result.update({
        "file_type": file_type,
        "modules_used": [
            f"{file_type}_analyzer",
            "internet_verification" if internet_data else None
        ]
    })
    final_result["modules_used"] = [m for m in final_result["modules_used"] if m]

    return final_result

# ---- Real-Time Detection ----
video_result_queue = Queue(maxsize=1)
live_running = False
verdict_history = deque(maxlen=100)
analysis_lock = Lock()

def live_detection_loop():
    global live_running

    session_start = datetime.now()
    session_start_str = session_start.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[AuthenticityAI LIVE] Session started at {session_start_str} | Device: {device.upper()} ({device_name})")

    stop_event = Event()
    audio_thread = Thread(target=live_audio_thread, args=(stop_event,))
    audio_thread.daemon = True
    audio_thread.start()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check connection/drivers.")
        stop_event.set()
        audio_thread.join(timeout=2.0)
        return

    print("[LIVE MODE] Press 'q' or ESC to quit | Silent analysis in progress...")

    # Load face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Smoothing variables
    smoothed_x = smoothed_y = smoothed_w = smoothed_h = None
    alpha = 0.65           # 0.5–0.8 range: higher = faster response, lower = more stable
    face_timeout = 2.0     # keep last face for 2 seconds if lost
    last_face_time = time.time()

    prev_time = time.time()
    frame_count = 0
    analysis_counter = 0

    while live_running:
        ret, frame = cap.read()
        if not ret:
            print("[WARNING] Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)

        frame_count += 1
        current_time = time.time()
        elapsed = current_time - prev_time
        fps = frame_count / elapsed if elapsed > 0 else 0.0

        # Create display frame
        display_frame = frame.copy()

        # Detect faces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=6, minSize=(80, 80))

        face_detected_this_frame = len(faces) > 0

        if face_detected_this_frame:
            # Take largest face
            (x, y, w, h) = max(faces, key=lambda f: f[2]*f[3])

            # Initialize or smooth
            if smoothed_x is None:
                smoothed_x = x
                smoothed_y = y
                smoothed_w = w
                smoothed_h = h
            else:
                smoothed_x = alpha * x + (1 - alpha) * smoothed_x
                smoothed_y = alpha * y + (1 - alpha) * smoothed_y
                smoothed_w = alpha * w + (1 - alpha) * smoothed_w
                smoothed_h = alpha * h + (1 - alpha) * smoothed_h

            last_face_time = current_time

        # Use last known face if recent and no detection this frame
        use_last_face = (current_time - last_face_time < face_timeout) and smoothed_x is not None

        if face_detected_this_frame or use_last_face:
            # Add padding around smoothed box
            padding = int(0.45 * max(smoothed_w, smoothed_h))
            x1 = max(0, int(smoothed_x) - padding)
            y1 = max(0, int(smoothed_y) - padding)
            x2 = min(frame.shape[1], int(smoothed_x + smoothed_w) + padding)
            y2 = min(frame.shape[0], int(smoothed_y + smoothed_h) + padding)

            # Crop and resize (square aspect for clean view)
            face_crop = frame[y1:y2, x1:x2]
            display_frame = cv2.resize(face_crop, (640, 640), interpolation=cv2.INTER_LINEAR)

        else:
            # No recent face → smooth fade to blur
            display_frame = cv2.GaussianBlur(frame, (79, 79), 25)

        # Run analysis in background (on full original frame)
        analysis_counter += 1
        if analysis_counter % 3 == 0:
            if video_result_queue.empty():
                def video_analyze_thread():
                    with analysis_lock:
                        try:
                            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                                cv2.imwrite(tmp.name, frame)  # full frame = better accuracy
                                tmp_path = tmp.name
                            video_result = image_analyzer(tmp_path)
                            os.unlink(tmp_path)
                            verdict = video_result.get("verdict", "Analyzing...")
                            score = video_result.get("final_score", video_result.get("confidence", 0.0))
                            video_result_queue.put({"verdict": verdict, "score": score})
                        except Exception as exc:
                            video_result_queue.put({"verdict": f"Video Error: {str(exc)[:40]}", "score": 0.0})
                        finally:
                            gc.collect()

                Thread(target=video_analyze_thread, daemon=True).start()

        # Audio result (silent)
        if not audio_result_queue.empty():
            audio_res = audio_result_queue.get_nowait()
            # Used for report only

        # History entry (silent)
        now_str = datetime.now().strftime("%H:%M:%S")
        video_verdict = "Analyzing"
        video_score = 0.0
        audio_verdict = "Analyzing"
        audio_score = 0.0
        if not video_result_queue.empty():
            video_res = video_result_queue.get_nowait()
            video_verdict = video_res.get("verdict", "Analyzing")
            video_score = video_res.get("score", 0.0)
        if not audio_result_queue.empty():
            audio_res = audio_result_queue.get_nowait()
            audio_verdict = audio_res.get("verdict", "Analyzing")
            audio_score = audio_res.get("confidence", 0.0)

        overall_verdict = "REAL"
        if "DEEPFAKE" in video_verdict or "DEEPFAKE" in audio_verdict:
            overall_verdict = "DEEPFAKE"
        elif "SUSPICIOUS" in video_verdict or "SUSPICIOUS" in audio_verdict:
            overall_verdict = "SUSPICIOUS"

        entry = {
            "timestamp": now_str,
            "overall": overall_verdict,
            "video_verdict": video_verdict,
            "video_score": video_score,
            "audio_verdict": audio_verdict,
            "audio_score": audio_score,
            "fps": round(fps, 1)
        }
        verdict_history.append(entry)

        # Show stable, clean face view (no text, no flicker)
        cv2.imshow("AuthenticityAI - Live Detection", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break

    # Cleanup & generate audit report (unchanged from your version)
    stop_event.set()
    audio_thread.join(timeout=3.0)
    cap.release()
    cv2.destroyAllWindows()
    live_running = False

    session_end = datetime.now()
    session_duration = session_end - session_start
    total_frames = frame_count
    total_entries = len(verdict_history)

    verdicts = [e["overall"] for e in verdict_history]
    verdict_counts = Counter(verdicts)
    total_real = verdict_counts.get("REAL", 0)
    total_suspicious = verdict_counts.get("SUSPICIOUS", 0)
    total_deepfake = verdict_counts.get("DEEPFAKE", 0)

    avg_video_conf = sum(e["video_score"] for e in verdict_history) / total_entries if total_entries > 0 else 0.0
    avg_audio_conf = sum(e["audio_score"] for e in verdict_history) / total_entries if total_entries > 0 else 0.0
    avg_overall_conf = (avg_video_conf + avg_audio_conf) / 2

    max_streak = 1
    current_streak = 1
    current_verdict = verdicts[0] if verdicts else None
    for v in verdicts[1:]:
        if v == current_verdict:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1
            current_verdict = v

    timestamp = session_end.strftime("%Y%m%d_%H%M%S")
    report_txt = f"audit_report_authenticityai_{timestamp}.txt"
    report_json = f"audit_report_authenticityai_{timestamp}.json"

    with open(report_txt, "w", encoding="utf-8") as f:
        f.write("AUTHENTICITYAI FORENSIC AUDIT REPORT (Live Session)\n")
        f.write("=" * 80 + "\n")
        f.write(f"Session start: {session_start_str}\n")
        f.write(f"Session end:   {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration:      {str(session_duration).split('.')[0]}\n")
        f.write(f"Device used:   {device.upper()} ({device_name})\n")
        f.write(f"Total frames processed: {total_frames}\n")
        f.write(f"Total verdict entries:  {total_entries}\n\n")

        f.write("VERDICT STATISTICS:\n")
        f.write(f"  REAL        : {total_real} ({total_real/total_entries*100:.1f}% if total_entries > 0 else 'N/A')\n")
        f.write(f"  SUSPICIOUS  : {total_suspicious} ({total_suspicious/total_entries*100:.1f}% if total_entries > 0 else 'N/A')\n")
        f.write(f"  DEEPFAKE    : {total_deepfake} ({total_deepfake/total_entries*100:.1f}% if total_entries > 0 else 'N/A')\n\n")

        f.write("AVERAGE CONFIDENCE:\n")
        f.write(f"  Video   : {avg_video_conf:.1%}\n")
        f.write(f"  Audio   : {avg_audio_conf:.1%}\n")
        f.write(f"  Overall : {avg_overall_conf:.1%}\n\n")

        f.write(f"Longest consistent streak: {max_streak} frames ({current_verdict})\n\n")

        f.write("LAST 50 VERDICTS (most recent first):\n")
        f.write("-" * 80 + "\n")
        for entry in list(verdict_history)[-50:]:
            f.write(f"[{entry['timestamp']}] {entry['overall']} | "
                    f"Video: {entry['video_verdict']} {entry['video_score']:.1%} | "
                    f"Audio: {entry['audio_verdict']} {entry['audio_score']:.1%} | "
                    f"FPS: {entry['fps']}\n")
        f.write("-" * 80 + "\n\n")

        f.write("System: AuthenticityAI - D4RKD3V1L Verifier\n")
        f.write("Proof: All live detections logged for forensic review.\n")
        f.write("Note: GPU acceleration recommended for best performance.\n")

    json_data = {
        "session_start": session_start_str,
        "session_end": session_end.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": session_duration.total_seconds(),
        "device": f"{device.upper()} ({device_name})",
        "total_frames": total_frames,
        "verdict_counts": dict(verdict_counts),
        "percentages": {
            "REAL": total_real / total_entries * 100 if total_entries > 0 else 0,
            "SUSPICIOUS": total_suspicious / total_entries * 100 if total_entries > 0 else 0,
            "DEEPFAKE": total_deepfake / total_entries * 100 if total_entries > 0 else 0
        },
        "average_confidence": {
            "video": avg_video_conf,
            "audio": avg_audio_conf,
            "overall": avg_overall_conf
        },
        "longest_streak": {
            "length": max_streak,
            "verdict": current_verdict
        },
        "history": list(verdict_history)
    }

    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    print(f"\n[AuthenticityAI LIVE] Stopped.")
    print(f"Audit report saved as: {report_txt}")
    print(f"JSON version saved as: {report_json}")
    print("Open .txt for full statistics and forensic proof.")

# ---- CLI Entry Point ----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AuthenticityAI - Deepfake Forensic Detection System")
    parser.add_argument("input", nargs="?", default=None, help="File path OR 'live'")
    args = parser.parse_args()

    print_logo()

    if args.input == "live":
        print("[*] Starting REAL-TIME multimodal detection...")
        live_running = True
        live_detection_loop()
    elif args.input:
        try:
            type_print("[*] Initializing AuthenticityAI forensic pipeline...")
            time.sleep(0.3)

            type_print("[*] Running AI inference...")
            time.sleep(0.4)

            result = run_detection(args.input)

            print("\n========== FINAL AUTHENTICITY RESULT ==========")
            print("File Type       :", result.get("file_type", "Unknown"))
            print("Verdict         :", result.get("verdict", "N/A"))
            print("Confidence Score:", f"{result.get('final_score', 0):.1%}" if 'final_score' in result else "N/A")
            print("Modules Used    :", ", ".join(result.get("modules_used", [])))
            print("===========================================\n")

        except Exception as err:
            print("\n[ERROR]", str(err))
            sys.exit(1)
    else:
        print("Usage:")
        print("  File mode  : python AuthenticityAI_main.py path/to/file.jpg")
        print("  Live mode  : python AuthenticityAI_main.py live")
        sys.exit(1)