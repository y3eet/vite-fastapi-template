from app.core.config import settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.PORT),
        reload=True,
        log_level="info",
    )
