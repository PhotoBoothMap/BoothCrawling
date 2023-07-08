from database.repository import Repository
from dto.booth_data import CrawlingData
from utils.photo_booth_crawler import PhotoBoothCrawler
from utils.csv_utils import CSVUtils

search_keyword_list = ["즉석사진", "인생네컷", "포토이즘박스", "하루필름", "포토시그니처", "셀픽스", "플랜비스튜디오", "포토이즘컬러드", "인싸포토", "홍대네컷", "포토스트리트", "포토매틱", "포토그레이", "비룸스튜디오", "모노멘션"]
# search_keyword_list = ["셀픽스"]

# get exist brand info
repository = Repository()
brand_info = repository.get_brand_id_name()

# get booth_data from kakao map
crawler = PhotoBoothCrawler(search_keyword_list, brand_info)
crawling_result_data: CrawlingData = crawler.search()

# write booth_data to csv
CSVUtils().write_booth_data_to_csv(crawling_result_data.booth_data_list)

# insert brand data to db
new_brand_list = crawler.get_new_brand_name_list()
if len(new_brand_list) > 0:
    repository.insert_new_brand(new_brand_list)
    brand_info = repository.get_brand_id_name()
    for booth in crawling_result_data.booth_data_list:
        if booth.brand_id is None:
            booth.brand_id = brand_info[booth.brand_name]

# insert booth data to db
if len(crawling_result_data.booth_data_list) > 0:
    repository.insert_booth(crawling_result_data.booth_data_list)
else:
    print("there is no booth to insert")
