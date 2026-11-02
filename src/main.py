"""
Command line runner for the Music Recommender Simulation.

Usage:
    python -m src.main                              # every profile, balanced mode
    python -m src.main --profile chill_lofi         # one profile
    python -m src.main --mode mood_first            # switch scoring strategy
    python -m src.main --diversity                  # penalize repeat artists/genres
    python -m src.main --compare-modes --profile high_energy_pop
"""

import argparse
import os

try:
    from src.recommender import SCORING_MODES, load_songs, recommend_songs
except ImportError:  # running as `python src/main.py`
    from recommender import SCORING_MODES, load_songs, recommend_songs

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "songs.csv")

PROFILES = {
    # The starter's default pop/happy profile
    "default_pop_happy": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "high_energy_pop": {
        "genre": "pop", "mood": "happy", "energy": 0.9, "likes_acoustic": False,
        "mood_tags": ["euphoric", "bright"], "popularity": 85,
    },
    "chill_lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True,
        "mood_tags": ["cozy", "mellow"], "instrumentalness": 0.85,
    },
    "deep_intense_rock": {
        "genre": "rock", "mood": "intense", "energy": 0.92, "likes_acoustic": False,
        "mood_tags": ["aggressive", "rebellious"], "decade": "2000s", "liveness": 0.35,
    },
    # Adversarial / edge-case profiles
    "conflicted_sad_but_hyped": {"genre": "folk", "mood": "sad", "energy": 0.9, "valence": 0.2},
    "ghost_genre_kpop": {"genre": "k-pop", "mood": "happy", "energy": 0.7},
    "acoustic_headbanger": {
        "genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": True,
    },
}


def format_table(recommendations) -> str:
    """Render recommendations as an ASCII table with one reason per line."""
    headers = ["#", "Title", "Artist", "Genre", "Score", "Reasons"]
    rows = []
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        rows.append([str(rank), song["title"], song["artist"], song["genre"],
                     f"{score:.2f}", explanation.split("; ")])

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            lines = cell if isinstance(cell, list) else [cell]
            widths[i] = max(widths[i], *(len(line) for line in lines))

    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

    def render(cells):
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths)) + " |"

    out = [border, render(headers), border]
    for row in rows:
        reasons = row[-1]
        for i, reason in enumerate(reasons):
            out.append(render((row[:-1] if i == 0 else [""] * (len(row) - 1)) + [reason]))
        out.append(border)
    return "\n".join(out)


def describe(prefs: dict) -> str:
    """One-line summary of a profile's preferences."""
    return ", ".join(f"{k}={v}" for k, v in prefs.items())


def show(name: str, prefs: dict, songs, k: int, mode: str, diversity: bool) -> None:
    """Print the ranked recommendations for one profile."""
    recs = recommend_songs(prefs, songs, k=k, mode=mode, diversity=diversity)
    print(f"\n=== Profile: {name} | mode: {mode}{' + diversity' if diversity else ''} ===")
    print(f"Prefs: {describe(prefs)}")
    print(format_table(recs))


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument("--profile", choices=PROFILES, help="run a single profile")
    parser.add_argument("--mode", choices=SCORING_MODES, default="balanced")
    parser.add_argument("--diversity", action="store_true", help="penalize repeat artists/genres")
    parser.add_argument("--compare-modes", action="store_true", help="run every scoring mode")
    parser.add_argument("-k", type=int, default=5)
    args = parser.parse_args()

    songs = load_songs(DATA_PATH)
    print(f"Loaded songs: {len(songs)}")

    names = [args.profile] if args.profile else list(PROFILES)
    modes = list(SCORING_MODES) if args.compare_modes else [args.mode]
    for name in names:
        for mode in modes:
            show(name, PROFILES[name], songs, args.k, mode, args.diversity)


if __name__ == "__main__":
    main()
