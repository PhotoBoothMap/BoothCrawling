from config import Config
from db_utils import query_db


def get_brand_id_by_name(brand_id):
    query = f"select id, name from brand where name = '{brand_id}'"
    data = query_db(query, Config.DATABASE_URI).all()
    brand = data[0]
    # result = [row._asdict() for row in data]
    return brand._asdict()


def get_brand_list():
    query = "select name from brand"
    data = query_db(query, Config.DATABASE_URI).all()
    result = [row[0] for row in data]

    return result
