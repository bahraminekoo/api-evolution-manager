from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    backend_port: int = 8000
    frontend_port: int = 5173
    log_level: str = "INFO"
    
    class Config:
        # Look for .env in project root
        env_file = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
        case_sensitive = False


settings = Settings()
