# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

#打包python -m PyInstaller --onefile --collect-all selenium main.py
import json
import pickle
import re
import sys
import time
import traceback
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from selenium.common import NoSuchDriverException, NoSuchWindowException, WebDriverException, \
    ElementNotInteractableException, SessionNotCreatedException,NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from task.tool import color
from task.watch_ppt import __ppt
from task.watch_vido import study_page,check_face
from task.quiz_ai import Answer
from task.tool.send_wx import send_error
from task.do_work import do_work

def get_cookie(driver):
    try:
        pickle.dump(driver.get_cookies(), open(r'task/tool/cookies.pkl', 'wb'))
        return True
    except PermissionError:
        print(color.red('请在关闭该窗口后，再右键点击刷课程序用管理员权限打开'))
        return False
    except Exception :
        print(color.red(f'获取cookie失败'),flush=True)
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n" + error_msg)
        return True


def auto_login_with_cookies(driver):
    if not driver.title=='用户登录':
        return True
    try:
        # 清除可能存在的旧cookie
        driver.delete_all_cookies()
        try:
            cookies = pickle.load(open(r'task/tool/cookies.pkl', 'rb'))
        except:
            return False
        # 逐个添加cookie
        for cookie in cookies:
            try:
                # 移除可能引起问题的属性
                cookie_to_add = cookie.copy()

                # Selenium的add_cookie方法不支持'sameSite'参数，需要移除
                if 'sameSite' in cookie_to_add:
                    del cookie_to_add['sameSite']

                # 确保domain格式正确
                if cookie_to_add['domain'].startswith('.'):
                    # 对于以点开头的domain，确保浏览器在当前域的正确上下文中
                    pass

                driver.add_cookie(cookie_to_add)
                # print(color.green(f"成功添加cookie: {cookie['name']}"),flush=True)

            except Exception as e:
                pass
                # print(color.red(f"添加cookie {cookie['name']} 时出错: {e}"),flush=True)

        # 刷新页面使cookie生效
        driver.refresh()

        # 等待页面加载
        time.sleep(3)
        #  访问需要登录的页面测试
        test_url = "https://i.chaoxing.com"  # 个人中心页面
        driver.get(test_url)
        # 验证登录是否成功
        if driver.title!='用户登录':
            print(color.green("自动登录验证成功！"),flush=True)
            return True
        else:
            print(color.red("登录可能已过期"),flush=True)
            return False

    except Exception as e:
        print(color.red(f"自动登录过程中出错"),flush=True)
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n" + error_msg)
        return False

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
    time.sleep(1)
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
    if not auto_login_with_cookies(driver):
        print(color.red('登陆失败，请打开手机端学习通，扫码登录'), flush=True)
        while driver.title=='用户登录':
            time.sleep(1)
    if get_cookie(driver):
        print(color.green('登录成功'), flush=True)
    else:
        return
    # 转到页面内窗口
    #点击课程
    try:
        driver.find_element(By.CSS_SELECTOR, '[title="新泛雅"]').click()
        time.sleep(1)
    except:
        try:
            driver.find_element(By.CSS_SELECTOR, '[title*="课程"]').click()
            time.sleep(1)
        except NoSuchElementException:
            try:
                driver.find_element(By.CSS_SELECTOR, '[title*="首页"]').click()
                time.sleep(1)
            except:
                pass
    try:
        time.sleep(3)
        driver.switch_to.frame('frame_content')

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

def save_course_lst(driver,class_name,course_elements,phone_number):
    have_task_course_element=driver.find_element(By.ID,'stuNormalCourseListDiv')
    new_course_elements=have_task_course_element.find_elements(By.CLASS_NAME,class_name)
    if len(course_elements)==0:
        new_course_elements=course_elements
    course_list = [course_element.get_attribute('title') for course_element in new_course_elements if
                   course_element.get_attribute('title')!= '']
    if len(course_list) == 0:
        print(color.red(f'获取课程列表失败'), flush=True)
    else:
        try:
            with open(r'task/tool/course_name.json', 'r', encoding='utf-8') as f:
                dit = json.load(f)
            with open(r'task/tool/course_name.json', 'w', encoding='utf-8') as f:
                new_list = dit.get(phone_number,[]) + course_list
                # 去重
                new_list = list(set(new_list))
                dit[phone_number]= new_list
                json.dump(dit, f)
            print(color.green(f'保存课程列表成功,共有{len(new_list)}个课程'), flush=True)
        except:
            print(color.red('保存课程列表失败'), flush=True)


