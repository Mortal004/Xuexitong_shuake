import time

from setuptools.command.setopt import option_base

from task.tool import color
import pyautogui
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from task.tool.check import find_image_on_screen,check


def speed0(driver):
    try:
        time.sleep(0.3)
        print(color.blue('调节倍数'), flush=True)
        element = driver.find_element(By.XPATH, '//*[@id="video"]/div[6]/div[1]/div[2]')
        txt = element.text
        if txt != '2x':
            ac = ActionChains(driver)
            # 鼠标移动到 元素上
            ac.move_to_element(element).perform()
            element = driver.find_element(By.XPATH, '//*[@id="video"]/div[6]/div[1]/div[1]/ul/li[1]')
            element.click()
        print(color.green('调节成功'), flush=True)
    except:
        try:
            if txt != '2x':
                element = driver.find_element(By.CSS_SELECTOR,
                                              '[class="vjs-playback-rate vjs-menu-button vjs-menu-button-popup vjs-button"]')
                element.click()
                element.click()
                element.click()
                print(color.green('已调节成功'), flush=True)
            else:
                raise
        except:
            print(color.yellow('未找到倍数，或已经调节'), flush=True)



def vido_question():
    i=1
    while i<3:
        try:
            img_Ture = pyautogui.locateOnScreen(r'task\img\img_Ture.png', confidence=0.9)
            img_False = pyautogui.locateOnScreen(r'task\img\img_False.png', confidence=0.9)
            img_submit = pyautogui.locateOnScreen(r'task\img\img_submit.png', confidence=0.8)
        except pyautogui.ImageNotFoundException:
            return
        if i==1:
            print(color.green('已检测到视频中有题目'),flush=True)
            pyautogui.click(img_Ture, duration=0.4)
            print(color.green('第一次答题完毕'),flush=True)
        elif i==2:
            pyautogui.click(img_False, duration=0.4)
            print(color.green('第二次答题完毕'),flush=True)
        # 提交
        pyautogui.click(img_submit, duration=0.4)
        pyautogui.move(0, -50)
        time.sleep(2)
        i+=1

def video_question1(i,driver):
    driver.switch_to.default_content()
    driver.switch_to.frame('iframe')
    element = driver.find_elements(By.CSS_SELECTOR, '[class="ans-attach-online ans-insertvideo-online"]')
    driver.switch_to.frame(element[i])
    k=0
    while k<4:
        try:
            element=driver.find_element(By.CLASS_NAME,'tkTopic')
            print(color.yellow('已检测到视频中有题目'), flush=True)
            # title_type=element.find_element(By.CLASS_NAME,'tkTopic_title').text
            options=element.find_element(By.CLASS_NAME,'tkItem_ul')
            options=options.find_elements(By.TAG_NAME,'li')
            options[k].click()
            k+=1
            #提交
            submit=element.find_element(By.ID,'videoquiz-submit')
            submit.click()
        except:
            break

def study_page(driver,course_name):
    cond=False
    driver.switch_to.default_content()

    driver.switch_to.frame('iframe')
    try:
        # 判断是否完成任务
        elements1 = driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
        print(color.magenta(f'已检测到{len(elements1)}个视频'),flush=True)
    except:
        pyautogui.scroll(-250)
        print(color.green('视频已完成,点击下一节'),flush=True)
        return

    for i in range(len(elements1)):
        element1=elements1[i]
        try:
            txt = element1.get_attribute('aria-label')
        except:
            txt=''
        if txt == '任务点未完成':
            elements=driver.find_elements(By.CSS_SELECTOR,'[class="ans-attach-online ans-insertvideo-online"]')
            element=elements[i]
            driver.switch_to.frame(element)
            print(color.green(f'开始播放第{i + 1}个视频'),flush=True)
            driver.find_element(By.CLASS_NAME,'vjs-big-play-button').click()

            #点击我知道了
            driver.switch_to.default_content()
            driver.switch_to.frame('iframe')
            element = driver.find_elements(By.CSS_SELECTOR,'[class="ans-attach-online ans-insertvideo-online"]')
            driver.switch_to.frame(element[i])
            time.sleep(1)
            try:
                element=driver.find_element(By.CLASS_NAME,'writeNote_vid_blue')
                element.click()
            except:
                pass
            #待完善
            try:
                print(color.blue('调节音量'), flush=True)
                element = driver.find_element(By.XPATH, '//*[@id="video"]/div[6]/div[6]')
                element.click()
                print(color.green('调节成功'), flush=True)
            except:
                print(color.yellow('未找到音量，或已经调节'), flush=True)


            print(color.yellow('请不要将鼠标移动至谷歌窗口外，或将窗口最小化，这都有可能导致视频暂停，现在鼠标左右移动是正常的，目的是为了防止熄屏'),flush=True)
            driver.switch_to.default_content()
            driver.switch_to.frame('iframe')
            # 判断是否完成任务
            while True:
                driver.switch_to.default_content()
                driver.switch_to.frame('iframe')
                elements2= driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
                element2=elements2[i]
                txt = element2.get_attribute('aria-label')
                if txt=='任务点已完成':
                    pyautogui.scroll(-250)
                    print(color.green(f'已完成第{i + 1}个视频'),flush=True)
                    cond=True
                    break
                else:
                    video_question1(i,driver)
                    pyautogui.move(20,0,)
                    time.sleep(1)
                    pyautogui.move(-20,0)
                    continue
        driver.switch_to.default_content()
        driver.switch_to.frame('iframe')
        pyautogui.scroll(-250)
        # print('第{}个视频已完成'.format(i+1))
    print(color.green('所有视频均已完成'),flush=True)
    if cond and judge_active(driver):
        save_vido(driver,course_name)
    #跳转到下一节
    # driver.switch_to.default_content()
    # driver.find_element(By.XPATH,'//*[@id="prevNextFocusNext"]').click()
    return

def save_vido(driver,course_name):
    driver.switch_to.default_content()
    element = driver.find_element(By.CLASS_NAME, 'prev_title')
    title = element.get_attribute('title')
    f = open(f'《{course_name}》的刷课记录.txt', 'a', encoding='utf-8')
    f.write(
        f'已刷完:《{title}》章节中的所有视频\n完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n\n')

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



if __name__ == '__main__':
    vido_question()