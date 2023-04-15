import os

from dotenv import load_dotenv

load_dotenv()


class Config(object):
    STRICT_SLASHES = False
    DATABASE_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}".format(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        db=os.getenv("DB_NAME"),
    )


class Development(Config):
    DEBUG = True


class Production(Config):
    DEBUG = False
