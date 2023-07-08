import os
from dataclasses import asdict
from typing import List

import pandas as pd

from datetime import date

from dto.booth_data import BoothData


class CSVUtils:
    @staticmethod
    def write_booth_data_to_csv(booth_data_list: List[BoothData]):
        booth_list = [asdict(booth_data) for booth_data in booth_data_list]

        now = date.today().strftime("%Y_%m_%d")
        df = pd.DataFrame(booth_list)
        df.drop_duplicates()
        i = 1
        while os.path.exists(f"data/data_{now}/photo_booth_{now}_{i}.csv"):
            i = i + 1
        df.to_csv(f"../data/data_{now}/photo_booth_{now}_{i}.csv", mode='a', header=False, index=True)
