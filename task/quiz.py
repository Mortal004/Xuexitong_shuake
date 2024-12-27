import time
import pyautogui
from task.tool.Match import match
from task.tool.getanswer import GetAnswer
from task.tool.no_secret import DecodeSecret

# 导入全局变量
from task.tool.globalvar import spliter
from task.tool import color

# 第三方库
from selenium.webdriver.common.by import By


def use_extension(item0,i):
    k=0
    while k<=0.8:
        try:
            pyautogui.hotkey('alt','c')
            size = item0.size
            num1 = pyautogui.locateOnScreen(fr'task\img\img_{i}.png', confidence=0.95-k)
            print(color.blue(color.magenta(f'正在搜索第{i + 1}题')),flush=True)
            pyautogui.moveTo(num1, duration=0.5)
            pyautogui.dragRel(size['width'], size['height'] + 80, duration=1)
            time.sleep(3)
            return size['height'] + 80
        except:
            print(color.yellow('未知错误,再来一次'),flush=True)
            k+=0.1
            continue

def get_question_date(driver,course_name,frame):
    time.sleep(3)
    driver.switch_to.default_content()
    driver.switch_to.frame('iframe')
    # 判断是否完成任务
    elements = driver.find_elements(By.CLASS_NAME, 'ans-job-icon ')
    for element in elements:
        try:
            txt = element.get_attribute('aria-label')
            break
        except:
            continue
    else:
        print(color.yellow('无法检测测试是否已完成，默认已完成'),flush=True)
        txt = '任务点已完成'
    if txt == '任务点已完成':
        pyautogui.scroll(-250)
        print(color.green('测试已完成'),flush=True)
        # driver.switch_to.default_content()
        # driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
        return
    else:
        print(color.green('开始做题'), flush=True)
        # element = driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
        driver.switch_to.frame(frame)
        driver.switch_to.frame('frame_content')

        # 实例化 DecodeSecret 类
        decodeSecret = DecodeSecret(1)
        print(color.yellow("启用字体解密"),flush=True)
        decodeSecret.getFontFace(driver)

        # 获取页面中的所有题目
        questionList0 = driver.find_elements(By.CSS_SELECTOR, '[class="singleQuesId"]')

        print(color.yellow("当前页面共有{}题".format(len(questionList0))),flush=True)

        title_lst = []  # 解码后的题目及其类型
        ans_num=0
        for i in range(len(questionList0)):
            spliter.print()
            item0 = questionList0[i]
            title_option=decodeSecret.decode(item0.text)
            __questionList = []
            item_title = item0.find_element(By.CSS_SELECTOR, '[class="clearfix font-cxsecret fontLabel"]')
            title = decodeSecret.decode(item_title.text)
            title_lst.append(title)

            # 获取问题
            question = title[title.find("】") + 1:]

            # 题目类型
            questionType = title[title.find("【") + 1: title.find("】")]

            # 判断题目能否解决
            if questionType not in ("单选题", "多选题", "判断题"):
                print(color.blue("程序能回答的题有：单选题、多选题、判断题"),flush=True)
                print(color.yellow("本题类型为：" + questionType),flush=True)
                print(color.yellow("跳过该题"),flush=True)
                pyautogui.scroll(-int(round(item0.size['height']*0.7)))
                continue

            # 获取问题答案
            use_extension(item0, i)
            myGetAnswer = GetAnswer()
            answerList,answer_options_dicts_lst = myGetAnswer.getAnswer(title_option, driver,questionType)
            pyautogui.click(pyautogui.locateOnScreen(r'task\img\img_close.png',confidence=0.8),duration=0.5)

            # 判断是否找到答案
            if answerList is None or len(answerList) == 0:
                print(color.yellow('未找到该题答案，开始下一题'),flush=True)
                continue
            driver.switch_to.frame('iframe')
            # element = driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
            driver.switch_to.frame(frame)
            driver.switch_to.frame('frame_content')
            if questionType in ("单选题", "多选题"):
                # 获取题目选项的WebElement对象
                optionWebElementList = item0.find_elements(By.TAG_NAME, 'li')

                if questionType=='单选题':
                    __questionList.append(match(answer_options_dicts_lst, questionType, question, answerList,  optionWebElementList))
                elif questionType=='多选题':
                    __questionList=match(answer_options_dicts_lst, questionType, question, answerList, optionWebElementList)
                try:
                    finish(__questionList)
                except:
                    print(color.red('error'),flush=True)
                    pyautogui.scroll(-(item0.size['height']*0.8))
                    continue

            elif questionType == "判断题":
                answerWebElementList = item0.find_elements(By.TAG_NAME, "label")
                __questionList.append(match(answer_options_dicts_lst, questionType, question, answerList, answerWebElementList))
                finish(__questionList)
            else:
                print("当前题目类型程序无法判断",flush=True)
                print("题目类型：" + questionType,flush=True)
                print("题目内容：" + question,flush=True)
                print("跳过该题目",flush=True)
            pyautogui.scroll(-int(round(item0.size['height']*0.75)))
            ans_num+=1
        ans_rate=ans_num/len(questionList0)
        __submit(driver,course_name,frame,ans_rate)
        return

