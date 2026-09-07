from django.shortcuts import render, redirect, get_object_or_404
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
        chore.completed = True
        chore.save()
        return redirect("task_list")
