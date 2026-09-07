from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListView.as_view(), name="task_list"),
    path("create/", views.CreateChoreView.as_view(), name="create_chore"),
]
