from spotify_api import get_music_for_state
from games_api import get_relaxing_games


def get_relief_actions(state="MILD STRESS"):
    # Map to simplified buckets for music selection
    music_state = {
        "RELAXED": "RELAXED",
        "MILD STRESS": "MILD",
        "HIGH STRESS": "HIGH",
    }.get(state, "MILD")

    return {
        "music": get_music_for_state(music_state),
        "games": get_relaxing_games()
    }
