## Goal

Chores can repeat on a daily, weekly, or monthly cadence. When a recurring chore is completed the app prompts the user to create the next occurrence. Users can skip a single occurrence without completing it, and can edit either one occurrence or the entire series.

## Acceptance criteria

- [ ] The `Chore` model includes a `recurrence` field accepting values: `none`, `daily`, `weekly`, `monthly`. Default is `none`.
- [ ] The create and edit chore forms include a recurrence selector showing options: None, Daily, Weekly, Monthly.
- [ ] Completing a chore where `recurrence != none` shows a confirmation dialog asking whether to create the next occurrence, with choices Yes and No.
- [ ] Choosing Yes creates a new chore with the same title, assignee, notes, priority, tags, and recurrence, with `due_date` shifted forward by the recurrence interval (daily: +1 day, weekly: +7 days, monthly: +1 month). The new chore is not marked complete.
- [ ] Choosing No completes the current chore without creating a new occurrence.
- [ ] A "Skip occurrence" action exists on the detail view of a recurring chore. Skipping advances the chore's `due_date` by one recurrence interval without marking it complete, and does not create a new record.
- [ ] Editing a recurring chore prompts the user to choose whether changes apply to the current occurrence only or the entire series.
- [ ] If the user chooses "current occurrence only," only the open chore is modified.
- [ ] If the user chooses "entire series," all chores sharing the same recurrence series identifier are updated with the new field values.
- [ ] New recurring chores created by the completion prompt are linked to the same series as their parent so that "edit entire series" affects them.
- [ ] The calendar view renders recurring chores on their computed due dates.
- [ ] All recurrence logic is covered by at least one automated test (model method, view, or equivalent).

## Out of scope

- Custom recurrence intervals (e.g., "every 3 days", "every 2 weeks") — moved to follow-up task #12.
- Recurrence patterns based on weekdays or month-end — moved to follow-up task #12.
- Yearly recurrence frequency — moved to follow-up task #12.
- A dedicated "recurring templates" management view — moved to follow-up task #13.
- Bulk editing of recurring series from the list view — moved to follow-up task #13.
- Automatic recurrence without user confirmation — explicit product decision per plan §18.

## Constraints

- Changes stay inside `chores/models.py`, `chores/forms.py`, `chores/views.py`, and their associated templates.
- Follow the existing UI patterns in `_docs/design-system.md` for form controls and modal dialogs.
- Reuse the existing create chore form for next-occurrence creation; do not build a separate template.
- Recurring chores share a series identifier (e.g., `series_id`) so the series can be targeted for bulk edits.
- Use Django's `dateutil.relativedelta` or `timedelta` for due-date arithmetic; do not hand-roll calendar math.
- Preserve the existing completion flow for non-recurring chores unchanged.
