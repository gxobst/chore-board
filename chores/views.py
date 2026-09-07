from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_POST
from .forms import ChoreForm
from .models import Chore
import calendar
from datetime import date, timedelta


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
            form.save()
            return redirect("task_list")
        return render(request, "chores/chore_form.html", {"form": form})


class TaskListView(View):
    def get(self, request):
        chores = Chore.objects.filter(completed=False).order_by("due_date", "created_at")
        today = timezone.localdate()
        return render(request, "chores/task_list.html", {"chores": chores, "today": today})


class TaskDetailView(View):
    def get(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        return render(request, "chores/task_detail.html", {"chore": chore})


class TaskEditView(View):
    def get(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        form = ChoreForm(instance=chore)
        return render(request, "chores/chore_form.html", {"form": form, "chore": chore, "is_edit": True})

    def post(self, request, pk):
        chore = get_object_or_404(Chore, pk=pk)
        form = ChoreForm(request.POST, instance=chore)
        if form.is_valid():
            form.save()
            return redirect("task_detail", pk=chore.pk)
        return render(request, "chores/chore_form.html", {"form": form, "chore": chore, "is_edit": True})


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
        chore.mark_complete()
        chore.save()
        return redirect("task_list")


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
