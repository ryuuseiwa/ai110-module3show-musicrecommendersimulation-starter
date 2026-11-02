# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I gave Claude Code (agent mode in VS Code) the full project spec (the "Show What You Know: Music Recommender Simulation" PDF) and asked it to complete every phase plus all four optional challenges. That covered: expanding the dataset, implementing `load_songs` / `score_song` / `recommend_songs`, adding 5+ advanced features (Challenge 1), multiple scoring modes (Challenge 2), a diversity penalty (Challenge 3), and a formatted table (Challenge 4), then documenting everything.

**Prompts used:**

- "can you do whatever is asked here + the optional? thank you" (with the project PDF attached)
- The spec's own prompts guided the work, for example: use the `csv` module and convert numeric fields to numbers, score numeric features by *closeness* to the user's target rather than by size, return a numeric score *and* a list of reasons, and suggest adversarial profiles such as "energy 0.9 + mood sad".

**What did the agent generate or change?**

- `data/songs.csv`: added 10 songs in 10 new genres and 5 new columns (`popularity`, `release_decade`, `mood_tags`, `instrumentalness`, `liveness`).
- `src/recommender.py`: CSV loader, closeness-based `score_song` that returns `(score, reasons)`, `recommend_songs` using `sorted()` with deterministic tie-breaking, the `ScoringMode` strategies, the greedy diversity re-rank, and the `Recommender` / `UserProfile` OOP wrapper used by the tests.
- `src/main.py`: 7 profiles (4 normal, 3 adversarial), CLI flags (`--profile`, `--mode`, `--diversity`, `--compare-modes`, `-k`), and an ASCII table renderer that prints one reason per line.
- `tests/test_recommender.py`: 6 new tests.
- `README.md`, `model_card.md`, and this file, with the terminal output pasted in from real runs.
- Commands it ran: created `.venv`, installed `pytest`, ran `pytest` and `python -m src.main` with different flags, and made several git commits.

**What did you verify or fix manually?**

- **Import bug in the starter:** `src/main.py` used `from recommender import ...`, which crashes under `python -m src.main`. Fixed to `from src.recommender import ...`, with a fallback for `python src/main.py`.
- **Feature coverage:** the first version loaded `instrumentalness` and `liveness` but did not score them, which does not meet Challenge 1 ("scoring accounts for the new attributes"). Added both as optional closeness targets and re-ran everything.
- **Math checks:** checked score totals by hand against the reasons, for example Sunrise City = 2.00 + 1.00 + 1.47 = 4.47, and that diversity penalties were subtracted correctly (Focus Flow: −1.00 artist, −1.00 for two earlier lofi picks).
- **Backward compatibility:** new `Song` / `UserProfile` fields have defaults, so the original starter tests still build `Song(...)` without them. All 8 tests pass.
- **Docs match reality:** every output block in the README and model card is pasted from an actual run, not written by hand.

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

**Strategy pattern**, in a lightweight form based on data.

**How did AI help you brainstorm or implement it?**

Two options came up. The first was a classic Strategy: an abstract `Scorer` base class with `GenreFirstScorer`, `MoodFirstScorer`, and so on, each overriding `score()`. The second was a single scoring algorithm with each strategy as a **frozen dataclass of weights**. All four requested modes ("Genre-First", "Mood-First", "Energy-Focused", plus the default) use the *same* rules with *different* emphasis, so subclasses would have copied the same scoring code four times. We picked the weights-object version. It keeps `score_song` in one place, makes a new mode a one-line addition, and makes the Phase 4 "weight shift" experiment a mode of its own (`energy_focused`) instead of a temporary code edit.

**How does the pattern appear in your final code?**

- `ScoringMode` dataclass in [src/recommender.py](src/recommender.py): the strategy (one weight per feature).
- `SCORING_MODES` dict: the registry of available strategies (`balanced`, `genre_first`, `mood_first`, `energy_focused`).
- `score_song(user_prefs, song, mode)` looks up the strategy by name and applies its weights. `recommend_songs` and `Recommender` just pass the mode through.
- `src/main.py` exposes it as `--mode <name>` and `--compare-modes`, so a user can switch strategies without touching code.
