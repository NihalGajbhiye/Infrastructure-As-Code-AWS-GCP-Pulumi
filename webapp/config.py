import os
from dotenv import load_dotenv
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))

# Checking if we are running on Github Actions
ON_GITHUB = os.getenv("GITHUB_ACTION") == "true"

# Load .env file we are not on GITHUB and .env exist
if not ON_GITHUB:
    env_path = Path(basedir, '.env')
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)

class Config:
    DB_USER = os.getenv("DATABASE_USER")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
    HOST_NAME = os.getenv("HOST_NAME")
    DB_NAME = os.getenv("DATABASE_NAME")
    SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{HOST_NAME}:5432/{DB_NAME}'


    