# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import time
from selenium.webdriver.common.by import By

from task.tool import color


def __ppt(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
    ppt_iframes = driver.find_elements(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-ppt"]')
    ppt_num=len(ppt_iframes)
    try:
        pdf_iframes = driver.find_elements(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-pdf"]')
        pdf_num=len(pdf_iframes)
        all_iframes=[ppt_iframes,pdf_iframes]
    except:
        all_iframes=[ppt_iframes]
    print(color.green(f'已检测到{ppt_num}个PPT'), flush=True)
    for iframes in all_iframes:
        for num in range(len(iframes)):
            ppt_iframe = iframes[num]
            driver.switch_to.default_content()
            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
            try:
                # 定位到该元素的前一个兄弟元素
                ppt_iframe.find_element(By.XPATH, "preceding-sibling::div[1]")
                print(color.green("该PPT存在任务点"), flush=True)
            except:
                print(color.green("该PPT不存在任务点"), flush=True)
                continue
            #检查任务点是否已完成
            # 定位到该元素的上一级（父元素）
            parent_element = ppt_iframe.find_element(By.XPATH, "..")
            # 获取 parent_element 的class值
            parent_element_class = parent_element.get_attribute("class")
            if parent_element_class == 'ans-attach-ct ans-job-finished':
                print(color.green("该PPT已完成"), flush=True)
                continue
            else:
                print(color.green("该PPT未完成"), flush=True)

            print(color.green(f'开始播放第{num + 1}个PPT'), flush=True)
            # 滚动到PPT
            driver.execute_script("arguments[0].scrollIntoView();", ppt_iframe)
            time.sleep(1)
            driver.switch_to.frame(ppt_iframe)
            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="panView"]'))
            print(color.green("正在检索PPT数量..."),flush=True)
            time.sleep(1)
            imgList = driver.find_elements(By.TAG_NAME, 'li')
            print(color.green("共有{}张PPT".format(len(imgList))),flush=True)
            for i in range(len(imgList)):
                # print('\r'+"观看第{}张PPT".format(i+1), end="")
                driver.execute_script("window.scrollBy(0,2000)")
                # time.sleep(0.1)
            # pyautogui.scroll(-200)
            print(color.green(f'已看完第{num+1}个ppt'),flush=True)
            time.sleep(1)
