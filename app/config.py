from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Load environment variables from .env
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = "NotifyMe"
    app_version: str = "1.0.0"

    # MySQL
    mysql_user: str
    mysql_password: str
    mysql_host: str
    mysql_port: int
    mysql_db: str

    # Redis
    redis_host: str
    redis_port: int
    redis_db: int

    # RabbitMQ
    rabbitmq_url: str

    # Elasticsearch
    elasticsearch_host: str

    # Logstash
    logstash_host: str
    logstash_port: int

settings = Settings()
