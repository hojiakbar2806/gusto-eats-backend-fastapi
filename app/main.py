import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from app.database import Base, engine
from app.routers import user_router, auth_router, product_router, category_router, review_router, order_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(review_router)
app.include_router(category_router)


@app.get("/{main_dir}/{img_dir}/{filename}", tags=["Get files"])
async def get_file(main_dir: str = "product", img_dir: str = "", filename: str = ""):
    file_path = os.path.join(main_dir, img_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
