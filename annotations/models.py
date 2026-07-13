"""
Models for image annotation feature.
"""
from django.db import models
from django.contrib.auth.models import User
import os


def image_upload_path(instance, filename):
    return f'images/{instance.user.id}/{filename}'


class UploadedImage(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to=image_upload_path)
    filename   = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    width      = models.IntegerField(null=True, blank=True)
    height     = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} (User: {self.user.username})"

    def delete(self, *args, **kwargs):
        """
        Delete the image file when the model instance is deleted.
        Works for both local storage and Cloudinary.
        - Local: removes the file from disk via os.remove
        - Cloudinary: the storage backend handles deletion automatically
          when we call image.delete(save=False)
        """
        if self.image:
            try:
                # This works for both local and Cloudinary storage backends
                self.image.delete(save=False)
            except Exception:
                # If anything fails (e.g. file already gone), continue
                pass
        super().delete(*args, **kwargs)


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
