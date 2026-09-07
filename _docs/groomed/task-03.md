## Goal

The home screen of the app: a list view that shows all incomplete chores sorted by due date (earliest first), giving the user a single glance at what needs to be done and when.

## Acceptance criteria

- [ ] Navigating to the app root (`/`) renders the task list view
- [ ] Only chores with `completed=False` are shown; completed chores are excluded
- [ ] Chores are sorted by due date ascending (earliest due date first)
- [ ] When two chores share the same due date, they are ordered by creation date (oldest first) as a stable tiebreaker
- [ ] Each row displays: chore title, due date, assignee name, and priority
- [ ] Empty optional fields (e.g., no assignee selected, no priority set) render as a placeholder (e.g., "Unassigned", "—") rather than breaking layout
- [ ] Tapping or clicking a chore row navigates to the task detail view for that chore
- [ ] When no incomplete chores exist, an empty-state message is shown (e.g., "No chores yet — add your first one")
- [ ] The list re-renders with updated data after a chore is created via the create form (redirect back to this view)
- [ ] The view is responsive and usable on mobile viewports (no horizontal overflow)

## Out of scope

- Filtering by assignee, priority, status, or tags — moved to #10
- Search by title or notes — moved to #10
- Overdue highlighting (red styling) — moved to #11
- Bulk reminder email generation from the list — moved to #8
- Calendar view — moved to #6
- Completed view and restore — moved to #5
- Marking a chore complete directly from the list — must open the task detail view (#4)

## Constraints

- Files: `chores/views.py`, `chores/templates/chores/task_list.html`, `chores/urls.py`
- Use Django's class-based `ListView` or a function-based view querying the `Chore` model
- Query must filter `completed=False` and order by `due_date` then `created_at`
- Template must follow the design system in `_docs/design-system.md`
- Do not add new dependencies; use only what is already in `pyproject.toml`
- Follow the testing guidelines in `_docs/testing-guidelines.md` — write tests for the view, sorting, and empty state
