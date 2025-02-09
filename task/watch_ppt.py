import time

import pyautogui
from selenium.webdriver.common.by import By

from task.tool import color


def __ppt(driver):

    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
    elements = driver.find_elements(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-ppt"]')
    ppt_num=len(elements)
    if ppt_num==0:
        elements = driver.find_elements(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-pdf"]')
        ppt_num=len(elements)
    print(color.green(f'已检测到{ppt_num}个PPT'), flush=True)
    for num in range(ppt_num):
        driver.switch_to.default_content()
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
        print(color.green(f'开始播放第{num + 1}个PPT'), flush=True)
        element = elements[num]
        driver.switch_to.frame(element)
        driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="panView"]'))
        print(color.green("正在检索PPT数量..."),flush=True)
        time.sleep(1)
        imgList = driver.find_elements(By.TAG_NAME, 'li')
        print(color.green("共有{}张PPT".format(len(imgList))),flush=True)
        for i in range(len(imgList)):
            # print('\r'+"观看第{}张PPT".format(i+1), end="")
            driver.execute_script("window.scrollBy(0,2000)")
            # time.sleep(0.1)
        pyautogui.scroll(-200)
        print(color.green(f'已看完第{num+1}个ppt'),flush=True)
        time.sleep(1)
