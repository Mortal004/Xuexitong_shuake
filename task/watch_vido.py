# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import time
from task.tool import color
import pyautogui
from selenium.webdriver.common.by import By

def video_question(driver):
    try:
        element=driver.find_element(By.CLASS_NAME,'tkTopic')
        print(color.yellow('已检测到视频中有题目'), flush=True)
        options = element.find_element(By.CLASS_NAME,'tkItem_ul')
        options=options.find_elements(By.TAG_NAME,'li')
        for option in options:
            option.click()
            #提交
            submit=element.find_element(By.ID,'videoquiz-submit')
            submit.click()
            #继续学习
            try:
                continue_learn=element.find_element(By.ID,'videoquiz-continue')
                continue_learn.click()
            except:
                pass
    except:
        return

def check_face(driver):
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR,"[class='popDiv1 wid640  faceCollectQrPopVideo  popClass faceRecognition_0']")
            print(color.red('请按照要求手机扫码进行人脸认证'),flush=True)
            time.sleep(1)
        except:
            break

def study_page(driver,course_name,lock_screen):
    cond=False
    driver.switch_to.default_content()

    driver.switch_to.frame('iframe')
    try:
        # 判断是否完成任务
        elements1 = driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
        print(color.magenta(f'已检测到{len(elements1)}个视频包含有任务点'),flush=True)
    except:
        pyautogui.scroll(-250)
        print(color.green('视频已完成,点击下一节'),flush=True)
        return

    for i in range(len(elements1)):
        element1=elements1[i]
        # 定位到该元素的上一级（父元素）
        parent_element = element1.find_element(By.XPATH, "..")
        try:
            # 获取 parent_element 的class值
            parent_element_class=parent_element.get_attribute("class")
            txt = element1.get_attribute('aria-label')
        except:
            txt = ''
            parent_element_class=''
        if txt == '任务点未完成' and parent_element_class=='ans-attach-ct':
            vido_iframe=element1.find_element(By.XPATH, "following-sibling::iframe[1]")
            driver.execute_script("arguments[0].scrollIntoView();", vido_iframe)
            driver.switch_to.frame(vido_iframe)
            print(color.green(f'开始播放第{i + 1}个视频'),flush=True)
            time_start=time.time()
            try:
                driver.find_element(By.CLASS_NAME,'vjs-big-play-button').click()
            except:
                pass
            #点击我知道了
            driver.switch_to.default_content()
            check_face(driver)
            driver.switch_to.frame('iframe')
            driver.switch_to.frame(vido_iframe)
            time.sleep(1)
            try:
                element=driver.find_element(By.CLASS_NAME,'writeNote_vid_blue')
                element.click()
            except:
                pass
            try:
                print(color.blue('调节音量'), flush=True)
                element = driver.find_element(By.XPATH, '//*[@id="video"]/div[6]/div[6]')
                element.click()
                print(color.green('调节成功'), flush=True)
            except:
                print(color.yellow('未找到音量，或已经调节'), flush=True)
            time.sleep(1)
            element=driver.find_element(By.CLASS_NAME,'vjs-duration-display')
            total_time=element.text
            print(color.green(f'该视频总时长为：{total_time}'),flush=True)
            print(color.yellow('请不要将窗口最小化，这有可能导致脚本异常'),flush=True)
            driver.switch_to.default_content()
            driver.switch_to.frame('iframe')
            last_time=0
            # 判断是否完成任务
            while True:
                driver.switch_to.default_content()
                driver.switch_to.frame('iframe')
                elements2= driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
                element2=elements2[i]
                # 定位到该元素的上一级（父元素）
                parent_element2 = element2.find_element(By.XPATH, "..")
                # 获取 parent_element2 的class值
                parent_element2_class = parent_element2.get_attribute("class")
                txt = element2.get_attribute('aria-label')
                if txt=='任务点已完成' or parent_element2_class=='ans-attach-ct ans-job-finished':
                    # pyautogui.scroll(-250)
                    print(color.green(f'已完成第{i + 1}个视频'),flush=True)
                    time_end=time.time()
                    print(color.green('总共耗费了%.2f秒.' % (time_end - time_start)),flush=True)
                    cond=True
                    break
                else:
                    driver.switch_to.default_content()
                    driver.switch_to.frame('iframe')
                    driver.switch_to.frame(vido_iframe)
                    video_question(driver)
                    element=driver.find_element(By.CLASS_NAME,'vjs-current-time-display')
                    current_time=element.text
                    if last_time==current_time and current_time!='':
                        try:
                            print(color.red(f'当前视频播放被暂停,点击继续播放'),flush=True)
                            driver.find_element(By.CSS_SELECTOR,'[class="vjs-play-control vjs-control vjs-button vjs-paused"]').click()
                        except:
                            print(color.red(f'点击失败'), flush=True)
                    last_time=current_time
                    if current_time==total_time:
                        try:
                            print(color.yellow('视频已播放完毕，但任务点仍未完成，开始重播'),flush=True)
                            driver.find_element(By.CSS_SELECTOR,'[class="vjs-play-control vjs-control vjs-button vjs-paused vjs-ended"]').click()
                        except:
                            print(color.red(f'点击失败'), flush=True)
                    if lock_screen:
                        pyautogui.move(20, 0, )
                        pyautogui.move(-20,0)
        driver.switch_to.default_content()
        driver.switch_to.frame('iframe')
    print(color.green('所有视频均已完成'),flush=True)
    if cond and judge_active(driver):
        save_vido(driver,course_name)
    return

def save_vido(driver,course_name):
    driver.switch_to.default_content()
    element = driver.find_element(By.CLASS_NAME, 'prev_title')
    title = element.get_attribute('title')
    try:
        f = open(fr'task\record\《{course_name}》的刷课记录.txt', 'a', encoding='utf-8')
        f.write(
            f'已刷完:《{title}》章节中的所有视频\n完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n\n')
    except:
        pass
def judge_active(driver):
    driver.switch_to.default_content()
    element=driver.find_element(By.CSS_SELECTOR, '[class="prev_ul clearfix"]')
    elements = element.find_elements(By.CSS_SELECTOR, '[title="视频"]')
    num=len(elements)
    try:
        txt=elements[num-1].get_attribute('class')
    except IndexError:
        txt = 'active'
    if txt=='active':
        return True
    else:
        return False


