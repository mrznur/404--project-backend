"""
Serializers for the annotations app.
"""
from rest_framework import serializers
from .models import UploadedImage, Annotation


class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'image', 'label', 'points', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_points(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError('Points must be an array.')
        if len(value) < 3:
            raise serializers.ValidationError('A polygon must have at least 3 points.')
        for point in value:
            if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                raise serializers.ValidationError('Each point must have x and y properties.')
            if not isinstance(point['x'], (int, float)) or not isinstance(point['y'], (int, float)):
                raise serializers.ValidationError('x and y must be numbers.')
        return value


class UploadedImageSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True, read_only=True)
    image_url   = serializers.SerializerMethodField()

    class Meta:
        model  = UploadedImage
        fields = ['id', 'filename', 'image_url', 'width', 'height', 'uploaded_at', 'annotations']
        read_only_fields = ['id', 'filename', 'uploaded_at', 'width', 'height']

    def get_image_url(self, obj):
        """
        Return the full public URL for the image.
        - With Cloudinary: obj.image.url returns a full https://res.cloudinary.com/... URL
        - With local storage: we build the absolute URI using the request context
        """
        if not obj.image:
            return None

        try:
            url = obj.image.url
            # Cloudinary URLs are already absolute (start with https://)
            if url.startswith('http'):
                return url
            # Local dev — build absolute URL from request
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return None


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UploadedImage
        fields = ['id', 'image', 'filename']
        read_only_fields = ['id', 'filename']

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('No image file provided.')
        valid_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        ext = '.' + value.name.lower().split('.')[-1]
        if ext not in valid_ext:
            raise serializers.ValidationError(f'Invalid format. Allowed: {", ".join(valid_ext)}')
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('Image cannot exceed 10MB.')
        return value

    def create(self, validated_data):
        image_file = validated_data['image']
        validated_data['filename'] = image_file.name
        instance = super().create(validated_data)

        # Get dimensions — works for local files; Cloudinary files can't be opened via .path
        try:
            from PIL import Image as PILImage
            img = PILImage.open(instance.image.path)
            instance.width, instance.height = img.size
            instance.save()
        except Exception:
            pass  # skip — dimensions are optional

        return instance
