from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Chore(models.Model):
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

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return self.title
