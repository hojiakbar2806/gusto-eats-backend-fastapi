from fastapi import  Request


def get_host_url(request: Request) -> str:
    return str(request.url)