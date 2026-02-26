import requests

CLIENT_ID = "6d87b8a9ba5a43d487cabbe63d2297e1"
CLIENT_SECRET = "d529ece987334d20acad0bcd7512f831"

def get_access_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    try:
        return r.json()["access_token"]
    except Exception:
        # Fail gracefully for offline/test environments
        return None

def _fallback_playlists(state: str):
    base = {
        "RELAXED": [
            {"name": "Calm Instrumentals", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DWXm0PxhhaP4S"}},
            {"name": "Evening Acoustic", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX0FOF1IUWK1W"}},
        ],
        "MILD": [
            {"name": "Lo-Fi Chill", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX9RwfGbeGQwP"}},
            {"name": "Focus Flow", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DWZeKCadgRdKQ"}},
        ],
        "HIGH": [
            {"name": "Breathing & Calm", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX4eRPd9frC1m"}},
            {"name": "Stress Relief", "external_urls": {"spotify": "https://open.spotify.com/playlist/37i9dQZF1DX3rxVfibe1L0"}},
        ],
    }
    return base.get(state, base["MILD"])


def get_music_for_state(state: str):
    query_map = {
        "RELAXED": "calm acoustic instrumental focus",
        "MILD": "lofi chill focus relax",
        "HIGH": "breathing meditation stress relief calm",
    }

    token = get_access_token()
    if not token:
        return _fallback_playlists(state)

    try:
        q = query_map.get(state, query_map["MILD"])
        r = requests.get(
            "https://api.spotify.com/v1/search",
            params={"q": q, "type": "playlist", "limit": 5},
            headers={"Authorization": f"Bearer {token}"}
        )
        items = r.json().get("playlists", {}).get("items", [])
        return items if items else _fallback_playlists(state)
    except Exception:
        return _fallback_playlists(state)
