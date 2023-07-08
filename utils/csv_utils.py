import os
from dataclasses import asdict
from typing import List

import pandas as pd

from datetime import date

from dto.booth_data import BoothData


class CSVUtils:
    @staticmethod
    def create_folder():
        now = date.today().strftime("%Y_%m_%d")
        directory = f"data/data_{now}"
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    def write_booth_data_to_csv(self, booth_data_list: List[BoothData]):
        self.create_folder()
        booth_list = [asdict(booth_data) for booth_data in booth_data_list]

        now = date.today().strftime("%Y_%m_%d")
        df = pd.DataFrame(booth_list)
        df.drop_duplicates()
        i = 1
        while os.path.exists(f"data/data_{now}/photo_booth_{now}_{i}.csv"):
            i = i + 1
        df.to_csv(f"data/data_{now}/photo_booth_{now}_{i}.csv", mode='a', header=False, index=True)
        print(f"write photo_booth_{now}_{i}.csv")
