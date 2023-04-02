import json
import re
import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from datetime import date
import pandas as pd


class PhotoBoothCrawler:
    def __init__(self):
        self.booth_list = []
        self.driver = self.set_chrome_driver()
        self.driver.get(url="https://map.kakao.com/")

    @staticmethod
    def set_chrome_driver():
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        return webdriver.Chrome(desired_capabilities=desired_capabilities, chrome_options=options)

    def start_search(self):
        input_selector = "search.keyword.query"
        search_btn_selector = "search.keyword.submit"
        dimmed_layer_selector = "dimmedLayer"
        self.driver.implicitly_wait(3)
        self.driver.find_element(By.ID, dimmed_layer_selector).click()
        self.driver.find_element(By.ID, input_selector).send_keys("즉석사진")
        self.driver.find_element(By.ID, search_btn_selector).click()

    def get_data_from_log(self):
        log = self.driver.get_log("performance")
        log_data = None
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
                        match = re.search(r'\((.*?)\)', response.text)
                        if match:
                            log_data = json.loads(match.group(1))
                            break

        return log_data

    def set_data_to_list(self, log_data):
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

            self.booth_list.append(booth)

    def convert_dict_to_csv(self):
        now = date.today().strftime("%Y_%m_%d")
        df = pd.DataFrame(self.booth_list)
        df.to_csv(f"photo_booth_{now}.csv", index=True)

    def search(self):
        self.start_search()
        log_data = self.get_data_from_log()
        self.set_data_to_list(log_data)
        self.convert_dict_to_csv()


crawler = PhotoBoothCrawler()
crawler.search()
