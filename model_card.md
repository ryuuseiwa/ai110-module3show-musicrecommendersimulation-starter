# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0**

---

## 2. Intended Use  

VibeFinder suggests the top 5 songs from a small catalog for a listener who describes their taste: a favorite genre, a favorite mood, and how energetic they want the music to be. They can also give mood tags, a popularity level, a decade, and how acoustic, instrumental, or "live" they like their music.

It assumes the user knows what they want and can say it in these labels. It does not learn from listening history.

**Intended use:** classroom exploration of how recommenders turn data into ranked suggestions, and of where bias comes from.

**Not intended for:** real users, real products, or any decision that matters. The catalog is 20 made-up songs, and the weights are hand-picked opinions, not learned from data. It should not be used to judge which artists or genres are "better".

---

## 3. How the Model Works  

Think of it as a judge holding a scorecard. For every song in the catalog, the judge gives points:

- **2 points** if the song's genre is exactly the user's favorite genre.
- **1 point** if the mood matches exactly.
- **Up to 1.5 points** for energy, based on how *close* the song is to the energy the user asked for. A perfect match gets all 1.5. A song that is far off gets close to nothing. Being louder is not automatically better.
- **Small bonuses (up to 0.5 each)** for matching mood tags like "cozy" or "euphoric", for popularity, decade, and happiness level (valence) close to what the user wants, for being acoustic (or electric) as the user prefers, and for instrumentalness and liveness.

Every time the judge gives points, it writes down why, for example "genre match (+2.00)". Once every song has a score, the songs are sorted from highest to lowest and the top 5 are shown with their reasons.

**Changes from the starter:** the starter had no logic. I added the five extra song features, the closeness-based scoring, a reasons list, four switchable "scoring modes" that use different weights (genre-first, mood-first, energy-focused, balanced), and an optional diversity rule. That rule takes points away from a song when its artist or genre is already in the list.

---

## 4. Data  

- **20 songs** in `data/songs.csv`. The starter had 10. I added 10 more to cover genres and moods that were missing: hip hop, metal, classical, country, r&b, edm, reggae, folk, blues, and latin, plus moods like angry, melancholic, nostalgic, romantic, euphoric, sad, and playful.
- **Features:** genre, mood, energy, tempo, valence, danceability, acousticness, and five new ones: popularity (0–100), release decade, detailed mood tags, instrumentalness, and liveness.
- **Limits:** 14 different genres for 20 songs, so most genres have exactly **one** song. Only lofi (3 songs) and pop (2, plus "indie pop") have more than one. The numbers were written by hand, not measured from real audio. There is no k-pop, Bollywood, Afrobeats, gospel, or anything non-English-labeled, and nothing about lyrics, language, or culture.

---

## 5. Strengths  

- **Clear, single-genre tastes work well.** "Chill Lofi" gets three lofi tracks, then ambient and jazz, which is a playlist I would actually listen to. "Deep Intense Rock" puts Storm Runner first and metal second, which feels right.
- **Closeness scoring works as intended.** For a user who wants 0.35 energy, a 0.35 song earns more than a 0.90 song. It does not just favor the loudest songs.
- **Every recommendation is explainable.** The reasons column shows exactly which features earned points, so surprises are easy to debug.
- **Mood tags help a lot.** For High-Energy Pop, they pull the EDM track "Laser Bloom" (euphoric, bright) into the top 4 even though its genre does not match. That is a sensible cross-genre suggestion.

---

## 6. Limitations and Bias 

**Main weakness: genre labels are an all-or-nothing gate, and the catalog is uneven.** A genre match is worth 2 points, the most of any single rule, but it only counts if the label matches *exactly*. "Rooftop Lights" is a happy, upbeat song tagged "indie pop", yet a "pop" fan gives it zero genre credit. A user whose genre is missing (I tested "k-pop") never gets genre points at all. Their list becomes "anything with similar energy": synthwave, hip hop, and latin next to each other. Because most genres have only one song, a fan of a minority genre like reggae or blues gets one real match and four fillers, while lofi and pop fans get several strong matches. The system quietly serves "majority" tastes better. This is a filter bubble in miniature: whatever labels and genres are common in the data decide whose recommendations feel good.

Other issues I noticed:

- **Energy is a universal fallback.** Every song earns some energy points, so very loud songs (Gym Hero, Laser Bloom, Iron Cathedral) appear in many high-energy lists regardless of style.
- **Contradictory tastes get resolved by weight, not understanding.** A "sad but high-energy" user gets a quiet folk song first because genre + mood (3 points) beat energy (1.5 points).
- **Preferences that are ignored stay ignored.** An "acoustic headbanger" (metal + likes acoustic) gets almost no acoustic credit (+0.01), because no metal song in the data is acoustic. The system cannot tell the user that their combination does not exist in the catalog.
- **Tempo and danceability are not scored**, so two songs with the same energy but very different tempos look the same.

