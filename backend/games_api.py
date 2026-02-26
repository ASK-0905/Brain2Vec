import os
import requests

GAME_API_URL = os.getenv("GAME_API_URL")


def get_relaxing_games():
    """Return a list of relaxing game suggestions.

    Tries to fetch suggestions from GAME_API_URL if set; otherwise returns a
    small static fallback list so the feature works offline.
    """
    # Static fallback games
    fallback = [
        {
            "name": "Breathing Exercise",
            "description": "Guided breathing to calm down",
            "url": "https://example.com/breathing"
        },
        {
            "name": "Memory Match",
            "description": "A gentle concentration game",
            "url": "https://example.com/memory-match"
        },
        {
            "name": "Color Tap",
            "description": "Simple tapping game to focus",
            "url": "https://example.com/color-tap"
        }
    ]

    if not GAME_API_URL:
        return fallback

    try:
        r = requests.get(GAME_API_URL, timeout=5)
        data = r.json()
        # Expecting a list of game dicts
        if isinstance(data, list) and len(data) > 0:
            return data
    except Exception:
        pass

    return fallback
