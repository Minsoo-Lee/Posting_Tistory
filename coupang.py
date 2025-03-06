import hmac
import hashlib
import requests
import json
import time
from time import gmtime, strftime
from urllib.parse import urlencode, quote
from PIL import Image, ImageOps
import os

REQUEST_METHOD = "GET"
DOMAIN = "https://api-gateway.coupang.com"
URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/search"

ACCESS_KEY = "fbc7221c-2848-403a-b9a9-9fd2c483992a"
SECRET_KEY = "d7536e66e606fe2957264cd8fae57f7b20588d7a"

def get_auth(method, url):
    path, *query = url.split("?")

    # 날짜 포맷: 'yyMMddTHHmmssZ'
    datetime_gmt = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'

    # 메시지 구성
    message = datetime_gmt + method + path + (query[0] if query else "")

    # 서명 생성
    signature = hmac.new(bytes(SECRET_KEY, "utf-8"),
                         message.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    logging.debug(f"HMAC Message: {message}")
    logging.debug(f"HMAC Signature: {signature}")

    wait(1)

    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(ACCESS_KEY, datetime_gmt,
                                                                                          signature)

def search_products(keyword, limit, auth):
    URL = ("/v2/providers/affiliate_open_api/apis/openapi/products/search?keyword=" +
           quote(keyword) + "&limit=" + str(limit))
    url = "{}{}".format(DOMAIN, URL)

    response = requests.request(method=REQUEST_METHOD, url=url, headers={"Authorization": auth,
                                                                         "Content-Type": "application/json;charset=UTF-8"})

    wait(1)

    return response.json()['data']['productData']

def filter_products(keyword, result):
    keywords = keyword.split(" ")
    wait(1)
    return [product for product in result if
            all(keyword in product["productName"] for keyword in keywords)]

def get_data(keyword, limit, auth):
    result = search_products(keyword, limit, auth)
    wait(1)
    return json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False)

def get_url(data):
    data = json.loads(data)
    url = [item["productUrl"] for item in data]
    wait(1)
    return url[0]

def download_images(data):
    data = json.loads(data)
    image_urls = [item["productImage"] for item in data]
    index = 1
    for image_url in image_urls:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(f"{index}.jpg", "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"이미지 다운로드 완료: {index}.jpg")
            index += 1
        else:
            print("이미지 다운로드 실패, 상태 코드:", response.status_code)
        wait(1)
    return image_urls

def add_border(size, color):
    for index in range(1, 6):
        # 이미지 열기
        image = Image.open(f"{index}.jpg")  # 저장한 이미지 파일 경로

        # 테두리 크기 및 색상 설정
        border_size = size  # 원하는 테두리 두께
        border_color = color  # 원하는 색상

        # 테두리 추가 (ImageOps.expand 사용)
        bordered_image = ImageOps.expand(image, border=border_size, fill=border_color)

        # 결과 저장
        bordered_image.save(f"{index}.jpg")
        wait(1)

def remove_images():
    for index in range(1, 6):
        file_path = f"{index}.jpg"
        os.remove(file_path)
        wait(1)

def wait(sec):
    time.sleep(sec)

# keyword = "맥북 M4 프로"
# result = search_products("맥북 M4 프로", 5)
# print(json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False))

