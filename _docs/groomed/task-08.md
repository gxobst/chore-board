## Goal

The app generates a pre-filled email draft via a `mailto:` link that groups overdue, due-today, and due-tomorrow chores into a single message, so a user can quickly send a reminder from their own email client without leaving the app.

## Acceptance criteria

- [x] A "Generate reminder" action is visible on the task detail page.
- [x] A bulk "Generate reminder" action is available on the task list view.
- [x] Clicking either action opens the user's default mail client via a `mailto:` link.
- [x] The email subject line references chores needing attention (e.g., "Chore reminders").
- [x] The email body groups chores into three clearly labeled sections: Overdue, Due Today, Due Tomorrow.
- [x] Each chore entry in the body shows only the chore title and due date.
- [x] Chore notes, priority, assignee, and tags are NOT included in the email body.
- [x] When no chores are overdue, due today, or due tomorrow, the action is hidden or displays a message indicating no reminders are needed.
- [x] Special characters and spaces in chore titles are properly URL-encoded in the `mailto:` link.
- [x] All active chores needing attention are combined into a single email draft (not one email per chore).

## Implementation notes

- Added `get_reminder_mailto()` helper in `chores/views.py` that queries active chores, groups them by urgency (overdue/due today/due tomorrow), and returns a `mailto:` URL with URL-encoded subject and body.
- Updated `TaskListView` and `TaskDetailView` to pass `reminder_mailto` to templates.
- Added "Generate Reminder" button to `task_list.html` and `task_detail.html` templates, shown only when `reminder_mailto` is not None.
- 17 tests in `chores/tests.py` covering all acceptance criteria.

## Out of scope

- Automatic email sending — the user must manually send from their own client (per plan §17 Email Mechanism).
- Push/SMS/in-app notifications — not in MVP (plan §20).
- Scheduling reminders for future delivery — not in MVP.
- Reminder preferences or settings page — not in MVP (plan §19).
- Per-chore individual reminder emails — always combined into one draft (plan §17 Reminder Grouping).

## Constraints

- Use `mailto:` links only — no email-sending backend or third-party email API.
- Email content must include only chore title and due date (plan §17 Email Content).
- Reminder triggers are strictly: overdue, due today, due tomorrow (plan §17 Reminder Timing).
- Files: task detail template, task list template, and associated view logic.
- Follow the existing design system in `_docs/design-system.md`.
- Follow testing guidelines in `_docs/testing-guidelines.md` — cover the empty-state case.
