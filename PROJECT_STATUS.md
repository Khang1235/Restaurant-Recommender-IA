# CS IA — Restaurant Recommender: Project Status

Last updated: 2026-10-13 (package v7)

## Where things stand

**The product runs end to end.** All assessed functions are implemented.
23 tests pass (15 pipeline, 8 accounts).

**Architecture:** `desktop.py` starts Flask on a free local port on a
background thread and shows the pages in a native pywebview window. The
tkinter version (`main.py`, `gui.py`, `login_gui.py`) was removed in v6 so
there is only one file to run. The processing modules are unchanged by that
move.

**Dataset:** 222 restaurants across 6 Northern Vietnam cities
(Hanoi 61, Hai Phong 35, Sapa 34, Ninh Binh 31, Nam Dinh 31, Ha Long 30),
8 food categories.

**Verification:** 85 of 222 verified against Google Places
(83 clean match, 2 thin data cross-checked against guides, 0 unresolved
mismatches). 135 pending.

**Scope:** single-destination recommendation with budget-constrained course
generation, behind a sign-in. The route/journey extension (multi-city travel,
departure times, meal scheduling) is **not** implemented — see the scope note
in `README.md`. Criterion A matches the implemented scope.

**Packaging:** `RestaurantRecommender.spec` and `build_windows.bat` build a
standalone Windows `.exe` with PyInstaller. `paths.py` keeps read-only files
(templates, stylesheet, CSV) separate from the writable database so both
work packaged and from source. Optional — it earns no marks.

## Verified behaviour

Checked against the real dataset:

| Case | Result |
|---|---|
| `load_from_csv` first run | 222 inserted |
| `load_from_csv` second run | 0 inserted (edits preserved) |
| Hanoi, 300,000 VND, 3 meals | 3 picked, 260,000 spent |
| Hanoi, 300,000 VND, 3 meals, Street food | 3 picked, 125,000 spent |
| Ninh Binh, 150,000 VND, 3 meals | 3 picked, 125,000 spent |
| Hanoi, 600,000 VND, 10 meals | 10 picked, exactly 600,000 spent |
| Hanoi, 300,000 VND, 10 meals | 0 picked — genuinely infeasible (10 cheapest sum to 405,000) |
| `edit_restaurant` with a bad column name | `ValueError`, no SQL executed |
| Register, sign in, generate course | All routes return 200/302 as expected |
| Same, run from a frozen PyInstaller bundle in an unrelated folder | 222 rows load, page renders |

## Known limitations (Criterion E material)

**135 restaurants share one adjusted rating.** Unverified rows carry
`review_count = 0`, so the Bayesian formula returns exactly the dataset mean
for every one of them. They cannot be ordered relative to each other; the
tiebreak in `rank_restaurants` decides the order. Impact is very uneven:

| City | Total | Tied | Share |
|---|---|---|---|
| Hanoi | 61 | 8 | 13% |
| Hai Phong | 35 | 23 | 66% |
| Sapa | 34 | 26 | 76% |
| Nam Dinh | 31 | 26 | 84% |
| Ninh Binh | 31 | 27 | 87% |
| Ha Long | 30 | 27 | 90% |

In Ha Long the ranking is close to inert — 90% of the candidate pool is a
single tied block. In Hanoi it works as designed. This is the strongest
evaluation point available and it can be stated with numbers.

**Soft preference ranking is visible to the user.** Because preference is a
40% ranking signal rather than a hard filter, asking for Seafood in Ha Long
returns a Cafe in the third slot. Deliberate (see `DECISIONS_LOG.md` D4.1),
but it looks like a bug unless the interface explains it.

**Greedy course generation is not optimal.** It takes the highest-scoring
feasible restaurant at each slot. A cheaper early pick could sometimes fund a
better later one. Constructing a concrete example from the dataset would
strengthen Criterion E.

**Low review count does not mean low quality.** Two thin-data entries are
well-known local institutions that attract few online reviews.
`MIN_REVIEWS = 50` penalises exactly these — a real trade-off, not a pure
improvement.

**Google Places lookups were wrong 13% of the time.** 11 of the first 87
returned the wrong branch, the wrong city, or a similarly-named different
business. Each was resolved individually rather than accepted. This is a
method finding worth stating in E.

**Platforms disagree.** One restaurant showed 999+ reviews on one platform and
3 on another, because they measure different things (delivery orders vs
reviews).

**Category coverage is uneven by design.** Ninh Binh has no seafood
(landlocked), Ha Long no street food (resort city), Nam Dinh is heavily street
food (pho heartland). Preference ranking does less work where one category
dominates.

## Still to do

**Writing — this is where the remaining marks are:**

| Criterion | Marks | State |
|---|---|---|
| A — Problem specification | 4 | Done, 317 words, SC1–SC7 |
| B — Planning | 4 | Done, 149 words |
| C — System overview | 6 | Done, 151 words prose, 4 figures, 5 algorithms, 22-row test table |
| **D — Development** | **12** | **Not drafted.** 1,000 words. Biggest single block of marks in the IA. |
| **E — Evaluation** | **4** | **Not drafted.** 400 words. Evaluate SC1–SC7, then justify improvements. |

Total documentation cap is 2,000 words, stated on page 1.

**Before submission:**
- Replace `[Replace with the exact wording your school requires.]` in the
  acknowledgement block of `auth.py`, `app.py`, `desktop.py`, `paths.py`,
  `RestaurantRecommender.spec` and the templates.
- Fill in the AI tool use table in `AI_USE_ACKNOWLEDGEMENT.md`.
- Record the video showing the tests and the demo cases above.
- Check pywebview opens a window on the actual demo machine.

**Dataset:** 135 rows pending verification. Low direct mark value — this is
Criterion E material and there is already enough documented. Do not let it eat
writing time.

## Files

| File | What it is |
|---|---|
| `desktop.py` | Entry point — free port, Flask thread, native window |
| `app.py` | Flask routes, sessions, page rendering |
| `paths.py` | File locations, source vs packaged |
| `templates/`, `static/style.css` | Sign-in, register and main pages |
| `auth.py` | Accounts, PBKDF2 password hashing, sign-in |
| `restaurant.py` | Restaurant dataclass with Bayesian `adjusted_rating()` |
| `database.py` | SQLite layer, CSV loader, whitelisted `edit_restaurant` |
| `filters.py` | Location / budget / preference filters |
| `ranking.py` | Scoring and sorting with deterministic tiebreak |
| `course_generator.py` | Greedy course builder with cheapest-completion reservation |
| `budget.py` | Spending calculations |
| `validation.py` | Input validation |
| `test_recommender.py` | 15 passing tests |
| `test_auth.py` | 8 passing tests |
| `merge_google.py` | Merges verification batches; lists pending rows |
| `google_batches/` | Verification results — **only `batch10.json` is present** |
| `RestaurantRecommender.spec`, `build_windows.bat` | Optional executable build |
| `DECISIONS_LOG.md` | Design decisions D1.1–D8, keyed for Criterion D |
| `HOW_TO_RUN.md` | Setup, running, packaging, and the stale-database trap |
| `AI_USE_ACKNOWLEDGEMENT.md` | Template — must be completed before submission |

**Note:** `google_batches/batch01.json` through `batch09.json` are missing from
this package. `merge_google.py` will only re-apply batch10, so the other
verification results exist in the CSV but not in reproducible form. Find those
files before doing any more verification work.
