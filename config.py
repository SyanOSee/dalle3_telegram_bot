# Third-party
from dotenv import load_dotenv

# Standard
from pathlib import Path
import os

load_dotenv('./.env')  # Load environment variables from .env

BASE = Path(__file__).resolve().parent
SQLITE_PATH = BASE / 'database' / 'sqlite_db.db'

# Define project directories
project = {
    'base': BASE,
    'storage': BASE / 'storage'
}

# Define bot configuration
bot = {
    'token': os.getenv('BOT_TOKEN'),
}

# Define API configuration
api = {
    'token': os.getenv('OPENAI_API_KEY'),
    'base_url': 'https://api.proxyapi.ru/openai/v1'
}

# Define database configuration
database = {
    'host': os.getenv('DATABASE_HOST'),
    'port': os.getenv('DATABASE_PORT'),
    'user': os.getenv('DATABASE_USER'),
    'password': os.getenv('DATABASE_PASSWORD'),
}

# Define server configuration
server = {
    'host': os.getenv('PANEL_HOST'),
    'port': os.getenv('PANEL_PORT'),
    'secret_key': os.getenv('SECRET_KEY')
}