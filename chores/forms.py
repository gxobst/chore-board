from django import forms
from .models import Chore, Tag

PARTNER_CHOICES = [
    ("", "---"),
    ("Alex", "Alex"),
    ("Jordan", "Jordan"),
]

PRIORITY_CHOICES = [
    ("", "---"),
    ("Low", "Low"),
    ("Medium", "Medium"),
    ("High", "High"),
]


class ChoreForm(forms.ModelForm):
    tags_text = forms.CharField(
        required=False,
        label="Tags",
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(
            attrs={"placeholder": "e.g., Kitchen, Cleaning", "class": "form-input"}
        ),
    )

    class Meta:
        model = Chore
        fields = ["title", "due_date", "assignee", "notes", "priority"]
        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date", "class": "form-input"}
            ),
            "notes": forms.Textarea(
                attrs={"rows": 3, "class": "form-input"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].widget.attrs["class"] = "form-input"
        self.fields["assignee"].widget = forms.Select(
            choices=PARTNER_CHOICES, attrs={"class": "form-input"}
        )
        self.fields["priority"].widget = forms.Select(
            choices=PRIORITY_CHOICES, attrs={"class": "form-input"}
        )
        if self.instance.pk:
            self.fields["tags_text"].initial = ", ".join(
                tag.name for tag in self.instance.tags.all()
            )

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title

    def clean_tags_text(self):
        tags_text = self.cleaned_data.get("tags_text", "")
        if not tags_text:
            return []
        return [t.strip() for t in tags_text.split(",") if t.strip()]

    def save(self, commit=True):
        chore = super().save(commit=commit)
        if commit:
            self._save_tags(chore)
        return chore

    def _save_tags(self, chore):
        tag_names = self.cleaned_data.get("tags_text", [])
        tags = []
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        chore.tags.set(tags)
