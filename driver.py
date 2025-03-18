import selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pyautogui, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys
import os
from PIL import Image
from urllib import request
from io import BytesIO
import threading
from webdriver_manager.chrome import ChromeDriverManager
import base64

driver = None
url = "https://www.tistory.com"
img_path = ""
thread_end = False
thread = None

def init_chrome():
    global driver
    if driver is None:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument("--incognito")  # 시크릿 모드 추가
        driver = webdriver.Chrome(options=chrome_options)
        time.sleep(1)


def open_tistory():
    global driver, url
    driver.get(url)

def click_login():
    element = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/div/div[1]/a")
    element.click()
    time.sleep(1)
    element = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/a[2]")
    element.click()
    time.sleep(1)

def login(id, pw):
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[1]/div/input").send_keys(id)
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[2]/div/input").send_keys(pw)
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[4]/button[1]").click()
    time.sleep(5)

def enter_url(posting_url):
    driver.get(posting_url)
    time.sleep(5)

def enter_posting():
    posting_url = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div[2]/a[1]").get_attribute("href")
    driver.get(posting_url)
    time.sleep(1)
    try:
        alert = driver.switch_to.alert
        alert.dismiss()  # OK 클릭 (alert.dismiss() 사용하면 취소 버튼 클릭)
    except:
        pass
    time.sleep(1)
    return posting_url

def select_category(category):
    driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[1]/div/button").click()
    time.sleep(1)
    element = driver.find_element(By.XPATH, '//*[@id="category-list"]')
    time.sleep(1)

    # elements에는 클릭할 수 있는 요소들을, category_names에는 카테고리명만 저장하여 맵으로 변환
    elements = element.find_elements(By.CSS_SELECTOR, 'div[role="option"]')
    category_names = [e.get_attribute("aria-label") for e in elements]
    categories = dict(zip(category_names, elements))

    # 카테고리 클릭, 카테고리가 없다면 일단 에러 반환
    # 실행 버튼 활성화 타임, 그리고 로직 일부 순환으로 예외처리를 마무리 할 것
    try:
        categories[category].click()
        print("카테고리가 존재합니다.")
    except:
        print("카테고리가 존재하지 않습니다.")
    time.sleep(1)

def post_title(title):
    driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[2]/textarea").send_keys(title)
    time.sleep(1)

def enter_iframe():
    iframe = driver.find_element(By.TAG_NAME, "iframe")  # iframe 태그를 찾기
    driver.switch_to.frame(iframe)  # 해당 iframe으로 전환
    time.sleep(1)

def post_content(content, is_center = True):
    if is_center is True:
        content_html = f'<div style="text-align: center; line-height: 2;">{content}</div>'
    else:
        content_html = f'<div style="text-align: line-height: 2;">{content}</div>'

    editor = driver.find_element(By.TAG_NAME, "body")
    editor.send_keys(" ")  # 입력 활성화
    time.sleep(0.5)

    # 새로운 div를 추가
    script = """
        var div = document.createElement('div');
        div.innerHTML = arguments[0];
        document.body.appendChild(div);
        """
    driver.execute_script(script, content_html)
    time.sleep(1)
    # driver.find_element(By.XPATH, "//*[@id='tinymce']").send_keys(content)

    # new
    # return '<div style="text-align: center; line-height: 2;">' + content + '</div>'

    # editor = driver.find_element(By.TAG_NAME, "body")
    # editor.send_keys(" ")  # 공백을 한 번 입력해서 입력 상태 활성화
    # time.sleep(0.5)

    # driver.execute_script("arguments[0].innerHTML = arguments[1];", editor, content)
    # time.sleep(1)
    #
    # # 입력 이벤트 트리거
    # driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", editor)
    # driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", editor)
    # time.sleep(1)

