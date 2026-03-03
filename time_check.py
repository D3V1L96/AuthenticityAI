

def check_timeline(metadata_date=None, first_seen_date=None) -> dict:
    if metadata_date and first_seen_date:
        if metadata_date > first_seen_date:
            return {"timeline_anomaly": True}

    return {"timeline_anomaly": False}
