from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert 
import time
import os
import shutil
import threading
from seleniumbase import Driver, get_driver

chrome_profile = os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedata\chromeprofile")
chrome_driver = os.path.join(os.path.dirname(os.path.dirname(__file__)),"chromedata\chromedriver.exe")

def create_new_profile_data(chrome_profile,chrome_driver=chrome_driver):
    driver = Driver(uc=True, user_data_dir=chrome_profile,headless=True, headless2=True)
    driver.get("https://google.com")
    # input()
    # driver.close()
    # driver.quit()

def remove_chrome_profile_data(chrome_profile):
    try:
        shutil.rmtree(chrome_profile)
    except:
        pass
    try:
        os.makedirs(chrome_profile)
    except:
        pass

create_new_profile_data(chrome_profile)