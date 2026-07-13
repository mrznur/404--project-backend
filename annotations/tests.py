from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from .models import UploadedImage
from .serializers import UploadedImageSerializer


class UploadedImageSerializerTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='demo',
            email='demo@example.com',
            password='demo1234',
        )

    def test_data_uri_images_are_returned_as_is(self):
        image = UploadedImage.objects.create(
            user=self.user,
            image_data='data:image/png;base64,AAAA',
            filename='demo.png',
            content_type='image/png',
        )

        serializer = UploadedImageSerializer(image)

        self.assertEqual(serializer.data['image_url'], 'data:image/png;base64,AAAA')

    def test_relative_image_paths_become_absolute_urls(self):
        image = UploadedImage.objects.create(
            user=self.user,
            image_data='/media/images/demo.png',
            filename='demo.png',
            content_type='image/png',
        )
        request = RequestFactory().get('/api/annotations/images/')

        serializer = UploadedImageSerializer(image, context={'request': request})

        self.assertEqual(serializer.data['image_url'], 'http://testserver/media/images/demo.png')
