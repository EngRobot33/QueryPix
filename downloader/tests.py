from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestImageDownloaderApi:

    @patch('utils.images.download_and_store_images')
    def test_valid_request(self, mock_download):
        mock_images = [
            {'image': 'image1.jpg', 'search_query': 'iran'},
            {'image': 'image2.jpg', 'search_query': 'iran'}
        ]
        mock_download.return_value = mock_images

        client = APIClient()
        url = reverse('download-images')
        data = {'search_query': 'iran', 'max_images': 2}

        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_missing_parameters(self):
        client = APIClient()
        url = reverse('download-images')
        data = {'search_query': 'iran'}

        response = client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

