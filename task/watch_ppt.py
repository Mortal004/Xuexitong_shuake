# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import time
from selenium.webdriver.common.by import By

from task.tool import color
from task.tool.common import Common

class PPT(Common):
    def __init__(self, driver, course_name):
        super().__init__(
            driver,
            '[class="ans-attach-online insertdoc-online-ppt"], [class="ans-attach-online insertdoc-online-pdf"]',
            "PPT",
            course_name
        )

    def start(self):
        self.driver.switch_to.frame(self.iframe)
        self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, '[id="panView"]'))
        print(color.green("正在检索PPT数量..."), flush=True)
        time.sleep(1)
        img_list = self.driver.find_elements(By.TAG_NAME, 'li')
        print(color.green(f"共有{len(img_list)}张PPT"), flush=True)
        for i in range(len(img_list)):
            self.driver.execute_script("window.scrollBy(0,2000)")
        print(color.green("已看完PPT"), flush=True)
        time.sleep(2)
        self.driver.switch_to.parent_frame()

def __ppt(driver, course_name):
    ppt = PPT(driver, course_name)
    ppt.main()