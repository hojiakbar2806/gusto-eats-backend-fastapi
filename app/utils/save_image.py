from fastapi import UploadFile, HTTPException
import os
import shutil


def save_image(image: UploadFile, name: str, dir: str):
    try:
        file_name, file_ext = os.path.splitext(image.filename)
        print(file_ext)
        file_location = f"{dir}/{name}{file_ext}"
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)
        return file_location
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error saving image: {str(e)}")
