import json

def detect_trackers(scripts):
    with open("tracker_list.json") as f:
        tracker_db = json.load(f)

    results = []

    for tracker, info in tracker_db.items():
        detected_tags = set()

        for keyword in info["keywords"]:
            for script in scripts:
                if keyword in script:
                    detected_tags.add(keyword)

        if detected_tags:
            results.append({
                "Tracker": tracker.replace("_", " ").title(),
                "Company": info["company"],
                "Category": info["category"],
                "Detected Tags": ", ".join(sorted(detected_tags)),
                "Description": info["description"]
            })

    return results
