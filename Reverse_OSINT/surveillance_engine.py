def analyze_surveillance(trackers):
    confidence = 0
    categories = set()

    for t in trackers:
        confidence += t["Risk Weight"]
        categories.add(t["Category"])

    # Bonus risk logic
    if "Advertising" in categories and "Analytics" in categories:
        confidence += 20

    if len(categories) >= 3:
        confidence += 20

    confidence = min(confidence, 100)

    if confidence >= 70:
        level = "RED"
    elif confidence >= 40:
        level = "ORANGE"
    else:
        level = "GREEN"

    return confidence, level
