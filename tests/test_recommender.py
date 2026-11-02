from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


from src.recommender import SCORING_MODES, load_songs, recommend_songs, score_song


def test_load_songs_converts_numeric_fields():
    songs = load_songs("data/songs.csv")
    assert len(songs) >= 15
    first = songs[0]
    assert isinstance(first["energy"], float)
    assert isinstance(first["popularity"], int)
    assert isinstance(first["mood_tags"], list) and first["mood_tags"]


def test_score_song_rewards_closeness_not_magnitude():
    prefs = {"energy": 0.5}
    near, _ = score_song(prefs, {"genre": "x", "mood": "y", "energy": 0.5, "acousticness": 0.5})
    far, _ = score_song(prefs, {"genre": "x", "mood": "y", "energy": 1.0, "acousticness": 0.5})
    assert near > far


def test_score_song_returns_reasons():
    score, reasons = score_song({"genre": "pop", "mood": "happy", "energy": 0.8},
                                {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2})
    assert score == 4.5
    assert "genre match (+2.00)" in reasons
    assert "mood match (+1.00)" in reasons


def test_recommend_songs_sorted_highest_first():
    songs = load_songs("data/songs.csv")
    recs = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.35}, songs, k=5)
    scores = [score for _, score, _ in recs]
    assert len(recs) == 5
    assert scores == sorted(scores, reverse=True)
    assert recs[0][0]["genre"] == "lofi"


def test_every_scoring_mode_runs():
    songs = load_songs("data/songs.csv")
    for mode in SCORING_MODES:
        assert len(recommend_songs({"genre": "rock", "energy": 0.9}, songs, k=3, mode=mode)) == 3


def test_diversity_penalty_limits_repeat_artists():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "lofi", "mood": "chill", "energy": 0.35}
    plain = recommend_songs(prefs, songs, k=3)
    diverse = recommend_songs(prefs, songs, k=3, diversity=True)
    assert sum(s["genre"] == "lofi" for s, _, _ in plain) == 3
    assert sum(s["genre"] == "lofi" for s, _, _ in diverse) < 3
