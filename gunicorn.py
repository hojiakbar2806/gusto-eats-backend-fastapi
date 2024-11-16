import os

# bind = "0.0.0.0:8000"  # IP va port
workers = 1           # Workerlar soni
worker_class = "uvicorn.workers.UvicornWorker"  # Uvicorn worker
timeout = 30           # Har bir worker uchun timeout
loglevel = "info"     # Log darajasi
accesslog = "-"       # Kirish logini stdout ga yo'naltirish
errorlog = "-"        # Xato logini stdout ga yo'naltirish
keepalive = 5         # Xatolarni oldini olish uchun saqlash vaqti
max_requests = 1000    # Har bir workerda maksimal so'rovlar
max_requests_jitter = 100  # Max so'rovlar vaqti tasodifiy muqaddas so'rovlar
preload_app = True    # Ilovani oldindan yuklash

# Qo'shimcha o'zgaruvchilar
proc_name = "my_fastapi_app"  # Jarayon nomi
