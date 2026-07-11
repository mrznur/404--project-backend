"""
Serializers for the annotations app.
Handles image uploads and annotation data.
"""
from rest_framework import serializers
from .models import UploadedImage, Annotation


class AnnotationSerializer(serializers.ModelSerializer):
    """Serializer for polygon annotations."""

    class Meta:
        model = Annotation
        fields = ['id', 'image', 'label', 'points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_points(self, value):
        """Ensure points is a list of coordinate objects."""
        if not isinstance(value, list):
            raise serializers.ValidationError('Points must be an array.')
        if len(value) < 3:
            raise serializers.ValidationError('A polygon must have at least 3 points.')
        for point in value:
            if not isinstance(point, dict):
                raise serializers.ValidationError('Each point must be an object.')
            if 'x' not in point or 'y' not in point:
                raise serializers.ValidationError('Each point must have x and y properties.')
            if not isinstance(point['x'], (int, float)) or not isinstance(point['y'], (int, float)):
                raise serializers.ValidationError('x and y must be numbers.')
        return value


class UploadedImageSerializer(serializers.ModelSerializer):
    """Serializer for uploaded images with annotations."""
    annotations = AnnotationSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = UploadedImage
        fields = ['id', 'filename', 'image_url', 'width', 'height', 'uploaded_at', 'annotations']
        read_only_fields = ['id', 'filename', 'uploaded_at', 'width', 'height']

    def get_image_url(self, obj):
        """Return full URL for the image."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ImageUploadSerializer(serializers.ModelSerializer):
    """Serializer for uploading images."""

    class Meta:
        model = UploadedImage
        fields = ['id', 'image', 'filename']
        read_only_fields = ['id', 'filename']

    def validate_image(self, value):
        """Validate uploaded file is an image."""
        if not value:
            raise serializers.ValidationError('No image file provided.')

        # Check file extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        ext = value.name.lower().split('.')[-1]
        if f'.{ext}' not in valid_extensions:
            raise serializers.ValidationError(f'Invalid image format. Allowed: {", ".join(valid_extensions)}')

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError('Image file size cannot exceed 10MB.')

        return value

    def create(self, validated_data):
        """Create image and store filename + dimensions."""
        image_file = validated_data['image']
        validated_data['filename'] = image_file.name

        # Create the instance
        instance = super().create(validated_data)

        # Try to get image dimensions
        try:
            from PIL import Image
            img = Image.open(instance.image.path)
            instance.width, instance.height = img.size
            instance.save()
        except Exception:
            pass  # Skip if unable to read dimensions

        return instance
