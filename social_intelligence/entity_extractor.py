import re

# Expandable gazetteer (can later be replaced with spaCy / GeoNames)
KNOWN_LOCATIONS = [
    "India", "Mumbai", "Delhi", "London", "New York",
    "Los Angeles", "Dubai", "Paris", "Singapore"
]

def extract_locations(text: str):
    """
    Extract locations from:
    - plain text
    - hashtags (#Mumbai, #LondonLife, #PathaanInDelhi)
    """
    if not text:
        return []

    found = set()

    # ---------- Plain text ----------
    for loc in KNOWN_LOCATIONS:
        if re.search(rf"\b{re.escape(loc)}\b", text, re.IGNORECASE):
            found.add(loc)

    # ---------- Hashtags ----------
    hashtags = re.findall(r"#(\w+)", text)
    for tag in hashtags:
        for loc in KNOWN_LOCATIONS:
            if loc.lower() in tag.lower():
                found.add(loc)

    return list(found)
