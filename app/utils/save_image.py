import os
import shutil

from fastapi import HTTPException, UploadFile

from app.core.config import settings


async def save_image(image: UploadFile, name: str, dir: str) -> str:
    try:
        safe_name = name.strip().replace(" ", "_")
        _, file_ext = os.path.splitext(image.filename)
        file_ext = file_ext.replace(" ", "_")
        file_location = os.path.join(dir, f"{safe_name}{file_ext}")

        os.makedirs(dir, exist_ok=True)

        # Save the file
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)

        return file_location
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving image: {str(e)}"
        )


def is_valid_image(image: UploadFile) -> bool:
    content = image.file.read()
    image.file.seek(0, 0)
    if len(content) > settings.MAX_FILE_SIZE:
        return False

    if image.content_type not in settings.ALLOWED_IMAGE_TYPE:
        return False

    return True
