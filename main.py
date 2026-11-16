# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

#打包python -m PyInstaller --onefile --collect-all selenium main.py
import json
import re
import pickle
import time
import traceback
import pyautogui
from selenium.common import NoSuchDriverException, NoSuchWindowException, WebDriverException, \
    ElementNotInteractableException, SessionNotCreatedException, NoSuchElementException, \
    ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium import webdriver

from task.finish_vote import finish_vote
from task.tool.common import save_process
from core.config_manager import ConfigManager
from task.tool.face import get_cookie,auto_login_with_cookies,delete_face_popup
from task.finish_dicussion import finish_discussion
from task.play_audio import play_audio
from task.tool import color
from task.watch_live import watch_live
from task.watch_ppt import __ppt
from task.watch_vido import study_page
from task.quiz_ai import  finish_quiz
from task.tool.send_wx import send_error
from task.tool import mailer
from task.do_work import do_work
from task.reading import reading
from task.tool.disable_monitor import DisableMonitor
condition=True#用于判断是否调节倍数
error_num=0#错误次数
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
    time.sleep(1)
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


def save_course_lst(driver,class_name,course_elements,phone_number):
    try:
        have_task_course_element=driver.find_element(By.ID,'stuNormalCourseListDiv')
    except:
        have_task_course_element=driver
    try:
        new_course_elements=have_task_course_element.find_elements(By.CSS_SELECTOR, f'[class*="{class_name}"]')
        if len(new_course_elements)!=0:
            course_elements=new_course_elements
        course_list = [course_element.get_attribute('title') for course_element in course_elements if
                       course_element.get_attribute('title')!= '']
        if len(course_list)==0:
            course_list=[course_element.text for course_element in new_course_elements if
                       course_element.text!= '']
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
                    dit[phone_number]=new_list
                    json.dump(dit, f, ensure_ascii=False, indent=2)
                print(color.green(f'保存课程列表成功,共有{len(new_list)}个课程'), flush=True)
            except:
                print(color.red('保存课程列表失败'), flush=True)
    except:
        print(color.red('保存课程列表失败'), flush=True)

def experience(driver):
    # 体验最新版本
    try:
        element = driver.find_element(By.CLASS_NAME, 'experience')
        time.sleep(1)
        element.click()
        print(color.green('正在体验最新版本'), flush=True)
    except NoSuchElementException:
        pass

def choice_course(driver, course_name,speed,task_type,phone_number):
    # time.sleep(200)
    """
    选择指定名称的课程

    参数:
    driver: WebDriver 对象，用于控制浏览器
    course_name: 字符串，要选择的课程名称

    返回:
    无
    """
    # 点击课程
    try:
        driver.find_element(By.CSS_SELECTOR, '[title="新泛雅"]').click()
        time.sleep(1)
    except:
        try:
            element = driver.find_element(By.CSS_SELECTOR, '[title*="课程"]')
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)  # 稍等滚动动画完成
            element.click()
            time.sleep(1)
        except NoSuchElementException and ElementNotInteractableException:
            try:
                driver.find_element(By.CSS_SELECTOR, '[title*="首页"]').click()
                time.sleep(1)
            except:
                pass
    try:
        time.sleep(3)
        driver.switch_to.frame('frame_content')

        # 选择‘我的课程’并点击
        element = driver.find_element(By.CLASS_NAME, 'course-tab')
        elements = element.find_elements(By.TAG_NAME, 'div')
        for element in elements:
            if element.text == '我学的课':
                element.click()
                break
        element.click()
        time.sleep(1)
    except:
        pass
    try:
        print(color.green(f'正在定位《{course_name}》...'),flush=True)
        # experience(driver)
        # turn_page(driver,'课程')
        # 查找所有课程名称元素
        course_elements = driver.find_elements(By.CLASS_NAME, "course-name")
        class_name = "course-name"
        if len(course_elements) == 0:
            course_elements = driver.find_elements(By.CLASS_NAME, 'courseName')
            class_name = "courseName"
        if len(course_elements) == 0:
            # turn_page(driver, '个人空间')
            # driver.switch_to.frame('frame_content')
            course_elements = driver.find_elements(By.CSS_SELECTOR, '[class="w_cour_txtH fl"]')
            class_name="w_cour_txtH fl"
        save_course_lst(driver,class_name,course_elements,phone_number)
        # 遍历所有课程元素
        for course_element in course_elements:
            # 如果课程元素的标题属性与指定的课程名称匹配
            if  course_name in course_element.get_attribute('title') or course_name in course_element.text:
                # 滚动到课程名称元素的位置
                driver.execute_script("arguments[0].scrollIntoView();", course_element)
                if task_type!='作业':
                    set_speed(speed, driver)
                # 使用 JavaScript 点击课程名称元素
                driver.execute_script("arguments[0].click();", course_element)
                # 打印选择的课程名称
                print(color.green(f'您已选择《{course_name}》'), flush=True)
                break
        else:
            # 体验最新版本
            driver.execute_script("arguments[0].click();",driver.find_element(By.CSS_SELECTOR, ".experience"))
            print(color.green('正在体验最新版本'), flush=True)
            if not turn_page(driver,'新泛雅'):
                turn_page(driver,'课程')
            element=driver.find_elements(By.XPATH,'//*[@id="stukc"]/div[1]/div[1]/div/a')
            time.sleep(2)
            if len(element)!=0:
                element[0].click()
                driver.find_element(By.XPATH,'//*[experience@id="stukc"]/div[1]/div[1]/div/div/ul/li[1]').click()
            choice_course(driver,course_name,speed,task_type,phone_number)
    except Exception as r:
        #继续教育
        print(color.red(f"未找到《{course_name}》这门课程，请检查名称是否正确，或手动选择你要刷课的课程，打开该课程后等待片刻"),
              flush=True)
        now_window_handles=len(driver.window_handles)
        while len(driver.window_handles)==now_window_handles:
            time.sleep(1)
        time.sleep(1)
        return

