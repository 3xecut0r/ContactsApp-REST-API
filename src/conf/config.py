from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "qwerty"
    postgres_port: int = "5433"
    sqlalchemy_database_url: str = "postgresql+psycopg2://:@:5432/postgres"
    secret_key: str = "secret"
    algorithm: str = "HS128"
    mail_username: str = "test@example.com"
    mail_password: str = "0987654321"
    mail_from: str = "test@example.com"
    mail_port: int = 465
    mail_server: str = "smtp.gmail.com"
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str = "qwerty"
    cloudinary_api_key: str = "zxcvbnm"
    cloudinary_api_secret: str = "mnbvcxz"

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
