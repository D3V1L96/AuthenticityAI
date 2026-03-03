## Security & Privacy Notes

AuthenticityAI is designed with **privacy, security, and responsible use** as core principles. Please read the following carefully before deployment or use.

### 1. Local Processing & No Data Transmission
- All AI inference (video, audio, and image analysis) runs **entirely on your device** — no frames, audio chunks, or files are uploaded to any cloud server.
- Internet features (reverse image/video search, source credibility checks) are **optional** and only used in file mode when explicitly enabled.
- No telemetry, usage tracking, or logging of analyzed content is performed.

### 2. Model & Dependency Security
- All models are downloaded directly from trusted sources (Hugging Face, official PyTorch indexes, SpeechBrain GitHub).
- We recommend verifying model checksums (SHA256) on first download if operating in high-security environments.
- Dependencies (torch, transformers, opencv-python, etc.) are pinned in `requirements.txt` — avoid `pip install --upgrade` without reviewing changes.

### 3. Known Limitations & Attack Surface
- **Adversarial attacks**: Advanced deepfakes (2026+) may evade detection. AuthenticityAI is not infallible — treat verdicts as **strong indicators**, not absolute proof.
- **False positives/negatives**: Compression artifacts, poor lighting, background noise, or accent variations can lower accuracy.
- **Microphone/webcam access**: Live mode requires microphone and camera permissions — only grant when actively using the tool.
- **Temporary files**: Short-lived temp files (.jpg/.wav) are created and immediately deleted during analysis — ensure your system has secure temp folder deletion policies.

### 4. Responsible Use Guidelines
- **Do not** use AuthenticityAI to harass, dox, or defame individuals based solely on its verdicts.
- **Do not** rely exclusively on AuthenticityAI for legal evidence without expert forensic validation (chain-of-custody, multiple tools, human review).
- **Do not** share or publish raw analysis results without context — deepfake verdicts can be misinterpreted or taken out of context.
- Always cross-verify high-stakes decisions with multiple independent sources/methods.

### 5. Recommendations for High-Security Environments
- Run inside a **sandbox** or air-gapped machine for sensitive investigations.
- Disable internet access entirely if reverse search is not needed.
- Use a dedicated, hardened OS instance (e.g. Tails, Qubes OS, or Windows Sandbox).
- Regularly audit and update dependencies (`pip check`, `pip-audit`).
- Consider compiling from source or using frozen executables to reduce supply-chain risks.

### 6. Reporting Security Issues
If you discover a vulnerability, model bypass, or privacy concern, please report it responsibly:

- Email: [your-security-email@example.com] (PGP key available on request)
- GitHub Security Advisories (preferred for open-source contributors)

We take all reports seriously and follow coordinated disclosure practices.

**AuthenticityAI is a tool to empower verification — not to replace human judgment or due process.**

By using AuthenticityAI, you agree to use it responsibly and in compliance with applicable laws.
