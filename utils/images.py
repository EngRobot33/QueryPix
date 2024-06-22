import asyncio
import logging
import uuid
from datetime import datetime
from io import BytesIO

import aiohttp
from PIL import Image as PilImage
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile

from downloader.models import Image

logger = logging.getLogger('downloader')


async def fetch_image(session, url):
    logger.debug(f"Fetching image from URL: {url}")
    async with session.get(url) as response:
        if response.status == 200:
            return await response.read()
        logger.error(f"Failed to fetch image from URL: {url}")
        return None


async def download_images(session, search_query, max_images):
    search_url = f"https://www.google.com/search?q={search_query}&source=lnms&tbm=isch"

    logger.debug(f"Searching for images with query: {search_query}")

    async with session.get(search_url) as response:
        html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    image_tags = soup.find_all('img')

    tasks = []
    for img_tag in image_tags[:max_images + 1]:
        img_url = img_tag.get('src')
        if img_url and img_url.startswith('http'):
            tasks.append(fetch_image(session, img_url))

    images_data = await asyncio.gather(*tasks)
    logger.debug(f"Downloaded {len(images_data)} images")
    return images_data


def resize_image(image_data):
    try:
        logger.debug("Resizing image")
        image = PilImage.open(BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')

        image = image.resize((300, 300))
        output = BytesIO()
        image.save(output, format='JPEG')
        logger.debug("Image resized successfully")
        return output.getvalue()
    except Exception as e:
        logger.error(f"Error resizing image: {e}")
        return None


async def save_image_to_db(search_query, resized_image):
    image_instance = Image(search_query=search_query)
    unique_filename = f"{search_query}-{uuid.uuid4().hex}-{datetime.now().strftime('%Y-%m-%d')}.JPEG"
    await sync_to_async(image_instance.image.save)(unique_filename, ContentFile(resized_image))
    await sync_to_async(image_instance.save)()
    logger.debug(f"Image saved to database with query: {search_query}")
    return image_instance


async def handle_images(search_query, max_images):
    async with aiohttp.ClientSession() as session:
        images_data = await download_images(session, search_query, max_images)
        saved_images = []
        for image_data in images_data:
            if image_data:
                resized_image = resize_image(image_data)
                if resized_image:
                    try:
                        image_instance = await save_image_to_db(search_query, resized_image)
                        saved_images.append(image_instance)
                    except Exception as e:
                        logger.error(f"Error saving image to database: {e}")
        return saved_images


def download_and_store_images(search_query, max_images):
    logger.debug(f"Starting download and store process for query: {search_query}")
    images = asyncio.run(handle_images(search_query, max_images))
    logger.debug(f"Completed download and store process for query: {search_query}")
    return images
