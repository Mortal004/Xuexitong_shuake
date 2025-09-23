# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import json
import sys
import time
import traceback
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from selenium.common import NoSuchDriverException, NoSuchWindowException, WebDriverException, \
    ElementNotInteractableException, SessionNotCreatedException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from task.tool import color
from task.watch_ppt import __ppt
from task.watch_vido import study_page
# from task.quiz import get_question_date
from task.quiz_deepseek  import Answer
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
    driver.get("https:i.chaoxing.com/")
    turn_page(driver,'用户登录')
    print(color.green('正在登录中...'), flush=True)
    # 自动登录
    element = driver.find_element(By.ID, 'phone')
    element1 = driver.find_element(By.ID, 'pwd')
    element.send_keys(phone_number)  # 替换成你的手机号码
    element1.send_keys(password)  # 替换成你的密码

    # 点击登录
    login_button = driver.find_element(By.ID, 'loginBtn')
    try:
        login_button.click()
    except:
       pass
    time.sleep(3)
    # 转到页面内窗口
    #点击课程
    try:
        driver.find_element(By.CSS_SELECTOR, '[title="新泛雅"]').click()
        time.sleep(1)
    except:
        try:
            driver.find_element(By.CSS_SELECTOR,'[title="课程"]').click()
            time.sleep(1)
        except:
            pass
    try:
        time.sleep(3)
        driver.switch_to.frame('frame_content')
        try:
            # 体验最新版本
            element=driver.find_element(By.CSS_SELECTOR,'[class="experience fr"]')
            print(color.green('正在体验最新版本'), flush=True)
            element.click()
            turn_page(driver,'新泛雅')
        except:
            pass
        # 选择‘我的课程’并点击
        element=driver.find_element(By.CLASS_NAME,'course-tab')
        elements=element.find_elements(By.TAG_NAME,'div')
        for element in elements:
            if element.text== '我学的课':
                element.click()
                break
        element.click()
        time.sleep(1)
    except:
        pass

def set_speed_extension(driver,browser):
    #打开设置页面
    time.sleep(2)
    driver.get(f'{browser}://extensions/?id=mjhlabbcmjflkpjknnicihkfnmbdfced')
    if browser=='edge':
        driver.find_element(By.ID,'itemOptions').click()
        driver.refresh()  # 使用 Selenium 刷新
        time.sleep(2)
        # 获取所有标签页句柄并切换到最新标签页
        handles = driver.window_handles
        driver.switch_to.window(handles[-1])  # 假设新标签页是最后一个
        # switch_to_new_window(driver,'extension://mjhlabbcmjflkpjknnicihkfnmbdfced/options.html')
    elif browser=='chrome':
        # 等待宿主元素加载
        host_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "extensions-manager"))
        )
        # 获取 Shadow Root
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", host_element)

        host_element2=shadow_root.find_element(By.ID, "toolbar")
        # 获取 Shadow Root
        shadow_root2 = driver.execute_script("return arguments[0].shadowRoot", host_element2)

        # 定位 Shadow DOM 中的元素
        shadow_root2.find_element(By.ID,'devMode').click()
        # time.sleep(2000)
        driver.get('chrome-extension://mjhlabbcmjflkpjknnicihkfnmbdfced/options.html')
    elements=driver.find_elements(By.CLASS_NAME,'fieldValue')
    elements[len(elements)-1].click()
    element=driver.find_element(By.XPATH,'//*[@id="App"]/div[2]/div[2]/div[3]/div[1]/div[1]/div/div[5]/input')
    element.clear()
    element.send_keys('1')

def choice_course(driver, course_name,speed,condition):
    # time.sleep(200)
    """
    选择指定名称的课程

    参数:
    driver: WebDriver 对象，用于控制浏览器
    course_name: 字符串，要选择的课程名称

    返回:
    无
    """
    print(color.green(f'正在定位《{course_name}》课程...'),flush=True)
    # 查找所有课程名称元素
    course_elements = driver.find_elements(By.CLASS_NAME, 'course-name')
    if len(course_elements)==0:
        course_elements = driver.find_elements(By.CLASS_NAME, 'courseName')
    if len(course_elements)==0:
        turn_page(driver, '个人空间')
        driver.switch_to.frame('frame_content')
        course_elements = driver.find_elements(By.CSS_SELECTOR, '[class="w_cour_txtH fl"]')
    # 遍历所有课程元素
    for course_element in course_elements:
        # 如果课程元素的标题属性与指定的课程名称匹配
        if  course_name in course_element.get_attribute('title') or course_name in course_element.text:
            # 滚动到课程名称元素的位置
            driver.execute_script("arguments[0].scrollIntoView();", course_element)
            if condition:
                set_speed(speed,driver)
            # 使用 JavaScript 点击课程名称元素
            driver.execute_script("arguments[0].click();", course_element)

            # 打印选择的课程名称
            print(color.green(f'您已选择观看《{course_name}》'), flush=True)
            #体验最新版本
            try:
                turn_page(driver,course_name)
                element=driver.find_element(By.CLASS_NAME,'experience')
                time.sleep(1)
                element.click()
                print(color.green('正在体验最新版本'),flush=True)
                # 遍历所有窗口句柄
                # choice_course(driver,course_name,speed,False)
            except:
                pass

            break
    else:
        print(color.red(f"未找到《{course_name}》这门课程，请确认好课程名称后再试，"
                        "或者检查账号密码是写正确，如果没有问题，请再试一次并且横屏拍摄视频发送至作者邮箱（2022865286@qq.com)"),flush=True)
        data = []
        try:
            with open('task/tool/course_name.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            pass
        try:
            data.remove(course_name)
        except ValueError:
            pass
        with open('task/tool/course_name.json', 'w') as f:
            json.dump(data, f)
        sys.exit(1)
    turn_page(driver,course_name)

def check_face(driver):
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR,"[class='popDiv wid640 faceCollectQrPop popClass']")
            print(color.red('请按照要求手机扫码进行人脸认证'),flush=True)
            time.sleep(2)
        except:
            break

