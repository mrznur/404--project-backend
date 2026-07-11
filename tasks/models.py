"""
Task model for Kanban board functionality.
Each task belongs to a user and has date + status + metadata.
"""
from django.db import models
from django.contrib.auth.models import User


class Task(models.Model):
    """
    Represents a task in the Kanban board.
    """
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateField()
    tags = models.CharField(max_length=255, blank=True, default='', help_text='Comma-separated tags')
    order = models.IntegerField(default=0, help_text='Order within the column')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', 'order', 'created_at']
        indexes = [
            models.Index(fields=['user', 'due_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.status} ({self.due_date})"
