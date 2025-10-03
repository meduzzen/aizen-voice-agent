import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings
from app.routers import router


def _include_router(app: FastAPI) -> None:
    app.include_router(router)


def run():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _include_router(app)
    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:run",
        host=settings.app.HOST,
        port=settings.app.PORT,
        reload=settings.app.RELOAD,
        factory=True,
    )
