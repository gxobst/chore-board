import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.db.models import Q
from .forms import ChoreForm
from .models import Chore, Tag
import calendar
from datetime import date, timedelta
from urllib.parse import quote


def get_reminder_mailto():
    """Generate a mailto link for all chores needing attention.

    Returns the mailto URL string, or None if no chores are overdue,
    due today, or due tomorrow.
    """
    today = timezone.localdate()
    tomorrow = today + timedelta(days=1)

    chores = Chore.objects.filter(completed=False).order_by("due_date")

    overdue = []
    due_today = []
    due_tomorrow = []

    for chore in chores:
        if chore.due_date < today:
            overdue.append(chore)
        elif chore.due_date == today:
            due_today.append(chore)
        elif chore.due_date == tomorrow:
            due_tomorrow.append(chore)

    if not overdue and not due_today and not due_tomorrow:
        return None

    lines = ["Chore reminders", ""]

    if overdue:
        lines.append("Overdue:")
        for chore in overdue:
            lines.append(
                f"- {chore.title} (due {chore.due_date.strftime('%b %d, %Y')})"
            )
        lines.append("")

    if due_today:
        lines.append("Due Today:")
        for chore in due_today:
            lines.append(
                f"- {chore.title} (due {chore.due_date.strftime('%b %d, %Y')})"
            )
        lines.append("")

    if due_tomorrow:
        lines.append("Due Tomorrow:")
        for chore in due_tomorrow:
            lines.append(
                f"- {chore.title} (due {chore.due_date.strftime('%b %d, %Y')})"
            )
        lines.append("")

    body = "\n".join(lines)
    subject = "Chore reminders"

    return f"mailto:?subject={quote(subject, safe='')}&body={quote(body, safe='')}"


class CreateChoreView(View):
    def get(self, request):
        initial = {}
        due_date = request.GET.get('due_date')
        if due_date:
            initial['due_date'] = due_date
        form = ChoreForm(initial=initial)
        return render(request, "chores/chore_form.html", {"form": form})

    def post(self, request):
        form = ChoreForm(request.POST)
        if form.is_valid():
            chore = form.save()
            if chore.is_recurring() and not chore.series_id:
                chore.assign_series_id()
            return redirect("task_list")
        return render(request, "chores/chore_form.html", {"form": form})


class TaskListView(View):
    def get(self, request):
        # Start with all chores; default to active only (no status filter)
        chores = Chore.objects.all()
        status = request.GET.get("status", "")
        if status == "completed":
            chores = chores.filter(completed=True)
        elif status == "active":
            chores = chores.filter(completed=False)
        else:
            # Default: show active chores only (matches existing behavior)
            chores = chores.filter(completed=False)

        # Filter by assignee
        assignee = request.GET.get("assignee", "")
        if assignee:
            chores = chores.filter(assignee=assignee)

        # Filter by priority
        priority = request.GET.get("priority", "")
        if priority:
            chores = chores.filter(priority=priority)

        # Filter by tags (multi-select, OR within tags)
        tag_ids = request.GET.getlist("tags")
        if tag_ids:
            chores = chores.filter(tags__id__in=tag_ids).distinct()

        # Search by title and notes (case-insensitive)
        search = request.GET.get("search", "")
        if search:
            chores = chores.filter(
                Q(title__icontains=search) | Q(notes__icontains=search)
            )

        # Order by due_date ascending
        chores = chores.order_by("due_date", "created_at")

        # Get filter options for dropdowns
        assignees = (
            Chore.objects.exclude(assignee="")
            .values_list("assignee", flat=True)
            .distinct()
            .order_by("assignee")
        )
        priorities = ["Low", "Medium", "High"]
        all_tags = Tag.objects.all().order_by("name")

        today = timezone.localdate()
        mailto = get_reminder_mailto()

        # Determine if any filter is active for "Clear all" display
        has_active_filters = any([assignee, priority, status, tag_ids, search])

        context = {
            "chores": chores,
            "today": today,
            "reminder_mailto": mailto,
            "assignees": assignees,
            "priorities": priorities,
            "all_tags": all_tags,
            "current_assignee": assignee,
            "current_priority": priority,
            "current_status": status,
            "current_tag_ids": [int(t) for t in tag_ids],
            "search_query": search,
            "has_active_filters": has_active_filters,
        }
        return render(request, "chores/task_list.html", context)


