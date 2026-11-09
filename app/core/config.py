from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra='ignore')
    database_url: str = 'sqlite:///./personal.db'
    api_key: str
    github_username: str
    github_token: str

settings = Settings()