"""
Views for the annotations app.
Handles image upload and polygon annotation CRUD.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import UploadedImage, Annotation
from .serializers import (
    UploadedImageSerializer,
    ImageUploadSerializer,
    AnnotationSerializer,
)


class ImageListCreateView(APIView):
    """
    GET  /api/annotations/images/          - List all uploaded images for user
    POST /api/annotations/images/upload/   - Upload a new image
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        images = UploadedImage.objects.filter(user=request.user)
        serializer = UploadedImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        image = serializer.save(user=request.user)
        # Return full image data including URL
        return Response(
            UploadedImageSerializer(image, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ImageDetailView(APIView):
    """
    GET    /api/annotations/images/<id>/  - Get image details with annotations
    DELETE /api/annotations/images/<id>/  - Delete image and all its annotations
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, image_id, user):
        try:
            return UploadedImage.objects.get(id=image_id, user=user)
        except UploadedImage.DoesNotExist:
            return None

    def get(self, request, image_id):
        image = self.get_object(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = UploadedImageSerializer(image, context={'request': request})
        return Response(serializer.data)

    def delete(self, request, image_id):
        image = self.get_object(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        image.delete()  # Also deletes the file via model's delete method
        return Response({'message': 'Image deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class AnnotationListCreateView(APIView):
    """
    GET  /api/annotations/images/<id>/annotations/  - List annotations for an image
    POST /api/annotations/images/<id>/annotations/  - Create a new annotation
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_image(self, image_id, user):
        try:
            return UploadedImage.objects.get(id=image_id, user=user)
        except UploadedImage.DoesNotExist:
            return None

    def get(self, request, image_id):
        image = self.get_image(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

        annotations = image.annotations.all()
        serializer = AnnotationSerializer(annotations, many=True)
        return Response(serializer.data)

    def post(self, request, image_id):
        image = self.get_image(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

        data = {**request.data, 'image': image.id}
        serializer = AnnotationSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        annotation = serializer.save()
        return Response(AnnotationSerializer(annotation).data, status=status.HTTP_201_CREATED)


class AnnotationDetailView(APIView):
    """
    GET    /api/annotations/<annotation_id>/  - Get single annotation
    PUT    /api/annotations/<annotation_id>/  - Update annotation
    DELETE /api/annotations/<annotation_id>/  - Delete annotation
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self, annotation_id, user):
        try:
            return Annotation.objects.get(id=annotation_id, image__user=user)
        except Annotation.DoesNotExist:
            return None

    def get(self, request, annotation_id):
        annotation = self.get_object(annotation_id, request.user)
        if not annotation:
            return Response({'error': 'Annotation not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AnnotationSerializer(annotation).data)

    def put(self, request, annotation_id):
        annotation = self.get_object(annotation_id, request.user)
        if not annotation:
            return Response({'error': 'Annotation not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AnnotationSerializer(annotation, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        annotation = serializer.save()
        return Response(AnnotationSerializer(annotation).data)

    def delete(self, request, annotation_id):
        annotation = self.get_object(annotation_id, request.user)
        if not annotation:
            return Response({'error': 'Annotation not found.'}, status=status.HTTP_404_NOT_FOUND)
        annotation.delete()
        return Response({'message': 'Annotation deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
