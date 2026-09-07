from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("create/", views.CreateChoreView.as_view(), name="create_chore"),
    path("<int:pk>/", views.TaskDetailView.as_view(), name="task_detail"),
    path("<int:pk>/edit/", views.TaskEditView.as_view(), name="task_edit"),
    path("<int:pk>/delete/", views.TaskDeleteView.as_view(), name="task_delete"),
    path("<int:pk>/complete/", views.TaskCompleteView.as_view(), name="task_complete"),
    path("completed/", views.CompletedView.as_view(), name="completed"),
    path("<int:pk>/restore/", views.RestoreChoreView.as_view(), name="restore_chore"),
    path("completed/bulk-restore/", views.BulkRestoreView.as_view(), name="bulk_restore"),
]
