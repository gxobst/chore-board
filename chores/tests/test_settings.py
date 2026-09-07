"""Tests for Settings page (Task 9): export, import, and clear all data."""
import json
import pytest
from datetime import date
from io import BytesIO

from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile

from chores.models import Chore, Tag


@pytest.mark.django_db
class TestSettingsPage(TestCase):
    """Tests for the Settings page accessibility."""

    def setUp(self):
        self.client = Client()

    def test_settings_page_returns_200(self):
        """Settings page is accessible and returns 200."""
        response = self.client.get("/settings/")
        assert response.status_code == 200

    def test_settings_page_contains_export_import_clear(self):
        """Settings page displays Export, Import, and Clear All Data actions."""
        response = self.client.get("/settings/")
        content = response.content.decode()
        assert "Export" in content
        assert "Import" in content
        assert "Clear All Data" in content

    def test_settings_link_in_bottom_nav(self):
        """Bottom navigation bar includes a link to Settings."""
        response = self.client.get("/")
        content = response.content.decode()
        assert 'href="/settings/"' in content


@pytest.mark.django_db
class TestExportDataView(TestCase):
    """Tests for the export data functionality."""

    def setUp(self):
        self.client = Client()

    def test_export_returns_json_download(self):
        """Export returns a JSON file download."""
        response = self.client.get("/settings/export/")
        assert response.status_code == 200
        assert response["Content-Type"] == "application/json"
        assert "attachment" in response["Content-Disposition"]

    def test_export_filename_has_date(self):
        """Exported file has a descriptive filename with date."""
        response = self.client.get("/settings/export/")
        disposition = response["Content-Disposition"]
        assert "chores-backup-" in disposition
        assert ".json" in disposition

    def test_export_contains_all_chores(self):
        """Export contains all chores (active and completed)."""
        chore1 = Chore.objects.create(
            title="Active chore",
            due_date=date(2025, 1, 15),
            completed=False,
        )
        chore2 = Chore.objects.create(
            title="Completed chore",
            due_date=date(2025, 1, 10),
            completed=True,
        )

        response = self.client.get("/settings/export/")
        data = json.loads(response.content)
        assert "chores" in data
        assert len(data["chores"]) == 2
        titles = [c["title"] for c in data["chores"]]
        assert "Active chore" in titles
        assert "Completed chore" in titles

    def test_export_empty_database(self):
        """Export with no chores returns empty array."""
        response = self.client.get("/settings/export/")
        data = json.loads(response.content)
        assert data["chores"] == []

    def test_export_preserves_chore_fields(self):
        """Export preserves all chore fields."""
        tag = Tag.objects.create(name="kitchen")
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date=date(2025, 1, 15),
            assignee="Alex",
            notes="Use soap",
            priority="High",
            recurrence="weekly",
            completed=False,
        )
        chore.tags.add(tag)

        response = self.client.get("/settings/export/")
        data = json.loads(response.content)
        exported = data["chores"][0]
        assert exported["title"] == "Wash dishes"
        assert exported["due_date"] == "2025-01-15"
        assert exported["assignee"] == "Alex"
        assert exported["notes"] == "Use soap"
        assert exported["priority"] == "High"
        assert exported["recurrence"] == "weekly"
        assert exported["completed"] is False
        assert "kitchen" in exported["tags"]


