from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.views.decorators.http import require_POST
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
