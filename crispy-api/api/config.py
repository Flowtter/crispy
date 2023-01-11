from starlette.config import Config

config = Config(".env")

DEBUG = config("DEBUG", cast=bool, default=True)
HOST = config("HOST", default="0.0.0.0")
PORT = config("PORT", cast=int, default=1337)
MONGO_URI = config("MONGO_URI", default="mongodb://localhost/tests")

ASSETS = config("ASSETS", default="assets")

ASSETS = "assets"
