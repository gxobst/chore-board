# Couples Chore Tracker — MVP Feature Scope

## 1. Product Goal

A mobile-friendly web app for couples to manage household chores, with a strong focus on due dates, reminders, and shared visibility.

---

## 2. Target Users

- Couples managing shared household responsibilities.
- Users who want a lightweight chore tracker without creating accounts.

---

## 3. Core Problem Being Solved

The MVP primarily solves:

- Remembering chores that need to be done.
- Tracking deadlines.
- Prompting partners about overdue, due today, and upcoming chores.

---

## 4. Platform

- Mobile-friendly web app.
- Feature-focused MVP.
- Tech stack intentionally not discussed as part of this brainstorming session.

---

## 5. Access & Sharing

### Accounts

- No account creation required.
- No login required.

### Sharing

- Shared household code/link feature remains in the MVP.
- However, there is no real cross-device sync in the MVP.
- The shared link only works on the same browser/device.

### Sync

- No real-time sync between partners on separate devices.
- Data is stored locally in the browser.

---

## 6. Storage & Data Handling

### Storage

- Chore data is stored using browser/local storage.

### Backup

- Users can export chore data as a JSON file.
- Users can import a previously exported JSON backup.

### Data Management

- Users can clear all data.
- Export, import, and clear-data actions are available from a Settings page.

---

## 7. Main Views

The MVP includes:

1. Task List view
2. Calendar view
3. Completed view
4. Settings page

---

## 8. Task List View

### Default Sorting

- Tasks are sorted by due date by default.

### Filters

The MVP supports filtering by:

- Assignee
- Priority
- Status
- Tags

### Search

The MVP includes search for:

- Task title
- Task notes

### Overdue Behavior

- Overdue chores are highlighted in red.
- On load, the app can prompt the user to generate an email reminder for chores needing attention.

---

## 9. Calendar View

- Calendar is included in the MVP.
- Users can add chores by clicking a date.
- Calendar is not drag-and-drop in the MVP.

---

## 10. Chore Fields

Each chore includes:

| Field | MVP Behavior |
|---|---|
| Title | Required |
| Due date | Required |
| Assignee | Selectable from two partner names |
| Notes | Optional text |
| Priority | Low, Medium, or High |
| Tags | Multiple custom tags |

### Field Defaults

| Field | Default |
|---|---|
| Title | Empty |
| Due date | Empty until selected, but required |
| Assignee | Empty until selected |
| Priority | Empty until selected |
| Notes | Empty |
| Tags | Empty |

---

## 11. Assignees

- Assignees are limited to two predefined partner names.
- Partner names are set directly when creating a task.
- Partner names are not editable through a global Settings page in the MVP.

---

## 12. Priorities

Priority levels:

- Low
- Medium
- High

Priority is not required by default. The user selects it when needed.

---

## 13. Tags / Categories

- Chores can have multiple tags.
- Tags are created freely by the user.
- Tags are not limited to a predefined list.
- Users can filter chores by tags.

Example tags:

- Kitchen
- Bathroom
- Groceries
- Errands
- Cleaning

---

## 14. Task Detail Screen

Users must open a task to perform most actions.

Available actions:

- Mark complete
- Edit chore
- Delete chore
- Generate email reminder

Users cannot mark a chore complete directly from the list or calendar without opening the task.

---

## 15. Completed Chores

- Completed chores move to a separate Completed view.
- Completed chores do not stay in the main task list with a strikethrough.
- Users can restore accidentally completed chores.
- Completed view includes bulk actions:
  - Bulk restore
  - Bulk delete

---

## 16. Overdue / Postponement Behavior

- There is no snooze button.
- There is no postpone button.
- To move a chore to a later date, the user must manually edit the due date.

---

## 17. Reminders

### Reminder Basis

Reminders are based on:

- Due dates

### Reminder Channel

Reminders are handled through:

- Email

### Email Mechanism

Because the MVP uses local storage and does not automatically send emails:

- The app generates a pre-filled email draft.
- The user sends the email from their own email client.

### Reminder Timing

The app suggests reminders for:

- Overdue chores
- Chores due today
- Chores due soon, such as tomorrow

### Reminder Grouping

