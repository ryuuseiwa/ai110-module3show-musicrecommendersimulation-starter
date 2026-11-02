import csv
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Tuple, Optional

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Advanced features (optional so older call sites still work)
    popularity: int = 50
    release_decade: str = ""
    mood_tags: List[str] = field(default_factory=list)
    instrumentalness: float = 0.0
    liveness: float = 0.0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    favorite_mood_tags: List[str] = field(default_factory=list)
    target_popularity: Optional[int] = None
    preferred_decade: Optional[str] = None
    target_valence: Optional[float] = None
    target_instrumentalness: Optional[float] = None
    target_liveness: Optional[float] = None

    def to_prefs(self) -> Dict:
        """Convert the profile into the user_prefs dict used by score_song."""
        return {
            "genre": self.favorite_genre,
            "mood": self.favorite_mood,
            "energy": self.target_energy,
            "likes_acoustic": self.likes_acoustic,
            "mood_tags": self.favorite_mood_tags,
            "popularity": self.target_popularity,
            "decade": self.preferred_decade,
            "valence": self.target_valence,
            "instrumentalness": self.target_instrumentalness,
            "liveness": self.target_liveness,
        }

@dataclass(frozen=True)
class ScoringMode:
    """A scoring strategy: the weight each feature contributes to a song's score."""
    name: str
    description: str
    genre: float = 2.0
    mood: float = 1.0
    energy: float = 1.5
    acoustic: float = 0.5
    mood_tags: float = 0.5
    popularity: float = 0.5
    decade: float = 0.5
    valence: float = 0.5
    instrumentalness: float = 0.5
    liveness: float = 0.25

SCORING_MODES: Dict[str, ScoringMode] = {
    "balanced": ScoringMode(
        "balanced", "Default recipe: genre > energy > mood, small bonuses for extras"),
    "genre_first": ScoringMode(
        "genre_first", "Genre dominates; everything else is a tie-breaker",
        genre=4.0, mood=0.5, energy=1.0, mood_tags=0.25),
    "mood_first": ScoringMode(
        "mood_first", "Mood and mood tags lead; genre is a light hint",
        genre=0.75, mood=2.5, mood_tags=1.0, energy=1.5, valence=1.0),
    "energy_focused": ScoringMode(
        "energy_focused", "Experiment: genre weight halved, energy weight doubled",
        genre=1.0, energy=3.0),
}

ARTIST_PENALTY = 1.0
GENRE_PENALTY = 0.5
MAX_TAG_MATCHES = 2

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song], mode: str = "balanced"):
        self.songs = songs
        self.mode = mode

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k Song objects for a user, best first."""
        by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(user.to_prefs(), [asdict(s) for s in self.songs], k, self.mode)
        return [by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of a song's score for a user."""
        score, reasons = score_song(user.to_prefs(), asdict(song), self.mode)
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from a CSV file into dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row.get("popularity") or 50),
                "release_decade": row.get("release_decade", ""),
                "mood_tags": [t for t in (row.get("mood_tags") or "").split(";") if t],
                "instrumentalness": float(row.get("instrumentalness") or 0.0),
                "liveness": float(row.get("liveness") or 0.0),
            })
    return songs

def _closeness(target: float, actual: float, scale: float = 1.0) -> float:
    """Return 1.0 when actual equals target, falling linearly to 0.0 at a gap of `scale`."""
    return max(0.0, 1.0 - abs(target - actual) / scale)

def score_song(user_prefs: Dict, song: Dict, mode: str = "balanced") -> Tuple[float, List[str]]:
    """Score one song against user preferences, returning (score, reasons)."""
    w = SCORING_MODES[mode]
    score = 0.0
    reasons = []

    def add(points: float, reason: str) -> None:
        nonlocal score
        score += points
        reasons.append(f"{reason} (+{points:.2f})")

    if user_prefs.get("genre") and song["genre"] == user_prefs["genre"]:
        add(w.genre, "genre match")
    if user_prefs.get("mood") and song["mood"] == user_prefs["mood"]:
        add(w.mood, "mood match")

    if user_prefs.get("energy") is not None:
        add(w.energy * _closeness(user_prefs["energy"], song["energy"]),
            f"energy {song['energy']:.2f} vs target {user_prefs['energy']:.2f}")

    if user_prefs.get("valence") is not None:
        add(w.valence * _closeness(user_prefs["valence"], song["valence"]),
            f"valence {song['valence']:.2f} vs target {user_prefs['valence']:.2f}")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        fit = song["acousticness"] if likes_acoustic else 1.0 - song["acousticness"]
        add(w.acoustic * fit, "acoustic fit" if likes_acoustic else "electric/produced fit")

    shared = [t for t in user_prefs.get("mood_tags") or [] if t in song.get("mood_tags", [])]
    if shared:
        add(w.mood_tags * min(len(shared), MAX_TAG_MATCHES), "mood tags " + "/".join(shared))

    if user_prefs.get("popularity") is not None:
        add(w.popularity * _closeness(user_prefs["popularity"], song.get("popularity", 50), 100),
            f"popularity {song.get('popularity', 50)} vs target {user_prefs['popularity']}")

    for feature in ("instrumentalness", "liveness"):
        if user_prefs.get(feature) is not None:
            add(getattr(w, feature) * _closeness(user_prefs[feature], song.get(feature, 0.0)),
                f"{feature} {song.get(feature, 0.0):.2f} vs target {user_prefs[feature]:.2f}")

    if user_prefs.get("decade") and song.get("release_decade") == user_prefs["decade"]:
        add(w.decade, f"from the {song['release_decade']}")

    return round(score, 4), reasons

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    mode: str = "balanced",
    diversity: bool = False,
) -> List[Tuple[Dict, float, str]]:
    """Rank all songs by score and return the top k as (song, score, explanation)."""
    scored = [(song, *score_song(user_prefs, song, mode)) for song in songs]
    # Highest score first; song id breaks ties so output is deterministic.
    scored = sorted(scored, key=lambda item: (-item[1], item[0]["id"]))

    if not diversity:
        return [(song, score, "; ".join(reasons)) for song, score, reasons in scored[:k]]

    # Greedy re-rank: each pick lowers the score of songs sharing its artist or genre.
    picked = []
    remaining = list(scored)
    while remaining and len(picked) < k:
        best = None
        for song, score, reasons in remaining:
            artist_hits = sum(1 for p, _, _ in picked if p["artist"] == song["artist"])
            genre_hits = sum(1 for p, _, _ in picked if p["genre"] == song["genre"])
            penalty = ARTIST_PENALTY * artist_hits + GENRE_PENALTY * genre_hits
            adjusted = score - penalty
            if best is None or adjusted > best[1]:
                notes = list(reasons)
                if artist_hits:
                    notes.append(f"artist already listed (-{ARTIST_PENALTY * artist_hits:.2f})")
                if genre_hits:
                    notes.append(f"genre already listed (-{GENRE_PENALTY * genre_hits:.2f})")
                best = (song, round(adjusted, 4), notes)
        picked.append(best)
        remaining = [r for r in remaining if r[0]["id"] != best[0]["id"]]
    return [(song, score, "; ".join(reasons)) for song, score, reasons in picked]
