"""
Serializers for the annotations app.
Images stored as Base64 in DB — works on Vercel without external storage.
"""
import base64
from rest_framework import serializers
from .models import UploadedImage, Annotation


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Annotation
        fields = ['id', 'image', 'label', 'points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_points(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Points must be an array.')
        if len(value) < 3:
            raise serializers.ValidationError('A polygon must have at least 3 points.')
        for point in value:
            if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                raise serializers.ValidationError('Each point must have x and y.')
            if not isinstance(point['x'], (int, float)) or not isinstance(point['y'], (int, float)):
                raise serializers.ValidationError('x and y must be numbers.')
        return value


class UploadedImageSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model  = UploadedImage
        fields = ['id', 'filename', 'image_url', 'width', 'height', 'uploaded_at', 'annotations']
        read_only_fields = ['id', 'filename', 'uploaded_at', 'width', 'height']

    def get_image_url(self, obj):
        if not obj.image_data:
            return ''

        if obj.image_data.startswith(('data:', 'http://', 'https://')):
            return obj.image_data

        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.image_data)

        return obj.image_data


class ImageUploadSerializer(serializers.Serializer):
    """Accept a file upload and convert to Base64."""
    image = serializers.ImageField()

    def validate_image(self, value):
        valid_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        ext = '.' + value.name.lower().split('.')[-1]
        if ext not in valid_ext:
            raise serializers.ValidationError(f'Invalid format. Allowed: {", ".join(valid_ext)}')
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Image cannot exceed 10MB.')
        return value

    def create(self, validated_data):
        image_file   = validated_data['image']
        content_type = image_file.content_type or 'image/jpeg'

        # Read and encode to Base64
        raw   = image_file.read()
        b64   = base64.b64encode(raw).decode('utf-8')
        # Store as a full data URI so <img src="..."> works directly in browser
        data_uri = f'data:{content_type};base64,{b64}'

        # Try to get image dimensions
        width, height = None, None
        try:
            from PIL import Image as PILImage
            import io
            img = PILImage.open(io.BytesIO(raw))
            width, height = img.size
        except Exception:
            pass

        user = self.context['request'].user
        instance = UploadedImage.objects.create(
            user         = user,
            image_data   = data_uri,
            filename     = image_file.name,
            content_type = content_type,
            width        = width,
            height       = height,
        )
        return instance
