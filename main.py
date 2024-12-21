import json
import sys
import time
import traceback

from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException, NoSuchDriverException, NoSuchWindowException, WebDriverException, \
    NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from task.tool import color
from task.watch_ppt import __ppt
from task.watch_vido import study_page
from task.tool.interface import  Answerable
from task.quiz import get_question_date
from task.tool.send_wx import send_error


def login_study(driver,phone_number,password):
    """
    使用指定的手机号和密码登录学习通网站。

    参数:
    driver: WebDriver 对象，用于控制浏览器。
    phone_number: 字符串，登录使用的手机号码。
    password: 字符串，登录使用的密码。

    返回:
    无。
    """
    # 打开网页
    driver.get("https://passport2.chaoxing.com/login?fid=&newversion=true&refer=https%3A%2F%2Fi.chaoxing.com")

    # 自动登录
    element = driver.find_element(By.ID, 'phone')
    element1 = driver.find_element(By.ID, 'pwd')
    element.send_keys(phone_number)  # 替换成你的手机号码
    element1.send_keys(password)  # 替换成你的密码

    # 点击登录
    login_button = driver.find_element(By.ID, 'loginBtn')
    login_button.click()

    time.sleep(3)
    # 转到页面内窗口
    driver.switch_to.frame('frame_content')

    # 选择‘我的课程’并点击
    element=driver.find_element(By.XPATH,'//*[@id="divbox"]/div/div/div[1]/div[2]')
    element.click()
    time.sleep(3)

