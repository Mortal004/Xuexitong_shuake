import time

import pyautogui
from selenium.webdriver.common.by import By

from task.tool import color


def __ppt(driver):
    print(color.green("正在检索PPT数量..."),flush=True)
    time.sleep(2)
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
    element = driver.find_element(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-ppt"]')
    driver.switch_to.frame(element)
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="panView"]'))
    imgList = driver.find_elements(By.TAG_NAME, 'li')
    print(color.green("共有{}张PPT".format(len(imgList))),flush=True)
    for i in range(len(imgList)):
        # print('\r'+"观看第{}张PPT".format(i+1), end="")
        driver.execute_script("window.scrollBy(0,2000)")
        # time.sleep(0.1)
    pyautogui.scroll(-200)
    print(color.green('已看完ppt'),flush=True)

