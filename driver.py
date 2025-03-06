import selenium
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import pyautogui, time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
from PIL import Image
from urllib import request
from io import BytesIO
import threading
from webdriver_manager.chrome import ChromeDriverManager


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
        time.sleep(2)

def open_tistory():
    global driver, url
    driver.get(url)

def click_login():
    element = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/div/div[1]/a")
    element.click()
    time.sleep(2)
    element = driver.find_element(By.XPATH, "/html/body/div[5]/div/div/a[2]")
    element.click()
    time.sleep(2)

def login(id, pw):
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[1]/div/input").send_keys(id)
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[2]/div/input").send_keys(pw)
    driver.find_element(By.XPATH, "/html/body/div/div/div/main/article/div/div/form/div[4]/button[1]").click()
    time.sleep(2)

def click_posting():
    driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div/div/div/div[2]/div/div[1]/div[2]/a[1]").click()
    time.sleep(2)

def select_category():
    category_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '카테고리')]"))
    )
    category_button.click()

    # 2. 원하는 카테고리 선택 (예: "JAVA")
    category_item = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='JAVA']"))
    )
    category_item.click()

    # driver.find_element(By.XPATH, '//*[@id="category-btn"]').click()
    # driver.find_element(By.XPATH, "//div[@aria-label='JAVA']").click()
    time.sleep(2)

