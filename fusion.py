def fuse_results(results: list, internet_data: dict = None) -> dict:
    base_score = sum(r["ai_score"] for r in results) / len(results)

    internet_score = 0.0
    if internet_data:
        internet_score += internet_data.get("match_confidence", 0) * 0.3
        internet_score += (1 - internet_data.get("credibility_score", 0.5)) * 0.2
        if internet_data.get("timeline_anomaly"):
            internet_score += 0.2

    final_score = min(base_score + internet_score, 1.0)

    if final_score < 0.30:
        verdict = "REAL"
    elif final_score < 0.60:
        verdict = "SUSPICIOUS"
    else:
        verdict = "AI / DEEPFAKE"

    return {
        "final_score": round(final_score, 3),
        "verdict": verdict
    }