def new_find_mission(driver,speed):

    course_list=driver.find_element(By.CLASS_NAME,'list-four')
    #寻找正在学习中的课程
    all_course=course_list.find_elements(By.TAG_NAME,'li')
    for course in all_course:
        try:
            course.find_element(By.CSS_SELECTOR,"[class='list-status studying']").click()
            set_speed(speed, driver)
            return
        except NoSuchElementException:
            pass
    else:
        print(color.red('该页未找到正在学习中的课程，点击下一页'),flush=True)
        driver.find_element(By.CLASS_NAME,'arrow').click()
        time.sleep(2)
        new_find_mission(driver,speed)

def find_mission(driver,task_type,speed,course_name,review):
    # 点击开始学习
    try:
        element = driver.find_element(By.CSS_SELECTOR,'[class="start-study readclosecoursepop"]')
        element.click()
    except:
        pass
    experience(driver)
    # 点击章节/作业标签
    elements=driver.find_elements(By.CLASS_NAME, 'nav_content')
    if not elements:
        try:
            driver.find_element(By.CSS_SELECTOR, "li[data-nav-name='章节']").click()
        except:
            try:
                driver.find_element(By.CSS_SELECTOR, '[data-nav-id="2"]').click()
            except:
                print(color.red('如该课程存在人脸识别，请检查是否开启跳过人脸功能，可在设置页面的更多设置中打开'),flush=True)
    for element in elements:
        if element.text== task_type:
            element.click()
            break
    try:
        driver.switch_to.frame(driver.find_element(By.TAG_NAME, 'iframe'))
    except NoSuchElementException:
        table = driver.find_element(By.CSS_SELECTOR, "[class='tabs font15 color333 fl']")
        # 点击全部知识点
        table.find_elements(By.TAG_NAME, 'a')[2].click()
        time.sleep(1)
        new_find_mission(driver,speed)
        return True
    # 切换到名为 frame_content-zj 的 iframe
    if task_type == '作业':
        return True
    try:
        if review:
            #查找第一个任务点
            element=driver.find_element(By.CLASS_NAME, 'catalog_tishi56')
        else:
            # 查找待完成任务点的元素
            element = driver.find_element(By.CSS_SELECTOR, '.catalog_tishi120')
    except:
        driver.switch_to.default_content()
        iframes=driver.find_elements(By.TAG_NAME, 'iframe')
        # print(len(iframes))
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            try:
                element= driver.find_element(By.CSS_SELECTOR, '.catalog_tishi120')
                break
            except:
                driver.switch_to.default_content()
                continue
        else:
            print(color.red('所有任务点均已完成，如需刷学习时长或次数，请在设置页面开启复习模式'),flush=True)
            return False
    refresh_process(driver,course_name)
    # 打印提示信息，表示已检测到未完成点
    print(color.magenta('已检测到任务点'),flush=True)
    time.sleep(0.5)
    #滚动到未完成的任务点的位置
    driver.execute_script("arguments[0].scrollIntoView();", element)
    set_speed(speed, driver)
    # 点击待完成任务点的元素
    driver.execute_script("arguments[0].click();", element)
    return True

