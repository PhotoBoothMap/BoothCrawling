import json
import os
from typing import Union

import requests
import time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from datetime import date
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

from database.db_query import DatabaseQuery


class PhotoBoothCrawler:
    def __init__(self, input_search_list):
        self.db_query = DatabaseQuery()
        self.search_list = input_search_list
        self.brand_info = self.db_query.get_brand_id_name()
        self.booth_list = []
        self.new_brand = []
        self.driver = self.set_chrome_driver()
        self.driver.implicitly_wait(1)
        self.driver.get(url="https://map.kakao.com/")

    @staticmethod
    def set_chrome_driver():
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("headless")
        return webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=desired_capabilities, chrome_options=options)

    def start_search(self, idx, keyword):
        input_selector = "search.keyword.query"
        search_btn_selector = "search.keyword.submit"
        dimmed_layer_selector = "dimmedLayer"

        if idx == 0:
            self.driver.find_element(By.ID, dimmed_layer_selector).click()
        self.driver.find_element(By.ID, input_selector).clear()
        self.driver.find_element(By.ID, input_selector).send_keys(keyword)
        self.driver.find_element(By.ID, search_btn_selector).click()
        time.sleep(0.1)
        self.move_page()

    def move_page(self):
        idx = 1
        flag = True
        while flag:
            print(f"page {idx}")
            next_page = idx % 5 + 1

            if idx == 1:
                # 더보기 버튼
                show_more_btn = self.driver.find_element(By.ID, "info.search.place.more")
                if "HIDDEN" in show_more_btn.get_attribute("class"):
                    flag = False
                else:
                    show_more_btn.click()
            else:
                if idx % 5 == 0:
                    next_page_set_btn = self.driver.find_element(By.ID, "info.search.page.next")
                    if "disabled" in next_page_set_btn.get_attribute("class"):
                        flag = False
                    else:
                        next_page_set_btn.click()

                else:
                    next_page_btn = self.driver.find_element(By.ID, f"info.search.page.no{next_page}")
                    if "HIDDEN" in next_page_btn.get_attribute("class"):
                        flag = False
                    else:
                        next_page_btn.click()
            idx += 1
            time.sleep(0.1)

    def get_data_from_log(self):
        log = self.driver.get_log("performance")
        log_data_list = []
        idx = 1
        for entry in log:
            message = entry["message"]
            if "Network.requestWillBeSent" in message:
                params = json.loads(entry["message"])["message"]["params"]
                try:
                    request = params["request"]
                except:
                    continue
                else:
                    if request["url"].startswith("https://search.map.kakao.com"):
                        response = requests.get(url=request["url"], headers=request["headers"])
                        first_bracket_idx = response.text.index("(")+1
                        log_data = json.loads(response.text[first_bracket_idx:-2])
                        print(f"log_page {idx}")
                        idx += 1
                        log_data_list.append(log_data)

        return log_data_list

    def set_data_to_list(self, log_data_list):
        for log_data in log_data_list:
            place_data_list = log_data["place"]
            for place in place_data_list:
                booth = {
                    "booth_id": place.get("confirmid", None),
                    "booth_name": place.get("name", None),
                    "brand": place.get("brandName", None),
                    "address": place.get("address", None),
                    "address_disp": place.get("address_disp", None),
                    "new_address": place.get("new_address", None),
                    "new_address_disp": place.get("new_address_disp", None),
                    "homepage": place.get("homepage", None),
                    "pay_keywords": place.get("pay_keywords_disp", None),
                    "booth_type": "photoBooth",
                    "x_coordinate": place.get("x", None),
                    "y_coordinate": place.get("y", None),
                    "latitude": place.get("lat", None),
                    "longitude": place.get("lon", None),
                    "tel": place.get("tel", None),
                    "status": "activate"
                }

                booth = self.filter_booth_data(booth)

                if booth is not None:
                    booth = self.convert_brand_name_to_id(booth)
                    self.booth_list.append(booth)

    @staticmethod
    def filter_booth_data(booth: dict) -> Union[dict, None]:
        brand_name = booth.get("brand")
        if brand_name is None:
            return None

        # 1차 필터링 (사진 부스 아닌 장소)
        if brand_name in ["ATM", "피자", "공간대여", "사격,궁도", "서비스,산업", "오락실", "제조업", "기업"]:
            return None

        if brand_name in ["즉석사진", "사진", "사진관,포토스튜디오", "사진인화,현상", "대여사진관"]:
            brand_name = booth.get("booth_name").split(" ")[0]
            booth["brand"] = brand_name

        return booth

    def convert_brand_name_to_id(self, booth):
        flag = False
        for brand in list(self.brand_info.keys()):
            booth_name = booth["booth_name"].replace(" ", "")
            if brand in booth_name:
                brand_id = self.brand_info[brand]
                booth["brand"] = brand_id
                flag = True
                break

        if not flag:
            if booth["brand"] not in self.new_brand and booth["brand"] != "포토":
                self.new_brand.append(booth["brand"])

        return booth

    def convert_dict_to_csv(self):
        now = date.today().strftime("%Y_%m_%d")
        df = pd.DataFrame(self.booth_list)
        df.drop_duplicates()
        df.to_csv(f"data/data_{now}/photo_booth_{now}.csv", index=True)

    @staticmethod
    def create_folder():
        now = date.today().strftime("%Y_%m_%d")
        directory = f"data/data_{now}"
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    def remove_validation(self):
        confirm_id_list = []
        new_booth_list = []

        for booth in self.booth_list:
            if booth["booth_id"] not in confirm_id_list:
                confirm_id_list.append(booth["booth_id"])
                new_booth_list.append(booth)

        self.booth_list = new_booth_list

    def update_db(self):
        self.db_query.insert_new_brand(self.new_brand)
        # confirm_id_list = selfdb_query.get_confirm_id_list()
        self.db_query.insert_booth(self.booth_list)

    def search(self):
        for idx, keyword in enumerate(self.search_list):
            print(f"{idx}.{keyword}")
            self.start_search(idx, keyword)
            time.sleep(0.2)
        log_data_list = self.get_data_from_log()
        self.set_data_to_list(log_data_list)
        self.create_folder()
        self.convert_dict_to_csv()
        self.remove_validation()
        self.db_query.insert_new_brand(self.new_brand)
        self.db_query.insert_booth(self.booth_list)


search_list = ["즉석사진", "인생네컷", "포토이즘박스", "하루필름", "포토시그니처", "셀픽스", "플랜비스튜디오", "포토이즘컬러드", "인싸포토", "홍대네컷", "포토스트리트", "포토매틱", "포토그레이", "비룸스튜디오", "모노멘션"]

crawler = PhotoBoothCrawler(search_list)
crawler.search()
