import time
from selenium.webdriver.common.by import By

from task.tool.common import Common,turn_page

class Live(Common):
    def __init__(self,driver,live_url,course_name):
        super().__init__(driver,live_url,"直播",course_name)
    def start(self):
        """这里有两种直播形式
            一种带iframe的，一种不带"""
        self.iframe.click()
        turn_page(self.driver, '直播')
        # time.sleep(1000)
        #点击播放
        try:
            live_iframe = self.driver.find_element(By.ID, "middleFrame")
            self.driver.switch_to.frame(live_iframe)
            self.driver.find_element(By.CLASS_NAME, "vjs-big-play-button").click()
        except:
            pass
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
        # print('直播时长的90%:',duration_00*0.9,flush=True)
        time.sleep(duration_00)
        self.driver.close()
        turn_page(self.driver, '学生学习页面')


def watch_live(driver,live_url,course_name):
    live=Live(driver,live_url,course_name)
    live.main()
