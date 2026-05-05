"""
Application configuration management using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union

class Settings(BaseSettings):
    """
    Settings class holding environment variables.
    Pydantic automatically loads these from a .env file if it exists.
    """
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Allows a comma-separated list of origins or a list, defaults to localhost:3000
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to a list if necessary."""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return self.CORS_ORIGINS

settings = Settings()
