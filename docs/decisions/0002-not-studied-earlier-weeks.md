# 0002 — "Not Studied" looks at every week before the reported week

- Status: accepted
- Date: 2026-11-22
- Requirement: R5 (weekly report includes a "Not Studied" section listing
  courses logged in an earlier week with no sessions this week)
- Decided by: the project owner, when asked in round 2; recorded here with
  the reasons

## Y-statement

In the context of **the "Not Studied" section of the weekly report (R5)**,
facing **R5's wording "logged in an earlier week", which does not say how far
back to look, or whether sessions after the reported week count when someone
reports a past week**,
we decided for **listing a course when it has at least one session dated
before the Monday of the reported week and none inside that week, ignoring
sessions dated after the week**
and against **looking only at the previous week, and looking at every other
week including later ones**,
to achieve **a list that catches courses dropped weeks ago (the neglect the
problem statement worries about most), and a past week's report that always
shows the same thing it showed in that week, no matter what was logged later**,
accepting **that a course the student has finished or dropped for good stays
in the list every week, and that every report scans all stored history**.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| **Only the previous week** | A short list that hides courses abandoned more than a week ago, which are the most neglected ones. A course studied in week 1 and skipped in weeks 2 and 3 would drop out of the list in week 3. |
| **Any other week, including later weeks** | Simpler to state, but a past week's report would change after new sessions are logged, and a course started *after* that week would be called "not studied" in it. |
| **Any earlier week, ignoring later ones** (chosen) | Catches long-neglected courses, and past reports stay stable. |

## Consequences

- `not_studied()` in `study_logger/report.py` reads all sessions and puts each
  one into "before the week", "in the week" or "after the week" (ignored).
- Courses that ended for good can't be hidden yet. If that gets annoying, a
  later round could add a way to archive a course or a look-back limit; either
  one needs a new requirement.
- The empty-section message tells the two cases apart: "every course was
  studied this week" when there is earlier history, and "no courses were
  logged in earlier weeks" when there is none.
