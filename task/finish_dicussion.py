import random

from selenium.webdriver.common.by import By
import ast

from task.DeepSeekAsk import DeepSeekAsk
import time
from task.do_work import turn_page
from task.common import Common

class Discussion(Common):
    def __init__(self,driver,API):
        super().__init__(driver,'[src="/ananas/modules/insertbbs/index.html?v=2025-0109-1519&castscreen=0"]',"讨论")
        self.question = None
        self.answer = []
        self.API=API
    def get_answer(self):
        try:
            self.answer = DeepSeekAsk(self.API, self.question, '简答题')
        except Exception as e:
            print(f'答题时出错了{e}',flush=True)

    def start(self):
        self.iframe.click()
        turn_page(self.driver,'话题详情')
        self.question=self.driver.find_element(By.CLASS_NAME,'topicDetail_title').text
        #回复的窗口元素
        replay_element=self.driver.find_element(By.CLASS_NAME,'textareawrap')
        replay_element=replay_element.find_element(By.TAG_NAME,'textarea')
        replay_button=self.driver.find_element(By.CSS_SELECTOR,'[class="jb_btn jb_btn_92 fr fs14 addReply"]')
        self.get_answer()
        # self.answer = '你好'
        if type(self.answer) is str:
            self.answer = ast.literal_eval(self.answer)  # 转换为列表
        if self.answer:
            replay_element.click()
            replay_element.send_keys(self.answer[0])
            replay_button.click()
        time.sleep(2)
        self.driver.close()
        turn_page(self.driver,'学生学习页面')
def finish_discussion(driver,API):
    discussion= Discussion(driver,API)
    discussion.mian()
