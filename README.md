# 🎵 Music Recommender Simulation

## Project Summary

**VibeFinder 1.0** is a small, explainable, content-based music recommender that runs in the terminal. It loads a 20-song catalog from `data/songs.csv`, compares every song against a user's "taste profile" (favorite genre, mood, target energy, and optional extras like mood tags, popularity, and decade), gives each song a score with a list of reasons, and prints the top 5 as a table.

On top of the core project it also has:

- **5 advanced song features**: popularity, release decade, detailed mood tags, instrumentalness, and liveness (Challenge 1)
- **4 switchable scoring modes**: `balanced`, `genre_first`, `mood_first`, and `energy_focused` (Challenge 2)
- **A diversity penalty** that stops one artist or genre from filling the whole list (Challenge 3)
- **ASCII table output** that lists every reason behind each score (Challenge 4)

---

## How The System Works

### How real recommenders work

Big platforms like Spotify and YouTube mix two ideas:

- **Collaborative filtering** uses *other people's behavior*: "users who liked what you liked also liked X". It needs a lot of interaction data (plays, likes, skips, playlist adds, replays, listening time), and it knows nothing about the songs themselves. That is why it struggles with brand-new songs and brand-new users (the "cold start" problem).
- **Content-based filtering** uses *the songs' own attributes*: genre, mood, tempo, energy, valence, acousticness, and on Spotify even audio analysis and lyrics. It can recommend a song nobody has heard yet, but it tends to keep suggesting "more of the same".

Real systems combine both, then re-rank the candidates for freshness, diversity, and business rules. The data they use falls into two groups. **Explicit signals** are likes, follows, and playlist adds. **Implicit signals** are skips, replays, listening time, time of day, and device.

### What VibeFinder prioritizes

VibeFinder is purely **content-based**. There are no other users, so it cannot do collaborative filtering. It prioritizes **genre first, then how close the song's energy is to the user's target, then mood**. Every point it awards comes with a reason, so you can always see why a song was picked.

### Features used

| `Song` (from the CSV) | `UserProfile` / `user_prefs` |
|---|---|
| `genre`, `mood` | `genre` / `favorite_genre` |
| `energy`, `valence` (0.0–1.0) | `mood` / `favorite_mood` |
| `acousticness` (0.0–1.0) | `energy` / `target_energy` |
| `popularity` (0–100) | `likes_acoustic` (True / False / not set) |
| `release_decade` (e.g. `2010s`) | `mood_tags` (e.g. `["cozy", "mellow"]`) |
| `mood_tags` (e.g. `euphoric;bright`) | `popularity`, `decade`, `valence`, `instrumentalness`, `liveness` (optional targets) |
| `instrumentalness`, `liveness` (0.0–1.0) | |
| `tempo_bpm`, `danceability` (loaded, not scored) | |

### Algorithm recipe (balanced mode)

| Rule | Points |
|---|---|
| Genre matches exactly | **+2.0** |
| Mood matches exactly | **+1.0** |
| Energy closeness | **+1.5 × (1 − \|song − target\|)** |
| Acoustic fit (if `likes_acoustic` is set) | +0.5 × acousticness, or +0.5 × (1 − acousticness) |
| Each shared mood tag (max 2) | +0.5 |
| Popularity closeness | +0.5 × (1 − \|gap\| / 100) |
| Valence / instrumentalness closeness | +0.5 × (1 − \|gap\|) |
| Liveness closeness | +0.25 × (1 − \|gap\|) |
| Release decade matches | +0.5 |

The key idea for numeric features is **closeness, not size**. A song at energy 0.80 earns the most points when the user wants 0.80, not when it is the loudest song in the catalog.

- **Scoring rule** (`score_song`): judges *one* song and returns `(score, reasons)`.
- **Ranking rule** (`recommend_songs`): runs the scoring rule on *every* song, sorts with `sorted()` (highest first, song id breaks ties), and keeps the top `k`. You need both: a score means nothing until it is compared against the other songs' scores.

### Data flow

```
User prefs (dict) ──┐
                    ├─► for each song: score_song() ─► (song, score, reasons)
songs.csv ─► load_songs() ─┘                                 │
                                                             ▼
                              sorted(highest first) ─► [optional diversity re-rank] ─► top k ─► table
```

### Scoring modes (Strategy pattern)

