from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
  DATABASE_URL:str
  ALGORITHM:str
  SECRET_KEY:str
  ACCESS_TOKEN_EXPIRY:int
  OVERSPEED_LIMIT_KMH:int


  model_config=SettingsConfigDict(
    env_file="./.env",
    extra="ignore"
  )


setting=Settings()


