from selenium.webdriver.common.by import By
from task.tool import color

class Common:
    def __init__(self,driver,iframe_element,type):
        self.type=type
        self.driver=driver
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
        self.iframes = self.driver.find_elements(By.CSS_SELECTOR,iframe_element)
        live_num = len(self.iframes)
        print(color.green(f'{self.type}数量：{live_num}'))

    def check_audio_finished(self):
        # 检查任务点是否已完成
        # 定位到该元素的上一级（父元素）
        parent_element = self.iframe.find_element(By.XPATH, "..")
        # 获取 parent_element 的class值
        parent_element_class = parent_element.get_attribute("class")
        if parent_element_class == 'ans-attach-ct ans-job-finished':
            print(color.green(f"该{self.type}已完成"), flush=True)
            return True
        else:
            # print(color.green("该音频未完成"), flush=True)
            return False

    def check_exist_mission(self):
        try:
            # 定位到该元素的前一个兄弟元素
            self.iframe.find_element(By.XPATH, "preceding-sibling::div[1]")
            print(color.green(f"该{self.type}存在任务点"), flush=True)
            return True
        except:
            print(color.green(f"该{self.type}不存在任务点"), flush=True)
            return False
    def mian(self):
        num=0
        for iframe in self.iframes:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(self.driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
            self.iframe = iframe
            # 检测是否存在任务点
            if not self.check_exist_mission():
                continue
            # 检查任务点是否已完成
            if self.check_audio_finished():
                continue
            # 滚动到
            self.driver.execute_script("arguments[0].scrollIntoView();", self.iframe)
            print(color.green(f'开始第{num + 1}个{self.type}'), flush=True)
            self.start()
            print(color.green(f'第{num + 1}个{self.type}已完成'), flush=True)
            num+=1
    def start(self):
        pass