---

## 7. Evaluation  

I tested **7 profiles**: 3 normal ones (High-Energy Pop, Chill Lofi, Deep Intense Rock), the starter's default pop/happy profile, and 3 adversarial ones designed to trick the scoring:

- **Conflicted**: folk, sad, but energy 0.9 and valence 0.2
- **Ghost genre**: k-pop, a genre that is not in the catalog
- **Acoustic headbanger**: metal and angry, but likes acoustic music

For each one I looked at whether the top 5 "felt" right and read the reasons column to see which rule was driving the ranking. I also ran the experiments described in the README: a weight shift, all four modes on the same user, and the diversity penalty. Finally, I added 6 automated tests on top of the 2 starter tests.

### Outputs (balanced mode)

**High-Energy Pop**
```
=== Profile: high_energy_pop | mode: balanced ===
Prefs: genre=pop, mood=happy, energy=0.9, likes_acoustic=False, mood_tags=['euphoric', 'bright'], popularity=85
+---+----------------+---------------+-----------+-------+------------------------------------+
| # | Title          | Artist        | Genre     | Score | Reasons                            |
+---+----------------+---------------+-----------+-------+------------------------------------+
| 1 | Sunrise City   | Neon Echo     | pop       | 6.25  | genre match (+2.00)                |
|   |                |               |           |       | mood match (+1.00)                 |
|   |                |               |           |       | energy 0.82 vs target 0.90 (+1.38) |
|   |                |               |           |       | electric/produced fit (+0.41)      |
|   |                |               |           |       | mood tags euphoric/bright (+1.00)  |
|   |                |               |           |       | popularity 78 vs target 85 (+0.46) |
+---+----------------+---------------+-----------+-------+------------------------------------+
| 2 | Gym Hero       | Max Pulse     | pop       | 4.92  | genre match (+2.00)                |
|   |                |               |           |       | energy 0.93 vs target 0.90 (+1.46) |
|   |                |               |           |       | electric/produced fit (+0.47)      |
|   |                |               |           |       | mood tags euphoric (+0.50)         |
|   |                |               |           |       | popularity 84 vs target 85 (+0.49) |
+---+----------------+---------------+-----------+-------+------------------------------------+
| 3 | Rooftop Lights | Indigo Parade | indie pop | 3.52  | mood match (+1.00)                 |
|   |                |               |           |       | energy 0.76 vs target 0.90 (+1.29) |
|   |                |               |           |       | electric/produced fit (+0.33)      |
|   |                |               |           |       | mood tags bright (+0.50)           |
|   |                |               |           |       | popularity 66 vs target 85 (+0.41) |
+---+----------------+---------------+-----------+-------+------------------------------------+
| 4 | Laser Bloom    | Kiloherz      | edm       | 3.40  | energy 0.95 vs target 0.90 (+1.43) |
|   |                |               |           |       | electric/produced fit (+0.49)      |
|   |                |               |           |       | mood tags euphoric/bright (+1.00)  |
|   |                |               |           |       | popularity 88 vs target 85 (+0.48) |
+---+----------------+---------------+-----------+-------+------------------------------------+
| 5 | Storm Runner   | Voltline      | rock      | 2.29  | energy 0.91 vs target 0.90 (+1.48) |
|   |                |               |           |       | electric/produced fit (+0.45)      |
|   |                |               |           |       | popularity 55 vs target 85 (+0.35) |
+---+----------------+---------------+-----------+-------+------------------------------------+
```

