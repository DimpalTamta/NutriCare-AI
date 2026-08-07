# recipe/video_handler.py
import os
import re
from typing import Dict, Optional
from utils.utils import get_logger

logger = get_logger(__name__)
LOCAL_VIDEO_DIR = "data/videos"
YOUTUBE_ID_PATTERN = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([A-Za-z0-9_-]{11})")

def extract_youtube_id(url: str) -> Optional[str]:
    match = YOUTUBE_ID_PATTERN.search(url)
    return match.group(1) if match else None

def get_youtube_embed_url(url: str) -> Optional[str]:
    vid = extract_youtube_id(url)
    return f"https://www.youtube.com/embed/{vid}" if vid else None

def resolve_local_video(filename: str) -> Optional[str]:
    path = os.path.join(LOCAL_VIDEO_DIR, filename)
    return path if os.path.exists(path) else None

def get_video_source(recipe: Dict) -> Dict:
    youtube = recipe.get("video_url")
    if youtube and extract_youtube_id(str(youtube)):
        return {"type": "youtube", "value": get_youtube_embed_url(str(youtube))}
    local = recipe.get("local_video")
    if local:
        resolved = resolve_local_video(str(local))
        if resolved:
            return {"type": "local", "value": resolved}
    return {"type": "none", "value": None}