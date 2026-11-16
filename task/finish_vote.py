# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
import random
import time
from selenium.webdriver.common.by import By
from task.tool.common import Common,turn_page

class Vote(Common):
    def __init__(self,driver,iframe_element,course_name):
        super().__init__(driver,iframe_element,'问卷',course_name)
        self.iframe_element = iframe_element
    def start(self):
        #点击打开问卷
        self.iframe.click()
        time.sleep(3)
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element(By.ID,'voteIframe'))
        questions = self.driver.find_elements(By.CLASS_NAME,'question-item')
        print('问卷题目总数：',len(questions),flush=True)
        num=1
        for question in questions:
            # question_type = question.find_element(By.CSS_SELECTOR,'[class="topic-type fl"]')
            # question_text = question.find_element(By.CSS_SELECTOR,'[class="topic-txt fs15"]')
            question_choose=question.find_elements(By.CSS_SELECTOR,'[type="radio"]')
            if len(question_choose)==0:
                question_choose=question.find_elements(By.CSS_SELECTOR,'[type="checkbox"]')
            if len(question_choose)>0:
                random.choice(question_choose).click()
            else:
                tex_box=question.find_element(By.TAG_NAME,'textarea')
                tex_box.click()
                tex_box.send_keys('无')
            print(f'第{num}题已做答完毕',flush=True)
            time.sleep(1)
            num += 1
        print('作答完毕,3秒后提交',flush=True)
        time.sleep(3)
        self.driver.find_element(By.ID,'submitSuccess').click()
        confirm=self.driver.find_elements(By.CSS_SELECTOR,'[class="jb_btn jb_btn_92 fr fs14 dialog_affrim"]')
        if len(confirm)>0:
            confirm.click()
        time.sleep(2)
        #返回
        self.driver.find_element(By.CLASS_NAME,'breadcrumb').click()
        time.sleep(2)
        self.driver.switch_to.default_content()


def finish_vote(driver,page_message_dict,course_name):
    vote=Vote(driver,page_message_dict,course_name)
    vote.main()