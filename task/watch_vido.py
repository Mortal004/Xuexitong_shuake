import time
from task.tool import color
import pyautogui
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from task.tool.check import find_image_on_screen,check


def speed():# 待完善，功能：拖动进度条到视频结尾
    while True:
        time.sleep(1)
        if check('black'):
            continue
        else :
            break
    print(color.blue('尝试拖动进度条'))
    pyautogui.moveRel(-100, -100, duration=1)
    time.sleep(0.5)
    try:
        pyautogui.click(find_image_on_screen('line1',threshold=0.8)[0], find_image_on_screen('line1',threshold=0.8)[2],
                        duration=1)
        print(color.green("已匹配到进度条"))
    except:
        try:
            pyautogui.click(find_image_on_screen('line2',threshold=0.6)[0], find_image_on_screen('line2',threshold=0.6)[2]+5,
                            duration=1)
            print(color.green("已匹配到进度条1"))
        except:
            print(color.yellow("未匹配到进度条"))

def vido_question(condition):# 要用时直接复制粘贴，不要调用
    try:
        img_Ture = pyautogui.locateOnScreen(r'.\img\img_Ture.png', confidence=0.9)
        img_False = pyautogui.locateOnScreen(r'.\img\img_False.png', confidence=0.9)
        img_submit = pyautogui.locateOnScreen(r'.\img\img_submit.png', confidence=0.8)

        print(color.green('已检测到视频中有题目'))
        # answerWebElementList = element.find_elements(By.TAG_NAME, "li")
        if condition:
            # __questionList.append(answerWebElementList[0])
            pyautogui.click(img_Ture, duration=0.4)
            condition = False
            print(color.green('第一次答题完毕'))
        else:
            # __questionList.append(answerWebElementList[1])
            pyautogui.click(img_False, duration=0.4)
            print(color.green('第二次答题完毕'))
            condition = True

        # 提交
        # driver.find_element(By.XPATH,'//*[@id="videoquiz-submit"]').click()
        pyautogui.click(img_submit, duration=0.4)
        pyautogui.move(0, -50)
        time.sleep(2)
        # continue
    except:
        condition = True
        return

def study_page(driver,course_name):
    cond=False
    driver.switch_to.default_content()

    driver.switch_to.frame('iframe')
    try:
        # 判断是否完成任务
        elements1 = driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
        print(color.magenta(f'已检测到{len(elements1)}个视频'))
    except:
        pyautogui.scroll(-250)
        print(color.green('视频已完成,点击下一节'))
        return

    for i in range(len(elements1)):
        element1=elements1[i]
        try:
            txt = element1.get_attribute('aria-label')
        except:
            txt=''
        if txt == '任务点未完成':
            elements=driver.find_elements(By.XPATH,'//*[@id="ext-gen1050"]/iframe')
            element=elements[i]
            driver.switch_to.frame(element)
            element=driver.find_element(By.XPATH,'//*[@id="video"]/button')
            print(color.green(f'开始播放第{i + 1}个视频'))
            element.click()

            #点击我知道了
            driver.switch_to.default_content()
            driver.switch_to.frame('iframe')
            element = driver.find_elements(By.XPATH, '//*[@id="ext-gen1050"]/iframe')
            driver.switch_to.frame(element[i])
            time.sleep(1)
            try:
                element=driver.find_element(By.XPATH,'//*[@id="ext-gen1049"]/div[2]/div[1]/div[4]/div[2]/div/div/div[2]/a')
                element.click()
            except:
                pass
            #待完善
            speed()

            try:
                print(color.blue('调节倍数'))
                element=driver.find_element(By.XPATH,'//*[@id="video"]/div[6]/div[1]/div[2]')
                txt=element.text
                if txt!='2x':
                    ac = ActionChains(driver)
                    # 鼠标移动到 元素上
                    ac.move_to_element(element).perform()
                    element=driver.find_element(By.XPATH,'//*[@id="video"]/div[6]/div[1]/div[1]/ul/li[1]')
                    element.click()
                print(color.green('调节成功'))
            except:
                print(color.yellow('未找到倍数，或已经调节'))
            try:
                print(color.blue('调节音量'))
                element=driver.find_element(By.XPATH,'//*[@id="video"]/div[6]/div[6]')
                element.click()
                print(color.green('调节成功'))
            except:
                print(color.yellow('未找到音量，或已经调节'))

            driver.switch_to.default_content()
            driver.switch_to.frame('iframe')
            condition = True
            # 判断是否完成任务
            while True:
                # driver.switch_to.default_content()
                # driver.switch_to.frame('iframe')
                elements2= driver.find_elements(By.CLASS_NAME, 'ans-job-icon-clear ')
                element2=elements2[i]
                txt = element2.get_attribute('aria-label')
                if txt=='任务点已完成':
                    pyautogui.scroll(-250)
                    print(color.green(f'已完成第{i + 1}个视频'))
                    cond=True
                    break
                else:
                    pyautogui.move(20,0,)
                    time.sleep(1)
                    pyautogui.move(-20,0)
                    continue
        driver.switch_to.default_content()
        driver.switch_to.frame('iframe')
        pyautogui.scroll(-250)
        # print('第{}个视频已完成'.format(i+1))
    print(color.green('所有视频均已完成，开始下一节'))
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
        f'已刷完:《{title}》章节中的所有视频，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n\n')

def judge_active(driver):
    driver.switch_to.default_content()
    element=driver.find_element(By.CSS_SELECTOR, '[class="prev_ul clearfix"]')
    elements = element.find_elements(By.TAG_NAME, 'li')
    num=len(elements)
    txt=elements[num-1].get_attribute('class')
    if txt=='active':
        return True
    else:
        return False



if __name__ == '__main__':
    speed()