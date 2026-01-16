
# Load environment variables from .env
from dotenv import load_dotenv
from os import getenv

load_dotenv()


# Fetch variables
USER = getenv("USER")
PASSWORD = getenv("PASSWORD")
HOST = getenv("HOST")
PORT = getenv("PORT")
DBNAME = getenv("DATABASE_Name")

PLAYLIST_ID = "UUUoYtTky7mURqrkp593xAgw"
CHANNEL_ID =  "UCUoYtTky7mURqrkp593xAgw"
YOUTUBE_API_KEY = getenv("YOUTUBE_API_KEY")


REDIS_URL = getenv("REDIS_URL")