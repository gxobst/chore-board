"""Tests for Task 11: Overdue highlighting on the task list view."""
import pytest
from datetime import date, timedelta

from django.test import TestCase, Client
from django.utils import timezone

from chores.models import Chore


@pytest.mark.django_db
class TestOverdueHighlighting(TestCase):
    """Tests for the overdue highlighting feature on the task list view."""

    def setUp(self):
        self.client = Client()
        self.today = timezone.localdate()

    def test_past_due_chore_is_highlighted_overdue(self):
        """A chore with due date in the past and not completed is marked with overdue styling."""
        past_date = self.today - timedelta(days=3)
        Chore.objects.create(
            title="Overdue chore",
            due_date=past_date,
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "overdue" in content
        # Verify the overdue class is on the chore card
        assert 'class="chore-card overdue"' in content

    def test_today_due_chore_is_not_highlighted(self):
        """A chore due today is NOT highlighted as overdue — today is not 'in the past.'"""
        Chore.objects.create(
            title="Due today chore",
            due_date=self.today,
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        # The chore card should NOT have the overdue class
        assert 'class="chore-card overdue"' not in content
        # But the chore should still appear
        assert "Due today chore" in content

    def test_future_due_chore_is_not_highlighted(self):
        """A chore due in the future is NOT highlighted as overdue."""
        future_date = self.today + timedelta(days=5)
        Chore.objects.create(
            title="Future chore",
            due_date=future_date,
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="chore-card overdue"' not in content
        assert "Future chore" in content

    def test_completed_past_due_chore_not_in_task_list(self):
        """A completed chore (even with past due date) does not appear in the task list."""
        past_date = self.today - timedelta(days=7)
        Chore.objects.create(
            title="Completed overdue chore",
            due_date=past_date,
            completed=True,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        # Completed chore should not appear in the task list
        assert "Completed overdue chore" not in content
        # No chore card should have the overdue class
        assert 'class="chore-card overdue"' not in content

    def test_mixed_chores_only_overdue_highlighted(self):
        """Only past-due active chores get the overdue class; today/future do not."""
        past_date = self.today - timedelta(days=2)
        future_date = self.today + timedelta(days=2)
        Chore.objects.create(title="Past chore", due_date=past_date, completed=False)
        Chore.objects.create(title="Today chore", due_date=self.today, completed=False)
        Chore.objects.create(title="Future chore", due_date=future_date, completed=False)

        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()

        # Only one overdue card
        assert content.count('class="chore-card overdue"') == 1
        # All three chores appear
        assert "Past chore" in content
        assert "Today chore" in content
        assert "Future chore" in content

    def test_overdue_highlighting_evaluated_at_render_time(self):
        """Highlighting is evaluated at render time — no stale state after due date edit."""
        past_date = self.today - timedelta(days=5)
        future_date = self.today + timedelta(days=5)
        chore = Chore.objects.create(
            title="Editable chore",
            due_date=past_date,
            completed=False,
        )

        # Initially overdue
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' in content

        # Edit due date to future
        chore.due_date = future_date
        chore.save()

        # No longer overdue after edit
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' not in content
        assert "Editable chore" in content

    def test_editing_to_past_date_adds_overdue_highlighting(self):
        """When a chore's due date is edited from today/future to a past date, the red highlighting appears."""
        future_date = self.today + timedelta(days=5)
        past_date = self.today - timedelta(days=1)
        chore = Chore.objects.create(
            title="Becoming overdue",
            due_date=future_date,
            completed=False,
        )

        # Initially NOT overdue
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' not in content

        # Edit due date to past
        chore.due_date = past_date
        chore.save()

        # Now overdue
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' in content

    def test_editing_to_today_removes_overdue_highlighting(self):
        """When a chore's due date is edited from past to today, the red highlighting is removed."""
        past_date = self.today - timedelta(days=3)
        chore = Chore.objects.create(
            title="No longer overdue",
            due_date=past_date,
            completed=False,
        )

        # Initially overdue
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' in content

        # Edit due date to today
        chore.due_date = self.today
        chore.save()

        # No longer overdue
        response = self.client.get("/")
        content = response.content.decode()
        assert 'class="chore-card overdue"' not in content

    def test_overdue_css_uses_design_system_red(self):
        """The overdue styling uses the design system's red/error color token (#dc2626)."""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        # The base template CSS should define the overdue style with #dc2626
        assert "#dc2626" in content
        assert ".chore-card.overdue" in content

    def test_overdue_chore_shows_due_date(self):
        """An overdue chore still displays its due date in the card."""
        past_date = self.today - timedelta(days=1)
        Chore.objects.create(
            title="Overdue with date",
            due_date=past_date,
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Overdue with date" in content
        assert 'class="chore-card overdue"' in content

    def test_empty_list_no_overdue(self):
        """When no chores exist, no overdue highlighting is present on any chore card."""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        # No chore card should have the overdue class
        assert 'class="chore-card overdue"' not in content

    def test_yesterday_is_overdue(self):
        """A chore due yesterday is highlighted as overdue."""
        yesterday = self.today - timedelta(days=1)
        Chore.objects.create(
            title="Due yesterday",
            due_date=yesterday,
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'class="chore-card overdue"' in content

    def test_multiple_overdue_chores_all_highlighted(self):
        """Multiple past-due chores all get the overdue class."""
        Chore.objects.create(
            title="Overdue 1",
            due_date=self.today - timedelta(days=1),
            completed=False,
        )
        Chore.objects.create(
            title="Overdue 2",
            due_date=self.today - timedelta(days=10),
            completed=False,
        )
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert content.count('class="chore-card overdue"') == 2