class TaskDetailView(View):
    def get(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        mailto = get_reminder_mailto()
        return render(request, "chores/task_detail.html", {"chore": chore, "reminder_mailto": mailto})


class TaskEditView(View):
    def get(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        form = ChoreForm(instance=chore)
        is_recurring = chore.is_recurring()
        return render(request, "chores/chore_form.html", {
            "form": form, "chore": chore, "is_edit": True,
            "is_recurring": is_recurring
        })

    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            # Check if this is a recurring chore and user chose series scope
            scope = request.POST.get("series_scope", "current")
            if scope == "series" and chore.series_id:
                # Update all chores in the series
                series_chores = Chore.objects.filter(series_id=chore.series_id)
                title = form.cleaned_data.get("title")
                assignee = form.cleaned_data.get("assignee")
                notes = form.cleaned_data.get("notes")
                priority = form.cleaned_data.get("priority")
                recurrence = form.cleaned_data.get("recurrence")
                series_chores.update(
                    title=title,
                    assignee=assignee,
                    notes=notes,
                    priority=priority,
                    recurrence=recurrence,
                )
                # Handle tags for all series chores
                tag_names = form.cleaned_data.get("tags_text", [])
                tags = []
                for name in tag_names:
                    from .models import Tag
                    tag, _ = Tag.objects.get_or_create(name=name)
                    tags.append(tag)
                for c in series_chores:
                    c.tags.set(tags)
            else:
                form.save()
            return redirect("task_detail", pk=chore.pk)
        return render(request, "chores/chore_form.html", {
            "form": form, "chore": chore, "is_edit": True,
            "is_recurring": chore.is_recurring()
        })


class TaskDeleteView(View):
    def get(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        return render(request, "chores/task_confirm_delete.html", {"chore": chore})

    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        chore.delete()
        return redirect("task_list")


class TaskCompleteView(View):
    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        create_next = request.POST.get("create_next")
        
        chore.mark_complete()
        chore.save()
        
        if chore.is_recurring() and create_next == "yes":
            if not chore.series_id:
                chore.assign_series_id()
                chore.save()
            chore.create_next_occurrence()
        
        return redirect("task_list")


class SkipOccurrenceView(View):
    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        chore.skip_occurrence()
        return redirect("task_detail", pk=chore.pk)


class CompletedView(View):
    def get(self, request):
        chores = Chore.objects.filter(completed=True).order_by("-completed_at")
        return render(request, "chores/completed.html", {"chores": chores})


class RestoreChoreView(View):
    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        chore.restore()
        chore.save()
        return redirect("completed")


class BulkRestoreView(View):
    def post(self, request):
        chore_ids = request.POST.getlist("chore_ids")
        if chore_ids:
            Chore.objects.filter(pk__in=chore_ids, completed=True).update(
                completed=False, completed_at=None
            )
        return redirect("completed")


class CalendarView(View):
    def get(self, request):
        today = timezone.localdate()
        
        # Get year and month from query params, default to current month
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        try:
            year = int(year) if year else today.year
            month = int(month) if month else today.month
        except (ValueError, TypeError):
            year = today.year
            month = today.month
        
        # Validate month/year bounds
        if month < 1 or month > 12:
            month = today.month
            year = today.year
        
        # Calculate previous and next month
        prev_month = month - 1
        prev_year = year
        if prev_month < 1:
            prev_month = 12
            prev_year -= 1
        
        next_month = month + 1
        next_year = year
        if next_month > 12:
            next_month = 1
            next_year += 1
        
        # Get the calendar for the month
        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        month_days = cal.monthdayscalendar(year, month)
        
        # Get all active (non-completed) chores for this month
        from datetime import date
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        active_chores = Chore.objects.filter(
            completed=False,
            due_date__gte=first_day,
            due_date__lte=last_day
        )
        
        # Build a set of days with chores
        chore_days = set(active_chores.values_list('due_date', flat=True))
        
        # Build calendar grid with extra info
        grid = []
        for week in month_days:
            week_data = []
            for day in week:
                if day == 0:
                    week_data.append({'day': 0, 'date': None, 'has_chore': False, 'is_today': False, 'is_padding': True})
                else:
                    current_date = date(year, month, day)
                    week_data.append({
                        'day': day,
                        'date': current_date,
                        'has_chore': current_date in chore_days,
                        'is_today': current_date == today,
                        'is_padding': False,
                    })
            grid.append(week_data)
        
        # Month name
        month_name = calendar.month_name[month]
        
        context = {
            'grid': grid,
            'year': year,
            'month': month,
            'month_name': month_name,
            'prev_year': prev_year,
            'prev_month': prev_month,
            'next_year': next_year,
            'next_month': next_month,
            'today': today,
        }
        return render(request, "chores/calendar.html", context)


class SettingsView(View):
    def get(self, request):
        return render(request, "chores/settings.html")


class ExportDataView(View):
    def get(self, request):
        chores = Chore.objects.all().order_by("due_date", "created_at")
        data = []
        for chore in chores:
            data.append({
                "title": chore.title,
                "due_date": chore.due_date.isoformat(),
                "assignee": chore.assignee,
                "notes": chore.notes,
                "priority": chore.priority,
                "tags": [tag.name for tag in chore.tags.all()],
                "completed": chore.completed,
                "completed_at": chore.completed_at.isoformat() if chore.completed_at else None,
                "created_at": chore.created_at.isoformat() if chore.created_at else None,
                "recurrence": chore.recurrence,
                "series_id": str(chore.series_id) if chore.series_id else None,
            })
        
        export_data = {"chores": data}
        json_str = json.dumps(export_data, indent=2)
        
        today = timezone.localdate()
        filename = f"chores-backup-{today.isoformat()}.json"
        
        response = HttpResponse(json_str, content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class ImportDataView(View):
    def post(self, request):
        if "file" not in request.FILES:
            return render(request, "chores/settings.html", {
                "import_error": "No file selected."
            })
        
        uploaded_file = request.FILES["file"]
        
        if uploaded_file.size == 0:
            return render(request, "chores/settings.html", {
                "import_error": "The uploaded file is empty."
            })
        
        try:
            content = uploaded_file.read().decode("utf-8")
            data = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return render(request, "chores/settings.html", {
                "import_error": "Invalid JSON file. Please upload a valid JSON file."
            })
        
        if not isinstance(data, dict) or "chores" not in data:
            return render(request, "chores/settings.html", {
                "import_error": "Invalid file format. Expected a JSON file with a 'chores' array."
            })
        
        chores_data = data["chores"]
        if not isinstance(chores_data, list):
            return render(request, "chores/settings.html", {
                "import_error": "Invalid file format. 'chores' must be an array."
            })
        
        imported_count = 0
        for chore_data in chores_data:
            if not isinstance(chore_data, dict):
                continue
            
            title = chore_data.get("title", "").strip()
            if not title:
                continue
            
            due_date_str = chore_data.get("due_date", "")
            try:
                due_date = date.fromisoformat(due_date_str)
            except (ValueError, TypeError):
                due_date = timezone.localdate()
            
            assignee = chore_data.get("assignee", "")
            notes = chore_data.get("notes", "")
            priority = chore_data.get("priority", "")
            recurrence = chore_data.get("recurrence", "none")
            completed = chore_data.get("completed", False)
            tag_names = chore_data.get("tags", [])
            
            chore = Chore.objects.create(
                title=title,
                due_date=due_date,
                assignee=assignee,
                notes=notes,
                priority=priority,
                recurrence=recurrence,
                completed=completed,
            )
            
            if tag_names and isinstance(tag_names, list):
                tags = []
                for name in tag_names:
                    tag, _ = Tag.objects.get_or_create(name=name)
                    tags.append(tag)
                chore.tags.set(tags)
            
            imported_count += 1
        
        return render(request, "chores/settings.html", {
            "import_success": f"Successfully imported {imported_count} chore{'s' if imported_count != 1 else ''}."
        })


class ClearDataView(View):
    def get(self, request):
        return render(request, "chores/confirm_clear.html")
    
    def post(self, request):
        Chore.objects.all().delete()
        return render(request, "chores/settings.html", {
            "clear_success": "All data has been removed."
        })
