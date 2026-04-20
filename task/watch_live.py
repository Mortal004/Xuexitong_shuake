
from task.common import Common
from task.do_work import turn_page

class Live(Common):
    def __init__(self,driver):
        super().__init__(driver,'[src="/ananas/modules/live/index.html?v=2023-1218-1127"]',"直播")
    def start(self):
        self.iframe.click()
        turn_page(self.driver, '直播')
        print('请自行补充代码')


def watch_live(driver):
    live=Live(driver)
    live.main()
