# Backlog

## 1. Chore model and database setup
Goal: A working Chore model with all MVP fields and a migrated database.
Description: Define the `Chore` model in `chores/models.py` with fields for title, due date, assignee, notes, priority, tags, and completion status. Create and apply the initial migration so the database is ready. This is the foundation every other task builds on.

## 2. Create chore form
Goal: A working form to add a new chore with all fields.
Description: Build a page where the user can create a chore by filling in title, due date, assignee, notes, priority, and tags. On submit, the chore is saved to the database and the user is redirected to the task list. Validation ensures title and due date are required.

## 3. Task list view
Goal: All active chores displayed in a list sorted by due date.
Description: Create the main list view that shows all incomplete chores ordered by due date (earliest first). Each row shows the chore title, due date, assignee, and priority. This is the home screen of the app.

## 4. Task detail view
Goal: A user can open a chore to view, edit, delete, or mark it complete.
Description: Build a detail page for a single chore that shows all fields and provides actions: edit (reuse the create form), delete (with confirmation), and mark complete. Completing a chore moves it out of the active list.

## 5. Completed view and restore
Goal: Completed chores are visible in a separate view and can be restored.
Description: Create a Completed view that lists all chores marked complete, with the most recently completed first. Each entry has a restore button that moves it back to the active list. Include a bulk-restore action for multiple selections.

## 6. Calendar view
Goal: A monthly calendar where users can see chores and add new ones by clicking a date.
Description: Build a calendar page showing the current month. Dates with chores due are highlighted. Clicking a date opens the create chore form with the due date pre-filled. Navigation moves between months.

## 7. Recurring chores
Goal: Chores can repeat daily, weekly, or monthly, with next-occurrence creation on completion.
Description: Add a recurrence field (none, daily, weekly, monthly) to the chore model and form. When a recurring chore is marked complete, prompt the user to create the next occurrence. Support skipping a single occurrence and editing either the current occurrence or the whole series.

## 8. Reminder email draft
Goal: The app generates a pre-filled email draft for chores needing attention.
Description: Add a "generate reminder" action on the task detail page and a bulk action on the list view. The draft groups overdue, due today, and due-tomorrow chores into a single email body containing each chore's title and due date. The email opens in the user's default mail client via a `mailto:` link.

## 9. Settings page
Goal: Users can export, import, and clear all chore data.
Description: Build a Settings page with three actions: export all chores as a JSON file download, import chores from a previously exported JSON file, and clear all data (with confirmation). Data is stored in the Django database.

## 10. Search and filters
Goal: Users can filter the task list by assignee, priority, status, and tags, and search by title or notes.
Description: Add filter controls above the task list for assignee, priority, status, and tags, plus a search box. Filters combine (AND logic). Search matches against title and notes (case-insensitive). The list updates to reflect active filters and search terms.

## 11. Overdue highlighting
Goal: Overdue chores are visually highlighted in the task list.
Description: On the task list view, any chore whose due date is in the past and is not completed is highlighted with red styling. This makes overdue items immediately visible without requiring the user to read every due date.
