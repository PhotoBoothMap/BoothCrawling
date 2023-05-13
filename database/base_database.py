from config import Config
from sqlalchemy import create_engine, text


class BaseDatabase:
    def __init__(self):
        self.db_uri = Config.DATABASE_URI

    def get_db_engine(self):
        db_engine = create_engine(
            self.db_uri,
            connect_args={"connect_timeout": 900, "options": "-csearch_path=real_db"},
        )
        return db_engine

    def query_db(self, query):
        sql = text(query)
        engine = create_engine(self.db_uri)
        with engine.begin() as con:
            results = con.execute(sql)
        return results

    def insert_query_db(self, query):
        sql = text(query)
        engine = create_engine(self.db_uri)
        with engine.begin() as con:
            con.execute(sql)