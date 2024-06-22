from django.urls import path

from downloader.api.views import ImageDownloaderApi

urlpatterns = [
    path('download-images/', ImageDownloaderApi.as_view(), name='download-images'),
]