def refresh_process(driver,course_name):
    try:
        process_text=driver.find_element(By.CLASS_NAME, 'xs_head_name').text.strip()
        # 分别提取两个数字
        match = re.search(r'已完成任务点\s*[:：]\s*(\d+)\s*/\s*(\d+)', process_text)
        if match:
            done = int(match.group(1))  # 7
            total = int(match.group(2))  # 17
            save_process(course_name,done,total)
    except Exception as r:
        print(color.red(f'刷新进度失败'), flush=True)

# ==================== 邮箱通知辅助 ====================
def _mail_notify(func, *args):
    """发送通知；任何异常都只打印，不影响刷课"""
    try:
        return func(*args)
    except Exception as exc:
        print(color.yellow(f'[邮箱] 通知发送异常：{exc}'), flush=True)
        return False


def _course_context(account_info):
    """邮件里标明是哪门课出的问题（多端模式下每门课一个进程）"""
    try:
        courses = (account_info or {}).get('cour') or []
        return '、'.join(str(c) for c in courses)
    except Exception:
        return ''

def _section_task_stats(driver):
    """统计当前小节的任务点，返回 (总数, 已完成数)"""
    total = done = 0
    try:
        driver.switch_to.default_content()
        try:
            driver.switch_to.frame('iframe')
        except Exception:
            return 0, 0
        icons = driver.find_elements(By.CSS_SELECTOR, '[class*="ans-job-icon"]')
        total = len(icons)
        for icon in icons:
            try:
                parent_class = icon.find_element(By.XPATH, '..').get_attribute('class') or ''
                label = icon.get_attribute('aria-label') or ''
                if 'ans-job-finished' in parent_class or '已完成' in label:
                    done += 1
            except Exception:
                continue
    except Exception:
        return 0, 0
    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
    return total, done

def _current_chapter_name(driver):
    """当前小节标题（学习页右上角的章节名）"""
    try:
        driver.switch_to.default_content()
        element = driver.find_element(By.CLASS_NAME, 'prev_title')
        return (element.get_attribute('title') or element.text or '').strip()
    except Exception:
        return ''

def _course_progress(course_name):
    """
    课程进度：直接读 course_process.json（和 GUI 里课程进度用的是同一份数据）
    返回 (已完成任务点, 总任务点) 或 None
    """
    try:
        from core.config_manager import ConfigManager
        data = ConfigManager().get_course_process()
        if course_name in data:
            done, total = data[course_name]
            return int(done), int(total)
    except Exception:
        pass
    return None


def _chapter_tabs(driver):
    """本章的小节 tab（#prev_tab 下的 li 列表）"""
    driver.switch_to.default_content()
    prev_tab = driver.find_element(By.ID, 'prev_tab')
    return prev_tab.find_elements(By.TAG_NAME, 'li')


def _chapter_key(driver):
    """用本章小节 tab 的文本组合作为章节标识，切章节后会变"""
    try:
        names = []
        for tab in _chapter_tabs(driver):
            names.append((tab.text or tab.get_attribute('title') or '').strip())
        return '|'.join(names)
    except Exception:
        return ''


def _current_section_index(driver):
    """当前小节在 tab 里的序号（找不到返回 -1）"""
    try:
        for index, tab in enumerate(_chapter_tabs(driver)):
            if 'active' in (tab.get_attribute('class') or ''):
                return index
    except Exception:
        pass
    return -1


