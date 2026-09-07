# Testing Guidelines

## General Principles

- Write tests for every new feature, including edge cases.
- Tests should be independent and not rely on shared mutable state.
- Run the full suite before marking a task complete: `uv run pytest`.

## Test Organization

- Place tests in the `tests/` directory or alongside the module (e.g., `chores/tests.py`).
- Name test files `test_<module>.py` and test functions `test_<behavior>`.

## What to Test

- **Models**: field validation, constraints, string representation, ordering.
- **Views**: HTTP status codes, template usage, context data, redirects.
- **Forms**: valid/invalid input, error messages, saving.
- **Edge cases**: empty input, boundary values, missing required fields, empty lists.

## Fixtures and Factories

- Use `pytest-django` fixtures or factory functions to create test data.
- Avoid relying on database state from other tests.

## Running Tests

- `uv run pytest` — full suite.
- `uv run pytest tests/test_home.py` — single file.
- `uv run pytest -x` — stop on first failure.
- `uv run pytest -k "test_name"` — run a specific test.

---

## Test Scenarios

These are the scenarios that must be covered. Each task should include tests for its relevant scenarios before being marked complete.

### Chore Model

- Blank title → validation error (required field).
- Blank due date → validation error (required field).
- Priority defaults to none/empty when not set.
- `is_completed` defaults to `False`.
- String representation returns the chore title.
- Chores are ordered by due date (earliest first).

### Create Chore

- GET returns 200 and renders the form.
- POST with valid data → creates a chore and redirects to the task list.
- POST with empty title → form error, no chore created.
- POST with empty due date → form error, no chore created.
- All fields (title, due date, assignee, notes, priority, tags) save correctly.

### Task List View

- GET returns 200.
- Only incomplete chores appear (completed chores are excluded).
- Chores are ordered by due date ascending.
- Empty list shows an appropriate empty-state message.
- Each row displays title, due date, assignee, and priority.

### Task Detail View

- GET returns 200 and displays all chore fields.
- Mark complete → `is_completed` becomes `True`, redirects away from active list.
- Delete → chore is removed from the database, redirects to task list.
- Edit → updates the chore fields, redirects to task list.
- Non-existent chore ID → 404.

### Completed View and Restore

- GET returns 200 and shows only completed chores.
- Completed chores are ordered most-recently-completed first.
- Restore action → `is_completed` becomes `False`, chore reappears in active list.
- Bulk restore → multiple selected chores restored at once.
- Empty completed list shows an appropriate message.

### Calendar View

- GET returns 200 and displays the current month.
- Dates with chores due are visually marked/highlighted.
- Clicking a date opens the create form with that date pre-filled.
- Next/previous month navigation updates the displayed month.

### Recurring Chores

- Recurrence field saves correctly (none, daily, weekly, monthly).
- Completing a recurring chore with "create next" → new chore created with due date shifted by the recurrence interval (daily: +1 day, weekly: +7 days, monthly: +1 month).
- Completing a recurring chore with "skip" → no new chore created.
- Editing current occurrence only → other occurrences unaffected.
- Editing entire series → all occurrences updated.

### Reminder Email Draft

- Generates a `mailto:` link with a pre-filled body.
- Body groups overdue, due today, and due-tomorrow chores.
- Body contains each chore's title and due date.
- Body does NOT contain notes, priority, assignee, or tags.
- No chores needing attention → empty or skipped reminder.

### Settings Page

- Export → returns a JSON file download containing all chores.
- Import → adds chores from a valid JSON file to the database.
- Clear all → removes every chore from the database.
- Import with malformed JSON → error message, no data changed.
- Import with empty file → error or no-op.

### Search and Filters

- Filter by assignee → only chores assigned to that person appear.
- Filter by priority → only chores with that priority appear.
- Filter by tag → only chores with that tag appear.
- Search by title → chores whose title contains the query (case-insensitive).
- Search by notes → chores whose notes contain the query (case-insensitive).
- Multiple filters combined → AND logic (all conditions must match).
- No matches → empty-state message shown.

### Overdue Highlighting

- A chore with due date in the past and not completed → marked with overdue styling.
- A chore with due date today or future → no overdue styling.
- A completed chore with past due date → no overdue styling.
