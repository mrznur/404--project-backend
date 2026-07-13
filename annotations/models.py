"""
Models for image annotation feature.
Images are stored as Base64 in the database — no filesystem needed.
This makes it work on Vercel without any external storage service.
"""
from django.db import models
from django.contrib.auth.models import User


class UploadedImage(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    # Store the Base64 encoded image data directly in the DB
    image_data  = models.TextField(help_text='Base64-encoded image with data URI prefix')
    filename    = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100, default='image/jpeg')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width       = models.IntegerField(null=True, blank=True)
    height      = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} (User: {self.user.username})"


class Annotation(models.Model):
    image      = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='annotations')
    label      = models.CharField(max_length=255, blank=True, default='')
    points     = models.JSONField(help_text='Array of {x, y} coordinate objects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Annotation '{self.label or 'Unlabeled'}' on {self.image.filename}"
