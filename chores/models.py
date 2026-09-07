import uuid
from django.db import models
from django.utils import timezone
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chore(models.Model):
    RECURRENCE_CHOICES = [
        ("none", "None"),
        ("daily", "Daily"),
        ("weekly", "Weekly"),
        ("monthly", "Monthly"),
    ]

    PRIORITY_CHOICES = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    title = models.CharField(max_length=200)
    due_date = models.DateField()
    assignee = models.CharField(max_length=100, blank=True, default="")
    notes = models.TextField(blank=True, default="")
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, blank=True, default=""
    )
    tags = models.ManyToManyField(Tag, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    recurrence = models.CharField(
        max_length=10, choices=RECURRENCE_CHOICES, default="none"
    )
    series_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["due_date", "created_at"]

    def __str__(self):
        return self.title

    def mark_complete(self):
        self.completed = True
        self.completed_at = timezone.now()

    def restore(self):
        self.completed = False
        self.completed_at = None

    def is_recurring(self):
        return self.recurrence != "none"

    def next_occurrence_date(self):
        """Calculate the next due date based on recurrence."""
        if not self.is_recurring():
            return None
        due = self.due_date
        if isinstance(due, str):
            due = date.fromisoformat(due)
        if self.recurrence == "daily":
            return due + timedelta(days=1)
        elif self.recurrence == "weekly":
            return due + timedelta(days=7)
        elif self.recurrence == "monthly":
            return due + relativedelta(months=1)
        return None

    def create_next_occurrence(self):
        """Create a new chore occurrence for recurring chores."""
        if not self.is_recurring():
            return None
        next_date = self.next_occurrence_date()
        if not next_date:
            return None

        new_chore = Chore.objects.create(
            title=self.title,
            due_date=next_date,
            assignee=self.assignee,
            notes=self.notes,
            priority=self.priority,
            recurrence=self.recurrence,
            series_id=self.series_id or uuid.uuid4(),
        )
        if self.series_id is None:
            self.series_id = new_chore.series_id
            self.save(update_fields=["series_id"])
        new_chore.tags.set(self.tags.all())
        return new_chore

    def skip_occurrence(self):
        """Advance due_date by one recurrence interval without completing."""
        if not self.is_recurring():
            return False
        next_date = self.next_occurrence_date()
        if next_date:
            self.due_date = next_date
            self.save(update_fields=["due_date"])
            return True
        return False

    def assign_series_id(self):
        """Assign a series_id if not already set."""
        if not self.series_id:
            self.series_id = uuid.uuid4()
            self.save(update_fields=["series_id"])