def _current_section_name(driver):
    """当前小节名称"""
    try:
        for tab in _chapter_tabs(driver):
            if 'active' in (tab.get_attribute('class') or ''):
                return (tab.text or '').strip()
    except Exception:
        pass
    return ''


# 本章任务点累计：{章节标识: {小节序号: (总数, 已完成数)}}
_chapter_tracker = {'key': None, 'sections': {}, 'progressed': False}


def _record_chapter_section(driver, before_done, after_total, after_done,
                            before_course=None, after_course=None):
    """
    把本节的任务点情况记到当前章节下：
      * 章节变了就重置累计；
      * 同一小节重复进入时用新数据覆盖，避免重复计数；
      * 本节完成数比进入时多（或课程任务点总数增加），就认为本章被脚本完成过任务点。
    """
    try:
        key = _chapter_key(driver)
        if _chapter_tracker['key'] != key:
            _chapter_tracker['key'] = key
            _chapter_tracker['sections'] = {}
            _chapter_tracker['progressed'] = False
        index = _current_section_index(driver)
        if index < 0:
            index = _current_section_name(driver) or 'unknown'
        _chapter_tracker['sections'][index] = (after_total, after_done)

        progressed = after_done > before_done
        # 有些任务点（如 PPT）完成后图标刷新有延迟，用课程任务点总数变化兜底
        if before_course and after_course and after_course[0] > before_course[0]:
            progressed = True
        if progressed:
            _chapter_tracker['progressed'] = True
    except Exception:
        pass


def _chapter_task_stats(driver):
    """本章任务点完成情况：累加本章已处理过的小节"""
    try:
        sections = _chapter_tracker.get('sections') or {}
        total = sum(item[0] for item in sections.values())
        done = sum(item[1] for item in sections.values())
        if total > 0:
            return done, total
    except Exception:
        pass
    return _section_task_stats(driver)


_notified_chapters = set()


def check_chapter(driver):
    """检查是否为章节的最后一小节"""
    try:
        tabs = _chapter_tabs(driver)
        if not tabs:
            return False
        return (tabs[-1].get_attribute('class') or '') == 'active'
    except Exception:
        return False


def notify_chapter_finished(driver, course_name):
    """
    跳转下一节之前调用：
      * 只有当前是本章最后一小节（再点下一节就进入下一章）才提醒；
      * 只要本次运行完成过本章任意一个任务点就提醒；
      * 同一门课的同一章节只提醒一次。
    """
    try:
        if not mailer.is_enabled():
            return False
        if not check_chapter(driver):
            return False
        if not _chapter_tracker.get('progressed'):
            return False
        chapter = _current_chapter_name(driver) or '未命名章节'
        key = (course_name, chapter)
        if key in _notified_chapters:
            return False
        done, total = _chapter_task_stats(driver)
        if total <= 0:
            return False
        section = _current_section_name(driver)
        progress = _course_progress(course_name)
        _notified_chapters.add(key)
        _chapter_tracker['progressed'] = False
        return _mail_notify(mailer.notify_chapter, course_name, chapter,
                            done, total, progress, section)
    except Exception:
        return False

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
            return True
        else:
            continue
    return False

def fold(driver):
    """折叠侧边目录"""
    try:
        element = driver.find_element(By.XPATH, '//*[@id="selector"]/div[2]')
        element.click()
        time.sleep(1)
    except:
        pass

def set_speed(speed,driver):
    global condition
    if not condition:
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
        condition=False
    except Exception as e:
        print(color.yellow(f'调节失败{e}'), flush=True)
        condition=True

