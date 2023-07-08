from dataclasses import asdict
from typing import List

from database.base_database import BaseDatabase
from dto.booth_data import BoothData


class Repository(BaseDatabase):
    def get_brand_id_by_name(self, brand_id):
        query = f"select id, name from brand where name = '{brand_id}'"
        data = self.query_db(query, ).all()
        brand = data[0]
        return brand._asdict()

    def get_brand_id_name(self):
        query = f"select id, name from brand order by id"
        data = self.query_db(query).all()
        brand_info = {}

        for row in data:
            brand_info[row[1]] = int(row[0])

        return brand_info

    def get_confirm_id_list(self):
        query = f"select confirm_id from photo_booth"
        data = self.query_db(query).all()
        return [x[0] for x in data]

    def insert_new_brand(self, brand_list):
        if len(brand_list) == 0:
            return
        query = "insert into brand (name) values "
        for brand in brand_list:
            query += f"('{brand}'),"

        self.insert_query_db(query[:-1])

    def insert_booth(self, booth_data_list: List[BoothData]):
        booth_list = [asdict(booth_data) for booth_data in booth_data_list]

        query = """
            insert into photo_booth (
                confirm_id,
                brand, 
                name, 
                address, 
                new_address, 
                homepage, 
                booth_type, 
                x_coordinate, 
                y_coordinate, 
                latitude, 
                longitude, 
                tel, 
                status
            )
                values
        """

        value_list = ["booth_id", "brand", "name", "address", "new_address", "homepage", "booth_type", "x_coordinate", "y_coordinate", "latitude", "longitude", "tel", "status"]
        for booth in booth_list:
            value_query = "("
            for value in value_list:
                data = booth.get(value)

                if data in [None, ""]:
                    value_query += "null, "

                elif value not in ["brand", "booth_id", "x_coordinate", "y_coordinate", "latitude", "longitude"]:
                    value_query += f"'{data}', "

                else:
                    value_query += f"{data}, "

            query += value_query[:-2] + "), "

        update_query = " on duplicate key update "
        for value in value_list[1:]:
            update_query += f"{value}=values({value}), "

        query = query[:-2] + update_query[:-2] + ";"
        self.insert_query_db(query)
        print(f"insert {len(booth_list)} booths")
