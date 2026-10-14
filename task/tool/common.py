from selenium.webdriver.common.by import By
from task.tool import color
import time
import ast
import json

class Common:
    def __init__(self,driver,iframe_element,type,course_name):
        self.course_name = course_name
        self.type=type
        self.driver=driver
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame("iframe")
        self.iframes = self.driver.find_elements(By.CSS_SELECTOR,iframe_element)
        num = len(self.iframes)
        print(color.green(f'{self.type}数量：{num}'),flush=True)

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
        # 定位到该元素的所有兄弟元素
        all_elements = self.iframe.find_elements(By.XPATH,  "preceding-sibling::* | following-sibling::*")
        for element in all_elements:
            class_attr = element.get_attribute("class") or ""
            if 'ans-job-icon ' in class_attr:
                print(color.green(f"该{self.type}存在任务点"), flush=True)
                return True
        print(color.green(f"该{self.type}不存在任务点"), flush=True)
        return False
    def main(self):
        num=0
        for iframe in self.iframes:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame("iframe")
            self.iframe = iframe
            num+=1

            # 检测是否存在任务点
            if not self.check_exist_mission():
                continue
            # 检查任务点是否已完成
            if self.check_audio_finished():
                continue
            # 滚动到
            self.driver.execute_script("arguments[0].scrollIntoView();", self.iframe.find_element(By.XPATH, "preceding-sibling::div[1]"))
            print(color.green(f'开始第{num}个{self.type}'), flush=True)
            self.start()
            print(color.green(f'第{num}个{self.type}已完成'), flush=True)
            save_record(self.driver, self.course_name, time, iframe, self.type)
    def start(self):
        pass

def turn_page(driver,page_name):
    #获取当前所有窗口的名称
    try:
        current_window_handle = driver.title
        if page_name in current_window_handle:
            return 'True'
    except:
        pass
    # 遍历所有窗口句柄
    for handle in driver.window_handles:
        # 先切换到该窗口
        driver.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if page_name in driver.title:
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，正好，跳出循环，
            return True
    return False
def save_record(driver, course_name, time, iframe, typ):
    save_process(course_name)
    if typ!='测验':
        try:
            driver.switch_to.default_content()
            element = driver.find_element(By.CLASS_NAME, 'prev_title')
            title = element.get_attribute('title')
            driver.switch_to.frame(driver.find_element(By.CSS_SELECTOR, '[id="iframe"]'))
            name = json.loads(iframe.get_attribute("data")).get('name',
                    json.loads(iframe.get_attribute("data")).get('title',
                    json.loads(iframe.get_attribute("data")).get('bookname', '')))
            with open(fr'task\record\《{course_name}》的刷课记录.txt', 'a', encoding='utf-8') as f:
                f.write(
                    f'已刷完:《{title}》章节中的{typ}:<{name}>，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n\n')
            print(color.green('已保存进度'), flush=True)
        except:
            print(color.red('保存进度失败'), flush=True)
def save_process(course_name,done=0,total=0):
    with open('task/tool/course_process.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        num_list=data.get(course_name,'')
        if num_list!='' and done==0:
            data[course_name]=[num_list[0]+1,num_list[1]]
        elif total!=0:
            data[course_name]=[done,total]
            print(color.green(f'已保存进度：{done}/{total}'), flush=True)
        with open('task/tool/course_process.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

