from pydantic import BaseSettings

class Settings(BaseSettings):
    # Application settings
    app_name: str = "D&D Character Creator"
    version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: str = "sqlite:///./test.db"
    database_echo: bool = False

    # External service settings
    external_service_url: str = "https://api.example.com"
    external_service_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()