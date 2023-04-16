from flask import Flask

from crawler import PhotoBoothCrawler
from db_query import get_brand_id_by_name, get_brand_id_name, get_confirm_id_list

app = Flask(__name__)


@app.route("/")
def health_check():
    return "hello world"


@app.route("/crawling")
def crawling_booth():
    search_list = ["즉석사진", "인생네컷", "포토이즘박스", "하루필름", "포토시그니처", "셀픽스", "플랜비스튜디오", "포토이즘컬러드", "인싸포토", "홍대네컷", "포토스트리트", "포토매틱", "포토그레이"]
    # search_list = ["즉석사진"]
    brand_info = get_brand_id_name()
    crawler = PhotoBoothCrawler(search_list, brand_info)
    crawler.search()
    return "end"


@app.route("/brands")
def test():
    brand_list = get_confirm_id_list()
    print(brand_list)
    return brand_list


if __name__ == "__main__":
    app.run(debug=True)