import random
import re
import requests
from urllib.parse import quote_plus
from flask import Flask, render_template, request

from projectsecrets import LASTFM_API_KEY, APP_SECRET_KEY, HF_TOKEN
from mapping import aggregate_emotions_to_tags

LASTFM_BASE_URL = "http://ws.audioscrobbler.com/2.0/"
HF_API_URL = "https://router.huggingface.co/hf-inference/models/SamLowe/roberta-base-go_emotions"

app = Flask(__name__)
app.secret_key = APP_SECRET_KEY

HF_HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

GENRE_TAGS = {
    "pop": "pop",
    "rock": "rock",
    "indie": "indie",
    "rnb": "rnb",
    "hiphop": "hip-hop",
    "electronic": "electronic",
    "metal": "metal",
    "acoustic": "acoustic",
}

GENRE_WORDS = [
    "pop", "rock", "indie", "r&b", "rnb", "hiphop", "hip-hop",
    "electronic", "edm", "metal", "acoustic", "jazz", "country"
]

REQUEST_PATTERNS = [
    r"i want\b.*",
    r"i'd like\b.*",
    r"give me\b.*",
    r"i need\b.*",
    r"i am looking for\b.*",
    r"i'm looking for\b.*",
    r"something .*",
]


def clean_text_for_emotion_model(text: str) -> str:
    t = text.lower()

    for g in GENRE_WORDS:
        t = t.replace(g, "")

    for pattern in REQUEST_PATTERNS:
        t = re.sub(pattern, "", t)

    t = re.sub(r"\s+", " ", t).strip()

    return t

def analyze_mood(text: str):
    payload = {"inputs": text}

    try:
        resp = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("HF API error:", e)
        # Fallback: neutral if HF fails
        return [{"label": "neutral", "score": 1.0}]

    if not data or not isinstance(data, list):
        return [{"label": "neutral", "score": 1.0}]

    candidates = data[0]
    if not isinstance(candidates, list) or not candidates:
        return [{"label": "neutral", "score": 1.0}]

    return candidates

def fetch_tracks_for_single_tag(tag: str, limit: int = 20):
    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": limit,
    }

    resp = requests.get(LASTFM_BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    return data.get("tracks", {}).get("track", [])


def get_tracks_for_tags(tags, limit_per_tag: int = 20, sample_size: int = 10):
    all_tracks = {}

    for tag in tags:
        try:
            tracks_raw = fetch_tracks_for_single_tag(tag, limit=limit_per_tag)
        except Exception as e:
            print(f"Last.fm error for tag '{tag}':", e)
            continue

        for t in tracks_raw:
            artist = t.get("artist", {})
            artist_name = artist.get("name") if isinstance(artist, dict) else artist

            name = t.get("name", "")
            key = (name.lower(), str(artist_name).lower())
            if key in all_tracks:
                continue

            image_url = None

            query = f"{name} {artist_name}".strip()
            spotify_url = f"https://open.spotify.com/search/{quote_plus(query)}"

            all_tracks[key] = {
                "name": name,
                "artist": artist_name,
                "url": t.get("url"),
                "spotify_url": spotify_url,
                "image": image_url,
                "playcount": t.get("playcount"),
            }

    tracks = list(all_tracks.values())

    if len(tracks) > sample_size:
        tracks = random.sample(tracks, sample_size)

    return tracks


# --- Flask route ---

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_text = request.form.get("mood_text", "").strip()
        selected_genres = request.form.getlist("genres")  # may be []

        if not user_text:
            return render_template(
                "index.html",
                error="Please type how you're feeling.",
                selected_genres=selected_genres,
            )

        cleaned = clean_text_for_emotion_model(user_text)
        emotions = analyze_mood(cleaned)

        if not emotions:
            return render_template(
                "index.html",
                error="Could not detect a mood.",
                selected_genres=selected_genres,
            )

        primary_tag, ranked_tags = aggregate_emotions_to_tags(emotions)

        top = max(emotions, key=lambda x: x.get("score", 0))
        detected_emotion = top.get("label")
        score = top.get("score")

        mood_tag = primary_tag

        genre_tags = [GENRE_TAGS[g] for g in selected_genres if g in GENRE_TAGS]
        tags_to_use = [mood_tag] + [t for t in genre_tags if t != mood_tag]

        if not tags_to_use:
            tags_to_use = [mood_tag]

        try:
            tracks = get_tracks_for_tags(tags_to_use)
        except Exception as e:
            return render_template(
                "index.html",
                error=f"Last.fm error: {e}",
                detected_emotion=detected_emotion,
                score=score,
                tag=mood_tag,
                user_text=user_text,
                ranked_tags=ranked_tags,
                selected_genres=selected_genres,
            )

        return render_template(
            "index.html",
            user_text=user_text,
            detected_emotion=detected_emotion,
            score=score,
            tag=mood_tag,
            tracks=tracks,
            ranked_tags=ranked_tags,
            selected_genres=selected_genres,
        )

    return render_template("index.html", selected_genres=[])


if __name__ == "__main__":
    app.run(debug=True)
