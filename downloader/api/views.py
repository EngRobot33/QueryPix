import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from downloader.api.serializers import ImageSerializer
from utils.images import download_and_store_images

logger = logging.getLogger('downloader')


class ImageDownloaderApi(APIView):
    """
    API view to handle image download and storage requests.
    """

    def post(self, request):
        search_query = request.data.get('search_query')
        max_images = request.data.get('max_images')

        if not search_query or not max_images:
            return Response({"error": "Invalid request parameters"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            max_images = int(max_images)
            images = download_and_store_images(search_query, max_images)
            serializer = ImageSerializer(images, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error occurred: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
