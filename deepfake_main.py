"""
Deepfake Detection System - with Real-Time Webcam + Audio + Detailed Audit Report
-------------------------
AI + Internet-assisted forensic verification pipeline + LIVE detection

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

# Live audio analyzer (thread + queue)
from live_audio_analyzer import live_audio_thread, audio_result_queue

audio_provider = AudioProvider()

def audio_analyzer(file_path):
    return audio_provider.analyze(file_path)

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
██████╗ ███████╗███████╗██████╗ ███████╗ █████╗ ██╗  ██╗███████╗
██╔══██╗██╔════╝██╔════╝██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██╔════╝
██║  ██║█████╗  █████╗  ██████╔╝█████╗  ███████║█████╔╝ █████╗  
██║  ██║██╔══╝  ██╔══╝  ██╔═══╝ ██╔══╝  ██╔══██║██╔═██╗ ██╔══╝  
██████╔╝███████╗███████╗██║     ██      ██║  ██║██║  ██╗███████╗
╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═      ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
"""
    type_print(banner, 0.0007)
    type_print(" AI DEEPFAKE FORENSIC VERIFICATION SYSTEM\n")
    type_print(" Author : D4RKD3V1L")
    type_print(" Motive : Expose synthetic lies. Defend digital truth.\n")
    type_print(" [ Zero Trust | Cyber Forensics | AI Intelligence | LIVE Mode + Audit ]")
    print("\n" + "=" * 60 + "\n")
    time.sleep(0.4)

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

    if file_type == "image":
        results.append(image_analyzer(input_path))
    elif file_type == "audio":
        results.append(audio_analyzer(input_path))
    elif file_type == "video":
        results.append(video_analyzer(input_path))

    if not results:
        raise RuntimeError("No analyzers executed")

    if file_type == "image":
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
    print(f"[LIVE] Session started at {session_start_str}")

    stop_event = Event()
    audio_thread = Thread(target=live_audio_thread, args=(stop_event,))
    audio_thread.daemon = True
    audio_thread.start()

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        stop_event.set()
        audio_thread.join(timeout=2.0)
        return

    print("[LIVE MODE] Press 'q' or ESC to quit | Analyzing frames...")

    prev_time = time.time()
    frame_count = 0
    analysis_counter = 0

    while live_running:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        frame_count += 1
        current_time = time.time()
        elapsed = current_time - prev_time
        fps = frame_count / elapsed if elapsed > 0 else 0.0

        display_frame = cv2.resize(frame, (640, 480))
        analysis_frame = display_frame.copy()

        analysis_counter += 1
        if analysis_counter % 3 == 0:  # Throttle video analysis
            if video_result_queue.empty():
                def video_analyze_thread():
                    with analysis_lock:
                        try:
                            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                                cv2.imwrite(tmp.name, analysis_frame)
                                tmp_path = tmp.name
                            video_result = image_analyzer(tmp_path)
                            os.unlink(tmp_path)
                            verdict = video_result.get("verdict", "Analyzing...")
                            score = video_result.get("final_score", video_result.get("confidence", 0.0))
                            video_result_queue.put({"verdict": verdict, "score": score})
                        except Exception as exc:
                            video_result_queue.put({"verdict": f"Video Err: {str(exc)[:40]}", "score": 0.0})
                        finally:
                            gc.collect()

                Thread(target=video_analyze_thread, daemon=True).start()

        # Video result (safe defaults)
        video_verdict = "Analyzing"
        video_score = 0.0
        video_text = "Video: Analyzing..."
        video_color = (255, 255, 0)
        if not video_result_queue.empty():
            video_res = video_result_queue.get_nowait()
            video_verdict = video_res.get("verdict", "Analyzing")
            video_score = video_res.get("score", 0.0)
            video_text = f"Video: {video_verdict} {video_score:.1%}"
            video_color = (0, 255, 0) if "REAL" in video_verdict.upper() else (0, 0, 255)

        # Audio result (safe defaults)
        audio_verdict = "Analyzing"
        audio_score = 0.0
        audio_text = "Audio: Analyzing..."
        audio_color = (255, 255, 0)
        if not audio_result_queue.empty():
            audio_res = audio_result_queue.get_nowait()
            audio_verdict = audio_res.get("verdict", "Analyzing")
            audio_score = audio_res.get("confidence", 0.0)
            audio_text = f"Audio: {audio_verdict} {audio_score:.1%}"
            audio_color = (0, 255, 0) if "REAL" in audio_verdict.upper() else (0, 0, 255)

        # Overall verdict
        overall_verdict = "REAL"
        if "DEEPFAKE" in video_verdict or "DEEPFAKE" in audio_verdict:
            overall_verdict = "DEEPFAKE"
        elif "SUSPICIOUS" in video_verdict or "SUSPICIOUS" in audio_verdict:
            overall_verdict = "SUSPICIOUS"

        overall_color = (0, 255, 0) if overall_verdict == "REAL" else (0, 0, 255)

        # History entry
        now_str = datetime.now().strftime("%H:%M:%S")
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

        # Draw on frame
        cv2.putText(display_frame, f"OVERALL: {overall_verdict}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, overall_color, 3)
        cv2.putText(display_frame, video_text, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, video_color, 2)
        cv2.putText(display_frame, audio_text, (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, audio_color, 2)
        cv2.putText(display_frame, f"FPS: {fps:.1f}", (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(display_frame, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    (20, display_frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Deepfake Forensic Live Detection - D4RKD3V1L", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break

    # Cleanup & generate detailed audit report
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

    # Longest streak
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
    report_txt = f"audit_report_live_{timestamp}.txt"
    report_json = f"audit_report_live_{timestamp}.json"

    # Text report
    with open(report_txt, "w", encoding="utf-8") as f:
        f.write("DEEPFAKE FORENSIC AUDIT REPORT (Live Session)\n")
        f.write("=" * 80 + "\n")
        f.write(f"Session start: {session_start_str}\n")
        f.write(f"Session end:   {session_end.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration:      {str(session_duration).split('.')[0]}\n")
        f.write(f"Total frames processed: {total_frames}\n")
        f.write(f"Total verdict entries:  {total_entries}\n\n")

        f.write("VERDICT STATISTICS:\n")
        f.write(f"  REAL        : {total_real} ({total_real/total_entries*100:.1f}% if total_entries > 0 else 'N/A') \n")
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

        f.write("System: D4RKD3V1L Deepfake Forensic Verifier\n")
        f.write("Proof: All live detections logged for forensic review.\n")
        f.write("Note: Memory optimized. If slow, check GPU usage (nvidia-smi).\n")

    # JSON report
    json_data = {
        "session_start": session_start_str,
        "session_end": session_end.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_seconds": session_duration.total_seconds(),
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

    print(f"\n[LIVE MODE] Stopped.")
    print(f"Detailed audit report saved as: {report_txt}")
    print(f"JSON version saved as: {report_json}")
    print("Open .txt for full statistics and proof.")

# ---- CLI Entry Point ----
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deepfake Forensic Detection System")
    parser.add_argument("input", nargs="?", default=None, help="File path OR 'live'")
    args = parser.parse_args()

    print_logo()

    if args.input == "live":
        print("[*] Starting REAL-TIME detection with detailed audit...")
        live_running = True
        live_detection_loop()
    elif args.input:
        try:
            type_print("[*] Initializing forensic pipeline...")
            time.sleep(0.3)

            type_print("[*] Running AI inference...")
            time.sleep(0.4)

            result = run_detection(args.input)

            print("\n========== FINAL RESULT ==========")
            print("File Type       :", result.get("file_type", "Unknown"))
            print("Verdict         :", result.get("verdict", "N/A"))
            print("Confidence Score:", f"{result.get('final_score', 0):.1%}" if 'final_score' in result else "N/A")
            print("Modules Used    :", ", ".join(result.get("modules_used", [])))
            print("=================================\n")

        except Exception as err:
            print("\n[ERROR]", str(err))
            sys.exit(1)
    else:
        print("Usage:")
        print("  File mode  : python deepfake_main.py path/to/file.jpg")
        print("  Live mode  : python deepfake_main.py live")
        sys.exit(1)