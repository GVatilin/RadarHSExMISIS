from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


class DefaultSettings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_USER: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str

    BACKEND_HOST: str
    BACKEND_PORT: int
    PATH_PREFIX : str

    VUE_APP_DNS_URL: str

    API_KEY: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    AWS_ACCESS_KEY_ID: str 
    AWS_SECRET_ACCESS_KEY: str 
    AWS_BUCKET_NAME: str

    PWD_CONTEXT: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    model_config = SettingsConfigDict(env_file="../.env", extra='ignore') 

    @property
    def OAUTH2_SCHEME(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=f"{self.PATH_PREFIX}/user/token"
        )

    @property
    def database_settings(self) -> dict:
        """
        Get all settings for connection with database.
        """
        return {
            "database": self.POSTGRES_DB,
            "user": self.POSTGRES_USER,
            "password": self.POSTGRES_PASSWORD,
            "host": self.POSTGRES_HOST,
            "port": self.POSTGRES_PORT,
        }

    @property
    def database_uri(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )
    
    @property
    def database_uri_sync(self) -> str:
        """
        Get uri for connection with database.
        """
        return "postgresql://{user}:{password}@{host}:{port}/{database}".format(
            **self.database_settings,
        )

settings: DefaultSettings | None = None

def get_settings() -> DefaultSettings:
    global settings
    if settings is None:
        settings = DefaultSettings()
    return settings
