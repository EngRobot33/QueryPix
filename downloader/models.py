import os

from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.models import BaseModel


def image_upload_path(instance, filename):
    return os.path.join('images', instance.search_query, filename)


class Image(BaseModel):
    image = models.ImageField(upload_to=image_upload_path)
    search_query = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return f'{self.search_query} -> {self.image.name}'
