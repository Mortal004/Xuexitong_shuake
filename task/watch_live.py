import time
from selenium.webdriver.common.by import By

from task.tool.common import Common
from task.do_work import turn_page

class Live(Common):
    def __init__(self,driver):
        super().__init__(driver,'[src="/ananas/modules/live/index.html?v=2023-1218-1127"]',"直播")
    def start(self):
        self.iframe.click()
        turn_page(self.driver, '直播')
        # time.sleep(1000)
        #获取时长
        while True:
            duration=self.driver.find_element(By.CSS_SELECTOR, '[class="vjs-remaining-time-display"]').text
            if duration=='-0:00' or duration=='0':
                time.sleep(1)
            else:
                break
        #删除-
        duration=duration.replace('-','')
        print('直播时长:',duration,flush=True)
        #静音
        self.driver.find_element(By.CLASS_NAME, "vjs-mute-control").click()
        #计算直播时长的90%
        duration_00=int(duration.split(':')[-1])*60+int(duration.split(':')[0])
        time.sleep(duration_00)
        self.driver.close()
        turn_page(self.driver, '学生学习页面')


def watch_live(driver):
    live=Live(driver)
    live.main()
