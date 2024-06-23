from fastapi import UploadFile
from app.settings import settings


def is_valid_image(image: UploadFile) -> bool:
    content = image.file.read()
    image.file.seek(0, 0)
    if len(content) > settings.MAX_FILE_SIZE:
        return False

    if image.content_type not in settings.ALLOWED_IMAGE_TYPE:
        return False

    return True
