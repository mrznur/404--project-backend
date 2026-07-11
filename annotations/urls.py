"""
URL patterns for the annotations app.
"""
from django.urls import path
from .views import (
    ImageListCreateView,
    ImageDetailView,
    AnnotationListCreateView,
    AnnotationDetailView,
)

urlpatterns = [
    # Image endpoints
    path('images/', ImageListCreateView.as_view(), name='image-list'),
    path('images/upload/', ImageListCreateView.as_view(), name='image-upload'),
    path('images/<int:image_id>/', ImageDetailView.as_view(), name='image-detail'),
    # Annotation endpoints per image
    path('images/<int:image_id>/annotations/', AnnotationListCreateView.as_view(), name='annotation-list-create'),
    # Individual annotation endpoints
    path('<int:annotation_id>/', AnnotationDetailView.as_view(), name='annotation-detail'),
]
