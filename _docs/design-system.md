# Design System

## Overview

A mobile-friendly web app for couples to track household chores. The design should be clean, simple, and easy to use on small screens.

## Layout

- Single-column layout on mobile, max-width container centered.
- Bottom navigation bar with links to: Task List, Calendar, Completed, Settings.
- Sticky header with the app name and current page title.

## Colors

- **Primary**: `#2563eb` (blue) — links, buttons, active states.
- **Success**: `#16a34a` (green) — completed actions.
- **Warning**: `#f59e0b` (amber) — due soon.
- **Danger**: `#dc2626` (red) — overdue chores, delete actions.
- **Neutral**: `#6b7280` (gray) — secondary text, borders.
- **Background**: `#f9fafb` (light gray) — page background.
- **Surface**: `#ffffff` (white) — cards, inputs.

## Typography

- System font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`.
- Base size: 16px. Headings: 1.25rem–1.5rem. Body: 1rem.
- Chore titles: bold, 1rem. Due dates: 0.875rem, gray.

## Components

### Chore Card
- White card with subtle shadow, rounded corners (8px).
- Shows: title, due date, assignee badge, priority indicator.
- Overdue: left border or background tint in red.
- Tap to open detail view.

### Buttons
- Primary: blue background, white text, rounded (6px), full-width on mobile.
- Secondary: white background, blue border/text.
- Danger: red background, white text — for delete actions.

### Forms
- Full-width inputs with labels above.
- Date picker for due date.
- Select dropdowns for assignee and priority.
- Tag input: type and press Enter to add a tag chip.

### Badges
- Assignee: small rounded pill with initials or name.
- Priority: colored dot (green/yellow/red) next to text.
- Tags: small gray chips, removable.

## Responsive Breakpoints

- Mobile-first. Tablet and desktop: max-width 720px container, larger touch targets.

## Accessibility

- Minimum touch target: 44x44px.
- Sufficient color contrast (WCAG AA).
- Focus visible on interactive elements.
- Form inputs always have associated labels.
