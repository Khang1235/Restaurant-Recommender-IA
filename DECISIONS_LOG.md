# Decisions log — CS IA Restaurant Recommender

## 2026-08-18 — D1.1 Runtime schema
**Chosen:** Store only the nine fields used by the Restaurant runtime model; discard curation metadata such as purpose, source, verification notes, and segment.

**Why:** These fields describe how the dataset was assembled rather than properties needed by the recommendation algorithm. Keeping them out of the runtime schema keeps the database focused on the application's actual inputs.

## 2026-08-18 — D1.2 All 222 rows
**Chosen:** Load all 222 restaurants rather than only the 87 with verified ratings.

**Why:** Verified-only loading made smaller cities functionally unusable: the runtime had only 3 Ha Long and 4 Ninh Binh candidates. Full coverage gives the recommender enough candidates to satisfy the meal-generation constraint, while verification status remains a documented limitation.

**Consequence:** Unverified restaurants must not be treated as if their ratings were real observations; the neutral-rating decision below handles this.

## 2026-08-18 — D1.3 Missing ratings
**Chosen:** For the 135 pending rows, use the mean of the verified ratings as the initial rating and set review_count to 0.

**Why:** Setting the rating to 0 would artificially lower the Bayesian prior, while skipping the rows destroys city coverage. With review_count = 0, Bayesian adjustment returns exactly the dataset mean, so pending restaurants begin neutral and gain no artificial evidence of quality.

**Effect on get_mean_rating():** The imputed values equal the verified mean, so including them does not shift the mean away from the verified-data mean.

## 2026-08-18 — D1.4 Empty special_features
**Chosen:** Convert blank feature cells to an empty list and strip empty feature entries.

**Why:** Python's `"".split(";")` returns `['']`, which would create a false feature and affect later feature handling.

## 2026-08-18 — D1.5 Re-running the loader
**Chosen:** Check for an existing ID and skip it instead of replacing the row.

**Why:** The application includes record editing. Replacing rows during a reload would silently destroy edits, so preserving existing IDs is safer even though it means a changed CSV row is not automatically propagated.

## 2026-08-18 — D2 Dataset-wide Bayesian prior
**Chosen:** Use the mean rating of the whole loaded dataset.

**Why:** A single global prior is stable and does not change when the user's destination or preferences change. This also keeps the Bayesian adjustment consistent between searches.

## 2026-08-18 — D3 Preference input
**Chosen:** Keep comma-separated preference input for the current GUI and perform case-insensitive matching.

**Why:** It is simple to implement and preserves the existing interface. A future checkbox/listbox would reduce spelling variations further, but this was not necessary for the current assessed scope.

## 2026-08-18 — D4.1 Soft preference ranking
**Chosen:** Do not hard-filter by food preference; use preference as 40% of the ranking score.

**Why:** Hard-filtering makes every surviving restaurant a preference match, turning the 40% term into a constant. Soft ranking preserves strong alternatives and makes the preference weight actually affect ordering.

## 2026-08-18 — D4.2 Bayesian threshold
**Chosen:** Keep MIN_REVIEWS = 50.

**Why:** A lower threshold would allow low-review ratings to influence the ranking more strongly, while a higher threshold would pull more restaurants toward the mean. 50 is retained as a compromise, but the evaluation notes that it can penalise legitimate local institutions with few online reviews.

## 2026-08-18 — D5.1 Budget constraint
**Chosen:** Enforce the user's total budget rather than a hard average price per meal.

**Why:** A per-meal cap prevents valid combinations such as two inexpensive meals plus one more expensive dinner. The success criterion is about total spending, so the algorithm should allow uneven meal prices as long as the final sum is within budget.

## 2026-08-18 — D5.2 Feasibility reservation
**Chosen:** Reserve the sum of the cheapest available restaurants for the remaining meal slots.

**Why:** The previous 0.5 average-budget reserve was arbitrary. Using actual candidate prices gives a stronger feasibility test: if the candidate is accepted, the remaining slots have at least a known cheapest-cost completion, subject to the unique-restaurant constraint.

## 2026-08-18 — D5.3 Short-course behaviour
**Chosen:** Return the longest valid course and explicitly tell the user when fewer meals than requested were scheduled.

**Why:** Raising an exception for an ordinary budget limitation would make the interface feel broken. Returning a partial result is useful, but it must be labelled clearly so the user cannot mistake it for a complete course.

## 2026-08-18 — D6 Database connection lifetime
**Chosen:** Reuse one SQLite connection while the GUI is open and close it when the window closes.

**Why:** The previous implementation reopened and rechecked the database on every button click. Keeping one connection reduces unnecessary setup work while still allowing the connection to be closed cleanly when the application exits.

## 2026-09-19 — D7 Dataset reduced to 222 rows
**Chosen:** Replace six unverifiable or corporate-owned venues and drop one that no guide corroborated.

**Why:** Four Google matches were the right operator at a different branch, so those rows were renamed to the venue actually matched (Duong's 2, Hong Hanh Signature, Dat Cang Du Hang, Xiu Pao Hanh Phuc). Two entries could not be confirmed at all and were replaced with independent restaurants verified against Google (La Verticale to November Restaurant, Club Opera to Khue Restaurant). Two more were Vinpearl resort restaurants, replaced to keep the dataset to independent venues (Pavilion to Vua Hai San Bai Chay, Accogliente to Com Nieu Phu Ong). Banh Da Cua 414 To Hieu had four reviews and no guide coverage, so it was removed rather than defended.

**Consequence:** D1.2 and D1.3 above are restated at 222 rows and 135 pending. No city fell below 30 candidates, so meal generation is unaffected.

## 2026-10-13 — D8 Resource paths separated from writable paths
**Chosen:** Resolve read-only files (templates, stylesheet, CSV dataset) and the writable database through a single module, `paths.py`, rather than by relative path.

**Why:** The program previously found `templates/`, `static/` and the CSV relative to the current working directory, and wrote the database next to its own source. Both assumptions hold only when the program is started from its own folder. Packaging it into a standalone executable breaks both: the read-only files are unpacked to a temporary folder recorded in `sys._MEIPASS`, and that folder is deleted on exit, so a database written there would be lost. Separating the two kinds of path makes the location explicit instead of incidental.

**Consequence:** Run from source the behaviour is unchanged — the database is still `data/restaurants.db`. Run as a packaged executable it moves to a per-user application folder. `database.py` was not modified; `app.py` passes the resolved path to the existing `get_connection(db_path)` parameter. Verified by building a frozen bundle, running it from an unrelated directory, and confirming all 222 rows load and the recommendation page renders.
