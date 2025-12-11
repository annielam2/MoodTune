from typing import Dict, List, Tuple

BASE_EMOTION_TO_TAG: Dict[str, str] = {
    # Positive / energetic
    "joy": "happy",
    "amusement": "happy",
    "excitement": "energetic",
    "love": "romantic",
    "optimism": "happy",
    "pride": "motivational",
    "admiration": "inspirational",
    "gratitude": "happy",
    "relief": "chill",

    # Calm / reflective
    "caring": "acoustic",
    "realization": "chill",
    "curiosity": "indie",
    "approval": "indie",
    "desire": "romantic",

    # Sad / emotional
    "sadness": "sad",
    "grief": "sad",
    "remorse": "sad",
    "disappointment": "sad",

    # Stress / anxiety / tension
    "nervousness": "dark",
    "fear": "dark",
    "confusion": "ambient",
    "embarrassment": "ambient",

    # Anger / aggression
    "anger": "angry",
    "annoyance": "angry",
    "disgust": "metal",
    "disapproval": "metal",

    # Surprise
    "surprise": "experimental",

    # Neutral baseline
    "neutral": "chill",
}


def emotion_to_tag(label: str) -> str:
    if not label:
        return "chill"
    return BASE_EMOTION_TO_TAG.get(label.lower(), "chill")


def aggregate_emotions_to_tags(
    emotions: List[Dict],
    min_score: float = 0.15,
    top_n: int = 3,
) -> Tuple[str, List[Tuple[str, float]]]:

    if not emotions:
        return "chill", [("chill", 1.0)]

    tag_weights: Dict[str, float] = {}

    for item in emotions:
        label = item.get("label")
        score = float(item.get("score", 0.0) or 0.0)

        if not label or score < min_score:
            continue

        tag = emotion_to_tag(label)
        tag_weights[tag] = tag_weights.get(tag, 0.0) + score

    if not tag_weights:
        return "chill", [("chill", 1.0)]

    total = sum(tag_weights.values())
    normalized = [(tag, w / total) for tag, w in tag_weights.items()]
    normalized.sort(key=lambda x: x[1], reverse=True)
    ranked_tags = normalized[:top_n]
    primary_tag = ranked_tags[0][0]

    return primary_tag, ranked_tags