Each mode is a `ScoringMode` object holding a set of weights. `score_song` stays the same no matter which one you pick.

| Mode | Genre | Mood | Energy | Mood tags | Idea |
|---|---|---|---|---|---|
| `balanced` | 2.0 | 1.0 | 1.5 | 0.5 | default recipe |
| `genre_first` | 4.0 | 0.5 | 1.0 | 0.25 | genre dominates |
| `mood_first` | 0.75 | 2.5 | 1.5 | 1.0 | vibe over label (valence 1.0) |
| `energy_focused` | 1.0 | 1.0 | 3.0 | 0.5 | the Phase 4 experiment: genre ½, energy ×2 |

### Diversity penalty

With `--diversity`, songs are picked one at a time. Each remaining song loses **1.0 for every pick by the same artist** and **0.5 for every pick in the same genre**. The penalty shows up as a reason in the table.

### Biases I expected before building

- Genre is worth the most points, so the system will **over-prioritize genre** and may bury a great song that matches the mood but has a different genre label.
- Exact-string matching means "indie pop" gets **zero** genre credit from a "pop" fan.
- Energy closeness is available to every song, so when nothing matches genre or mood, the list becomes "whatever has similar energy", regardless of style.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   python -m src.main                                     # all 7 profiles, balanced mode
   python -m src.main --profile chill_lofi                # one profile
   python -m src.main --mode mood_first                   # switch scoring mode
   python -m src.main --diversity                         # turn on the diversity penalty
   python -m src.main --profile high_energy_pop --compare-modes
   ```

   Profiles: `default_pop_happy`, `high_energy_pop`, `chill_lofi`, `deep_intense_rock`, `conflicted_sad_but_hyped`, `ghost_genre_kpop`, `acoustic_headbanger`.

### Running Tests

```bash
pytest
```

There are 8 tests covering CSV loading, closeness scoring, reasons, sort order, every scoring mode, and the diversity penalty.

---

## Sample Recommendation Output

Default "pop/happy" profile, `python -m src.main --profile default_pop_happy`:

```
=== Profile: default_pop_happy | mode: balanced ===
Prefs: genre=pop, mood=happy, energy=0.8
+---+-----------------+----------------+-----------+-------+------------------------------------+
| # | Title           | Artist         | Genre     | Score | Reasons                            |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 1 | Sunrise City    | Neon Echo      | pop       | 4.47  | genre match (+2.00)                |
|   |                 |                |           |       | mood match (+1.00)                 |
|   |                 |                |           |       | energy 0.82 vs target 0.80 (+1.47) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 2 | Gym Hero        | Max Pulse      | pop       | 3.31  | genre match (+2.00)                |
|   |                 |                |           |       | energy 0.93 vs target 0.80 (+1.30) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 3 | Rooftop Lights  | Indigo Parade  | indie pop | 2.44  | mood match (+1.00)                 |
|   |                 |                |           |       | energy 0.76 vs target 0.80 (+1.44) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 4 | Fuego Lento     | Los Brillantes | latin     | 1.50  | energy 0.80 vs target 0.80 (+1.50) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 5 | Concrete Verses | Block Theory   | hip hop   | 1.47  | energy 0.78 vs target 0.80 (+1.47) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
```

Output for every other profile is in the [model card](model_card.md#7-evaluation).

---

## Experiments You Tried

**1. Weight shift: genre ÷2, energy ×2** (`--mode energy_focused`, default pop/happy profile)

```
=== Profile: default_pop_happy | mode: energy_focused ===
Prefs: genre=pop, mood=happy, energy=0.8
+---+-----------------+----------------+-----------+-------+------------------------------------+
| # | Title           | Artist         | Genre     | Score | Reasons                            |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 1 | Sunrise City    | Neon Echo      | pop       | 4.94  | genre match (+1.00)                |
|   |                 |                |           |       | mood match (+1.00)                 |
|   |                 |                |           |       | energy 0.82 vs target 0.80 (+2.94) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 2 | Rooftop Lights  | Indigo Parade  | indie pop | 3.88  | mood match (+1.00)                 |
|   |                 |                |           |       | energy 0.76 vs target 0.80 (+2.88) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 3 | Gym Hero        | Max Pulse      | pop       | 3.61  | genre match (+1.00)                |
|   |                 |                |           |       | energy 0.93 vs target 0.80 (+2.61) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 4 | Fuego Lento     | Los Brillantes | latin     | 3.00  | energy 0.80 vs target 0.80 (+3.00) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
| 5 | Concrete Verses | Block Theory   | hip hop   | 2.94  | energy 0.78 vs target 0.80 (+2.94) |
+---+-----------------+----------------+-----------+-------+------------------------------------+
```

*Indie-pop* "Rooftop Lights" jumped from #3 to #2 and passed "Gym Hero". Energy gaps now cost twice as much, and Gym Hero (0.93) is further from 0.80 than Rooftop Lights (0.76). I think this is **more accurate** for a "happy pop" listener: Rooftop Lights *is* happy pop, it just has a different label. Positions 4–5 are still genre-less songs that only share an energy level, though, so the change made the list different, not uniformly better.

**2. Same conflicted user, every mode** (`--profile conflicted_sad_but_hyped --compare-modes`)

```
=== Profile: conflicted_sad_but_hyped | mode: balanced ===
| 1 | Pinewood Letters | Hollow Oak  | folk  | 4.05  | genre match (+2.00)                 |
| 2 | Crossroads Blue  | Delta Mae   | blues | 2.25  | mood match (+1.00)                  |
| 3 | Iron Cathedral   | Ashen Crown | metal | 1.89  | energy 0.97 vs target 0.90 (+1.40)  |
| 4 | Storm Runner     | Voltline    | rock  | 1.84  | energy 0.91 vs target 0.90 (+1.48)  |
| 5 | Gym Hero         | Max Pulse   | pop   | 1.67  | energy 0.93 vs target 0.90 (+1.46)  |
=== Profile: conflicted_sad_but_hyped | mode: genre_first ===
| 1 | Pinewood Letters | Hollow Oak  | folk      | 5.35  | genre match (+4.00)                 |
| 2 | Crossroads Blue  | Delta Mae   | blues     | 1.48  | mood match (+0.50)                  |
| 3 | Iron Cathedral   | Ashen Crown | metal     | 1.42  | energy 0.97 vs target 0.90 (+0.93)  |
| 4 | Storm Runner     | Voltline    | rock      | 1.35  | energy 0.91 vs target 0.90 (+0.99)  |
| 5 | Night Drive Loop | Neon Echo   | synthwave | 1.21  | energy 0.75 vs target 0.90 (+0.85)  |
=== Profile: conflicted_sad_but_hyped | mode: mood_first ===
| 1 | Pinewood Letters | Hollow Oak  | folk      | 4.75  | genre match (+0.75)                 |
| 2 | Crossroads Blue  | Delta Mae   | blues     | 4.17  | mood match (+2.50)                  |
| 3 | Iron Cathedral   | Ashen Crown | metal     | 2.38  | energy 0.97 vs target 0.90 (+1.40)  |
| 4 | Storm Runner     | Voltline    | rock      | 2.21  | energy 0.91 vs target 0.90 (+1.48)  |
| 5 | Night Drive Loop | Neon Echo   | synthwave | 1.99  | energy 0.75 vs target 0.90 (+1.27)  |
=== Profile: conflicted_sad_but_hyped | mode: energy_focused ===
| 1 | Pinewood Letters | Hollow Oak  | folk  | 3.65  | genre match (+1.00)                 |
| 2 | Storm Runner     | Voltline    | rock  | 3.33  | energy 0.91 vs target 0.90 (+2.97)  |
| 3 | Iron Cathedral   | Ashen Crown | metal | 3.28  | energy 0.97 vs target 0.90 (+2.79)  |
| 4 | Gym Hero         | Max Pulse   | pop   | 3.12  | energy 0.93 vs target 0.90 (+2.91)  |
| 5 | Crossroads Blue  | Delta Mae   | blues | 3.08  | mood match (+1.00)                  |
```

`energy_focused` lets loud rock and metal climb past the sad blues track. `mood_first` puts the two sad songs clearly on top. The mode you pick decides which half of a contradictory profile "wins".

**3. Diversity penalty** (`--profile chill_lofi --diversity`)

```
=== Profile: chill_lofi | mode: balanced + diversity ===
Prefs: genre=lofi, mood=chill, energy=0.35, likes_acoustic=True, mood_tags=['cozy', 'mellow'], instrumentalness=0.85
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| # | Title               | Artist         | Genre   | Score | Reasons                                      |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 1 | Library Rain        | Paper Lanterns | lofi    | 6.41  | genre match (+2.00)                          |
|   |                     |                |         |       | mood match (+1.00)                           |
|   |                     |                |         |       | energy 0.35 vs target 0.35 (+1.50)           |
|   |                     |                |         |       | acoustic fit (+0.43)                         |
|   |                     |                |         |       | mood tags cozy/mellow (+1.00)                |
|   |                     |                |         |       | instrumentalness 0.90 vs target 0.85 (+0.47) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 2 | Midnight Coding     | LoRoom         | lofi    | 5.75  | genre match (+2.00)                          |
|   |                     |                |         |       | mood match (+1.00)                           |
|   |                     |                |         |       | energy 0.42 vs target 0.35 (+1.40)           |
|   |                     |                |         |       | acoustic fit (+0.35)                         |
|   |                     |                |         |       | mood tags cozy/mellow (+1.00)                |
|   |                     |                |         |       | instrumentalness 0.85 vs target 0.85 (+0.50) |
|   |                     |                |         |       | genre already listed (-0.50)                 |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 3 | Spacewalk Thoughts  | Orbit Bloom    | ambient | 3.31  | mood match (+1.00)                           |
|   |                     |                |         |       | energy 0.28 vs target 0.35 (+1.40)           |
|   |                     |                |         |       | acoustic fit (+0.46)                         |
|   |                     |                |         |       | instrumentalness 0.95 vs target 0.85 (+0.45) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 4 | Focus Flow          | LoRoom         | lofi    | 2.80  | genre match (+2.00)                          |
|   |                     |                |         |       | energy 0.40 vs target 0.35 (+1.42)           |
|   |                     |                |         |       | acoustic fit (+0.39)                         |
|   |                     |                |         |       | mood tags mellow (+0.50)                     |
|   |                     |                |         |       | instrumentalness 0.88 vs target 0.85 (+0.48) |
|   |                     |                |         |       | artist already listed (-1.00)                |
|   |                     |                |         |       | genre already listed (-1.00)                 |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 5 | Coffee Shop Stories | Slow Stereo    | jazz    | 2.79  | energy 0.37 vs target 0.35 (+1.47)           |
|   |                     |                |         |       | acoustic fit (+0.45)                         |
|   |                     |                |         |       | mood tags cozy (+0.50)                       |
|   |                     |                |         |       | instrumentalness 0.60 vs target 0.85 (+0.38) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
```

Without the penalty, the top 3 are all lofi, and two are by LoRoom. With it, "Focus Flow" (second LoRoom track, third lofi track) drops from #3 to #4 and ambient "Spacewalk Thoughts" moves up to #3.

---

## Limitations and Risks

- **Tiny catalog**: 20 songs, and most genres have only 1 song. Someone who likes reggae gets one match and then filler.
- **Exact-match labels**: "pop" ≠ "indie pop", "chill" ≠ "relaxed". The system has no idea which genres or moods are related.
- **Energy is a universal fallback**: with no genre or mood match, the ranking turns into "songs with similar energy", which mixes metal, EDM, and pop together.
- **No listening history, lyrics, or language**: it cannot learn and it cannot tell a breakup song from a party song unless the tags say so.
- **Contradictions are resolved by weights, not understanding**: a "sad but high-energy" user gets a quiet folk song first because genre + mood points outweigh energy.

See the [model card](model_card.md) for the full analysis.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Building this showed me that a "recommendation" is just a score plus a sort. Nothing in the code understands music. It adds up points for matching labels and for numbers being close together, and yet the top results for clear profiles like "chill lofi" or "intense rock" feel right. Putting reasons next to each score was the most useful decision. It made every surprise easy to trace back to a specific weight, like Gym Hero showing up for both happy-pop and intense-rock users because it matches pop *and* intense *and* very high energy.

Bias shows up in quiet ways. The weights are my opinion of what matters (genre counts twice as much as mood), and the catalog decides who gets served well. Pop and lofi fans get several good matches. Fans of genres with one song, or of genres not in the data at all like k-pop, get filler ranked by energy alone. A real platform with the same structure but millions of users would turn those design choices into filter bubbles at scale. That is why diversity re-ranking and being open about "why you're seeing this" matter.
