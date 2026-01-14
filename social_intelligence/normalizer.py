def normalize_post(post, platform, index):
    if not isinstance(post, dict):
        return None

    text = (
        post.get("caption")
        or post.get("text")
        or post.get("message")
        or post.get("title")
        or "[NO_TEXT_AVAILABLE]"
    )

    timestamp = post.get("timestamp") or post.get("createdAt") or post.get("takenAt")

    has_image = False
    has_video = False
    image_url = None
    video_url = None

    if platform == "instagram":
        image_url = post.get("displayUrl")
        video_url = post.get("videoUrl")
        has_image = bool(image_url)
        has_video = bool(video_url)

    if platform == "facebook":
        attachments = post.get("attachments", {}).get("data", [])
        if attachments:
            media = attachments[0].get("media", {})
            image_url = media.get("image", {}).get("src")
            video_url = media.get("source")
            has_image = bool(image_url)
            has_video = bool(video_url)

    return {
        "text": text,
        "timestamp": timestamp,
        "has_image": has_image,
        "has_video": has_video,
        "image_url": image_url,
        "video_url": video_url,
        "platform": platform
    }
