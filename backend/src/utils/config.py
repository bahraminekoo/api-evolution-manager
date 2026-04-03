from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    backend_port: int = 8000
    frontend_port: int = 5173
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
