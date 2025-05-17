import os

from dotenv import load_dotenv
from pydantic import BaseModel
from app_environment import AppEnvironment
from dotenv import load_dotenv
load_dotenv()

app_env = AppEnvironment("local")

if app_env == AppEnvironment.test:
    load_dotenv(".env.test")
else:
    load_dotenv(".env", override=True)


class Env(BaseModel):
    APP_ENV: AppEnvironment
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    QD_PORT: int
    DEBUG: bool
    OPENAI_API_KEY: str
    GEMINI_API_KEY: str
    GEMINI_API_KEY_1: str    
    GEMINI_API_KEY_2: str
    GEMINI_API_KEY_3: str
    GEMINI_API_KEY_4: str
    GEMINI_API_KEY_5: str
    CHAT_FE_BASE_URL: str
    DOMAIN: str
    GROQ_API_KEY: str
    class Config:
        env_file = ".env"
    


env = Env.model_validate(os.environ)