@pytest.mark.django_db
class TestImportDataView(TestCase):
    """Tests for the import data functionality."""

    def setUp(self):
        self.client = Client()

    def _make_export_data(self, chores=None):
        """Helper to create valid export JSON data."""
        if chores is None:
            chores = []
        return json.dumps({"chores": chores}).encode("utf-8")

    def test_import_valid_json_adds_chores(self):
        """Import adds chores from a valid JSON file."""
        data = self._make_export_data([
            {
                "title": "Imported chore",
                "due_date": "2025-02-01",
                "assignee": "Jordan",
                "notes": "Test notes",
                "priority": "Medium",
                "tags": ["cleaning"],
                "completed": False,
                "recurrence": "none",
            }
        ])
        uploaded = SimpleUploadedFile("test.json", data, content_type="application/json")
        response = self.client.post("/settings/import/", {"file": uploaded})
        assert response.status_code == 200
        assert Chore.objects.count() == 1
        chore = Chore.objects.first()
        assert chore.title == "Imported chore"
        assert chore.due_date == date(2025, 2, 1)
        assert chore.assignee == "Jordan"

    def test_import_shows_success_message(self):
        """After successful import, user sees confirmation with count."""
        data = self._make_export_data([
            {"title": "Chore 1", "due_date": "2025-02-01"},
            {"title": "Chore 2", "due_date": "2025-02-02"},
        ])
        uploaded = SimpleUploadedFile("test.json", data, content_type="application/json")
        response = self.client.post("/settings/import/", {"file": uploaded})
        content = response.content.decode()
        assert "Successfully imported 2 chores" in content

    def test_import_malformed_json_shows_error(self):
        """Import with malformed JSON shows error and does not modify data."""
        Chore.objects.create(title="Existing", due_date=date(2025, 1, 1))
        bad_data = b"{invalid json content"
        uploaded = SimpleUploadedFile("bad.json", bad_data, content_type="application/json")
        response = self.client.post("/settings/import/", {"file": uploaded})
        assert response.status_code == 200
        content = response.content.decode()
        assert "Invalid JSON" in content
        # Existing data unchanged
        assert Chore.objects.count() == 1
        assert Chore.objects.first().title == "Existing"

    def test_import_empty_file_shows_error(self):
        """Import with empty file shows error and does not modify data."""
        Chore.objects.create(title="Existing", due_date=date(2025, 1, 1))
        uploaded = SimpleUploadedFile("empty.json", b"", content_type="application/json")
        response = self.client.post("/settings/import/", {"file": uploaded})
        assert response.status_code == 200
        content = response.content.decode()
        assert "empty" in content.lower()
        assert Chore.objects.count() == 1

    def test_import_wrong_schema_shows_error(self):
        """Import with valid JSON but no chores array shows error."""
        Chore.objects.create(title="Existing", due_date=date(2025, 1, 1))
        data = json.dumps({"tasks": []}).encode("utf-8")
        uploaded = SimpleUploadedFile("wrong.json", data, content_type="application/json")
        response = self.client.post("/settings/import/", {"file": uploaded})
        assert response.status_code == 200
        content = response.content.decode()
        assert "chores" in content.lower()
        assert Chore.objects.count() == 1

    def test_import_no_file_shows_error(self):
        """Import with no file selected shows error."""
        response = self.client.post("/settings/import/", {})
        assert response.status_code == 200
        content = response.content.decode()
        assert "No file" in content

    def test_import_allows_duplicates(self):
        """Import allows duplicate chores (no deduplication)."""
        def make_upload():
            data = self._make_export_data([
                {"title": "Duplicate chore", "due_date": "2025-02-01"},
            ])
            return SimpleUploadedFile("test.json", data, content_type="application/json")
        
        self.client.post("/settings/import/", {"file": make_upload()})
        self.client.post("/settings/import/", {"file": make_upload()})
        assert Chore.objects.filter(title="Duplicate chore").count() == 2

    def test_import_roundtrip(self):
        """Exported JSON can be re-imported and produces the same chores."""
        # Create a chore and export it
        Chore.objects.create(
            title="Roundtrip chore",
            due_date=date(2025, 3, 1),
            assignee="Alex",
            priority="High",
        )
        response = self.client.get("/settings/export/")
        exported_data = response.content

        # Clear the database
        Chore.objects.all().delete()
        assert Chore.objects.count() == 0

        # Re-import
        uploaded = SimpleUploadedFile("export.json", exported_data, content_type="application/json")
        self.client.post("/settings/import/", {"file": uploaded})

        assert Chore.objects.count() == 1
        chore = Chore.objects.first()
        assert chore.title == "Roundtrip chore"
        assert chore.due_date == date(2025, 3, 1)
        assert chore.assignee == "Alex"
        assert chore.priority == "High"


@pytest.mark.django_db
class TestClearDataView(TestCase):
    """Tests for the clear all data functionality."""

    def setUp(self):
        self.client = Client()

    def test_clear_page_shows_confirmation(self):
        """Clear All Data shows a confirmation page."""
        response = self.client.get("/settings/clear/")
        assert response.status_code == 200
        content = response.content.decode()
        assert "Warning" in content or "permanently" in content.lower()

    def test_clear_confirm_removes_all_data(self):
        """Confirming Clear All Data removes every chore."""
        Chore.objects.create(title="Chore 1", due_date=date(2025, 1, 1))
        Chore.objects.create(title="Chore 2", due_date=date(2025, 1, 2), completed=True)
        assert Chore.objects.count() == 2

        response = self.client.post("/settings/clear/", follow=True)
        assert response.status_code == 200
        assert Chore.objects.count() == 0

    def test_clear_cancel_leaves_data_unchanged(self):
        """Canceling the confirmation leaves all data unchanged."""
        Chore.objects.create(title="Chore 1", due_date=date(2025, 1, 1))
        assert Chore.objects.count() == 1

        # User clicks cancel (goes back to settings)
        response = self.client.get("/settings/")
        assert response.status_code == 200
        assert Chore.objects.count() == 1

    def test_clear_shows_success_message(self):
        """After clearing, user sees the settings page (data is gone)."""
        Chore.objects.create(title="Chore 1", due_date=date(2025, 1, 1))
        response = self.client.post("/settings/clear/", follow=True)
        assert response.status_code == 200
        # After clearing, user is redirected to settings page
        assert Chore.objects.count() == 0
        content = response.content.decode()
        # Settings page title visible
        assert "Settings" in content

    def test_clear_empty_database(self):
        """Clear on empty database is a no-op."""
        response = self.client.post("/settings/clear/", follow=True)
        assert response.status_code == 200
        assert Chore.objects.count() == 0
