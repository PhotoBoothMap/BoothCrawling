import json
import os

import requests
import time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from datetime import date
import pandas as pd


class PhotoBoothCrawler:
    def __init__(self, keywords):
        self.keywords = keywords
        self.booth_list = []
        self.brand_list = []
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
        return webdriver.Chrome(desired_capabilities=desired_capabilities, chrome_options=options)

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
            print(idx)
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
                        print(f"log_page={idx}")
                        idx += 1
                        log_data_list.append(log_data)

        return log_data_list

    def set_data_to_list(self, log_data_list):
        for log_data in log_data_list:
            place_data_list = log_data["place"]
            for place in place_data_list:
                booth = {
                    "booth_name": place.get("name"),
                    "brand_name": place.get("brandName"),
                    "address": place.get("address"),
                    "address_disp": place.get("address_disp"),
                    "new_address": place.get("new_address"),
                    "new_address_disp": place.get("new_address_disp"),
                    "homepage": place.get("homepage"),
                    "pay_keywords": place.get("pay_keywords_disp"),
                    "x": place.get("x"),
                    "y": place.get("y"),
                    "tel": place.get("tel")
                }
                brand_name = place.get("brandName")

                # 1차 필터링 (사진 부스 아닌 장소)
                if (brand_name not in self.keywords) and ("사진" not in brand_name) and ("포토" not in brand_name):
                    continue
                # 2차 가공 brand name 지정
                if brand_name in ["즉석사진", "사진", "사진관,포토스튜디오", "사진인화,현상", "대여사진관"]:
                    brand_name = place.get("name").split(" ")[0]
                    booth["brand_name"] = brand_name
                if brand_name not in self.brand_list:
                    self.brand_list.append(brand_name)
                self.booth_list.append(booth)

    def convert_dict_to_csv(self):
        now = date.today().strftime("%Y_%m_%d")
        df = pd.DataFrame(self.booth_list)
        df.drop_duplicates()
        df.to_csv(f"data_{now}/photo_booth_{now}.csv", index=True)

    @staticmethod
    def create_folder():
        now = date.today().strftime("%Y_%m_%d")
        directory = f"data_{now}"
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print('Error: Creating directory. ' + directory)

    def write_brand_list(self):
        now = date.today().strftime("%Y_%m_%d")
        file = open(f"data_{now}/brand_list_{now}.txt", "w")
        for brand in self.brand_list:
            file.write(f"{brand}\t")

    def search(self):
        for idx, keyword in enumerate(self.keywords):
            print(keyword)
            print(idx)
            self.start_search(idx, keyword)
            time.sleep(0.2)
        log_data_list = self.get_data_from_log()
        self.set_data_to_list(log_data_list)
        self.create_folder()
        self.convert_dict_to_csv()
        self.write_brand_list()


crawler = PhotoBoothCrawler(["즉석사진", "인생네컷", "포토이즘박스", "하루필름", "포토시그니처", "셀픽스", "플랜비스튜디오", "포토이즘컬러드", "인싸포토", "홍대네컷", "포토스트리트"])
crawler.search()
