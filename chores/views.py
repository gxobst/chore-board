from django.shortcuts import render, redirect
from django.views import View
from django.utils import timezone
from .forms import ChoreForm
from .models import Chore


class CreateChoreView(View):
    def get(self, request):
        form = ChoreForm()
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


class TaskDetailPlaceholderView(View):
    """Placeholder for Task 4 (Task Detail View). Returns 404 until implemented."""
    def get(self, request, pk):
        from django.http import Http404
        raise Http404("Task detail view not yet implemented.")