**Chill Lofi**
```
=== Profile: chill_lofi | mode: balanced ===
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
| 2 | Midnight Coding     | LoRoom         | lofi    | 6.25  | genre match (+2.00)                          |
|   |                     |                |         |       | mood match (+1.00)                           |
|   |                     |                |         |       | energy 0.42 vs target 0.35 (+1.40)           |
|   |                     |                |         |       | acoustic fit (+0.35)                         |
|   |                     |                |         |       | mood tags cozy/mellow (+1.00)                |
|   |                     |                |         |       | instrumentalness 0.85 vs target 0.85 (+0.50) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 3 | Focus Flow          | LoRoom         | lofi    | 4.80  | genre match (+2.00)                          |
|   |                     |                |         |       | energy 0.40 vs target 0.35 (+1.42)           |
|   |                     |                |         |       | acoustic fit (+0.39)                         |
|   |                     |                |         |       | mood tags mellow (+0.50)                     |
|   |                     |                |         |       | instrumentalness 0.88 vs target 0.85 (+0.48) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 4 | Spacewalk Thoughts  | Orbit Bloom    | ambient | 3.31  | mood match (+1.00)                           |
|   |                     |                |         |       | energy 0.28 vs target 0.35 (+1.40)           |
|   |                     |                |         |       | acoustic fit (+0.46)                         |
|   |                     |                |         |       | instrumentalness 0.95 vs target 0.85 (+0.45) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
| 5 | Coffee Shop Stories | Slow Stereo    | jazz    | 2.79  | energy 0.37 vs target 0.35 (+1.47)           |
|   |                     |                |         |       | acoustic fit (+0.45)                         |
|   |                     |                |         |       | mood tags cozy (+0.50)                       |
|   |                     |                |         |       | instrumentalness 0.60 vs target 0.85 (+0.38) |
+---+---------------------+----------------+---------+-------+----------------------------------------------+
```

**Deep Intense Rock**
```
=== Profile: deep_intense_rock | mode: balanced ===
Prefs: genre=rock, mood=intense, energy=0.92, likes_acoustic=False, mood_tags=['aggressive', 'rebellious'], decade=2000s, liveness=0.35
+---+----------------+-------------+-------+-------+-----------------------------------------+
| # | Title          | Artist      | Genre | Score | Reasons                                 |
+---+----------------+-------------+-------+-------+-----------------------------------------+
| 1 | Storm Runner   | Voltline    | rock  | 6.67  | genre match (+2.00)                     |
|   |                |             |       |       | mood match (+1.00)                      |
|   |                |             |       |       | energy 0.91 vs target 0.92 (+1.48)      |
|   |                |             |       |       | electric/produced fit (+0.45)           |
|   |                |             |       |       | mood tags aggressive/rebellious (+1.00) |
|   |                |             |       |       | liveness 0.31 vs target 0.35 (+0.24)    |
|   |                |             |       |       | from the 2000s (+0.50)                  |
+---+----------------+-------------+-------+-------+-----------------------------------------+
| 2 | Iron Cathedral | Ashen Crown | metal | 3.66  | energy 0.97 vs target 0.92 (+1.43)      |
|   |                |             |       |       | electric/produced fit (+0.48)           |
|   |                |             |       |       | mood tags aggressive/rebellious (+1.00) |
|   |                |             |       |       | liveness 0.35 vs target 0.35 (+0.25)    |
|   |                |             |       |       | from the 2000s (+0.50)                  |
+---+----------------+-------------+-------+-------+-----------------------------------------+
| 3 | Gym Hero       | Max Pulse   | pop   | 3.16  | mood match (+1.00)                      |
|   |                |             |       |       | energy 0.93 vs target 0.92 (+1.48)      |
|   |                |             |       |       | electric/produced fit (+0.47)           |
|   |                |             |       |       | liveness 0.15 vs target 0.35 (+0.20)    |
+---+----------------+-------------+-------+-------+-----------------------------------------+
| 4 | Laser Bloom    | Kiloherz    | edm   | 2.18  | energy 0.95 vs target 0.92 (+1.46)      |
|   |                |             |       |       | electric/produced fit (+0.49)           |
|   |                |             |       |       | liveness 0.40 vs target 0.35 (+0.24)    |
+---+----------------+-------------+-------+-------+-----------------------------------------+
| 5 | Sunrise City   | Neon Echo   | pop   | 1.95  | energy 0.82 vs target 0.92 (+1.35)      |
|   |                |             |       |       | electric/produced fit (+0.41)           |
|   |                |             |       |       | liveness 0.12 vs target 0.35 (+0.19)    |
+---+----------------+-------------+-------+-------+-----------------------------------------+
```

