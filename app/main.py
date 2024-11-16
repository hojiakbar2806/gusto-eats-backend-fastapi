import logging
import os

from aiogram import types
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app import routers
from app.bot import set_update, bot, set_command
from app.core.config import settings
from app.crud import get_all_products
from app.database.base import get_async_session, create_tables
from app.utils.helper import serialize_product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")
templates = Jinja2Templates(directory="app/template")

app.include_router(routers.auth_router)
app.include_router(routers.user_router)
app.include_router(routers.product_router)
app.include_router(routers.order_router)
app.include_router(routers.review_router)
app.include_router(routers.category_router)

# Webhook URL
WEBHOOK_PATH = f"/bot/{settings.BOT_TOKEN}"
WEBHOOK_URL = settings.WEBHOOK_URL + WEBHOOK_PATH


@app.on_event("startup")
async def on_startup():
    try:
        # Set up webhook
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != WEBHOOK_URL:
            await bot.set_webhook(url=WEBHOOK_URL)
            await set_command()
            logger.info("Webhook set successfully.")

        # Create database schema
        await create_tables()
    except Exception as e:
        logger.error(f"Failed to set up webhook or create database schema: {e}")


@app.post(WEBHOOK_PATH, tags=["Bot update"])
async def bot_webhook(update: dict):
    try:
        telegram_update = types.Update(**update)
        await set_update(bot, telegram_update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")


@app.get("/media/{filename}", tags=["Get files"])
async def get_file(filename: str):
    media_dir = "app/media"
    file_path = os.path.join(media_dir, filename)

    # Ensure security
    if not os.path.commonpath([file_path, media_dir]) == media_dir:
        logger.warning(f"Unauthorized access attempt: {file_path}")
        raise HTTPException(status_code=403, detail="Forbidden")

    # Check file existence
    if not os.path.isfile(file_path):
        logger.warning(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    # Serve the file
    try:
        return FileResponse(file_path)
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_async_session)):
    try:
        products = await get_all_products(db)
        serialized_products = [serialize_product(product) for product in products]
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "products": serialized_products, "settings": settings})
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")