def choice_course(driver, course_name,speed,condition,task_type,phone_number):
    # time.sleep(200)
    """
    选择指定名称的课程

    参数:
    driver: WebDriver 对象，用于控制浏览器
    course_name: 字符串，要选择的课程名称

    返回:
    无
    """
    try:
        print(color.green(f'正在定位《{course_name}》...'),flush=True)
        # 查找所有课程名称元素
        course_elements = driver.find_elements(By.CLASS_NAME, 'course-name')
        class_name="course-name"
        if len(course_elements)==0:
            course_elements = driver.find_elements(By.CLASS_NAME, 'courseName')
            class_name="courseName"
        if len(course_elements)==0:
            # turn_page(driver, '个人空间')
            driver.switch_to.frame('frame_content')
            course_elements = driver.find_elements(By.CSS_SELECTOR, '[class="w_cour_txtH fl"]')
            class_name="w_cour_txtH fl"
        save_course_lst(driver,class_name,course_elements,phone_number)
        # 遍历所有课程元素
        for course_element in course_elements:
            # 如果课程元素的标题属性与指定的课程名称匹配
            if  course_name in course_element.get_attribute('title') or course_name in course_element.text:
                # 滚动到课程名称元素的位置
                driver.execute_script("arguments[0].scrollIntoView();", course_element)
                if condition:
                    set_speed(speed,driver,task_type)
                # 使用 JavaScript 点击课程名称元素
                driver.execute_script("arguments[0].click();", course_element)

                # 打印选择的课程名称
                print(color.green(f'您已选择《{course_name}》'), flush=True)
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
            # 体验最新版本
            element=driver.find_element(By.CSS_SELECTOR,".experience")
            print(color.green('正在体验最新版本'), flush=True)
            element.click()
            turn_page(driver,'新泛雅')
            element=driver.find_elements(By.XPATH,'//*[@id="stukc"]/div[1]/div[1]/div/a')
            time.sleep(2)
            if len(element)!=0:
                element[0].click()
                driver.find_element(By.XPATH,'//*[@id="stukc"]/div[1]/div[1]/div/div/ul/li[1]').click()
            choice_course(driver,course_name,speed,condition,task_type,phone_number)
        turn_page(driver,course_name)
    except :

        print(color.red(f"未找到《{course_name}》这门课程，请检查名称是否正确，或手动选择你要刷课的课程，打开该课程后等待片刻"),
              flush=True)
        now_window_handles=len(driver.window_handles)
        while len(driver.window_handles)==now_window_handles:
            time.sleep(1)
        time.sleep(2)
        turn_page(driver, course_name)
        set_speed(speed, driver,task_type)
        return

    turn_page(driver,course_name)

def find_mission(driver,task_type):
    try:
        # 体验最新版本
        element = driver.find_element(By.CLASS_NAME, 'experience')
        print(color.green('正在体验最新版本'), flush=True)
        element.click()
    except:
        pass
    #点击开始学习
    try:
        element=driver.find_element(By.CSS_SELECTOR,'[CLASS="start-study readclosecoursepop"]')
        element.click()
    except:
        pass
    # 点击章节/作业标签
    elements=driver.find_elements(By.CLASS_NAME, 'nav_content')
    for element in elements:
        if element.text== task_type:
            element.click()
            break


    driver.switch_to.frame(driver.find_element(By.TAG_NAME,'iframe'))
    # 切换到名为 frame_content-zj 的 iframe
    if task_type == '作业':
        return
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
    try:
        element = driver.find_element(By.XPATH, '//*[@id="selector"]/div[2]')
        element.click()
        time.sleep(1)
    except:
        pass

def set_speed(speed,driver,task_type):
    if task_type == '作业':
        return
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
    driver.implicitly_wait(0)
    try:
        iframe = driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)
    except:
        return page_message_lst
    try:
        driver.find_element(By.CSS_SELECTOR, '[class="ans-attach-online ans-insertvideo-online"]')
        page_message_lst.append('视频')
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
        driver.find_element(By.XPATH,'//iframe[@src="/ananas/modules/work/index.html?v=2025-1028-1629&castscreen=0"]')
        page_message_lst.append('测验')
    except:
        pass
    driver.implicitly_wait(2)
    return page_message_lst

