from django.test import TestCase
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