def find_mission(driver):
    try:
        # 体验最新版本
        element = driver.find_element(By.CLASS_NAME, 'experience')
        print(color.green('正在体验最新版本'), flush=True)
        element.click()
    except:
        pass
    # 点击章节标签
    elements=driver.find_elements(By.CLASS_NAME, 'nav_content')
    for element in elements:
        if element.text== '章节':
            element.click()
            break
    # 切换到名为 frame_content-zj 的 iframe
    driver.switch_to.frame("frame_content-zj")
    try:
        # 查找待完成任务点的元素
        element = driver.find_element(By.CSS_SELECTOR, '.catalog_tishi120')
    except:
        print(color.red('所有任务点均已完成'),flush=True)
        sys.exit()
        
    # 打印提示信息，表示已检测到未完成点
    print(color.magenta('已检测到未完成点'),flush=True)
    time.sleep(0.5)
    # 点击待完成任务点的元素
    element.click()

def turn_page(driver,page_name):
    time.sleep(1)
    for handle in driver.window_handles:
        # print(len(driver.window_handles))
        # 先切换到该窗口
        driver.switch_to.window(handle)
        # 得到该窗口的标题栏字符串，判断是不是我们要操作的那个窗口
        if page_name in driver.title:
            # print(driver.title)
            # 如果是，那么这时候WebDriver对象就是对应的该该窗口，正好，跳出循环，
            break
        else:
            continue

    #折叠侧边目录

def fold(driver):
    element = driver.find_element(By.XPATH, '//*[@id="selector"]/div[2]')
    element.click()
    time.sleep(1)

def set_speed(speed,driver):
    print(color.blue(f'调节倍数为：{speed}X'), flush=True)
    try:
        speed=int(speed)-1
        # body = driver.find_element(By.TAG_NAME, 'div')
        # body.click()
        for i in range(int(speed)*10):
            pyautogui.press('d')
            action=ActionChains(driver)
            action.send_keys('d').perform()
            time.sleep(0.1)
        print(color.green('调节成功'), flush=True)
    except Exception as e:
        print(color.yellow(f'调节失败{e}'), flush=True)

