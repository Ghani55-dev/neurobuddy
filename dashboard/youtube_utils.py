import random
import requests
from neuropulse_core import settings

YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY  # 🔑 Replace with your actual key

def fetch_youtube_video(mood_score):
    # Customize search based on mood
    mood_topics = {
        1: "soothing relaxation nature music",
        2: "uplifting soft piano",
        3: "calm focus instrumental",
        4: "happy energy music",
        5: "motivational upbeat music"
    }

    search_query = mood_topics.get(mood_score, "calm music")

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": search_query,
        "type": "video",
        "videoEmbeddable": "true",
        "videoSyndicated": "true",  # Ensures it can be embedded
        "maxResults": 5,
        "key": YOUTUBE_API_KEY,
    }

    response = requests.get(url, params=params)
    data = response.json()

    videos = data.get("items", [])
    if not videos:
        return None

    video = random.choice(videos)
    video_id = video["id"]["videoId"]
    return f"https://www.youtube.com/embed/{video_id}"
