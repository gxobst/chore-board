# Task 10: Search and filters

## Goal

Users can quickly find relevant chores on the task list view by filtering on assignee, priority, status, and tags, and by searching within a chore's title and notes.

## Acceptance criteria

- [ ] A row of filter controls renders above the task list with dropdowns for assignee, priority, and status, and a multi-select control for tags.
- [ ] A text search box renders next to the filters.
- [ ] Selecting an assignee filter shows only chores assigned to that partner; the default (no selection) shows chores assigned to any partner.
- [ ] Selecting a priority filter shows only chores with that priority (Low / Medium / High); the default (no selection) shows chores of any priority.
- [ ] Selecting a status filter shows only active chores or only completed chores; the default (no selection) shows active chores only (matches current task-list behavior).
- [ ] Selecting one or more tags shows only chores that have at least one of the selected tags; the default (no selection) shows chores with any tags.
- [ ] Multiple filters combine with AND logic (e.g., assignee = Partner A AND priority = High returns only chores that match both).
- [ ] Typing into the search box filters chores whose title or notes contain the query string, case-insensitively.
- [ ] Search text and filters combine (a chore must match all active filters and the search query to appear).
- [ ] The list updates immediately when any filter or search term changes — no "Apply" button is required.
- [ ] A "Clear all filters" control resets every filter and the search box to its default state.
- [ ] When filters/search produce zero matching chores, an empty-state message is shown (e.g., "No chores match your filters").
- [ ] Filters and search do not affect the Calendar view or Completed view — they apply only to the task list view.

## Out of scope

- Persisting filter/search state across page reloads or browser sessions — out of scope for MVP; revisited if requested.
- Filtering or searching within the Calendar view — belongs to a future task if needed.
- Sorting options beyond the default due-date sort (sort controls are not part of this task).
- Full-text search across all chore fields (e.g., tags, assignee) — only title and notes are searchable.

## Constraints

- Stay within the existing task list view template and Django view; add filter/search logic there.
- Use the existing `Chore` model fields (`title`, `notes`, `assignee`, `priority`, `tags`, `completed`) — no model changes.
- Reuse the dropdown/select styling established in `_docs/design-system.md`.
- Tag multi-select may use a simple list of checkboxes or a basic multi-select widget — no external tag-library dependency.
- Filter logic runs server-side via query parameters (URL reflects active filters so the state is shareable).
- Keep the implementation consistent with the existing task list view from Task 3.

## Comment (Software Engineer — 2026-09-07)

Implemented all acceptance criteria for Task 10 (Search and filters):

1. **Views** (`chores/views.py`): Extended `TaskListView` to handle query parameters for `assignee`, `priority`, `status`, `tags` (multi-select), and `search`. Added `Q`-based case-insensitive search on title + notes. Added context data for filter dropdowns (assignees, priorities, all tags) and `has_active_filters` flag for the clear-all link.

2. **Template** (`chores/templates/chores/task_list.html`):
   - Added a filter bar with dropdowns for assignee, priority, status
   - Added tag multi-select checkboxes (OR logic within tags)
   - Added text search input (debounced 400ms auto-submit)
   - Auto-submit on select change, checkbox change, and search input
   - "Clear All" link resets all filters
   - Empty-state message changes when filters are active ("No chores match your filters")
   - No Apply button required — filters apply immediately on change

3. **Base template** (`chores/templates/chores/base.html`): Added `{lock extra_js 
## Comment (Software Engineer — 2026-09-07)

Verified implementation is complete and all tests pass:

- **Views** (`chores/views.py`): `TaskListView` handles `assignee`, `priority`, `status`, `tags` (multi-select), and `search` query parameters with proper filtering logic.
- **Template** (`chores/templates/chores/task_list.html`): Filter bar with dropdowns, tag checkboxes, text search, auto-submit on change, Clear All link, and contextual empty-state messages.
- **Base template** (`chores/templates/chores/base.html`): `{% block extra_js %}{% endblock %}` present for filter JavaScript.
- **Tests** (`chores/tests/test_search_filters.py`): 30 tests covering all acceptance criteria — all passing.

Full suite: 51 tests pass (30 search/filters + 21 settings). Commit: `104d989`.

Task remains open.
