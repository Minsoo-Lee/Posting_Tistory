import hmac
import hashlib
import requests
import json
import time
from time import gmtime, strftime
from urllib.parse import urlencode, quote
from PIL import Image, ImageOps
import os
from io import BytesIO

REQUEST_METHOD = "GET"
DOMAIN = "https://api-gateway.coupang.com"
URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/search"

ACCESS_KEY = "fbc7221c-2848-403a-b9a9-9fd2c483992a"
SECRET_KEY = "d7536e66e606fe2957264cd8fae57f7b20588d7a"

def get_hmac(method, url):
    path, *query = url.split("?")

    # 날짜 포맷: 'yyMMddTHHmmssZ'
    datetime_gmt = strftime('%y%m%d', gmtime()) + 'T' + strftime('%H%M%S', gmtime()) + 'Z'

    # 메시지 구성
    message = datetime_gmt + method + path + (query[0] if query else "")

    # 서명 생성
    signature = hmac.new(bytes(SECRET_KEY, "utf-8"),
                         message.encode("utf-8"),
                         hashlib.sha256).hexdigest()

    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(ACCESS_KEY, datetime_gmt,
                                                                                          signature)

def get_path(keyword, limit):
    return ("/v2/providers/affiliate_open_api/apis/openapi/products/search?keyword=" +
           quote(keyword.encode('utf-8')) + "&limit=" + str(limit))

def get_response(path):
    url = "{}{}".format(DOMAIN, path)

    response = requests.request(method=REQUEST_METHOD, url=url, headers={"Authorization": get_hmac("GET", path),
                                                                         "Content-Type": "application/json;charset=UTF-8"})

    wait(1)
    return response.json()['data']

def filter_products(keyword, result):
    keywords = keyword.split(" ")
    product_list = result['productData']
    wait(1)
    # print(json.dumps(product_list, indent=4, ensure_ascii=False))
    return [product for product in product_list if
            all(keyword in product["productName"] for keyword in keywords)]

# def get_data(keyword, path):
#     result = search_products(path)
#     wait(1)
#     return json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False)

def get_url(data):
    data = json.loads(data)
    url = [item["productUrl"] for item in data]
    wait(1)
    return url[0]

# 기존 코드 (이미지 다운로드만 실행)
# def download_images(data):
#     image_urls = [item["productImage"] for item in data]
#     index = 1
#     if len(image_urls) >= 4:
#         image_urls = image_urls[:4]
#     for image_url in image_urls:
#         response = requests.get(image_url, stream=True)
#         if response.status_code == 200:
#             with open(f"{index}.jpg", "wb") as file:
#                 for chunk in response.iter_content(1024):
#                     file.write(chunk)
#             print(f"이미지 다운로드 완료: {index}.jpg")
#             index += 1
#         else:
#             print("이미지 다운로드 실패, 상태 코드:", response.status_code)
#         wait(1)
#     return image_urls

# 수정 코드 - 사진 용량: 80kb, 사이즈: 1000px
def download_images(data, keyword):
    image_urls = [item["productImage"] for item in data]
    index = 1

    if len(image_urls) >= 4:
        image_urls = image_urls[:4]

    for image_url in image_urls:
        response = requests.get(image_url, stream=True)

        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))

            # 가로 세로 비율 유지하면서 100px로 리사이징
            image.thumbnail((1000, 1000))

            # 압축하여 80KB 이하로 저장
            output = BytesIO()
            quality = 95  # 초기 품질 값
            while True:
                output.seek(0)
                if image.mode == "RGBA":
                    image = image.convert("RGB")  # RGB 모드로 변환
                image.save(output, format="JPEG", quality=quality)
                print(quality)
                if output.tell() <= 80 * 1024 or quality <= 10:  # 80KB 이하 또는 품질이 너무 낮아질 경우
                    break
                quality -= 5  # 품질을 점진적으로 낮춤

            # 최종 이미지 저장
            with open(f"{index}.jpg", "wb") as file:
                file.write(output.getvalue())

            print(f"이미지 다운로드 및 변환 완료: {index}.jpg")
            index += 1
        else:
            print("이미지 다운로드 실패, 상태 코드:", response.status_code)
    return image_urls

def add_border(size, color, length):
    for index in range(1, length + 1):
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

def remove_images(length):
    for index in range(1, length + 1):
        file_path = f"{index}.jpg"
        os.remove(file_path)
        wait(1)

def wait(sec):
    time.sleep(sec)

# keyword = "맥북 M4 프로"
# result = search_products("맥북 M4 프로", 5)
# print(json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False))

