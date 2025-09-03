import uvicorn

from llm_service.core.app import app, get_settings

settings = get_settings()


def main() -> None:
    """Run the application server."""
    uvicorn.run(
        "llm_service.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        reload=settings.debug,
        log_config=None,  # Use our structlog configuration
    )


if __name__ == "__main__":
    main()
