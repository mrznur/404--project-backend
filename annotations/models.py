"""
Models for image annotation feature.
Stores uploaded images and polygon annotations.
"""
from django.db import models
from django.contrib.auth.models import User
import os


def image_upload_path(instance, filename):
    """Generate upload path: media/images/<user_id>/<filename>"""
    return f'images/{instance.user.id}/{filename}'


class UploadedImage(models.Model):
    """
    Represents an uploaded image file.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=image_upload_path)
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} (User: {self.user.username})"

    def delete(self, *args, **kwargs):
        """Delete the image file when model instance is deleted."""
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


class Annotation(models.Model):
    """
    Represents a polygon annotation on an image.
    Stores polygon points as JSON (list of x,y coordinates).
    """
    image = models.ForeignKey(UploadedImage, on_delete=models.CASCADE, related_name='annotations')
    label = models.CharField(max_length=255, blank=True, default='')
    points = models.JSONField(help_text='Array of {x, y} coordinate objects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        label_text = self.label if self.label else 'Unlabeled'
        return f"Annotation '{label_text}' on {self.image.filename}"
