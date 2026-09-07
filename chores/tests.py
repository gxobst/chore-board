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
            "recurrence": "none",
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
            "recurrence": "none",
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
            "recurrence": "none",
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
            "recurrence": "none",
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
                "recurrence": "none",
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
            "recurrence": "none",
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
            "recurrence": "none",
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
            "recurrence": "none",
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


class TaskDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            assignee="Alex",
            notes="Use soap",
            priority="High",
        )
        self.tag = Tag.objects.create(name="Kitchen")
        self.chore.tags.add(self.tag)

    def test_get_returns_200_and_displays_all_fields(self):
        url = reverse("task_detail", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wash dishes")
        self.assertContains(response, "Jan 15, 2025")
        self.assertContains(response, "Alex")
        self.assertContains(response, "Use soap")
        self.assertContains(response, "High")
        self.assertContains(response, "Kitchen")

    def test_detail_page_has_back_link(self):
        url = reverse("task_detail", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertContains(response, "Back to Task List")
        self.assertContains(response, reverse("task_list"))

    def test_detail_page_has_edit_button(self):
        url = reverse("task_detail", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertContains(response, "Edit")
        self.assertContains(response, reverse("task_edit", kwargs={"pk": self.chore.pk}))

    def test_detail_page_has_delete_button(self):
        url = reverse("task_detail", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertContains(response, "Delete")
        self.assertContains(response, reverse("task_delete", kwargs={"pk": self.chore.pk}))

    def test_detail_page_has_mark_complete_button(self):
        url = reverse("task_detail", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertContains(response, "Mark Complete")
        self.assertContains(response, reverse("task_complete", kwargs={"pk": self.chore.pk}))


class TaskCompleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            completed=False,
        )

    def test_mark_complete_sets_is_completed_true(self):
        url = reverse("task_complete", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.chore.refresh_from_db()
        self.assertTrue(self.chore.completed)

    def test_mark_complete_redirects_to_task_list(self):
        url = reverse("task_complete", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("task_list"))

    def test_completed_chore_not_in_active_list(self):
        url = reverse("task_complete", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        response = self.client.get(reverse("task_list"))
        self.assertNotContains(response, "Wash dishes")

    def test_completed_chore_appears_in_completed_view(self):
        """After marking complete, chore.completed=True so it would appear in completed view."""
        url = reverse("task_complete", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        self.chore.refresh_from_db()
        self.assertTrue(self.chore.completed)

    def test_complete_nonexistent_chore_returns_404(self):
        url = reverse("task_complete", kwargs={"pk": 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class TaskDeleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
        )

    def test_get_delete_confirmation_page(self):
        url = reverse("task_delete", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Delete Chore")
        self.assertContains(response, "Wash dishes")
        self.assertContains(response, "Are you sure")

    def test_post_delete_removes_chore(self):
        url = reverse("task_delete", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Chore.objects.count(), 0)

    def test_post_delete_redirects_to_task_list(self):
        url = reverse("task_delete", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("task_list"))

    def test_delete_nonexistent_chore_returns_404(self):
        url = reverse("task_delete", kwargs={"pk": 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)

    def test_cancel_delete_returns_to_detail(self):
        url = reverse("task_delete", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertContains(response, "Cancel")
        self.assertContains(response, reverse("task_detail", kwargs={"pk": self.chore.pk}))


class TaskEditViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chore = Chore.objects.create(
            title="Wash dishes",
            due_date="2025-01-15",
            assignee="Alex",
            notes="Use soap",
            priority="High",
        )
        self.tag = Tag.objects.create(name="Kitchen")
        self.chore.tags.add(self.tag)

    def test_get_edit_form_prefilled(self):
        url = reverse("task_edit", kwargs={"pk": self.chore.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wash dishes")
        self.assertContains(response, "Edit")

    def test_post_edit_updates_chore(self):
        url = reverse("task_edit", kwargs={"pk": self.chore.pk})
        data = {
            "title": "Clean dishes",
            "due_date": "2025-02-20",
            "assignee": "Jordan",
            "notes": "Use new soap",
            "priority": "Medium",
            "recurrence": "none",
            "tags_text": "Kitchen, Cleaning",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.title, "Clean dishes")
        self.assertEqual(str(self.chore.due_date), "2025-02-20")
        self.assertEqual(self.chore.assignee, "Jordan")
        self.assertEqual(self.chore.notes, "Use new soap")
        self.assertEqual(self.chore.priority, "Medium")

    def test_post_edit_redirects_to_detail(self):
        url = reverse("task_edit", kwargs={"pk": self.chore.pk})
        data = {
            "title": "Clean dishes",
            "due_date": "2025-02-20",
            "assignee": "Jordan",
            "notes": "Use new soap",
            "priority": "Medium",
            "recurrence": "none",
            "tags_text": "Kitchen, Cleaning",
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse("task_detail", kwargs={"pk": self.chore.pk}))

    def test_edit_nonexistent_chore_returns_404(self):
        url = reverse("task_edit", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_edit_with_invalid_data_shows_errors(self):
        url = reverse("task_edit", kwargs={"pk": self.chore.pk})
        data = {
            "title": "",
            "due_date": "2025-02-20",
            "assignee": "",
            "notes": "",
            "priority": "",
            "recurrence": "none",
            "tags_text": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")

    def test_edit_preserves_tags(self):
        url = reverse("task_edit", kwargs={"pk": self.chore.pk})
        data = {
            "title": "Wash dishes",
            "due_date": "2025-01-15",
            "assignee": "Alex",
            "notes": "Use soap",
            "priority": "High",
            "recurrence": "none",
            "tags_text": "Kitchen, Cleaning",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.chore.refresh_from_db()
        tag_names = list(self.chore.tags.values_list("name", flat=True))
        self.assertIn("Kitchen", tag_names)
        self.assertIn("Cleaning", tag_names)


class TaskDetailNotFoundTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_nonexistent_chore_returns_404(self):
        url = reverse("task_detail", kwargs={"pk": 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class CompletedViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("completed")

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_completed_view_shows_only_completed_chores(self):
        Chore.objects.create(title="Active", due_date="2025-01-15", completed=False)
        Chore.objects.create(title="Done", due_date="2025-01-16", completed=True)
        response = self.client.get(self.url)
        self.assertContains(response, "Done")
        self.assertNotContains(response, "Active")

    def test_completed_chores_ordered_most_recently_completed_first(self):
        import datetime
        from django.utils import timezone

        base = timezone.now()
        Chore.objects.create(
            title="Older",
            due_date="2025-01-15",
            completed=True,
            completed_at=base - datetime.timedelta(hours=2),
        )
        Chore.objects.create(
            title="Newer",
            due_date="2025-01-16",
            completed=True,
            completed_at=base,
        )
        response = self.client.get(self.url)
        content = response.content.decode()
        self.assertLess(content.index("Newer"), content.index("Older"))

    def test_completed_row_displays_title_and_completion_date(self):
        Chore.objects.create(
            title="Done Chore",
            due_date="2025-01-15",
            completed=True,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Done Chore")
        self.assertContains(response, "Completed:")

    def test_empty_completed_list_shows_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "No completed chores yet")

    def test_completed_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "chores/completed.html")

    def test_completed_view_accessible_from_navigation(self):
        response = self.client.get(reverse("task_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/completed/"')

    def test_completed_chores_not_in_task_list(self):
        Chore.objects.create(
            title="Done Chore",
            due_date="2025-01-15",
            completed=True,
        )
        response = self.client.get(reverse("task_list"))
        self.assertNotContains(response, "Done Chore")

    def test_completed_view_has_restore_buttons(self):
        Chore.objects.create(
            title="Done Chore",
            due_date="2025-01-15",
            completed=True,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Restore")


class RestoreChoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.chore = Chore.objects.create(
            title="Done Chore",
            due_date="2025-01-15",
            assignee="Alex",
            notes="Use soap",
            priority="High",
            completed=True,
        )
        self.tag = Tag.objects.create(name="Kitchen")
        self.chore.tags.add(self.tag)

    def test_restore_sets_completed_false(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.chore.refresh_from_db()
        self.assertFalse(self.chore.completed)

    def test_restore_redirects_to_completed_view(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("completed"))

    def test_restore_preserves_all_fields(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        self.chore.refresh_from_db()
        self.assertEqual(self.chore.title, "Done Chore")
        self.assertEqual(str(self.chore.due_date), "2025-01-15")
        self.assertEqual(self.chore.assignee, "Alex")
        self.assertEqual(self.chore.notes, "Use soap")
        self.assertEqual(self.chore.priority, "High")
        self.assertIn(self.tag, self.chore.tags.all())

    def test_restore_chore_reappears_in_active_list(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        response = self.client.get(reverse("task_list"))
        self.assertContains(response, "Done Chore")

    def test_restore_removes_from_completed_view(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        response = self.client.get(reverse("completed"))
        self.assertNotContains(response, "Done Chore")

    def test_restore_clears_completed_at(self):
        url = reverse("restore_chore", kwargs={"pk": self.chore.pk})
        self.client.post(url)
        self.chore.refresh_from_db()
        self.assertIsNone(self.chore.completed_at)

    def test_restore_nonexistent_chore_returns_404(self):
        url = reverse("restore_chore", kwargs={"pk": 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)


class BulkRestoreViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("bulk_restore")

    def test_bulk_restores_multiple_chores(self):
        chore1 = Chore.objects.create(title="Done 1", due_date="2025-01-15", completed=True)
        chore2 = Chore.objects.create(title="Done 2", due_date="2025-01-16", completed=True)
        Chore.objects.create(title="Active", due_date="2025-01-17", completed=False)

        response = self.client.post(self.url, {"chore_ids": [chore1.pk, chore2.pk]})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("completed"))

        chore1.refresh_from_db()
        chore2.refresh_from_db()
        self.assertFalse(chore1.completed)
        self.assertFalse(chore2.completed)

    def test_bulk_restore_chores_disappear_from_completed_view(self):
        chore1 = Chore.objects.create(title="Done 1", due_date="2025-01-15", completed=True)
        chore2 = Chore.objects.create(title="Done 2", due_date="2025-01-16", completed=True)

        self.client.post(self.url, {"chore_ids": [chore1.pk, chore2.pk]})
        response = self.client.get(reverse("completed"))
        self.assertNotContains(response, "Done 1")
        self.assertNotContains(response, "Done 2")

    def test_bulk_restore_chores_reappear_in_active_list(self):
        chore1 = Chore.objects.create(title="Done 1", due_date="2025-01-15", completed=True)
        chore2 = Chore.objects.create(title="Done 2", due_date="2025-01-16", completed=True)

        self.client.post(self.url, {"chore_ids": [chore1.pk, chore2.pk]})
        response = self.client.get(reverse("task_list"))
        self.assertContains(response, "Done 1")
        self.assertContains(response, "Done 2")

    def test_bulk_restore_with_empty_selection(self):
        response = self.client.post(self.url, {"chore_ids": []})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("completed"))

    def test_bulk_restore_clears_completed_at(self):
        chore = Chore.objects.create(title="Done", due_date="2025-01-15", completed=True)
        self.client.post(self.url, {"chore_ids": [chore.pk]})
        chore.refresh_from_db()
        self.assertIsNone(chore.completed_at)

    def test_bulk_restore_preserves_unselected_completed(self):
        selected = Chore.objects.create(title="Selected", due_date="2025-01-15", completed=True)
        other = Chore.objects.create(title="Other", due_date="2025-01-16", completed=True)
        self.client.post(self.url, {"chore_ids": [selected.pk]})
        other.refresh_from_db()
        self.assertTrue(other.completed)


class CalendarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("calendar")

    def test_get_returns_200_and_displays_current_month(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        import calendar as cal
        from django.utils import timezone
        today = timezone.localdate()
        month_name = cal.month_name[today.month]
        self.assertContains(response, month_name)
        self.assertContains(response, str(today.year))

    def test_calendar_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "chores/calendar.html")

    def test_calendar_has_month_navigation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Prev")
        self.assertContains(response, "Next")

    def test_calendar_has_today_button(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Today")

    def test_calendar_shows_day_headers(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            self.assertContains(response, day)

    def test_dates_with_chores_are_highlighted(self):
        from django.utils import timezone
        today = timezone.localdate()
        # Create an active chore for today
        Chore.objects.create(title="Active Chore", due_date=today, completed=False)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Check that the chore indicator class or element is present
        self.assertContains(response, "has-chore")

    def test_completed_chores_not_highlighted(self):
        from django.utils import timezone
        today = timezone.localdate()
        # Create a completed chore for today
        Chore.objects.create(title="Done Chore", due_date=today, completed=True)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Should NOT have any cell with has-chore class because the chore is completed
        content = response.content.decode()
        # Check that no calendar-cell has 'has-chore' class (ignore CSS definitions)
        self.assertNotContains(response, "calendar-cell  has-chore")
        self.assertNotContains(response, "calendar-cell today has-chore")
        # Also verify no chore indicator span element is present in HTML
        self.assertNotContains(response, 'chore-indicator"></span>')

    def test_clicking_date_opens_create_form_with_prefilled_date(self):
        from django.utils import timezone
        today = timezone.localdate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Check that there's a link to create chore with the date pre-filled
        date_str = today.strftime("%Y-%m-%d")
        create_url = reverse("create_chore")
        self.assertContains(response, f'{create_url}?due_date={date_str}')

    def test_next_month_navigation(self):
        from django.utils import timezone
        today = timezone.localdate()
        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        response = self.client.get(f"{self.url}?year={next_year}&month={next_month}")
        self.assertEqual(response.status_code, 200)
        import calendar as cal
        next_month_name = cal.month_name[next_month]
        self.assertContains(response, next_month_name)
        self.assertContains(response, str(next_year))

    def test_prev_month_navigation(self):
        from django.utils import timezone
        today = timezone.localdate()
        prev_month = today.month - 1
        prev_year = today.year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        response = self.client.get(f"{self.url}?year={prev_year}&month={prev_month}")
        self.assertEqual(response.status_code, 200)
        import calendar as cal
        prev_month_name = cal.month_name[prev_month]
        self.assertContains(response, prev_month_name)
        self.assertContains(response, str(prev_year))

    def test_padding_days_are_dimmed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Padding cells should have the 'padding' class
        self.assertContains(response, "padding")

    def test_today_is_highlighted(self):
        from django.utils import timezone
        today = timezone.localdate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Today's cell should have 'today' class
        self.assertContains(response, "today")

    def test_calendar_responsive_viewport(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "viewport")

    def test_calendar_navigation_links_in_context(self):
        from django.utils import timezone
        today = timezone.localdate()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Check that prev/next links are in the HTML
        content = response.content.decode()
        self.assertIn("calendar", content.lower())


import uuid
from datetime import date, timedelta


class RecurringChoreModelTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_recurrence_field_default_is_none(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15")
        self.assertEqual(chore.recurrence, "none")

    def test_recurrence_field_daily(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        self.assertEqual(chore.recurrence, "daily")

    def test_recurrence_field_weekly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="weekly")
        self.assertEqual(chore.recurrence, "weekly")

    def test_recurrence_field_monthly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="monthly")
        self.assertEqual(chore.recurrence, "monthly")

    def test_is_recurring_false_for_none(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="none")
        self.assertFalse(chore.is_recurring())

    def test_is_recurring_true_for_daily(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        self.assertTrue(chore.is_recurring())

    def test_is_recurring_true_for_weekly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="weekly")
        self.assertTrue(chore.is_recurring())

    def test_is_recurring_true_for_monthly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="monthly")
        self.assertTrue(chore.is_recurring())

    def test_next_occurrence_date_daily(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        self.assertEqual(chore.next_occurrence_date(), date(2025, 1, 16))

    def test_next_occurrence_date_weekly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="weekly")
        self.assertEqual(chore.next_occurrence_date(), date(2025, 1, 22))

    def test_next_occurrence_date_monthly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="monthly")
        self.assertEqual(chore.next_occurrence_date(), date(2025, 2, 15))

    def test_next_occurrence_date_none(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="none")
        self.assertIsNone(chore.next_occurrence_date())

    def test_create_next_occurrence_daily(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        new_chore = chore.create_next_occurrence()
        self.assertIsNotNone(new_chore)
        self.assertEqual(new_chore.title, "Test")
        self.assertEqual(new_chore.due_date, date(2025, 1, 16))
        self.assertEqual(new_chore.recurrence, "daily")
        self.assertFalse(new_chore.completed)

    def test_create_next_occurrence_weekly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="weekly")
        new_chore = chore.create_next_occurrence()
        self.assertEqual(new_chore.due_date, date(2025, 1, 22))

    def test_create_next_occurrence_monthly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="monthly")
        new_chore = chore.create_next_occurrence()
        self.assertEqual(new_chore.due_date, date(2025, 2, 15))

    def test_create_next_occurrence_none_returns_none(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="none")
        result = chore.create_next_occurrence()
        self.assertIsNone(result)

    def test_create_next_occurrence_links_series(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        new_chore = chore.create_next_occurrence()
        chore.refresh_from_db()
        self.assertIsNotNone(chore.series_id)
        self.assertEqual(chore.series_id, new_chore.series_id)

    def test_create_next_occurrence_preserves_fields(self):
        tag = Tag.objects.create(name="Kitchen")
        chore = Chore.objects.create(
            title="Test", due_date="2025-01-15", recurrence="daily",
            assignee="Alex", notes="Some notes", priority="High"
        )
        chore.tags.add(tag)
        new_chore = chore.create_next_occurrence()
        self.assertEqual(new_chore.title, "Test")
        self.assertEqual(new_chore.assignee, "Alex")
        self.assertEqual(new_chore.notes, "Some notes")
        self.assertEqual(new_chore.priority, "High")
        self.assertIn(tag, new_chore.tags.all())

    def test_skip_occurrence_daily(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        result = chore.skip_occurrence()
        self.assertTrue(result)
        chore.refresh_from_db()
        self.assertEqual(chore.due_date, date(2025, 1, 16))
        self.assertFalse(chore.completed)

    def test_skip_occurrence_weekly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="weekly")
        chore.skip_occurrence()
        chore.refresh_from_db()
        self.assertEqual(chore.due_date, date(2025, 1, 22))

    def test_skip_occurrence_monthly(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="monthly")
        chore.skip_occurrence()
        chore.refresh_from_db()
        self.assertEqual(chore.due_date, date(2025, 2, 15))

    def test_skip_occurrence_none_returns_false(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="none")
        result = chore.skip_occurrence()
        self.assertFalse(result)

    def test_assign_series_id(self):
        chore = Chore.objects.create(title="Test", due_date="2025-01-15", recurrence="daily")
        self.assertIsNone(chore.series_id)
        chore.assign_series_id()
        self.assertIsNotNone(chore.series_id)


class RecurringChoreFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_form_includes_recurrence_field(self):
        response = self.client.get(reverse("create_chore"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recurrence")

    def test_create_form_has_recurrence_options(self):
        response = self.client.get(reverse("create_chore"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "None")
        self.assertContains(response, "Daily")
        self.assertContains(response, "Weekly")
        self.assertContains(response, "Monthly")

    def test_create_chore_with_recurrence_daily(self):
        data = {
            "title": "Recurring Task",
            "due_date": "2025-01-15",
            "assignee": "Alex",
            "notes": "Notes",
            "priority": "High",
            "recurrence": "daily",
            "tags_text": "",
        }
        response = self.client.post(reverse("create_chore"), data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.recurrence, "daily")

    def test_create_chore_with_recurrence_weekly(self):
        data = {
            "title": "Recurring Task",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "recurrence": "weekly",
            "tags_text": "",
        }
        response = self.client.post(reverse("create_chore"), data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.recurrence, "weekly")

    def test_create_chore_with_recurrence_monthly(self):
        data = {
            "title": "Recurring Task",
            "due_date": "2025-01-15",
            "assignee": "",
            "notes": "",
            "priority": "",
            "recurrence": "monthly",
            "tags_text": "",
        }
        response = self.client.post(reverse("create_chore"), data)
        self.assertEqual(response.status_code, 302)
        chore = Chore.objects.first()
        self.assertEqual(chore.recurrence, "monthly")

    def test_edit_form_shows_series_scope_for_recurring(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        chore.assign_series_id()
        response = self.client.get(reverse("task_edit", kwargs={"pk": chore.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Current occurrence only")
        self.assertContains(response, "Entire series")

    def test_edit_form_hides_series_scope_for_non_recurring(self):
        chore = Chore.objects.create(
            title="Non-recurring", due_date="2025-01-15", recurrence="none"
        )
        response = self.client.get(reverse("task_edit", kwargs={"pk": chore.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Current occurrence only")
        self.assertNotContains(response, "Entire series")


class RecurringChoreCompleteViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_complete_recurring_chore_shows_dialog(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        response = self.client.get(reverse("task_detail", kwargs={"pk": chore.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create the next occurrence?")

    def test_complete_recurring_chore_yes_creates_next(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        response = self.client.post(url, {"create_next": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Chore.objects.count(), 2)
        new_chore = Chore.objects.exclude(pk=chore.pk).first()
        self.assertEqual(new_chore.due_date, date(2025, 1, 16))

    def test_complete_recurring_chore_no_does_not_create_next(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        response = self.client.post(url, {"create_next": "no"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Chore.objects.count(), 1)

    def test_complete_non_recurring_chore_no_dialog(self):
        chore = Chore.objects.create(
            title="Non-recurring", due_date="2025-01-15", recurrence="none"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Chore.objects.count(), 1)

    def test_complete_recurring_weekly_creates_next_in_7_days(self):
        chore = Chore.objects.create(
            title="Weekly", due_date="2025-01-15", recurrence="weekly"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        self.client.post(url, {"create_next": "yes"})
        new_chore = Chore.objects.exclude(pk=chore.pk).first()
        self.assertEqual(new_chore.due_date, date(2025, 1, 22))

    def test_complete_recurring_monthly_creates_next_in_1_month(self):
        chore = Chore.objects.create(
            title="Monthly", due_date="2025-01-15", recurrence="monthly"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        self.client.post(url, {"create_next": "yes"})
        new_chore = Chore.objects.exclude(pk=chore.pk).first()
        self.assertEqual(new_chore.due_date, date(2025, 2, 15))

    def test_complete_recurring_chore_links_series(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("task_complete", kwargs={"pk": chore.pk})
        self.client.post(url, {"create_next": "yes"})
        new_chore = Chore.objects.exclude(pk=chore.pk).first()
        chore.refresh_from_db()
        self.assertIsNotNone(chore.series_id)
        self.assertEqual(chore.series_id, new_chore.series_id)


class SkipOccurrenceViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_skip_occurrence_advances_due_date(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("skip_occurrence", kwargs={"pk": chore.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        chore.refresh_from_db()
        self.assertEqual(chore.due_date, date(2025, 1, 16))
        self.assertFalse(chore.completed)

    def test_skip_occurrence_no_new_record(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("skip_occurrence", kwargs={"pk": chore.pk})
        self.client.post(url)
        self.assertEqual(Chore.objects.count(), 1)

    def test_skip_occurrence_redirects_to_detail(self):
        chore = Chore.objects.create(
            title="Recurring", due_date="2025-01-15", recurrence="daily"
        )
        url = reverse("skip_occurrence", kwargs={"pk": chore.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("task_detail", kwargs={"pk": chore.pk}))


class EditSeriesViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_edit_current_occurrence_only_others_unaffected(self):
        series_id = uuid.uuid4()
        chore1 = Chore.objects.create(
            title="Original", due_date="2025-01-15", recurrence="daily", series_id=series_id
        )
        chore2 = Chore.objects.create(
            title="Original", due_date="2025-01-16", recurrence="daily", series_id=series_id
        )
        url = reverse("task_edit", kwargs={"pk": chore1.pk})
        data = {
            "title": "Updated",
            "due_date": "2025-01-20",
            "assignee": "Alex",
            "notes": "",
            "priority": "",
            "recurrence": "daily",
            "series_scope": "current",
            "tags_text": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        chore1.refresh_from_db()
        chore2.refresh_from_db()
        self.assertEqual(chore1.title, "Updated")
        self.assertEqual(chore2.title, "Original")

    def test_entire_series_updates_all(self):
        series_id = uuid.uuid4()
        chore1 = Chore.objects.create(
            title="Original", due_date="2025-01-15", recurrence="daily", series_id=series_id
        )
        chore2 = Chore.objects.create(
            title="Original", due_date="2025-01-16", recurrence="daily", series_id=series_id
        )
        url = reverse("task_edit", kwargs={"pk": chore1.pk})
        data = {
            "title": "Updated",
            "due_date": "2025-01-20",
            "assignee": "Alex",
            "notes": "New notes",
            "priority": "High",
            "recurrence": "daily",
            "series_scope": "series",
            "tags_text": "",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        chore1.refresh_from_db()
        chore2.refresh_from_db()
        self.assertEqual(chore1.title, "Updated")
        self.assertEqual(chore1.assignee, "Alex")
        self.assertEqual(chore1.notes, "New notes")
        self.assertEqual(chore1.priority, "High")
        self.assertEqual(chore2.title, "Updated")
        self.assertEqual(chore2.assignee, "Alex")
        self.assertEqual(chore2.notes, "New notes")
        self.assertEqual(chore2.priority, "High")