def run(driver,choice,course_name,API,lock_screen):
    while True:
        print(color.green('正在检测页面内容'), flush=True)
        page_message_lst=page_message(driver)
        if len(page_message_lst)==0:
            print(color.red('该页面无法识别'),flush=True)
        else:
            print(color.green(f'该页面含有{page_message_lst}'),flush=True)
            if 'ppt' in page_message_lst:
                __ppt(driver)
            if '视频' in page_message_lst:
                study_page(driver,course_name,lock_screen)
            if '测验' in page_message_lst:
                if choice!='不刷题':
                    driver.switch_to.default_content()
                    driver.switch_to.frame('iframe')
                    test_frames = driver.find_elements(By.XPATH,
                                                       '//iframe[@src="/ananas/modules/work/index.html?v=2025-1028-1629&castscreen=0"]')
                    print(color.magenta(f'已检测到{len(test_frames)}个测试'), flush=True)
                    for test_frame in test_frames:
                        try:
                            Answer(driver,test_frame,course_name,API,choice)
                        except :
                            error_msg = traceback.format_exc()
                            send_error("\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n"+error_msg)
                            print(color.yellow('❌ 出错了，具体原因请前往错误日志查看，请自行保存或提交,15秒后继续'), flush=True)
                            time.sleep(15)
                else:
                    print(color.yellow('您已选择不刷题，即将跳过测试题'),flush=True)
        driver.switch_to.default_content()
        print(color.green('跳转下一页'), flush=True)
        try:
            driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
        except ElementNotInteractableException:
            print(color.red('🎉 🎉 该课程全部已完结，撒花！！！'), flush=True)
            break
        # 确认
        try:
            driver.find_element(By.XPATH, '//*[@id="mainid"]/div[1]/div/div[3]/a[2]').click()
        except:
            pass
        time.sleep(1)

def start_browser(browser,driver_path):
    print(color.green('启动浏览器中...'), flush=True)
    if browser == 'chrome':
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
    else:
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
    # 创建Driver服务
    service = Service(driver_path)
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制提示
    options.add_extension(r"task\tool\speed.crx")
    options.add_argument("--enable-extensions")
    options.add_argument("--disable-web-security")

    if browser == 'chrome':
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # 初始化Chrome浏览器
        driver = webdriver.Edge(service=service, options=options)
        # 4. 执行JavaScript修改环境

    # driver.maximize_window()
    driver.implicitly_wait(2)
    return driver


def main(browser, driver_path, phone_number, password, choice, course_name, API, lock_screen,speed, task_type,homework):
    driver = start_browser(browser, driver_path)
    # set_speed_extension(driver,browser)
    login_study(driver, phone_number, password)
    choice_course(driver, course_name, speed, True, task_type,phone_number)
    time.sleep(1)
    check_face(driver)
    find_mission(driver,task_type)
    if task_type=='作业':
        do_work(driver,course_name,homework,API)
        return
    check_face(driver)
    turn_page(driver, '学生学习页面')
    check_face(driver)
    fold(driver)
    run(driver, choice, course_name, API, lock_screen)


def set_speed_extension(driver, browser):
    # 打开设置页面
    time.sleep(2)
    driver.get(f'{browser}://extensions/?id=mjhlabbcmjflkpjknnicihkfnmbdfced')
    if browser == 'edge':
        driver.find_element(By.ID, 'itemOptions').click()
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


def extract_browser_versions(error_text):
    """从错误信息中提取浏览器和驱动版本"""

    versions = {
        'driver_supported_version': None,  # 驱动支持的版本
        'browser_version': None,  # 浏览器当前版本
        'browser_type': None  # 浏览器类型
    }

    # 模式1: 匹配ChromeDriver/EdgeDriver支持的版本
    # 兼容两种格式:
    # 1. This version of ChromeDriver only supports Chrome version 140
    # 2. This version of EdgeDriver only supports Microsoft Edge version 120
    driver_pattern = r'This version of (ChromeDriver|Microsoft Edge WebDriver) only supports (?:Chrome|Microsoft Edge) version (\d+)'
    driver_match = re.search(driver_pattern, error_text)

    if driver_match:
        versions['browser_type'] = driver_match.group(1).replace('Driver', '')
        versions['driver_supported_version'] = driver_match.group(2)

    # 模式2: 匹配当前浏览器版本
    # 兼容多种格式:
    # 1. Current browser version is 143.0.7499.193
    # 2. Current Microsoft Edge version is 120.0.2210.91
    browser_pattern = r'Current (?:browser|Microsoft Edge) version is ([\d.]+)'
    browser_match = re.search(browser_pattern, error_text)

    if browser_match:
        versions['browser_version'] = browser_match.group(1)

    return versions


