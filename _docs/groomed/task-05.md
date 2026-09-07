## Goal

Completed chores are visible in a separate view, sorted most-recently-completed first, and can be restored back to the active task list individually or in bulk.

## Acceptance criteria

- [ ] A dedicated Completed view exists, accessible from the app navigation, that lists only chores marked complete.
- [ ] Completed chores are sorted by completion date, most recently completed first.
- [ ] Each completed chore row displays at minimum the chore title and the date it was completed.
- [ ] Each completed chore row has a "Restore" button that moves the chore back to the active task list.
- [ ] After restoring a single chore, it disappears from the Completed view and reappears in the active task list sorted by due date.
- [ ] Completed chores do NOT appear in the main task list view (no strikethrough, no hidden rows).
- [ ] A bulk-restore action exists: the user can select multiple completed chores and restore all of them in one action.
- [ ] After a bulk restore, all selected chores disappear from the Completed view and reappear in the active task list.
- [ ] When no chores are completed, the Completed view shows an empty-state message (e.g., "No completed chores yet").
- [ ] Restoring a chore preserves all original fields (title, due date, assignee, notes, priority, tags).

## Out of scope

- Bulk delete of completed chores — moved to a follow-up issue (not in current backlog).
- Undo after restore — the user must manually mark the chore complete again if restored by accident.
- Filtering or searching within the Completed view — belongs to task #10 (Search and filters), which covers the task list view.
- Sorting Completed view by anything other than completion date — not required for MVP.

## Constraints

- Files: stay within `chores/` app (views, urls, templates, models). Reuse the existing `Chore` model and its `completed` / completion-date fields established in earlier tasks.
- Libraries: use Django's built-in views and templates; no new dependencies.
- Guidelines: follow `_docs/design-system.md` for UI styling; follow `_docs/testing-guidelines.md` for tests.
- The Completed view must remain consistent with the data model from task #1 (Chore model) and the task list from task #3.
