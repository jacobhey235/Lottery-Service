from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    admin_password: str
    jwt_secret: str
    jwt_expiry_hours: int = 4

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    class Config:
        env_file = ".env"


settings = Settings()
