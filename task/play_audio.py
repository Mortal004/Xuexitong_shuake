# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
import time
from selenium.webdriver.common.by import By
from task.tool.common import Common
class Audio(Common):
    def __init__(self,driver,iframe_element):
        super().__init__(driver,iframe_element,'音频')
    def start(self):
        self.driver.switch_to.frame(self.iframe)
        play_button = self.driver.find_element(By.CSS_SELECTOR, '[class="vjs-play-control vjs-control vjs-button"]')
        play_button.click()
        vjs_duration = self.driver.find_element(By.CLASS_NAME, "vjs-duration-display")
        print('当前音频时长为{}'.format(vjs_duration.text),flush=True)
        #计算要点击快进十秒的次数，并只取整数部分
        # 例如：时长为1:30，点击快进十秒的次数为13次
        fast_forward_num = int(vjs_duration.text.split(':')[0]+vjs_duration.text.split(':')[1]) // 10
        vjs_fast_forward_button = self.driver.find_element(By.ID, "vjs-fast-forward-button")
        for i in range(fast_forward_num):
            vjs_fast_forward_button.click()
            time.sleep(0.1)
        # 检测是否完成播放
        while True:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
            if self.check_audio_finished():
                break
            time.sleep(1)
def play_audio(driver,iframe_element):
    audio = Audio(driver,iframe_element)
    audio.main()