def choice_course(driver, course_name):
    """
    选择指定名称的课程

    参数:
    driver: WebDriver 对象，用于控制浏览器
    course_name: 字符串，要选择的课程名称

    返回:
    无
    """
    # 查找所有课程名称元素
    course_elements = driver.find_elements(By.CLASS_NAME, 'course-name')

    # 遍历所有课程元素
    for course_element in course_elements:
        # 如果课程元素的标题属性与指定的课程名称匹配
        if course_element.get_attribute('title') == course_name:
            # 滚动到课程名称元素的位置
            driver.execute_script("arguments[0].scrollIntoView();", course_element)

            # 等待课程名称元素变为可点击状态
            try:
                WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'course-name')))
            except TimeoutException:
                print(color.red("等待课程名称元素可点击超时"))
                continue

            # 使用 JavaScript 点击课程名称元素
            driver.execute_script("arguments[0].click();", course_element)

            # 打印选择的课程名称
            print(color.green(f'您已选择观看《{course_name}》'))
            break
    else:
        print(color.red(f"未找到《 {course_name} 》这门课程，请确认好课程名称后再试"))
        data = []
        try:
            with open('course_name.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            pass
        try:
            data.remove(course_name)
        except ValueError:
            pass
        with open('course_name.json', 'w') as f:
            json.dump(data, f)
        sys.exit(1)

    # 遍历所有窗口句柄
    for handle in driver.window_handles:
        # 切换到当前窗口
        driver.switch_to.window(handle)
        # 如果当前窗口的标题包含指定的课程名称
        if course_name in driver.title:
            # 跳出循环，因为已经找到了匹配的窗口
            break

    # 点击章节标签
    driver.find_element(By.XPATH, '//*[@id="nav_4330"]/a').click()

    # 切换到名为 frame_content-zj 的 iframe
    driver.switch_to.frame("frame_content-zj")

    # 查找待完成任务点的元素
    element = driver.find_element(By.CSS_SELECTOR, '.catalog_tishi120')
    # 打印提示信息，表示已检测到未完成点
    print(color.magenta('已检测到未完成点'))

    # 点击待完成任务点的元素
    element.click()

def turn_page(driver):
    for handle in driver.window_handles:
        # 先切换到该窗口
        driver.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if '学生学习页面' in driver.title:
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，正好，跳出循环，
            break

    #折叠侧边目录

def fold(driver):
    element = driver.find_element(By.XPATH, '//*[@id="selector"]/div[2]')
    element.click()
    time.sleep(2)

def judge(driver):
    # time.sleep(3)
    print(color.green('正在检测页面内容'))
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame('iframe')
        try:
            element = driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
        except:
            element = driver.find_element(By.XPATH, '//*[@id="ext-gen1050"]/iframe')
        driver.switch_to.frame(element)
    except:
        print(color.green('该页面无法识别'))
        return 'Other'
    try:
        # driver.switch_to.frame('frame_content')
        driver.find_element(By.ID, 'reader')
        print(color.green('该页面为视频'))
        return 'Vido'
    except:
        try:
            driver.find_element(By.ID,'frame_content')
            print(color.green('该页面为测验'))
            return 'Test'
        except:
            try:
                driver.find_element(By.ID,'panView')
                print(color.green('该页面为PPT'))
                return 'PPT'
            except:
                print(color.red('该页面无法识别'))
                return 'Other'

def find_vido(driver,page_message_lst):
    try:
        driver.find_element(By.ID, 'reader')
        # print(color.magenta('该页面包含视频'))
        page_message_lst.append('Vido')
        return True
    except:
        return False

def find_test(driver,page_message_lst):
    try:
        driver.find_element(By.ID,'frame_content')
        # print(color.magenta('该页面包含测验'))
        page_message_lst.append('Test')
        return True
    except:
        return False

def find_ppt(driver,page_message_lst):
    try:
        driver.find_element(By.ID,'panView')
        # print(color.magenta('该页面包含PPT'))
        page_message_lst.append('PPT')
        return True
    except:
        return False

def page_message(driver,page_message_lst):
    print(color.green('正在检测页面内容'))
    driver.switch_to.default_content()
    driver.switch_to.frame('iframe')
    try:
        element= driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
    except:
        element= driver.find_element(By.XPATH, '//*[@id="ext-gen1050"]/iframe')
    driver.switch_to.frame(element)
    find_vido(driver, page_message_lst)
    find_test(driver, page_message_lst)
    find_ppt (driver, page_message_lst)

def run(driver,choice,course_name):
    while True:
        page_message_lst=[]
        page_message(driver,page_message_lst)
        print(color.green(f'该页面包含{page_message_lst}'))
        if 'Vido' in page_message_lst:
            study_page(driver,course_name)
        elif 'PPT' in page_message_lst:
            __ppt(driver)
        elif 'Test' in page_message_lst:
            if choice == '否':
                print(color.yellow('跳过测试题'))
            # 做题
            else:
                print(color.green('开始做题'))
                try:
                    get_question_date(driver,course_name)
                except Exception as e:
                    error_msg = traceback.format_exc()
                    send_error(error_msg)
                    print(color.red('出错了，请自行保存或提交'))
                    time.sleep(100)
                    turn_page(driver)
        else:
            print(color.yellow('该页面无法识别'))

        driver.switch_to.default_content()
        try:
            driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
        except:
            print(color.red('该课程全部已完结，撒花！！！'))
            break
        # 确认
        try:
            driver.find_element(By.XPATH, '//*[@id="mainid"]/div[1]/div/div[3]/a[2]').click()
        except:
            pass
        time.sleep(3)

def run1(driver,choice,course_name):
    while True:
        content=judge(driver)
        if content=='Vido':
                #播放视频
                study_page(driver,course_name)

        elif content=='Test':
            if choice=='是':
                print(color.green('开始做题'))
                try:
                    get_question_date(driver,course_name)
                except Exception as e:
                    error_msg = traceback.format_exc()
                    send_error(error_msg)
                    print(color.yellow('出错了，请自行保存或提交'))
                    time.sleep(100)
                    turn_page(driver)
            # 做题
            elif choice=='否':
                print(color.yellow('跳过测试题'))

        elif content=='PPT':
            # 播放PPT
            __ppt(driver)

        elif content=='Other':
            pass

        driver.switch_to.default_content()
        try:
            driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
        except ElementNotInteractableException:
            print(color.red('该课程全部已完结，撒花！！！'))
            break
        # 确认
        try:
            driver.find_element(By.XPATH, '//*[@id="mainid"]/div[1]/div/div[3]/a[2]').click()
        except:
            pass
        time.sleep(1)

def edge():#记得修改导入
    # 设置 Edge 选项
    options = Options()
    options.add_argument(r"C:\Users\HUAWEI\Downloads\zyb-227372.crx")  # 指定用户资料目录
    # 初始化 Edge WebDriver
    driver = webdriver.Edge(service=Service(r"D:\Download\edgedriver_win64\msedgedriver.exe"),options=options)

def main(phone_number,password,course_name,choice):
    with open('account_info.json', 'r', encoding='utf-8') as f:
        chrome_info = json.load(f)
# 设置ChromeDriver的路径
    driver_path = chrome_info['driver_path']
    # 创建ChromeDriver服务
    service = Service(driver_path)
    if choice=='是':
        # 可以设置Chrome启动选项（如果需要）
        options = Options()
        try:
            options.add_extension(chrome_info['extension_path'])
        except OSError:
            print(color.red('无法正常打开搜题插件，请检查地址是否正确，或检查版本是否与谷歌浏览器一致'))
            return
            # 初始化Chrome浏览器
        driver = webdriver.Chrome(service=service,options=options)
    else:
        driver = webdriver.Chrome(service=service)
    # driver.maximize_window()
    driver.implicitly_wait(2)
    __questionList: list[Answerable] = []
    if choice=='是':
        print(color.red('请扫码（20秒）'))
        time.sleep(2)  # 跳转到选择课程页面
    login_study(driver,phone_number,password)
    # #选课
    choice_course(driver,course_name)
    turn_page(driver)
    fold(driver)
    run1(driver,choice,course_name)

if __name__ == '__main__':
    try:
        with open('account_info.json', 'r', encoding='utf-8') as fil:
            account_info = json.load(fil)
            try:
                main(account_info['phone_number'],account_info['password'],account_info['cour'],account_info['choice'])
            except NoSuchWindowException as e:
                print(color.red('窗口意外关闭'))
            except NoSuchElementException as e:
                print(color.red('未找到未完成的任务点'))
            except NoSuchDriverException as e:
                print(color.red('无法正常打开谷歌驱动，请检查地址是否正确，或检查版本是否与谷歌浏览器一致'))
            except WebDriverException as e:
                if 'ERR_INTERNET_DISCONNECTED' in str(e):
                    print(color.red('你网都没连，刷个屁的课啊'))
                else:
                    print(color.red('出错了，具体原因请前往错误日志查看'))
                    error_msg = traceback.format_exc()
                    send_error(error_msg)
            except Exception as e:
                error_msg = traceback.format_exc()
                send_error(error_msg)
                print(color.red('出错了，具体原因请前往错误日志查看'))
    except FileNotFoundError:
        print(color.red('未填写信息或未保存，请前往设置页面重新设置'))