**Conflicted (sad but hyped)**
```
=== Profile: conflicted_sad_but_hyped | mode: balanced ===
Prefs: genre=folk, mood=sad, energy=0.9, valence=0.2
+---+------------------+-------------+-------+-------+-------------------------------------+
| # | Title            | Artist      | Genre | Score | Reasons                             |
+---+------------------+-------------+-------+-------+-------------------------------------+
| 1 | Pinewood Letters | Hollow Oak  | folk  | 4.05  | genre match (+2.00)                 |
|   |                  |             |       |       | mood match (+1.00)                  |
|   |                  |             |       |       | energy 0.30 vs target 0.90 (+0.60)  |
|   |                  |             |       |       | valence 0.30 vs target 0.20 (+0.45) |
+---+------------------+-------------+-------+-------+-------------------------------------+
| 2 | Crossroads Blue  | Delta Mae   | blues | 2.25  | mood match (+1.00)                  |
|   |                  |             |       |       | energy 0.45 vs target 0.90 (+0.83)  |
|   |                  |             |       |       | valence 0.35 vs target 0.20 (+0.43) |
+---+------------------+-------------+-------+-------+-------------------------------------+
| 3 | Iron Cathedral   | Ashen Crown | metal | 1.89  | energy 0.97 vs target 0.90 (+1.40)  |
|   |                  |             |       |       | valence 0.22 vs target 0.20 (+0.49) |
+---+------------------+-------------+-------+-------+-------------------------------------+
| 4 | Storm Runner     | Voltline    | rock  | 1.84  | energy 0.91 vs target 0.90 (+1.48)  |
|   |                  |             |       |       | valence 0.48 vs target 0.20 (+0.36) |
+---+------------------+-------------+-------+-------+-------------------------------------+
| 5 | Gym Hero         | Max Pulse   | pop   | 1.67  | energy 0.93 vs target 0.90 (+1.46)  |
|   |                  |             |       |       | valence 0.77 vs target 0.20 (+0.21) |
+---+------------------+-------------+-------+-------+-------------------------------------+
```

**Ghost genre (k-pop)**
```
=== Profile: ghost_genre_kpop | mode: balanced ===
Prefs: genre=k-pop, mood=happy, energy=0.7
+---+------------------+----------------+-----------+-------+------------------------------------+
| # | Title            | Artist         | Genre     | Score | Reasons                            |
+---+------------------+----------------+-----------+-------+------------------------------------+
| 1 | Rooftop Lights   | Indigo Parade  | indie pop | 2.41  | mood match (+1.00)                 |
|   |                  |                |           |       | energy 0.76 vs target 0.70 (+1.41) |
+---+------------------+----------------+-----------+-------+------------------------------------+
| 2 | Sunrise City     | Neon Echo      | pop       | 2.32  | mood match (+1.00)                 |
|   |                  |                |           |       | energy 0.82 vs target 0.70 (+1.32) |
+---+------------------+----------------+-----------+-------+------------------------------------+
| 3 | Night Drive Loop | Neon Echo      | synthwave | 1.43  | energy 0.75 vs target 0.70 (+1.42) |
+---+------------------+----------------+-----------+-------+------------------------------------+
| 4 | Concrete Verses  | Block Theory   | hip hop   | 1.38  | energy 0.78 vs target 0.70 (+1.38) |
+---+------------------+----------------+-----------+-------+------------------------------------+
| 5 | Fuego Lento      | Los Brillantes | latin     | 1.35  | energy 0.80 vs target 0.70 (+1.35) |
+---+------------------+----------------+-----------+-------+------------------------------------+
```

**Acoustic headbanger**
```
=== Profile: acoustic_headbanger | mode: balanced ===
Prefs: genre=metal, mood=angry, energy=0.95, likes_acoustic=True
+---+----------------+----------------+-------+-------+------------------------------------+
| # | Title          | Artist         | Genre | Score | Reasons                            |
+---+----------------+----------------+-------+-------+------------------------------------+
| 1 | Iron Cathedral | Ashen Crown    | metal | 4.49  | genre match (+2.00)                |
|   |                |                |       |       | mood match (+1.00)                 |
|   |                |                |       |       | energy 0.97 vs target 0.95 (+1.47) |
|   |                |                |       |       | acoustic fit (+0.01)               |
+---+----------------+----------------+-------+-------+------------------------------------+
| 2 | Laser Bloom    | Kiloherz       | edm   | 1.51  | energy 0.95 vs target 0.95 (+1.50) |
|   |                |                |       |       | acoustic fit (+0.01)               |
+---+----------------+----------------+-------+-------+------------------------------------+
| 3 | Gym Hero       | Max Pulse      | pop   | 1.50  | energy 0.93 vs target 0.95 (+1.47) |
|   |                |                |       |       | acoustic fit (+0.03)               |
+---+----------------+----------------+-------+-------+------------------------------------+
| 4 | Storm Runner   | Voltline       | rock  | 1.49  | energy 0.91 vs target 0.95 (+1.44) |
|   |                |                |       |       | acoustic fit (+0.05)               |
+---+----------------+----------------+-------+-------+------------------------------------+
| 5 | Fuego Lento    | Los Brillantes | latin | 1.43  | energy 0.80 vs target 0.95 (+1.28) |
|   |                |                |       |       | acoustic fit (+0.15)               |
+---+----------------+----------------+-------+-------+------------------------------------+
```

### Comparing profiles (in plain language)

