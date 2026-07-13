"""
Views for the annotations app.
Images stored as Base64 in DB — no filesystem needed, works on Vercel.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import UploadedImage, Annotation
from .serializers import UploadedImageSerializer, ImageUploadSerializer, AnnotationSerializer


class ImageListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        images = UploadedImage.objects.filter(user=request.user)
        return Response(UploadedImageSerializer(images, many=True).data)

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        image = serializer.save()
        return Response(UploadedImageSerializer(image).data, status=status.HTTP_201_CREATED)


class ImageDetailView(APIView):
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
        return Response(UploadedImageSerializer(image).data)

    def delete(self, request, image_id):
        image = self.get_object(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AnnotationListCreateView(APIView):
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
        return Response(AnnotationSerializer(image.annotations.all(), many=True).data)

    def post(self, request, image_id):
        image = self.get_image(image_id, request.user)
        if not image:
            return Response({'error': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnnotationSerializer(data={**request.data, 'image': image.id})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(AnnotationSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)


class AnnotationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]

    def get_object(self, annotation_id, user):
        try:
            return Annotation.objects.get(id=annotation_id, image__user=user)
        except Annotation.DoesNotExist:
            return None

    def get(self, request, annotation_id):
        ann = self.get_object(annotation_id, request.user)
        if not ann:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(AnnotationSerializer(ann).data)

    def put(self, request, annotation_id):
        ann = self.get_object(annotation_id, request.user)
        if not ann:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AnnotationSerializer(ann, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(AnnotationSerializer(serializer.save()).data)

    def delete(self, request, annotation_id):
        ann = self.get_object(annotation_id, request.user)
        if not ann:
            return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        ann.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
