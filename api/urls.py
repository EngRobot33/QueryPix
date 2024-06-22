from django.urls import path, include

urlpatterns = [
    path('downloader/', include('downloader.api.urls')),
]
