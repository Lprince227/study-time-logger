# Problem

College students that take several courses often can't recall how much time they spend on each course. By the end of each week such students can't tell which classes they have been neglecting until deadlines arrive.

# Initial requirements

- R1: Record a study session with a course name and a duration from the terminal
- R2: Store sessions in a plain file that persists between runs
- R3: Report total time per course for a given week
- R4: Reject invalid input (negative or non-numeric durations) with a clear message
- R5: Weekly report includes a section titled "Not Studied" which lists courses that were logged in an earlier week but have no sessions this week, shown with zero minutes