- **High-Energy Pop vs Chill Lofi:** these share *no* songs. The pop list is full of loud, produced tracks (energy 0.76–0.95). The lofi list is quiet, acoustic, and mostly instrumental (energy 0.28–0.42). This is what should happen: energy and acoustic preferences point in opposite directions, so the two users get opposite lists.
- **High-Energy Pop vs Deep Intense Rock:** both want loud music, so they overlap on Gym Hero, Laser Bloom, Storm Runner, and Sunrise City. What changes is the *order*. Genre and mood decide which song is #1 (Sunrise City vs Storm Runner), and energy fills in the rest.
- **Why does "Gym Hero" keep showing up?** It is #2 for pop fans *and* #3 for rock fans. To a non-programmer: Gym Hero is labeled "pop", its mood is "intense", and it is one of the most energetic songs in the catalog. A pop fan gets 2 points for the genre. A rock fan gets 1 point for the "intense" mood. Both get almost full energy points. It is the song that is "close enough" to many people at once, the same way a catchy gym anthem might show up in lots of real playlists.
- **Chill Lofi vs Conflicted:** both have quiet songs near the top, but for different reasons. Chill Lofi *asks* for low energy. The conflicted user asked for 0.9 energy but still gets quiet folk first because their genre and mood both point at a slow song. After #2, the conflicted list flips to metal and rock because only energy is left to match.
- **Deep Intense Rock vs Acoustic Headbanger:** both lists are led by the one song that matches their genre. After #1 they share loud songs (Laser Bloom, Gym Hero, Storm Runner). The "likes acoustic" preference makes almost no difference, because there are no loud acoustic songs to reward.
- **Default pop/happy vs Ghost genre (k-pop):** both want happy, upbeat music, and they get many of the same songs. But without a genre match, k-pop's top score is only 2.41 (vs 4.47), and #3–#5 are synthwave, hip hop, and latin that only share an energy level. The k-pop user is served by accident, not by design.

### What surprised me

- **"Rooftop Lights" (indie pop) beat "Sunrise City" (pop) for the k-pop user**, because 0.76 energy is closer to 0.70 than 0.82 is. It came down to a few hundredths of a point.
- **Halving genre and doubling energy** (the `energy_focused` mode) moved indie-pop Rooftop Lights above Gym Hero for the pop/happy user. That felt *more* accurate, a happy song for a happy-pop fan, but it also made genre-less filler score almost as high as real matches. It changed the list more than it improved it.
- **The diversity penalty** was the change that felt most like a real app. Chill Lofi with diversity on pushes the second LoRoom track (and third lofi song) below an ambient track, so the top 3 are no longer all one genre.

---

## 8. Future Work  

1. **Related genres and moods.** Give partial credit for neighbors (pop ↔ indie pop ↔ k-pop, chill ↔ relaxed ↔ calm) instead of exact-match-or-nothing.
2. **Tell the user when their taste is not in the catalog.** If the best score is low, say so ("no k-pop yet, here are close matches by vibe") instead of quietly showing filler.
3. **Learn from feedback.** Track likes and skips per session and nudge the weights. That would be a first step toward collaborative filtering once there are multiple users.
4. **Use tempo and danceability**, and let users give a range ("80–100 BPM") rather than one number.

---

## 9. Personal Reflection  

**Biggest learning moment:** realizing that "recommending" is literally scoring plus sorting. Once the scoring rule and the ranking rule were separated, everything else (modes, diversity, explanations) was a small change on top. The scoring rule judges one song. The ranking rule compares all of them.

**How AI tools helped, and where I had to double-check:** an AI coding assistant (Claude Code) wrote most of the code, the extra songs, and the first draft of these docs. It was fast, but I still had to verify things myself. I ran every profile and read the reasons column to make sure the math added up (for example 2.00 + 1.00 + 1.47 = 4.47). I checked that the added songs were valid CSV with numbers in range. I confirmed that the `python -m src.main` import path actually worked, because the starter's `from recommender import` would have crashed. I also caught that two of the "advanced" features were loaded but not yet used in scoring, and had them added. The comparisons and claims in this card are based on the actual terminal output, not on what the AI predicted the output would be.

**What surprised me about simple algorithms:** a handful of if-statements and one subtraction already "feel" like a recommender for clear tastes. The Chill Lofi list is genuinely good. But it falls apart in exactly the places a human would not: labels that are slightly different, tastes that contradict each other, and genres the data forgot.

**What I'd try next:** partial-credit genre similarity, a "you might also like" slot that deliberately picks something outside the user's genre, and a tiny fake user-history dataset to try collaborative filtering and compare it against this content-based version.
