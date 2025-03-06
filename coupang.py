import hmac
import hashlib
import requests
import json
from time import gmtime, strftime
from urllib.parse import urlencode, quote
import logging

logging.basicConfig(level=logging.DEBUG)

REQUEST_METHOD = "GET"
DOMAIN = "https://api-gateway.coupang.com"
URL = "/v2/providers/affiliate_open_api/apis/openapi/v1/products/search"

ACCESS_KEY = "fbc7221c-2848-403a-b9a9-9fd2c483992a"
SECRET_KEY = "d7536e66e606fe2957264cd8fae57f7b20588d7a"

def generateHmac(method, url):
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

    return "CEA algorithm=HmacSHA256, access-key={}, signed-date={}, signature={}".format(ACCESS_KEY, datetime_gmt,
                                                                                          signature)

def search_products(keyword, limit):
    URL = ("/v2/providers/affiliate_open_api/apis/openapi/products/search?keyword=" +
           quote(keyword) + "&limit=" + str(limit))
    authorization = generateHmac("GET", URL)
    url = "{}{}".format(DOMAIN, URL)

    response = requests.request(method=REQUEST_METHOD, url=url, headers={"Authorization": authorization,
                                                                         "Content-Type": "application/json;charset=UTF-8"})

    print(response.json())

    return response.json()['data']['productData']

def filter_products(keyword, result):
    keywords = keyword.split(" ")
    return [product for product in result if
            all(keyword in product["productName"] for keyword in keywords)]

def get_data(keyword, limit):
    result = search_products(keyword, limit)
    return json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False)

# keyword = "맥북 M4 프로"
# result = search_products("맥북 M4 프로", 5)
# print(json.dumps(filter_products(keyword, result), indent=4, ensure_ascii=False))

