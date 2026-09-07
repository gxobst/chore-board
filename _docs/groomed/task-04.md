## Goal

A user can open an individual chore from the task list to view all its fields and perform actions on it: edit, delete, or mark complete.

## Acceptance criteria

- [ ] Clicking a chore row in the task list navigates to a detail page for that chore
- [ ] The detail page displays all fields: title, due date, assignee, notes, priority, and tags
- [ ] An Edit action opens the chore form pre-filled with the current values
- [ ] Saving an edit persists the changes and shows the updated chore on the detail page
- [ ] A Delete action requires explicit confirmation before the chore is removed
- [ ] After confirming deletion, the chore is removed and the user is redirected to the task list
- [ ] A "Mark complete" action sets the chore's completion status to complete
- [ ] After marking complete, the chore no longer appears in the active task list
- [ ] After marking complete, the chore appears in the completed view
- [ ] After marking complete, the user is redirected to the task list
- [ ] Navigating to a detail page for a non-existent chore ID shows a 404 or not-found state
- [ ] The detail page provides a way to navigate back to the task list

## Out of scope

- Generate email reminder action on the detail page → moved to #8
- Recurrence prompt ("create next occurrence") when marking a recurring chore complete → moved to #7
- Bulk complete / bulk delete actions → moved to #5

## Constraints

- Reuse the create chore form from Task 2 for editing
- Follow the design system in `_docs/design-system.md`
- Follow testing guidelines in `_docs/testing-guidelines.md`
- Use Django's built-in patterns for confirmation and redirects
- Files: `chores/views.py`, `chores/templates/chores/` (or equivalent template directory)

---

## Comment — Implementation Summary (2026-09-07)

Implemented the Task Detail View with all acceptance criteria:

- **TaskDetailView** (`GET /<pk>/`): Displays all chore fields (title, due date, assignee, notes, priority, tags) with a back link to task list
- **TaskEditView** (`GET/POST /<pk>/edit/`): Reuses `ChoreForm` pre-filled with current values; saves changes and redirects to detail page
- **TaskDeleteView** (`GET/POST /<pk>/delete/`): Shows confirmation page on GET; deletes chore and redirects to task list on POST
- **TaskCompleteView** (`POST /<pk>/complete/`): Sets `chore.completed = True`, saves, and redirects to task list
- Non-existent chore IDs return 404 via `get_object_or_404`
- Added `btn-secondary` and `btn-danger` CSS classes for the action buttons
- 22 new tests covering all acceptance criteria (all 65 tests pass)

Commit: `6a51950`