def page_message(driver):
    """检测页面内容类型，返回包含视频、PPT、测验、直播、讨论、音频、阅读的字典"""
    # 内容类型配置：(名称, 查找方式, 选择器)
    CONTENT_TYPES = [
        ('视频', By.CSS_SELECTOR, '[class="ans-attach-online ans-insertvideo-online"]'),
        ('ppt', By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-ppt"]'),
        ('ppt', By.CSS_SELECTOR, '[class="ans-attach-online insertdoc-online-pdf"]'),
        ('测验', By.XPATH, '//iframe[@src="/ananas/modules/work/index.html?v=2025-1028-1629&castscreen=0"]'),
        ('直播', By.CSS_SELECTOR, '[src^="/ananas/modules/live/index.html"]'),
        ('讨论', By.CSS_SELECTOR, '[src^="/ananas/modules/insertbbs/index.html"]'),
        ('音频', By.CSS_SELECTOR, '[class="ans-attach-online ans-insertaudio"]'),
        ('阅读', By.CSS_SELECTOR, '[class="ans-attach-online ans-book"]'),
        ('阅读', By.CSS_SELECTOR, '[src^="/ananas/modules/read/indexV2.html"]'),
        ('问卷', By.CSS_SELECTOR, '[src^="/ananas/modules/zt/vote/index-pc-new.html"]')
    ]

    driver.switch_to.default_content()
    page_message_dict = {}

    original_wait = driver.timeouts.implicit_wait  # 保存原始等待时间
    driver.implicitly_wait(0)

    try:
        iframe = driver.find_element(By.ID, 'iframe')
        driver.switch_to.frame(iframe)

        for name, by, selector in CONTENT_TYPES:
            if name in page_message_dict:
                continue  # 已找到的类型跳过
            try:
                driver.find_element(by, selector)
                page_message_dict[name] = selector
            except NoSuchElementException:
                pass
    except NoSuchElementException:
        pass
    finally:
        driver.implicitly_wait(original_wait)  # 恢复原始等待时间

    return page_message_dict

course_finished = False
def click_next_page(driver, pass_face):
    """点击下一页按钮，处理各种异常情况"""
    global error_num, course_finished
    course_finished = False
    NEXT_PAGE_XPATH = '//*[@id="prevNextFocusNext"]'
    try:
        driver.find_element(By.XPATH, NEXT_PAGE_XPATH).click()
        return True
    except ElementNotInteractableException:
        course_finished = True
        print(color.red('🎉 🎉 该课程全部已完结，撒花！！！'), flush=True)
        return False
    except ElementClickInterceptedException:
    #     print(color.red('点击被拦截，尝试将浏览器最大化,如果还是报错，请在下次打开浏览器后手动把浏览器最大化'), flush=True)
    #     driver.maximize_window()
        time.sleep(1)
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, NEXT_PAGE_XPATH))
    except NoSuchElementException:
        print(color.red('加载中...'), flush=True)
        driver.implicitly_wait(5)
        error_num+=1
        if error_num==6:
            print(color.red('❌ 出错次数过多'), flush=True)
            _mail_notify(mailer.notify_error, '连续出错次数过多',
                         '点击「下一节」连续失败 6 次，已停止本门课程')
            return False
        try:
            driver.find_element(By.XPATH, NEXT_PAGE_XPATH).click()
        except Exception as e:
            driver.refresh()
            print(color.red(f'出错了，刷新一下'), flush=True)
            delete_face_popup(driver,pass_face)
            fold(driver)
        finally:
            driver.implicitly_wait(2)
    return True

chapter_name=''
def check_chapter_active(driver,multi_device):
    """判断该章节是否正在被学习"""
    global chapter_name
    record_path = fr'task\record\studying_record.txt'
    if not multi_device:
        return True
    try:
        element = driver.find_element(By.CLASS_NAME, 'prev_title')
        chapter_name = element.get_attribute('title')
        marker = f'正在刷{chapter_name}...\n'
        with open(record_path, 'a+', encoding='utf-8') as f:
            f.seek(0)
            if marker in f.read():
                print(color.yellow(f'检测到{chapter_name}章节正在学习中，跳过'), flush=True)
            else:
                f.write(marker)
                return True
    except FileNotFoundError:
        pass
    except NoSuchElementException:
        print(color.red('章节名称未找到，自动跳过该章节'), flush=True)

    return False

