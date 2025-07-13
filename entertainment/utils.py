# from .firebase_config import storage
# import uuid

# def upload_video_to_firebase(file_obj):
#     bucket = storage.bucket()
#     blob = bucket.blob(f'videos/{uuid.uuid4()}.mp4')
#     blob.upload_from_file(file_obj)
#     blob.make_public()
#     return blob.public_url

import re

# List of bad words (expand this with more keywords)
PROFANITY_LIST = [
    "badword1", "badword2", "abuse1", "abuse2", "hate", "racist", "xxx", "nsfw", "adult", "f**k"
]

SPAM_PATTERNS = [
    r"(http|www)\S+",  # links
    r"buy now", r"free", r"click here", r"subscribe"
]

def is_comment_clean(comment_text):
    """
    Checks if the given comment contains profanity or spam.
    Returns True if clean, False if it contains unwanted content.
    """
    text = comment_text.lower()

    # Check for bad/profane words
    for word in PROFANITY_LIST:
        if word in text:
            return False

    # Check for spam patterns
    for pattern in SPAM_PATTERNS:
        if re.search(pattern, text):
            return False

    return True
