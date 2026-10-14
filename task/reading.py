# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
import time

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from task.tool.common import Common,turn_page

class Reading(Common):
    def __init__(self,driver,iframe_element,course_name):
        super().__init__(driver,iframe_element,'阅读',course_name)
        self.iframe_element = iframe_element
    def start(self):
        self.driver.switch_to.frame(self.iframe)
        if 'class' in self.iframe_element:
            self.driver.switch_to.frame(self.driver.find_element(By.NAME, "bookifame"))
            try:
                read_web=self.driver.find_element(By.ID, "Readweb")
            except NoSuchElementException:
                print('未找到阅读内容',flush=True)
                return
            read_num=read_web.find_elements(By.CLASS_NAME, "duxiuimg")
            print('当前阅读页数有{}'.format(len(read_num)),flush=True)
            for i in range(1, 11):
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight*arguments[1])",
                    read_web, i / 10
                )
                time.sleep(0.8)
            time.sleep(2)
        elif 'src' in self.iframe_element:
            self.driver.switch_to.frame(self.driver.find_element(By.ID, 'frame_content'))
            self.driver.find_element(By.CLASS_NAME, "readInfo").click()
            turn_page(self.driver,'全屏显示 专题 章节')
            print('正在阅读中...',flush=True)
            time.sleep(10)
            self.driver.close()
            turn_page(self.driver, '学生学习页面')

def reading(driver,iframe_element,course_name):
    read=Reading(driver,iframe_element,course_name)
    read.main()