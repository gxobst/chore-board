from django.test import TestCase, Client
from django.urls import reverse
from django.db.utils import IntegrityError
from chores.models import Chore, Tag


class TagModelTest(TestCase):
    def test_tag_str_returns_name(self):
        tag = Tag.objects.create(name="Kitchen")
        self.assertEqual(str(tag), "Kitchen")

    def test_tag_name_unique(self):
        Tag.objects.create(name="Kitchen")
        with self.assertRaises(IntegrityError):
            Tag.objects.create(name="Kitchen")


class ChoreModelTest(TestCase):
    def test_chore_str_returns_title(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(str(chore), "Wash dishes")

    def test_create_chore_with_required_fields(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertIsNotNone(chore.pk)
        self.assertEqual(chore.title, "Wash dishes")
        self.assertEqual(str(chore.due_date), "2025-01-15")

    def test_chore_default_values(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(chore.assignee, "")
        self.assertEqual(chore.notes, "")
        self.assertEqual(chore.priority, "")
        self.assertFalse(chore.completed)

    def test_chore_with_all_fields(self):
        tag = Tag.objects.create(name="Kitchen")
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            assignee="Alice",
            notes="Use soap",
            priority="High",
        )
        chore.tags.add(tag)
        self.assertEqual(chore.assignee, "Alice")
        self.assertEqual(chore.notes, "Use soap")
        self.assertEqual(chore.priority, "High")
        self.assertIn(tag, chore.tags.all())

    def test_title_required(self):
        from django.core.exceptions import ValidationError
        chore = Chore(due_date="2025-01-15")
        with self.assertRaises(ValidationError):
            chore.full_clean()

    def test_due_date_required(self):
        chore = Chore(title="Wash dishes")
        with self.assertRaises(IntegrityError):
            chore.save()

    def test_assignee_optional(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(chore.assignee, "")

    def test_notes_optional(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(chore.notes, "")

    def test_priority_optional(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(chore.priority, "")

    def test_tags_optional(self):
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        self.assertEqual(chore.tags.count(), 0)

    def test_priority_choices(self):
        valid_choices = ["Low", "Medium", "High"]
        for choice in valid_choices:
            chore = Chore.objects.create(
                title=f"Chore {choice}", due_date="2025-01-15", priority=choice
            )
            self.assertEqual(chore.priority, choice)

    def test_m2m_tags_bidirectional(self):
        tag1 = Tag.objects.create(name="Kitchen")
        tag2 = Tag.objects.create(name="Cleaning")
        chore = Chore.objects.create(title="Wash dishes", due_date="2025-01-15")
        chore.tags.add(tag1, tag2)
        self.assertEqual(chore.tags.count(), 2)
        self.assertIn(chore, tag1.chore_set.all())
        self.assertIn(chore, tag2.chore_set.all())

    def test_chore_ordered_by_due_date(self):
        Chore.objects.create(title="Later", due_date="2025-02-15")
        Chore.objects.create(title="Earlier", due_date="2025-01-15")
        chores = list(Chore.objects.all())
        self.assertEqual(chores[0].title, "Earlier")
        self.assertEqual(chores[1].title, "Later")


class CreateChoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("create_chore")

    def test_get_returns_200_and_renders_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create New Chore")
        self.assertContains(response, "Title")
        self.assertContains(response, "Due Date")
        self.assertContains(response, "Assignee")
        self.assertContains(response, "Priority")
        self.assertContains(response, "Tags")
        self.assertContains(response, "Notes")

    def test_form_reachable_from_navigation(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Add")
        self.assertContains(response, self.url)

    def test_post_valid_data_creates_chore_and_redirects(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "Alex",
            "notes": "Use soap",
            "priority": "High",
            "tags_text": "Kitchen, Cleaning",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task_list"))
        self.assertEqual(Chore.objects.count(), 1)
        chore = Chore.objects.first()
        self.assertEqual(chore.title, "Wash dishes")
        self.assertEqual(str(chore.due_date), "2025-01-15")
        self.assertEqual(chore.assignee, "Alex")
        self.assertEqual(chore.notes, "Use soap")
        self.assertEqual(chore.priority, "High")
        self.assertEqual(chore.tags.count(), 2)

    def test_post_empty_title_shows_error_and_does_not_save(self):
        data = {
            "title": "",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertEqual(Chore.objects.count(), 0)

    def test_post_whitespace_title_shows_error_and_does_not_save(self):
        data = {
            "title": "   ",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertEqual(Chore.objects.count(), 0)

    def test_post_empty_due_date_shows_error_and_does_not_save(self):
        data = {
            "title": "Wash dishes",
            "due_date": "",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertEqual(Chore.objects.count(), 0)

    def test_post_assignee_optional(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.assignee, "")

    def test_post_assignee_from_predefined_partners(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "Jordan",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.assignee, "Jordan")

    def test_post_priority_optional(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.priority, "")

    def test_post_priority_choices(self):
        for priority in ["Low", "Medium", "High"]:
            data = {
                "title": f"Chore {priority}",
                "due_date": "2025-01-15",
                "assignee": "",
                "notes": "",
                "priority": priority,
                "tags_text": "",
            }
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 302)
            chore = Chore.objects.get(title=f"Chore {priority}")
            self.assertEqual(chore.priority, priority)

    def test_post_tags_accept_multiple_free_form(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "tags_text": "Kitchen, Cleaning, Urgent",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        tag_names = list(chore.tags.values_list("name", flat=True))
        self.assertIn("Kitchen", tag_names)
        self.assertIn("Cleaning", tag_names)
        self.assertIn("Urgent", tag_names)

    def test_post_notes_optional_free_text(self):
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "Use the new sponge",
            "priority": "",
            "tags_text": "",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.notes, "Use the new sponge")

    def test_form_layout_mobile_friendly(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "viewport")
        self.assertContains(response, "width=device-width")
        self.assertContains(response, "form-input")
        self.assertContains(response, "btn-primary")

    def test_form_has_labels_for_all_fields(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Title")
        self.assertContains(response, "Due Date")
        self.assertContains(response, "Assignee")
        self.assertContains(response, "Priority")
        self.assertContains(response, "Tags")
        self.assertContains(response, "Notes")

    def test_form_works_without_javascript(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")
        self.assertContains(response, "method=\"post\"")
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertNotContains(response, "onclick")
        self.assertNotContains(response, "onsubmit")

    def test_all_fields_save_correctly(self):
        data = {
            "title": "Clean bathroom",
            "due_date": "2025-03-20",
            "assignee": "Alex",
            "notes": "Scrub the tub",
            "priority": "Medium",
            "tags_text": "Bathroom, Deep Clean",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.title, "Clean bathroom")
        self.assertEqual(str(chore.due_date), "2025-03-20")
        self.assertEqual(chore.assignee, "Alex")
        self.assertEqual(chore.notes, "Scrub the tub")
        self.assertEqual(chore.priority, "Medium")
        self.assertEqual(chore.tags.count(), 2)
        tag_names = list(chore.tags.values_list("name", flat=True))
        self.assertIn("Bathroom", tag_names)
        self.assertIn("Deep Clean", tag_names)


class TaskListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("task_list")

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_only_incomplete_chores_appear(self):
        Chore.objects.create(title="Active", due_date="2025-01-15", completed=False)
        Chore.objects.create(title="Done", due_date="2025-01-16", completed=True)
        response = self.client.get(self.url)
        self.assertContains(response, "Active")
        self.assertNotContains(response, "Done")

    def test_chores_ordered_by_due_date_ascending(self):
        Chore.objects.create(title="Later", due_date="2025-02-15")
        Chore.objects.create(title="Earlier", due_date="2025-01-15")
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertLess(content.index("Earlier"), content.index("Later"))

    def test_empty_list_shows_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No chores yet")

    def test_row_displays_title_due_date_assignee_priority(self):
        Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            assignee="Alex",
            priority="High",
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Wash dishes")
        self.assertContains(response, "Alex")
        self.assertContains(response, "High")

    def test_chores_with_same_due_date_ordered_by_created_at(self):
        """When two chores share a due date, oldest created_at comes first."""
        from django.utils import timezone
        import datetime
        base = timezone.now()
        Chore.objects.create(title="First", due_date="2025-01-15", created_at=base)
        Chore.objects.create(title="Second", due_date="2025-01-15", created_at=base + datetime.timedelta(seconds=1))
        Chore.objects.create(title="Third", due_date="2025-01-15", created_at=base + datetime.timedelta(seconds=2))
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertLess(content.index("First"), content.index("Second"))
        self.assertLess(content.index("Second"), content.index("Third"))

    def test_empty_assignee_shows_placeholder(self):
        Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            assignee="",
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Unassigned")

    def test_empty_priority_shows_placeholder(self):
        Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            priority="",
        )
        response = self.client.get(self.url)
        self.assertContains(response, "—")

    def test_chore_row_links_to_detail_view(self):
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
        )
        response = self.client.get(self.url)
        self.assertContains(response, f'href="/{chore.pk}/"')

    def test_empty_state_shows_message_and_create_link(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No chores yet — add your first one")
        self.assertContains(response, reverse("create_chore"))

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "chores/task_list.html")

    def test_view_is_responsive_viewport_present(self):
        response = self.client.get(self.url)
        self.assertContains(response, "viewport")
        self.assertContains(response, "width=device-width")
