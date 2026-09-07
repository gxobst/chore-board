# Testing Guidelines

## General Principles

- Write tests for every new feature, including edge cases.
- Tests should be independent and not rely on shared mutable state.
- Run the full suite before marking a task complete: `uv run pytest`.

## Test Organization

- Place tests in the `tests/` directory or alongside the module (e.g., `chores/tests.py`).
- Name test files `test_<module>.py` and test functions `test_<behavior>`.

## What to Test

- **Models**: field validation, constraints, string representation.
- **Views**: HTTP status codes, template usage, context data, redirects.
- **Forms**: valid/invalid input, error messages, saving.
- **Edge cases**: empty input, boundary values, missing required fields.

## Fixtures and Factories

- Use `pytest-django` fixtures or factory functions to create test data.
- Avoid relying on database state from other tests.

## Running Tests

- `uv run pytest` — full suite.
- `uv run pytest tests/test_home.py` — single file.
- `uv run pytest -x` — stop on first failure.
- `uv run pytest -k "test_name"` — run a specific test.