def parse_versions_from_text(error_text):
    """从文本中解析版本信息的完整函数"""

    # 提取版本信息
    versions = extract_browser_versions(error_text)

    # 打印结果
    print(color.red("=" * 50))
    print("版本信息分析结果:")
    print("=" * 50)

    if versions['browser_type']:
        print(f"浏览器类型: {versions['browser_type']}")

    if versions['driver_supported_version']:
        print(f"驱动支持版本: {versions['driver_supported_version']}")

    if versions['browser_version']:
        print(f"浏览器当前版本: {versions['browser_version']}")

    # 给出建议
    print("\n" + "=" * 50)
    print("问题诊断和建议:")
    print("=" * 50)

    if versions['browser_type'] and versions['driver_supported_version'] and versions['browser_version']:
        driver_ver = int(versions['driver_supported_version'])
        browser_main_ver = int(versions['browser_version'].split('.')[0])

        if browser_main_ver > driver_ver:
            print(f"❌ 版本不兼容: {versions['browser_type']}浏览器版本(v{browser_main_ver})过高，"
                  f"但驱动仅支持到v{driver_ver}")
            print(f"📋 解决方案:")
            print(f"  1. 下载{versions['browser_type']}Driver {browser_main_ver}的版本")
            print(f"  2. 或降级{versions['browser_type']}浏览器到{driver_ver}版本")
        elif browser_main_ver < driver_ver:
            print(f"⚠️  浏览器版本(v{browser_main_ver})可能过旧")
            print(f"📋 建议: 更新{versions['browser_type']}浏览器到最新版本")
        else:
            print(f"✅ 版本匹配: {versions['browser_type']}浏览器和驱动版本一致")

    print("\n相关下载链接:")
    if versions['browser_type'] == 'Chrome':
        print("  • 谷歌驱动: https://chromedriver.chromium.org/")
        print("  • Chrome浏览器: https://www.google.com/chrome/")
    elif versions['browser_type'] == 'Microsoft Edge Web':
        print("  • Edge驱动: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
        print("  • Edge浏览器: https://www.microsoft.com/edge")
    print('\n具体操作步骤见用户须知')

    return versions

def run_main():
    try:
        with open(r'task/tool/account_info.json', 'r', encoding='utf-8') as fil:
            account_info = json.load(fil)
        main(account_info['browser'], account_info['driver_path'], account_info['phone_number'], account_info['password'],account_info['choice'],
            account_info['cour'],account_info['API'],account_info['lock_screen'],account_info['speed'],account_info['task_type'],account_info['homework'])
    except NoSuchWindowException as e:
        print(color.red('❌ 窗口意外关闭'),flush=True)
    except SessionNotCreatedException as e:
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n" + error_msg)
        # 执行分析
        result = parse_versions_from_text(error_msg)

    except WebDriverException as e:
        if 'ERR_INTERNET_DISCONNECTED' in str(e) or 'ERR_NAME_NOT_RESOLVED' in str(e):
            print(color.red('❌ 你网都没连，刷个屁的课啊'),flush=True)
        else:
            print(color.red('❌ 出错了，具体原因请前往错误日志查看'),flush=True)
            error_msg = traceback.format_exc()
            send_error("\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n"+error_msg)
    except PermissionError:
        print(color.red('请关闭该窗口后，再右键点击刷课程序用管理员权限打开'))
    except Exception as e:
        error_msg = traceback.format_exc()
        send_error("\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行查看用户须知文件自行解决\n"+error_msg)
        print(color.red('❌ 出错了，具体原因请前往错误日志查看'),flush=True)

if __name__ == '__main__':
    run_main()
