"""Tests for reminder email draft generation (Task 8)."""
import pytest
from datetime import date, timedelta
from unittest.mock import patch
from django.test import RequestFactory, TestCase
from django.utils import timezone

from chores.models import Chore
from chores.views import get_reminder_mailto, TaskListView, TaskDetailView


@pytest.mark.django_db
class TestGetReminderMailto:
    """Tests for the get_reminder_mailto helper function."""

    def _make_chore(self, title, due_date, completed=False):
        return Chore.objects.create(
            title=title,
            due_date=due_date,
            completed=completed,
        )

    def test_returns_none_when_no_chores(self):
        """No chores at all → returns None."""
        assert get_reminder_mailto() is None

    def test_returns_none_when_all_completed(self):
        """All chores completed → returns None."""
        today = timezone.localdate()
        self._make_chore("Old chore", today - timedelta(days=1), completed=True)
        assert get_reminder_mailto() is None

    def test_returns_none_when_no_chores_need_attention(self):
        """Chores exist but none are overdue/due today/due tomorrow → None."""
        today = timezone.localdate()
        self._make_chore("Future chore", today + timedelta(days=5))
        assert get_reminder_mailto() is None

    def test_includes_overdue_chores(self):
        """Overdue chores appear in the mailto body."""
        today = timezone.localdate()
        self._make_chore("Wash dishes", today - timedelta(days=2))
        mailto = get_reminder_mailto()
        assert mailto is not None
        assert "mailto:?" in mailto
        assert "Wash%20dishes" in mailto  # URL-encoded title
        assert "Overdue%3A" in mailto  # URL-encoded "Overdue:"

    def test_includes_due_today_chores(self):
        """Due-today chores appear in the mailto body."""
        today = timezone.localdate()
        self._make_chore("Take out trash", today)
        mailto = get_reminder_mailto()
        assert mailto is not None
        assert "Take%20out%20trash" in mailto
        assert "Due%20Today%3A" in mailto

    def test_includes_due_tomorrow_chores(self):
        """Due-tomorrow chores appear in the mailto body."""
        today = timezone.localdate()
        self._make_chore("Buy groceries", today + timedelta(days=1))
        mailto = get_reminder_mailto()
        assert mailto is not None
        assert "Buy%20groceries" in mailto
        assert "Due%20Tomorrow%3A" in mailto

    def test_groups_all_three_sections(self):
        """All three sections present when applicable."""
        today = timezone.localdate()
        self._make_chore("Overdue chore", today - timedelta(days=1))
        self._make_chore("Today chore", today)
        self._make_chore("Tomorrow chore", today + timedelta(days=1))
        mailto = get_reminder_mailto()
        assert "Overdue%3A" in mailto
        assert "Due%20Today%3A" in mailto
        assert "Due%20Tomorrow%3A" in mailto

    def test_body_contains_title_and_due_date(self):
        """Each entry shows title and due date."""
        today = timezone.localdate()
        self._make_chore("Clean bathroom", today - timedelta(days=1))
        mailto = get_reminder_mailto()
        # Title is URL-encoded
        assert "Clean%20bathroom" in mailto
        # Due date formatted as "Mon DD, YYYY" - comma is encoded as %2C
        due_str = (today - timedelta(days=1)).strftime("%b %d, %Y")
        assert due_str.replace(" ", "%20").replace(",", "%2C") in mailto

    def test_body_excludes_notes_priority_assignee_tags(self):
        """Notes, priority, assignee, and tags are NOT in the body."""
        today = timezone.localdate()
        chore = self._make_chore(
            "Test chore",
            today,
            completed=False,
        )
        chore.notes = "Some secret notes"
        chore.priority = "High"
        chore.assignee = "Alex"
        chore.save()

        mailto = get_reminder_mailto()
        # These should NOT appear (URL-encoded or not)
        assert "secret" not in mailto
        assert "High" not in mailto
        assert "Alex" not in mailto

    def test_special_characters_url_encoded(self):
        """Special characters in titles are URL-encoded."""
        today = timezone.localdate()
        self._makeChore = None  # noqa
        self._make_chore("Mop & sweep / floors", today)
        mailto = get_reminder_mailto()
        # & and / should be encoded
        assert "Mop%20%26%20sweep%20%2F%20floors" in mailto

    def test_subject_is_chore_reminders(self):
        """Subject line references 'Chore reminders'."""
        today = timezone.localdate()
        self._make_chore("Any chore", today)
        mailto = get_reminder_mailto()
        assert "subject=Chore%20reminders" in mailto

    def test_combines_all_chores_into_single_email(self):
        """Multiple chores → single mailto link, not one per chore."""
        today = timezone.localdate()
        self._make_chore("Chore A", today - timedelta(days=1))
        self._make_chore("Chore B", today)
        self._make_chore("Chore C", today + timedelta(days=1))
        mailto = get_reminder_mailto()
        # Only one mailto: prefix
        assert mailto.count("mailto:") == 1
        # All three chores present
        assert "Chore%20A" in mailto
        assert "Chore%20B" in mailto
        assert "Chore%20C" in mailto

    def test_only_one_section_shown_when_only_one_applies(self):
        """Only the relevant section headers appear."""
        today = timezone.localdate()
        self._make_chore("Only overdue", today - timedelta(days=3))
        mailto = get_reminder_mailto()
        assert "Overdue%3A" in mailto
        assert "Due%20Today%3A" not in mailto
        assert "Due%20Tomorrow%3A" not in mailto


