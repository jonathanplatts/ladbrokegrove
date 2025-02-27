from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings 


class Settings(BaseSettings):
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2880
    DB_HOST: str = "db"
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_PORT: int = 5432
    DB_URL: str | None = None # Optional
    GOOGLE_MAPS_API_KEY: str
    OPENAI_API_KEY: str

    @property
    def DATABASE_URL(self) -> str:
        return self.DB_URL or "postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