def page_message(driver):
    driver.switch_to.default_content()
    page_message_lst=[]
    try:
        iframe = driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
    except:
        return page_message_lst
    try:
        driver.find_element(By.CSS_SELECTOR, '[class="ans-attach-online ans-insertvideo-online"]')
        page_message_lst.append('vido')
    except:
        pass
    try:
        driver.find_element(By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-ppt"]')
        page_message_lst.append('ppt')
    except:
        try:
            driver.find_element(By.CSS_SELECTOR,'[class="ans-attach-online insertdoc-online-pdf"]')
            page_message_lst.append('ppt')
        except:
            pass
    try:
        driver.find_element(By.XPATH,'//iframe[@src="/ananas/modules/work/index.html?v=2024-1212-1629&castscreen=0"]')
        page_message_lst.append('test')
    except:
        pass
    return page_message_lst

def run(driver,choice,course_name,API,lock_screen,speed):
    while True:
        print(color.green('正在检测页面内容'), flush=True)
        page_message_lst=page_message(driver)
        if len(page_message_lst)==0:
            print(color.red('该页面无法识别'),flush=True)
        else:
            print(color.green(f'该页面含有{page_message_lst}'),flush=True)
            if 'ppt' in page_message_lst:
                __ppt(driver)
            if 'vido' in page_message_lst:
                study_page(driver,course_name,lock_screen,speed)
            if 'test' in page_message_lst:
                if choice!='不刷题':
                    driver.switch_to.default_content()
                    driver.switch_to.frame('iframe')
                    test_frames = driver.find_elements(By.XPATH,
                                                       '//iframe[@src="/ananas/modules/work/index.html?v=2024-1212-1629&castscreen=0"]')
                    print(color.magenta(f'已检测到{len(test_frames)}个测试'), flush=True)
                    for test_frame in test_frames:
                        try:
                            # if choice=='大学生搜题酱':
                            #     get_question_date(driver,course_name,test_frame)
                            if choice=='DeepSeek AI':
                                Answer(driver,test_frame,course_name,API)
                        except Exception as e:
                            error_msg = traceback.format_exc()
                            send_error(error_msg)
                            print(color.yellow('出错了，具体原因请前往错误日志查看，请自行保存或提交,15秒后继续'), flush=True)
                            time.sleep(15)
                else:
                    print(color.yellow('跳过测试题'),flush=True)
        driver.switch_to.default_content()
        print(color.green('跳转下一页'), flush=True)
        try:
            driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
        except ElementNotInteractableException:
            print(color.red('该课程全部已完结，撒花！！！'), flush=True)
            break
        # 确认
        try:
            driver.find_element(By.XPATH, '//*[@id="mainid"]/div[1]/div/div[3]/a[2]').click()
        except:
            pass
        time.sleep(1)

def main(phone_number,password,course_name,choice,speed,API,lock_screen):
    print(color.green('启动浏览器中...'), flush=True)
    with open(r'task\tool\account_info.json', 'r', encoding='utf-8') as f:
        browser_info = json.load(f)
    # 设置ChromeDriver的路径
    driver_path = browser_info['driver_path']
    browser=browser_info['browser']
    if browser=='chrome':
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
    else :
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
    # 创建Driver服务
    service = Service(driver_path)
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制提示
    options.add_extension(r"task\tool\speed.crx")
    if choice=='大学生搜题酱':
        # 可以设置Chrome启动选项（如果需要）
        try:
            options.add_extension(r"task\tool\zyb-227372.crx")
        except OSError:
            print(color.red('无法正常打开搜题插件，请检查地址是否正确，或检查版本是否与谷歌浏览器一致'),flush=True)
            return
    options.add_argument("--enable-extensions")
    options.add_argument("--disable-web-security")

    if browser=='edge':

        driver = webdriver.Edge(service=service, options=options)
    else:
        # 初始化Chrome浏览器
        driver = webdriver.Chrome(service=service, options=options)
    # driver.maximize_window()
    driver.implicitly_wait(2)
    # set_speed_extension(driver,browser)
    login_study(driver,phone_number,password)
    choice_course(driver,course_name,speed,True)
    check_face(driver)
    find_mission(driver)
    turn_page(driver,'学生学习页面')
    fold(driver)
    run(driver,choice,course_name,API,lock_screen,speed)

if __name__ == '__main__':
    try:
        with open(r'task\tool\account_info.json', 'r', encoding='utf-8') as fil:
            account_info = json.load(fil)
        try:
            main(account_info['phone_number'],account_info['password'],account_info['cour'],
                 account_info['choice'],account_info['speed'],account_info['API'],account_info['lock_screen'])
        except NoSuchWindowException as e:
            print(color.red('窗口意外关闭'),flush=True)
        except SessionNotCreatedException as e:
            error_msg = traceback.format_exc()
            send_error(
                "看报错信息自己如果无法解决,可以将错误信息发送至邮箱2022865286@qq.com (PS:赞助作者可优先解决)" + error_msg)
            print(color.red('无法正常运行驱动，请检查地址是否正确，或根据用户须知检查版本是否与浏览器一致，如果不一致，'
                            '请根据用户须知的指导前往下载相应版本的驱动，如果一致，请更换另外一个浏览器，但也要注意浏览器与驱动的版本是否一致，'
                            '如果还是不行，请重新下载脚本或关机重启。'),flush=True)
        except WebDriverException as e:
            if 'ERR_INTERNET_DISCONNECTED' in str(e) or 'ERR_NAME_NOT_RESOLVED' in str(e):
                print(color.red('你网都没连，刷个屁的课啊'),flush=True)
            else:
                print(color.red('出错了，具体原因请前往错误日志查看'),flush=True)
                error_msg = traceback.format_exc()
                send_error("看报错信息自己如果无法解决,可以将错误信息发送至邮箱2022865286@qq.com (PS:赞助作者可优先解决)"+error_msg)
        except Exception as e:
            error_msg = traceback.format_exc()
            send_error("看报错信息自己如果无法解决,可以将错误信息发送至邮箱2022865286@qq.com (PS:赞助作者可优先解决)"+error_msg)
            print(color.red('出错了，具体原因请前往错误日志查看'),flush=True)
    except FileNotFoundError:
        print(color.red('未填写信息或未保存，请前往设置页面重新设置'),flush=True)