def delete_record():
    """删除该章节的正在学习记录"""
    record_path = fr'task\record\studying_record.txt'
    try:
        with open(record_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return
    if chapter_name=='':
        content = re.sub(r'正在刷.*?\.\.\.\n', '', content)
    else:
        content = content.replace(f'正在刷{chapter_name}...\n', '')
    with open(record_path, 'w', encoding='utf-8') as f:
        f.write(content)

def run(driver,choice,course_name,API,lock_screen,pass_face,video_title_choice,
        discussion_choice,after_finish_question,pass_vido,speed,multi_device,review):
    while True:
        cond=True
        before_done = 0
        before_course = None
        delete_face_popup(driver,pass_face)
        if check_chapter_active(driver,multi_device):
            print(color.green('正在检测页面内容'), flush=True)
            # 记录本节进入时的任务点状态，用于判断本章是否有任务点被完成
            _before_total, before_done = _section_task_stats(driver)
            before_course = _course_progress(course_name)
            page_message_dict=page_message(driver)
            if len(page_message_dict)==0:
                print(color.red('该页面无法识别'),flush=True)
            else:
                print(color.green(f'该页面含有{list(page_message_dict.keys())}'),flush=True)
                if 'ppt' in page_message_dict.keys():
                    __ppt(driver,course_name)
                if '直播' in page_message_dict.keys():
                    watch_live(driver,page_message_dict['直播'],course_name)
                if '音频' in page_message_dict.keys():
                    play_audio(driver,page_message_dict['音频'],course_name)
                if '讨论' in page_message_dict.keys():
                    if discussion_choice!='跳过讨论':
                        finish_discussion(driver,API,page_message_dict['讨论'],discussion_choice,course_name)
                    else:
                        print(color.yellow(f'您已选择{discussion_choice}'), flush=True)

                if '阅读' in page_message_dict.keys():
                    reading(driver,page_message_dict['阅读'],course_name)
                if '问卷' in page_message_dict.keys():
                    finish_vote(driver,page_message_dict['问卷'],course_name)
                if '视频' in page_message_dict.keys():
                    try:
                        study_page(driver,course_name,lock_screen,API,video_title_choice,pass_vido,speed,pass_face,review)
                    except Exception as e:
                        driver.refresh()
                        print(color.red('出错了，刷新一下'),flush=True)
                        cond=False
                if '测验' in page_message_dict.keys():
                    if choice!='不刷题':
                        finish_quiz(driver, course_name, API, choice,after_finish_question)
                    else:
                        print(color.yellow('您已选择不刷题，即将跳过测试题'),flush=True)
            delete_record()
            # 记录本节处理后的任务点情况到当前章节
            try:
                after_total, after_done = _section_task_stats(driver)
                after_course = _course_progress(course_name)
                _record_chapter_section(driver, before_done, after_total, after_done,
                                        before_course, after_course)
            except Exception:
                pass
        driver.switch_to.default_content()
        if cond:
            print(color.green('跳转下一页'), flush=True)
            # 点下一节前判断：如果是本章最后一节且本章有任务点被完成，就发章节提醒
            notify_chapter_finished(driver, course_name)
            if not click_next_page(driver, pass_face):
                if course_finished:
                    _mail_notify(mailer.notify_course_done, course_name,
                                 _course_progress(course_name))
                break
            # 确认
            try:
                driver.find_element(By.XPATH, '//*[@id="mainid"]/div[1]/div/div[3]/a[2]').click()
            except:
                pass
        else:
            delete_face_popup(driver,pass_face)
            fold(driver)
        time.sleep(1)

def start_browser(browser,driver_path,speed):
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
    if speed!='1':
        options.add_extension(r"task\tool\speed.crx")
    options.add_extension(r"task\tool\chrome-extension.crx")
    options.add_argument("--enable-extensions")
    options.add_argument("--disable-web-security")

    if browser == 'chrome':
        driver = webdriver.Chrome(service=service, options=options)
    else:
        # 初始化Chrome浏览器
        driver = webdriver.Edge(service=service, options=options)

    driver.implicitly_wait(2)
    return driver



def main(browser, driver_path, phone_number, password, choice, course_lst,API,after_finish_question,lock_screen,
         speed, task_type,homework,pass_face,video_title_choice,discussion_choice,pass_vido,multi_device,review):
    driver = start_browser(browser, driver_path,speed)
    # time.sleep(20)
    login_study(driver, phone_number, password)
    # 登录成功后通知：已开始刷课
    # 多端模式下每门课一个子进程、会陆续启动，由 GUI 在最后一门课启动时统一发一封，
    # 这里就不再各自发信了（否则会收到"开始刷课"×课程数）。
    if not multi_device:
        _mail_notify(mailer.notify_start, course_lst, task_type)
    for course_name in course_lst:
        delete_record()
        choice_course(driver, course_name, speed,  task_type,phone_number)
        turn_page(driver, course_name)
        experience(driver)
        delete_face_popup(driver,pass_face,course_name)

        if find_mission(driver,task_type,speed,course_name,review):
            if task_type=='作业':
                do_work(driver,course_name,homework,API)
                # return
            else:
                turn_page(driver, '学生学习页面')

                if multi_device:
                    monitor = DisableMonitor(driver)
                    monitor.enable()

                delete_face_popup(driver,pass_face)
                fold(driver)
                pyautogui.hotkey('ctrl', 'm')
                run(driver, choice, course_name, API, lock_screen, pass_face,video_title_choice,discussion_choice,
                after_finish_question,pass_vido,speed,multi_device,review)
        elif task_type != '作业':
            # find_mission 返回 False 说明该课程所有任务点都已完成
            print(color.green(f'{course_name} 所有任务点均已完成'), flush=True)
            _mail_notify(mailer.notify_course_done, course_name, _course_progress(course_name))
        driver.close()
        turn_page(driver, '个人空间')


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
            print(f"版本不兼容: {versions['browser_type']}浏览器版本(v{browser_main_ver})过高，"
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
    print('\n具体操作步骤见官网:https://github.com/Mortal004/xuexitong-tutorial/')

    return versions

def run_main():
    account_info = {}
    try:
        # 用 ConfigManager 读配置：多端模式下 GUI 会反复重写该文件，
        # 直接 open+json.load 可能读到写了一半的内容。
        account_info = ConfigManager().load_account()
        if not account_info:
            raise Exception('读取 account_info.json 失败，请重新保存设置后再试')
        main(account_info['browser'], account_info['driver_path'], account_info['phone_number'], account_info['password'],
             account_info['choice'], account_info['cour'],account_info['API'],account_info['after_finish_question'],
             account_info['lock_screen'],account_info['speed'],account_info['task_type'],account_info['homework'],
             account_info['pass_face'],account_info['video_title_choice'],account_info['discussion_choice'],
             account_info['pass_vido'],account_info['multi_device'],account_info['review'])
    except NoSuchWindowException as e:
        print(color.red('❌ 窗口意外关闭'),flush=True)
        _mail_notify(mailer.notify_error, '窗口意外关闭', traceback.format_exc(),
                     _course_context(account_info))
    except SessionNotCreatedException as e:
        error_msg = traceback.format_exc()
        send_error(
            "\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行前往官网查看解决办法自行解决\n" + error_msg)
        _mail_notify(mailer.notify_error, '浏览器驱动异常', error_msg, _course_context(account_info))
        # 执行分析
        result = parse_versions_from_text(error_msg)

    except WebDriverException as e:
        if 'ERR_INTERNET_DISCONNECTED' in str(e) or 'ERR_NAME_NOT_RESOLVED' in str(e):
            print(color.red('❌ 你网都没连，刷个屁的课啊'),flush=True)
            _mail_notify(mailer.notify_error, '网络未连接', str(e), _course_context(account_info))
        else:
            print(color.red('❌ 出错了，具体原因请前往错误日志查看'),flush=True)
            error_msg = traceback.format_exc()
            send_error("\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行前往官网查看解决办法自行解决\n"+error_msg)
            _mail_notify(mailer.notify_error, '浏览器运行异常', error_msg, _course_context(account_info))
    except PermissionError:
        print(color.red('请关闭该窗口后，再右键点击刷课程序用管理员权限打开'))
        _mail_notify(mailer.notify_error, '权限不足', '请以管理员权限运行程序', _course_context(account_info))
    except Exception as e:
        error_msg = traceback.format_exc()
        send_error("\n作者只解决打赏用户提交的问题，请在赞助后将截图与报错信息一同发送至作者邮箱2022865286@qq.com,未赞助的用户请自行前往官网查看解决办法自行解决\n"+error_msg)
        _mail_notify(mailer.notify_error, '程序异常', error_msg, _course_context(account_info))
        print(color.red('❌ 出错了，具体原因请前往错误日志查看'),flush=True)

if __name__ == '__main__':
    run_main()
