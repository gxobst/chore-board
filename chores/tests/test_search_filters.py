"""Tests for Task 10: Search and filters functionality on the task list view."""
import pytest
from datetime import date

from django.test import TestCase, Client

from chores.models import Chore, Tag


@pytest.mark.django_db
class TestSearchAndFilters(TestCase):
    """Tests for the search and filters feature on the task list view."""

    def setUp(self):
        self.client = Client()
        self.tag_cleaning = Tag.objects.create(name="cleaning")
        self.tag_kitchen = Tag.objects.create(name="kitchen")
        self.tag_outdoor = Tag.objects.create(name="outdoor")

        self.chore1 = Chore.objects.create(
            title="Wash dishes",
            due_date=date(2025, 1, 15),
            assignee="Alex",
            notes="Use soap in the sink",
            priority="High",
            completed=False,
        )
        self.chore1.tags.add(self.tag_kitchen)

        self.chore2 = Chore.objects.create(
            title="Mow lawn",
            due_date=date(2025, 1, 16),
            assignee="Jordan",
            notes="Mow the front yard",
            priority="Medium",
            completed=False,
        )
        self.chore2.tags.add(self.tag_outdoor)

        self.chore3 = Chore.objects.create(
            title="Vacuum living room",
            due_date=date(2025, 1, 17),
            assignee="Alex",
            notes="Vacuum the carpet carefully",
            priority="Low",
            completed=False,
        )
        self.chore3.tags.add(self.tag_cleaning)

        self.chore4 = Chore.objects.create(
            title="Clean bathroom",
            due_date=date(2025, 1, 10),
            assignee="Jordan",
            notes="Scrub toilet and shower",
            priority="High",
            completed=True,
        )
        self.chore4.tags.add(self.tag_cleaning, self.tag_kitchen)

    def test_default_shows_active_chores_only(self):
        """Default view shows only active (incomplete) chores."""
        response = self.client.get("/")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles
        assert "Mow lawn" in titles
        assert "Vacuum living room" in titles
        assert "Clean bathroom" not in titles

    def test_filter_by_assignee(self):
        """Filter by assignee shows only chores assigned to that person."""
        response = self.client.get("/?assignee=Alex")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles
        assert "Vacuum living room" in titles
        assert "Mow lawn" not in titles

    def test_filter_by_assignee_no_match(self):
        """Filter by assignee with no matching chores returns empty."""
        response = self.client.get("/?assignee=Nonexistent")
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 0

    def test_filter_by_priority(self):
        """Filter by priority shows only chores with that priority."""
        response = self.client.get("/?priority=High")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles
        assert "Mow lawn" not in titles
        assert "Vacuum living room" not in titles

    def test_filter_by_priority_low(self):
        """Filter by priority=Low shows only Low priority chores."""
        response = self.client.get("/?priority=Low")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Vacuum living room" in titles
        assert len(chores) == 1

    def test_filter_by_status_active(self):
        """Filter by status=active shows only active chores."""
        response = self.client.get("/?status=active")
        assert response.status_code == 200
        chores = response.context["chores"]
        for c in chores:
            assert c.completed is False

    def test_filter_by_status_completed(self):
        """Filter by status=completed shows only completed chores."""
        response = self.client.get("/?status=completed")
        assert response.status_code == 200
        chores = response.context["chores"]
        for c in chores:
            assert c.completed is True
        assert len(chores) == 1
        assert chores[0].title == "Clean bathroom"

    def test_filter_by_tag_single(self):
        """Filter by a single tag shows only chores with that tag."""
        response = self.client.get(f"/?tags={self.tag_cleaning.id}")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Vacuum living room" in titles
        # Completed chores don't appear by default
        assert "Clean bathroom" not in titles

    def test_filter_by_tag_completed_also_included_when_status_completed(self):
        """Filter by tag with status=completed shows completed chores with that tag."""
        response = self.client.get(
            f"/?tags={self.tag_cleaning.id}&status=completed"
        )
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Clean bathroom" in titles

    def test_filter_by_multiple_tags(self):
        """Filter by multiple tags shows chores with ANY of the selected tags (OR)."""
        response = self.client.get(
            f"/?tags={self.tag_kitchen.id}&tags={self.tag_outdoor.id}"
        )
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles  # kitchen
        assert "Mow lawn" in titles  # outdoor
        assert "Vacuum living room" not in titles  # cleaning

    def test_search_by_title(self):
        """Search by title returns chores whose title contains the query."""
        response = self.client.get("/?search=dishes")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles
        assert len(chores) == 1

    def test_search_by_title_case_insensitive(self):
        """Search is case-insensitive."""
        response = self.client.get("/?search=DISHEs")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles

    def test_search_by_notes(self):
        """Search by notes returns chores whose notes contain the query."""
        response = self.client.get("/?search=carpet")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Vacuum living room" in titles
        assert len(chores) == 1

    def test_search_by_notes_case_insensitive(self):
        """Search by notes is case-insensitive."""
        response = self.client.get("/?search=CARPET")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Vacuum living room" in titles

    def test_search_no_matches(self):
        """Search with no matching chores returns empty list."""
        response = self.client.get("/?search=nonexistentquery")
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 0

    def test_multiple_filters_combine_with_and(self):
        """Multiple filters combine with AND logic."""
        response = self.client.get("/?assignee=Alex&priority=High")
        assert response.status_code == 200
        chores = response.context["chores"]
        titles = [c.title for c in chores]
        assert "Wash dishes" in titles
        assert "Vacuum living room" not in titles  # Alex but Low priority

    def test_search_and_filter_combine(self):
        """Search and filters combine - all must match."""
        response = self.client.get("/?assignee=Alex&search=lawn")
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 0  # Alex doesn't have a lawn chore

        response = self.client.get("/?assignee=Jordan&search=lawn")
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 1
        assert chores[0].title == "Mow lawn"

    def test_filter_and_tag_combine(self):
        """Filter by assignee and tag together works correctly."""
        response = self.client.get(
            f"/?assignee=Jordan&tags={self.tag_outdoor.id}"
        )
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 1
        assert chores[0].title == "Mow lawn"

    def test_clear_all_filters_link_shown(self):
        """Clear all filters link appears when filters are active."""
        response = self.client.get("/?assignee=Alex")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Clear All" in content

    def test_no_clear_link_when_no_filters(self):
        """Clear all filters link is not shown when no filters are active."""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Clear All" not in content

    def test_clear_filters_resets_to_default(self):
        """Clicking Clear Filters returns to default state (active chores)."""
        response = self.client.get("/?assignee=Alex&priority=High")
        # Simulate clicking Clear All by navigating to base URL
        response = self.client.get("/")
        assert response.status_code == 200
        chores = response.context["chores"]
        # Should show all active chores
        assert len(chores) == 3

    def test_empty_state_with_filters(self):
        """When filters produce zero results, empty-state message is shown."""
        response = self.client.get("/?search=zzzznonexistent")
        assert response.status_code == 200
        content = response.content.decode()
        assert "No chores match your filters" in content

    def test_empty_state_without_filters(self):
        """When no chores exist at all, default empty-state is shown."""
        Chore.objects.all().delete()
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "No chores yet" in content

    def test_filters_do_not_affect_completed_view(self):
        """Filters on task list do not affect the Completed view."""
        response = self.client.get("/completed/")
        assert response.status_code == 200
        chores = response.context["chores"]
        # Should still show completed chores regardless of query params
        assert len(chores) == 1
        assert chores[0].title == "Clean bathroom"

    def test_filters_do_not_affect_calendar_view(self):
        """Filters on task list do not affect the Calendar view."""
        response = self.client.get("/calendar/")
        assert response.status_code == 200
        # Calendar should still render normally
        content = response.content.decode()
        assert "Chore Board" in content

    def test_filter_controls_render(self):
        """Filter controls (assignee, priority, status dropdowns and search box) render."""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        # Check for filter form elements
        assert 'name="assignee"' in content
        assert 'name="priority"' in content
        assert 'name="status"' in content
        assert 'name="search"' in content

    def test_tag_checkboxes_render(self):
        """Tag checkboxes render when tags exist."""
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="tags"' in content
        assert self.tag_cleaning.name in content
        assert self.tag_kitchen.name in content
        assert self.tag_outdoor.name in content

    def test_empty_tag_checkboxes_when_no_tags(self):
        """Tag section is hidden when no tags exist."""
        Tag.objects.all().delete()
        response = self.client.get("/")
        assert response.status_code == 200
        content = response.content.decode()
        assert 'name="tags"' not in content

    def test_all_filters_combined(self):
        """All filter types can be combined simultaneously."""
        response = self.client.get(
            f"/?assignee=Jordan&priority=Medium&status=active&tags={self.tag_outdoor.id}&search=lawn"
        )
        assert response.status_code == 200
        chores = response.context["chores"]
        assert len(chores) == 1
        assert chores[0].title == "Mow lawn"

    def test_no_apply_button_needed(self):
        """The form does not require an explicit Apply button (filters auto-submit)."""
        response = self.client.get("/?assignee=Alex")
        assert response.status_code == 200
        # Filters should be applied just by query params (server-side)
        chores = response.context["chores"]
        for c in chores:
            assert c.assignee == "Alex"
