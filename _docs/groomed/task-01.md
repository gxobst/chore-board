## Goal
A `Chore` model defined in `chores/models.py` with all MVP fields and a migrated database, so that chores can be created, stored, and queried via the Django ORM — the foundation every other task builds on.

## Acceptance criteria
- [ ] `chores/models.py` defines a `Chore` model with the following fields:
  - `title`: required `CharField` (max length 200)
  - `due_date`: required `DateField`
  - `assignee`: optional `CharField` (max length 100, `blank=True`, default empty string)
  - `notes`: optional `TextField` (`blank=True`, default empty string)
  - `priority`: optional `CharField` with choices `Low`, `Medium`, `High` (`blank=True`, default empty string)
  - `tags`: `ManyToManyField` to a `Tag` model (optional, `blank=True`)
  - `completed`: `BooleanField` default `False`
- [ ] A `Tag` model exists with a single `name` field (`CharField`, `unique=True`) and a `__str__` returning the tag name.
- [ ] An initial migration file exists under `chores/migrations/` that creates the `Chore` table, the `Tag` table, and the M2M join table.
- [ ] Running `python manage.py migrate` applies the migration cleanly with no errors and no pending migrations remain.
- [ ] A chore can be created via the Django ORM (e.g. `Chore.objects.create(title="Wash dishes", due_date="2025-01-15")`) and is persisted to the database.
- [ ] Omitting `title` or `due_date` when saving a chore raises an `IntegrityError` (or validation error); omitting `assignee`, `notes`, `priority`, or `tags` is allowed.
- [ ] `Chore.__str__` returns the chore's title; `Tag.__str__` returns the tag's name.
- [ ] Tags can be created and assigned to a chore via the M2M relationship (e.g. `chores.tags.add(tag)`) and queried in both directions.

## Out of scope
- Recurrence frequency field (daily/weekly/monthly) → moved to #7 (Recurring chores)
- Admin site registration for `Chore` or `Tag` → no follow-up (not required by any MVP task)
- Seed data or fixture loading → no follow-up (not required by any MVP task)

## Constraints
- Stay inside the `chores/` app (`chores/models.py`, `chores/migrations/`).
- Use Django's built-in ORM — no new dependencies (see `_docs/AGENTS.md`: dependencies require approval).
- `Tag` names must be unique to avoid duplicates.
- Follow Django naming conventions for models, fields, and migration files.
- Refer to `_docs/plan.md` §10 (Chore Fields), §12 (Priorities), §13 (Tags) for field behavior and defaults.
