from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
        Settings class to manage configuration for the FastAPI project.

        Attributes:
            postgres_db (str): PostgreSQL database name.
            postgres_user (str): PostgreSQL username.
            postgres_password (str): PostgreSQL password.
            postgres_port (int): PostgreSQL port number.
            sqlalchemy_database_url (str): SQLAlchemy database URL.
            secret_key (str): Secret key for JWT token.
            algorithm (str): Algorithm for JWT token.
            mail_username (str): Username for sending emails.
            mail_password (str): Password for sending emails.
            mail_from (str): Email address for sending emails.
            mail_port (int): Email server port number.
            mail_server (str): Email server address.
            redis_host (str, optional): Redis server host (default is 'localhost').
            redis_port (int, optional): Redis server port (default is 6379).
            cloudinary_name (str): Cloudinary account name.
            cloudinary_api_key (str): Cloudinary API key.
            cloudinary_api_secret (str): Cloudinary API secret.

        Config:
            env_file (str): Name of the environment file (default is '.env').
            env_file_encoding (str): Encoding of the environment file (default is 'utf-8').
        """
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_port: int
    sqlalchemy_database_url: str
    secret_key: str
    algorithm: str
    mail_username: str
    mail_password: str
    mail_from: str
    mail_port: int
    mail_server: str
    redis_host: str = 'localhost'
    redis_port: int = 6379
    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


# Create an instance of the Settings class
settings = Settings()
