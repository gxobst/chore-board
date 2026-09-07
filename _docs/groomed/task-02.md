# Task 2: Create chore form

## Goal
A working form that lets a user create a new chore with all core fields, validates required inputs, saves the chore, and redirects to the task list.

## Acceptance criteria
- [ ] The create chore form is reachable from the app navigation
- [ ] The form displays input fields for: title, due date, assignee, notes, priority, and tags
- [ ] Title is required — submitting with an empty or whitespace-only title shows a validation error and does not save the chore
- [ ] Due date is required — submitting without a due date shows a validation error and does not save the chore
- [ ] Assignee is selectable from the two predefined partner names and is optional
- [ ] Priority is selectable from Low, Medium, or High and is optional
- [ ] Tags accepts multiple free-form custom tags entered by the user
- [ ] Notes accepts optional free-text input
- [ ] On successful submit, the chore persists and the user is redirected to the task list
- [ ] The form layout is usable on a mobile viewport (no horizontal overflow, tappable inputs)

## Out of scope
- Editing an existing chore — moved to #4 (Task detail view)
- Recurrence field on the form — moved to #7 (Recurring chores)
- Pre-filling the due date from a calendar click — moved to #6 (Calendar view)
- Chore model definition and storage setup — handled by #1 (Chore model and database setup)

## Constraints
- Use the design system in `_docs/design-system.md` for all UI styling
- Follow the testing guidelines in `_docs/testing-guidelines.md`
- Reuse the `Chore` model defined in Task 1
- Form must work without JavaScript enhancement (progressive enhancement)