@pytest.mark.django_db
class TestTaskListViewReminder:
    """Tests for reminder action in the task list view."""

    def _make_chore(self, title, due_date, completed=False):
        return Chore.objects.create(
            title=title,
            due_date=due_date,
            completed=completed,
        )

    def test_reminder_link_present_when_chores_need_attention(self):
        """Task list shows reminder link when chores need attention."""
        today = timezone.localdate()
        self._make_chore("Overdue chore", today - timedelta(days=1))
        factory = RequestFactory()
        request = factory.get("/")
        view = TaskListView()
        view.setup(request)
        response = view.get(request)
        assert response.status_code == 200
        content = response.content.decode()
        assert "mailto:" in content
        assert "Generate%20Reminder" in content or "Generate Reminder" in content

    def test_reminder_link_absent_when_no_chores_need_attention(self):
        """Task list hides reminder link when no chores need attention."""
        today = timezone.localdate()
        self._make_chore("Future chore", today + timedelta(days=5))
        factory = RequestFactory()
        request = factory.get("/")
        view = TaskListView()
        view.setup(request)
        response = view.get(request)
        assert response.status_code == 200
        content = response.content.decode()
        assert "mailto:" not in content


@pytest.mark.django_db
class TestTaskDetailViewReminder:
    """Tests for reminder action in the task detail view."""

    def _make_chore(self, title, due_date, completed=False):
        return Chore.objects.create(
            title=title,
            due_date=due_date,
            completed=completed,
        )

    def test_reminder_link_present_when_chores_need_attention(self):
        """Task detail shows reminder link when chores need attention."""
        today = timezone.localdate()
        chore = self._make_chore("Overdue chore", today - timedelta(days=1))
        factory = RequestFactory()
        request = factory.get(f"/{chore.pk}/")
        view = TaskDetailView()
        view.setup(request)
        response = view.get(request, pk=chore.pk)
        assert response.status_code == 200
        content = response.content.decode()
        assert "mailto:" in content

    def test_reminder_link_absent_when_no_chores_need_attention(self):
        """Task detail hides reminder link when no chores need attention."""
        today = timezone.localdate()
        chore = self._make_chore("Future chore", today + timedelta(days=5))
        factory = RequestFactory()
        request = factory.get(f"/{chore.pk}/")
        view = TaskDetailView()
        view.setup(request)
        response = view.get(request, pk=chore.pk)
        assert response.status_code == 200
        content = response.content.decode()
        assert "mailto:" not in content