If multiple chores need reminders:

- The app generates one combined email draft.

### Email Content

The reminder email includes:

- Chore title
- Due date

It does not include:

- Notes
- Priority
- Assignee
- Tags

---

## 18. Recurring Chores

Recurring chores are included in the MVP.

### Supported Frequencies

- Daily
- Weekly
- Monthly

### Completion Behavior

When a recurring chore is completed:

- The app asks the user whether to create the next occurrence.

### Skipping Occurrences

- Users can skip a single occurrence without deleting the entire recurring chore.

### Editing Recurring Chores

When editing a recurring chore:

- The app asks the user whether the edit applies to:
  - The current occurrence only
  - The entire series

---

## 19. Settings Page

The Settings page includes:

- Export chores as JSON
- Import chores from JSON
- Clear all data

The Settings page does not include:

- Partner name management
- Account management
- Notification preferences
- Sync settings

---

## 20. Out of Scope for MVP

The following are not included in the MVP:

- User accounts
- Login/authentication
- Real cross-device sync
- Automatic email sending
- Push notifications
- SMS notifications
- In-app notification center
- Snooze/postpone action
- Drag-and-drop calendar rescheduling
- Completing chores directly from list/calendar without opening them
- Global partner name settings
- Predefined tag library
- Analytics or chore-completion statistics
- Gamification
- Multiple households
- Invitation flow for partners

---

## 21. Key Assumptions

- Local storage may be cleared if the user clears browser data.
- The shared link does not provide real synchronization across separate devices.
- Email reminders depend on the user’s email client and manual sending.
- Partner names are handled through task creation rather than account/profile management.
- The MVP prioritizes simplicity over automatic synchronization.

---

## 22. Decision Log

| Area | Decision |
|---|---|
| Primary problem | Reminders and deadlines |
| Reminder basis | Due dates |
| Reminder channel | Email |
| Email mechanism | Pre-filled email draft |
| Task fields | Title, due date, assignee, notes, priority, tags |
| Due date requirement | Required for all chores |
| Priority levels | Low, Medium, High |
| Priority default | None until selected |
| Assignee model | Two predefined partner names |
| Assignee default | None until selected |
| Partner name setup | Set directly during task creation |
| Partner name settings | Not editable in Settings |
| Accounts | None |
| Sharing model | Shared household code/link |
| Sync | No real sync in MVP |
| Shared link behavior | Works only on same browser/device |
| Storage | Browser/local storage |
| Platform | Mobile-friendly web app |
| Main views | List + Calendar |
| Completed chores | Separate Completed view |
| Accidental completion | Restore from Completed view |
| Bulk actions | Bulk restore and bulk delete in Completed view |
| Snooze/postpone | Not included; edit due date manually |
| Recurring chores | Included |
| Recurrence frequencies | Daily, Weekly, Monthly |
| Recurring completion | Ask whether to create next occurrence |
| Skip occurrence | Supported |
| Edit recurring chore | Ask whether to edit current occurrence or full series |
| Filtering | Assignee, priority, status, tags |
| Sorting | Due date by default |
| Calendar adding | Click a date to open add form |
| Complete from list/calendar | Not allowed; must open task |
| Task detail actions | Complete, edit, delete, generate reminder |
| Reminder triggers | Overdue, due today, due soon |
| Multiple reminders | Combined into one email draft |
| Reminder email content | Title and due date only |
| Search | Title and notes |
| Tags | Multiple custom tags |
| Tag creation | Free-form custom tags |
| Tag filtering | Included |
| Export | JSON export included |
| Import | JSON import included |
| Clear data | Included |
| Settings page | Included for export/import/clear data |

---

## 23. MVP Summary

The MVP is a lightweight, mobile-friendly chore tracker for couples. It focuses on due dates, reminders, recurring chores, and simple local data management. Users can create chores with titles, required due dates, optional notes, optional priorities, custom tags, and one of two partner assignees. The app includes a task list, calendar view, completed view, and settings page. Reminders are generated as combined pre-filled email drafts for overdue, due today, and upcoming chores. Data is stored locally, with JSON export/import and clear-data options. Real account management and cross-device sync are excluded from the MVP.