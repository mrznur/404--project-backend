"""
URL patterns for the tasks app.
"""
from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskStatusUpdateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:task_id>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_id>/status/', TaskStatusUpdateView.as_view(), name='task-status-update'),
]
