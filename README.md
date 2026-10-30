# Northern Vietnam Restaurant Recommender

## Run

1. Install the two dependencies: `pip install -r requirements.txt`
2. Run: `python desktop.py`
3. The application opens in its own window.
4. Create an account, then sign in.
5. Select a destination, enter the total budget in VND, tick any food preferences, and set the number of meals (1-10).

`desktop.py` is the only file run directly. It starts Flask on a free local port on a background thread and displays the pages in a native window; nothing is exposed outside the machine and no browser opens.

The SQLite database is created automatically on the first run and kept between runs, so records edited through `edit_restaurant` are not overwritten. Run from source it lives at `data/restaurants.db`; run from a packaged executable it moves to a per-user application folder, because the bundle is temporary and read-only (`paths.py`).

See `HOW_TO_RUN.md` for setup in detail, for publishing to GitHub, and for building a standalone Windows executable.

## Implementation choices

- The application opens on a sign-in screen. Passwords are never stored: each account keeps a random 16-byte salt and a PBKDF2-HMAC-SHA256 hash (100,000 iterations), both from the standard library.
- A failed sign-in returns the same message whether the username is unknown or the password is wrong, so the screen cannot be used to discover which usernames exist.
- All 222 CSV rows are loaded. The 135 pending rows have no verified rating/review count, so they receive the mean of the verified ratings and `review_count = 0`. This makes their Bayesian-adjusted rating neutral rather than inventing a score.
- The Bayesian prior is the dataset-wide mean of the verified ratings.
- Food preference is a soft ranking signal weighted at 40%; it is not a hard filter.
- The total budget is enforced across the whole course. There is no hard `total_budget / num_meals` price cap.
- Course generation is greedy and uses the cheapest available prices for the remaining slots as a feasibility reservation.
- Duplicate restaurants are detected by ID.
- Restaurant editing uses a whitelist for SQL column names and parameterized values.
- The interface offers destinations and food categories as fixed choices populated from the database, so neither can be misspelt.
- All input validation lives in `validation.py` and is called by the interface, so the tested rules and the enforced rules are the same.
- The interface explicitly reports partial or impossible courses rather than presenting a short course as complete.
- The processing modules are independent of the interface: the interface layer was replaced twice (tkinter, then Flask, then Flask inside a pywebview window) without changes to filtering, ranking or course generation.

## Tests

Run: `python -m pytest -q test_recommender.py test_auth.py`

Current result: **23 tests passed** (15 recommender, 8 authentication).

## Acknowledgement

See `AI_USE_ACKNOWLEDGEMENT.md`. It must be completed before submission.

## Scope note

The route/schedule extension described in the implementation guide is not included in this version because the supplied project does not contain a travel-time dataset and the route model was still an open design decision. The implemented scope is the restaurant recommendation and budget-constrained course generator.
