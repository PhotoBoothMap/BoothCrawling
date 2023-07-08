import json
import time
from typing import Optional, List

import requests
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from dto.booth_data import BoothData, CrawlingData


class PhotoBoothCrawler:
    def __init__(self, search_keyword_list, brand_info):
        self.search_list = search_keyword_list
        self.brand_info = brand_info
        self.new_brand = []
        self.driver = self._set_chrome_driver()
        self.driver.implicitly_wait(1)
        self.driver.get(url="https://map.kakao.com/")

    @staticmethod
    def _set_chrome_driver():
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("headless")
        return webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=desired_capabilities, chrome_options=options)

    def _start_search(self, idx, keyword):
        input_selector = "search.keyword.query"
        search_btn_selector = "search.keyword.submit"
        dimmed_layer_selector = "dimmedLayer"

        if idx == 0:
            self.driver.find_element(By.ID, dimmed_layer_selector).click()
        self.driver.find_element(By.ID, input_selector).clear()
        self.driver.find_element(By.ID, input_selector).send_keys(keyword)
        self.driver.find_element(By.ID, search_btn_selector).click()
        time.sleep(0.1)
        self._move_page()

    def _move_page(self):
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

    def _get_data_from_log(self):
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
                        first_bracket_idx = response.text.index("(") + 1
                        log_data = json.loads(response.text[first_bracket_idx:-2])
                        print(f"log_page {idx}")
                        idx += 1
                        log_data_list.append(log_data)

        return log_data_list

    def _set_data_to_list(self, log_data_list) -> List[BoothData]:
        booth_list = list()
        for log_data in log_data_list:
            place_data_list = log_data["place"]
            for place in place_data_list:
                booth_data = BoothData(
                    confirm_id=int(place.get("confirmid", None)),
                    booth_name=place.get("name", None),
                    brand_id=None,
                    brand_name=place.get("brandName", None),
                    address=place.get("address", None),
                    address_disp=place.get("address_disp", None),
                    new_address=place.get("new_address", None),
                    new_address_disp=place.get("new_address_disp", None),
                    homepage=place.get("homepage", None),
                    pay_keywords=place.get("pay_keywords_disp", None),
                    booth_type="photoBooth",
                    x_coordinate=place.get("x", None),
                    y_coordinate=place.get("y", None),
                    latitude=place.get("lat", None),
                    longitude=place.get("lon", None),
                    tel=place.get("tel", None),
                    status="active"
                )

                filtered_booth_data = self._filter_booth_data(booth_data)

                if filtered_booth_data is not None:
                    booth_data = self._convert_brand_name_to_id(filtered_booth_data)
                    booth_list.append(booth_data)

        return booth_list

    @staticmethod
    def _filter_booth_data(booth_info: BoothData) -> Optional[BoothData]:
        brand_name = booth_info.brand_name

        if brand_name is None:
            return None

        # 1차 필터링 (사진 부스 아닌 장소)
        if brand_name in ["ATM", "피자", "공간대여", "사격,궁도", "서비스,산업", "오락실", "제조업", "기업"]:
            return None

        if brand_name in ["즉석사진", "사진", "사진관,포토스튜디오", "사진인화,현상", "대여사진관"]:
            temp_brand_name = brand_name.split(" ")[0]
            booth_info.brand_name = temp_brand_name

        return booth_info

    def _convert_brand_name_to_id(self, booth_data: BoothData) -> BoothData:
        for brand in list(self.brand_info.keys()):
            booth_name = booth_data.booth_name.replace(" ", "")

            if brand in booth_name:
                brand_id = self.brand_info[brand]
                booth_data.brand_id = brand_id
                break

        if booth_data.brand_id is None:
            if booth_data.brand_name not in self.new_brand and booth_data.brand_name != "포토":
                self.new_brand.append(booth_data.brand_name)

        return booth_data

    def search(self) -> CrawlingData:
        for idx, keyword in enumerate(self.search_list):
            print(f"{idx}.{keyword}")
            self._start_search(idx, keyword)
            time.sleep(0.2)
        log_data_list = self._get_data_from_log()
        booth_list = self._set_data_to_list(log_data_list)

        return CrawlingData(
            new_brand_name_list=self.new_brand,
            booth_data_list=booth_list,
        )

    def get_new_brand_name_list(self) -> List[str]:
        return self.new_brand
