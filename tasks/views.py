"""
Views for the tasks app.
CRUD endpoints for Kanban task management, filtered by date.
"""
from django.utils.dateparse import parse_date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer, TaskCreateUpdateSerializer, TaskStatusUpdateSerializer


class TaskListCreateView(APIView):
    """
    GET  /api/tasks/?date=YYYY-MM-DD  - List tasks for a specific date
    POST /api/tasks/                  - Create a new task
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        if not date_str:
            return Response(
                {'error': 'date query parameter is required (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        parsed_date = parse_date(date_str)
        if not parsed_date:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tasks = Task.objects.filter(user=request.user, due_date=parsed_date).order_by('status', 'order', 'created_at')
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskCreateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task = serializer.save(user=request.user)
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    """
    GET    /api/tasks/<id>/  - Retrieve a single task
    PUT    /api/tasks/<id>/  - Update a task
    DELETE /api/tasks/<id>/  - Delete a task
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id, user):
        try:
            return Task.objects.get(id=task_id, user=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskSerializer(task).data)

    def put(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskCreateUpdateSerializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task = serializer.save()
        return Response(TaskSerializer(task).data)

    def delete(self, request, task_id):
        task = self.get_object(task_id, request.user)
        if not task:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response({'message': 'Task deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class TaskStatusUpdateView(APIView):
    """
    PATCH /api/tasks/<id>/status/
    Updates task status and order (used after drag-and-drop).
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id, user=request.user)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = TaskStatusUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        task.status = serializer.validated_data['status']
        task.order = serializer.validated_data.get('order', task.order)
        task.save()

        return Response(TaskSerializer(task).data)