def post_href(link, text="클릭하여 이동"):
    script = f"""
        var body = document.body;
        var aTag = document.createElement('a');
        aTag.href = '{link}';
        aTag.target = '_blank';
        aTag.textContent = '{text}';

        // 스타일 추가
        aTag.style.display = 'inline-block';
        aTag.style.padding = '10px 20px';
        aTag.style.margin = '10px auto';
        aTag.style.fontSize = '16px';
        aTag.style.color = '#ffffff';
        aTag.style.backgroundColor = '#007BFF';
        aTag.style.border = 'none';
        aTag.style.borderRadius = '5px';
        aTag.style.textDecoration = 'none';
        aTag.style.textAlign = 'center';
        aTag.style.boxShadow = '2px 2px 10px rgba(0, 0, 0, 0.2)';
        aTag.style.cursor = 'pointer';

        // hover 효과 추가
        aTag.onmouseover = function() {{
            aTag.style.backgroundColor = '#0056b3';
        }};
        aTag.onmouseout = function() {{
            aTag.style.backgroundColor = '#007BFF';
        }};

        body.appendChild(aTag);
    """
    driver.execute_script(script)

# def post_href(link):
#     print(link)
#     script = """
#         var body = document.body;
#         var aTag = document.createElement('a');
#         aTag.href = '%s';
#         aTag.target = '_blank';
#         aTag.textContent = '%s';
#         body.appendChild(aTag);
#
#         // 강제로 링크 클릭 이벤트 추가
#         aTag.addEventListener('click', function(event) {
#             window.open(aTag.href, '_blank');  // 새 탭에서 링크 열기
#         });
#         """ % (link, link)
#
#     driver.execute_script(script)

def insert_script(content):
    editor = driver.find_element(By.TAG_NAME, "body")
    editor.send_keys(" ")  # 공백을 한 번 입력해서 입력 상태 활성화
    time.sleep(0.5)

    driver.execute_script("arguments[0].innerHTML = arguments[1];", editor, content)
    time.sleep(1)

    # 입력 이벤트 트리거
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", editor)
    driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", editor)
    time.sleep(1)

def post_image(index):
    image_path = f"{index}.jpg"  # 실제 로컬 이미지 경로
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    # base64로 변환
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # 새로운 img 태그를 추가하여 기존 내용 유지
    script = """
    var img = document.createElement('img');
    img.src = 'data:image/jpeg;base64,' + arguments[0];
    img.style.display = 'block';
    img.style.width = '400px';  // 가로 크기 조정
    img.style.height = 'auto';  // 세로 비율 유지
    img.style.margin = '10px auto';
    document.body.appendChild(img);
    """
    driver.execute_script(script, image_base64)
    # image_path = f"{index}.jpg"  # 실제 로컬 이미지 경로
    # with open(image_path, "rb") as image_file:
    #     image_data = image_file.read()
    #
    # # base64로 변환
    # import base64
    # image_base64 = base64.b64encode(image_data).decode('utf-8')
    #
    # # JavaScript를 사용해 이미지를 삽입 (base64로 변환된 이미지)
    # script = """
    # var body = document.querySelector('body');
    # var img = document.createElement('img');
    # img.src = 'data:image/jpeg;base64,' + arguments[0];
    # body.appendChild(img);
    # """

    # driver.execute_script(script, image_base64)

def quit_frame():
    driver.switch_to.default_content()

def click_posting():
    driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/button").click()
    time.sleep(1)

def post_public():
    driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div/form/fieldset/div[2]/div/dl[1]/dd/div[1]/label/input").click()
    time.sleep(1)
    driver.find_element(By.XPATH, "/html/body/div[5]/div/div/div/form/fieldset/div[3]/div/button[2]").click()
    time.sleep(1)

def align_center():
    driver.find_element(By.XPATH, "/html/body/div[1]/div/main/div/div[5]/div/div/div[1]/div/div/div/div/div/div[3]/div/div[2]/button").click()
    time.sleep(1)

def divide_content(content):
    return content.split("[사진 삽입]")

def make_final_content(content_list, length, path):
    result = ""
    i = 0
    for i in range(0, length):
        result += (content_list[i] + f'<br><img src="{path}/{i + 1}.jpg" alt="로컬 이미지"><br>')
    return result + content_list[i+ 1]
