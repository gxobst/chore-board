## Goal

A Settings page where users can export all chore data as a JSON file, import chores from a previously exported JSON file, and clear all chore data — giving users full control over their local data without leaving the app.

## Acceptance criteria

- [ ] A Settings page is accessible from the bottom navigation bar alongside Task List, Calendar, and Completed.
- [ ] The Settings page displays three clearly labeled actions: Export, Import, and Clear All Data.
- [ ] Export triggers a browser download of a JSON file containing every chore in the database (both active and completed).
- [ ] The exported JSON file has a descriptive filename (e.g., `chores-backup-YYYY-MM-DD.json`).
- [ ] The exported JSON can be re-imported into the app and produces the same chores.
- [ ] Import accepts a JSON file via a file input and adds the contained chores to the database.
- [ ] After a successful import, the user sees a confirmation message indicating how many chores were imported.
- [ ] Import with a malformed JSON file shows an error message and does not modify existing data.
- [ ] Import with an empty file shows an error message or is a no-op and does not modify existing data.
- [ ] Import with a valid JSON file that contains no chores array (wrong schema) shows an error message and does not modify existing data.
- [ ] Clear All Data shows a confirmation dialog before proceeding.
- [ ] Confirming Clear All Data removes every chore (active and completed) from the database.
- [ ] Canceling the confirmation dialog leaves all data unchanged.
- [ ] After clearing, the user sees a confirmation message that all data has been removed.
- [ ] The Settings page follows the design system in `_docs/design-system.md` (mobile-friendly layout, danger styling for destructive actions).

## Out of scope

- Partner name management — not in MVP (plan §19).
- Account management — not in MVP (plan §20).
- Notification preferences — not in MVP (plan §19).
- Sync settings — not in MVP (plan §19).
- Partial/selective export — export is always all chores.
- Import merge strategies (skip duplicates / overwrite duplicates) — out of scope for MVP; duplicates are allowed on import.
- Cloud backup or remote storage — data stays local (plan §5).

## Constraints

- Files: `chores/views.py` (or a new `chores/views/settings.py`), `chores/templates/chores/settings.html`, and URL configuration.
- Use Django's built-in `JsonResponse` or `HttpResponse` with `Content-Disposition: attachment` for export.
- Use Django's form/file handling for import — no third-party libraries.
- Clear All Data must require explicit user confirmation (e.g., a modal or confirmation page) before executing.
- Follow the existing design system in `_docs/design-system.md`.
- Follow testing guidelines in `_docs/testing-guidelines.md` — cover malformed JSON, empty file, and wrong-schema import cases.
