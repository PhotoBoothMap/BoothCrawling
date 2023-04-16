from config import Config
from db_utils import query_db, insert_query_db


def get_brand_id_by_name(brand_id):
    query = f"select id, name from brand where name = '{brand_id}'"
    data = query_db(query, Config.DATABASE_URI).all()
    brand = data[0]
    # result = [row._asdict() for row in data]
    return brand._asdict()


def get_brand_id_name():
    query = f"select id, name from brand order by id"
    data = query_db(query, Config.DATABASE_URI).all()
    brand_info = {}

    for row in data:
        brand_info[row[1]] = int(row[0])

    return brand_info


def get_confirm_id_list():
    query = f"select confirm_id from photo_booth"
    data = query_db(query, Config.DATABASE_URI).all()
    return [x[0] for x in data]


def insert_new_brand(brand_list):
    if len(brand_list) == 0:
        return
    query = "insert into brand (name) values "
    for brand in brand_list:
        query += f"('{brand}'),"

    insert_query_db(query[:-1], Config.DATABASE_URI).all()


def insert_booth(booth_list):
    confirm_id_list = get_confirm_id_list()
    query = "insert into photo_booth (brand, confirm_id, name, address, new_address, homepage, booth_type, x_coordinate, y_coordinate, tel, status) " \
            "values "

    value_list = ["brand", "booth_id", "booth_name", "address", "new_address", "homepage", "booth_type", "x_coordinate", "y_coordinate", "tel", "status"]
    value_query = ""
    for booth in booth_list:
        if int(booth["booth_id"]) in confirm_id_list:
            continue

        value_query += "("
        for value in value_list:
            data = booth.get(value)

            if data is None or "":
                value_query += "null, "

            elif value not in ["brand", "booth_id", "x_coordinate", "y_coordinate"]:
                value_query += f"'{data}', "

            else:
                value_query += f"{data}, "

        value_query = value_query[:-2] + "), "

    if value_query == "":
        return
    else:
        query += value_query

    insert_query_db(query[:-2], Config.DATABASE_URI).all()
