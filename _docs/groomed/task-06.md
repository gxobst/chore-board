## Goal

A monthly calendar view that surfaces chores on their due dates, supports month-to-month navigation, and lets the user add a new chore by clicking any date — with the due date pre-filled.

## Acceptance criteria

- [ ] The calendar page renders a full month grid (7-column, row-per-week) showing the current month by default with a visible month/year header.
- [ ] Dates that have at least one chore due are visually highlighted (dot, badge, or background tint) so the user can scan for busy days at a glance.
- [ ] Clicking any date opens the existing create-chore form with the due date pre-filled to the clicked date.
- [ ] Clicking a date that already has due chores still opens the create form (it does not open or list existing chores — that is the task detail view's job).
- [ ] Previous-month and next-month navigation controls move the calendar to the adjacent month and re-render the grid.
- [ ] A "Today" control returns the view to the current month and scrolls/focuses to today's date.
- [ ] Padding days from adjacent months shown at the edges of the grid are visually dimmed and do not accept clicks.
- [ ] The calendar layout is responsive and usable on a mobile viewport (no horizontal scroll, tappable date cells).
- [ ] Completed chores are not highlighted on the calendar — only active (incomplete) chores appear.

## Out of scope

- Drag-and-drop rescheduling of chores on the calendar — tracked as follow-up issue (see plan §20: "Drag-and-drop calendar rescheduling" is MVP-out).
- Opening or previewing existing chore details from a calendar date — tracked as follow-up issue; calendar click always opens the create form.
- Week-view or day-view modes — tracked as follow-up issue; monthly grid only for this task.
- Recurrence series visualization on the calendar — deferred to #7 (Recurring chores).

## Constraints

- Files: `chores/views.py`, `chores/templates/chores/calendar.html`, `chores/urls.py` (Django app structure established in #1–#5).
- Libraries: Use Python standard library `calendar` / `datetime` for date math; no third-party calendar widget dependencies.
- Guidelines: Mobile-first responsive layout; reuse the existing create-chore form component for the add flow; follow existing template inheritance and styling conventions.
- Data: Read from the `Chore` model created in #1; do not duplicate model logic.
- Plan alignment: Per plan §9, users add chores by clicking a date and the calendar is not drag-and-drop in the MVP.

---

## Comment (Software Engineer)

Implemented the calendar view per acceptance criteria:

1. **CalendarView** added to `chores/views.py` — renders month grid using Python's `calendar` module, supports year/month query params for navigation
2. **URL** `calendar/` added to `chores/urls.py`
3. **Template** `chores/templates/chores/calendar.html` — responsive month grid with day headers, prev/next navigation, Today button, clickable dates with prefilled due_date query param
4. **Date highlighting** — active (incomplete) chores get `has-chore` CSS class with background tint and a dot indicator
5. **Today highlighting** — current date gets `today` class with blue background
6. **Padding days** — adjacent month days marked with `padding` class, dimmed and non-clickable (no link)
7. **Completed chores not highlighted** — view filters `completed=False` only
8. **Click-to-add** — all date cells link to `/create/?due_date=YYYY-MM-DD`
9. **Navigation** — Prev/Next buttons compute adjacent month/year correctly, Today button returns to current month
10. **Responsive** — mobile-first CSS with 44px touch targets, larger cells on tablet/desktop

Tests added in `chores/tests.py::CalendarViewTest` (14 tests): 200 status, template, month/year display, nav controls, day headers, chore highlighting, completed chore exclusion, click-to-add links, prev/next month navigation, padding days, today highlighting, responsive viewport.

All 101 tests pass.