def finish(__questionList):
    webElementList = __questionList
    if len(webElementList) == 0:
        print(color.red("查找答案和选项答案不匹配"),flush=True)
        # continue
    for answerWebElement in webElementList:
        # driver.execute_script("arguments[0].scrollIntoView();", __questionList.qWebObj)
        time.sleep(1)
        answerWebElement.click()

def __submit(driver,course_name,frame,ans_rate):
    formatted_result="{:.2%}".format(ans_rate)
    print(color.red(f'本次答题率为{formatted_result}'),flush=True)
    if ans_rate>=0.9:
        # 点击提交
        print(color.yellow('5秒后提交'),flush=True)
        time.sleep(5)
        driver.find_element(By.XPATH, '//*[@id="RightCon"]/div[2]/div/div[3]/a[2]').click()
        time.sleep(2)
        # 点击确认
        driver.switch_to.default_content()
        driver.find_element(By.XPATH, '//*[@id="popok"]').click()
        try:
            time.sleep(1)
            save_score(driver,course_name,frame)
        except:
            print(color.yellow('未查询到本次测试成绩'),flush=True)
    else:
        print(color.yellow('3秒后保存'),flush=True)
        time.sleep(3)
        driver.find_element(By.XPATH,'//*[@id="RightCon"]/div[2]/div/div[3]/a[1]').click()

    # 下一节
    # print(color.green('开始下一节'),flush=True)
    # driver.find_element(By.XPATH, '//*[@id="prevNextFocusNext"]').click()
    return

def save_score(driver,course_name,frame):
    element= driver.find_element(By.CLASS_NAME,'prev_title')
    title=element.get_attribute('title')
    driver.switch_to.frame('iframe')
    # element = driver.find_element(By.XPATH, '//*[@id="ext-gen1049"]/div[2]/div/p/div/iframe')
    driver.switch_to.frame(frame)
    driver.switch_to.frame('frame_content')
    element=driver.find_element(By.CSS_SELECTOR,'.achievement i')
    score=element.text
    driver.switch_to.default_content()
    f = open(f'《{course_name}》的成绩记录.txt', 'a', encoding='utf-8')
    f.write(f'已完成:《{title}》章节，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}，测试得分：{score}分\n')


if __name__ == '__main__':
    time.sleep(1)
    for i in range(20):
        print(color.blue(color.magenta(f'正在搜索第{i + 1}题')),flush=True)

        num1 = pyautogui.locateOnScreen(fr'img\img_{i}.png', confidence=0.95)
        pyautogui.moveTo(num1, duration=0.5)
        pyautogui.scroll(-220)