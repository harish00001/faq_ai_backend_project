from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FAQ AI Backend"
    app_env: str = "development"
    app_debug: bool = True
    api_v1_str: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    database_url: str = "sqlite:///./faq_ai.db"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    index_dir: str = "./storage/index"
    index_file: str = "./storage/index/faiss.index"
    metadata_file: str = "./storage/index/metadata.json"
    top_k_default: int = 3
    similarity_threshold: float = 0.75

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
