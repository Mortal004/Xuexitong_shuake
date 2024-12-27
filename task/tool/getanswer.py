import io
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import pyautogui
from selenium.webdriver.common.by import By

from task.tool import color


# 修改 stdout 编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 自定义文件
class NoFoundAnswerException(Exception):
    """
    在接口中没有找到答案抛出此异常。
    """
    pass

class GetAnswer:
    __debug = False

    def __init__(self, debug=False):
        GetAnswer.__debug = debug
        self.__pool = ThreadPoolExecutor(max_workers=5)


    @staticmethod
    def extension_answer1(driver):
        driver.switch_to.default_content()
        host = driver.find_element(By.TAG_NAME, 'plasmo-csui')
        # 获取Shadow DOM内的元素的文本
        answer_text = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item > div:nth-child(2) > div:nth-child(3) > div > div");
            return elementInsideShadow.textContent;
            """, host
        )

        answer_choices = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item >div:nth-child(1) > div:nth-child(2) > div > div ");
            return elementInsideShadow.textContent;
            """, host
        )

        # 定制正则表达式应对紧密相连的情形
        pattern = r'([A-D])(?:\s*[:、.]*)\s*(.*?)(?=(\s*[A-D]|$))'
        matches = re.findall(pattern, answer_choices)

        # 将匹配项整理为字典，同时去除多余的空格
        choices_dict = {k: v.strip() for k, v, _ in matches}

        # 为字典键添加":"及后续空格
        formatted_dict = {v:f"{k}" for k, v in choices_dict.items()}

        try:
            answer = answer_text[answer_text.find("】") + 1:]
            #print(f'answer: {answer}')
            return answer,formatted_dict
        except:

            #print(f'answer: {answer_text}')
            return answer_text,formatted_dict

    @staticmethod
    def extension_answer2(driver):
        driver.switch_to.default_content()
        host = driver.find_element(By.TAG_NAME, 'plasmo-csui')
        # 找到Shadow DOM的宿主标签
        host = driver.find_element(By.TAG_NAME, 'plasmo-csui')
        result_2 = pyautogui.locateOnScreen(r'task\img\img_02.png', confidence=0.8)
        pyautogui.click(result_2)
        time.sleep(1)
        answer_text = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item > div:nth-child(2) > div:nth-child(3) > div > div");
            return elementInsideShadow.textContent;
            """, host
        )

        answer_choices = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item >div:nth-child(1) > div:nth-child(2) > div > div ");
            return elementInsideShadow.textContent;
            """, host
        )

        # 定制正则表达式应对紧密相连的情形
        pattern = r'([A-D])(?:\s*[:、.]*)\s*(.*?)(?=(\s*[A-D]|$))'
        matches = re.findall(pattern, answer_choices)

        # 将匹配项整理为字典，同时去除多余的空格
        choices_dict = {k: v.strip() for k, v, _ in matches}

        # 为字典键添加":"及后续空格
        formatted_dict = {v: f"{k}" for k, v in choices_dict.items()}

        try:
            answer = answer_text[answer_text.find("】") + 1:]
            # print(f'answer: {answer}')
            return answer, formatted_dict
        except:

            # print(f'answer: {answer_text}')
            return answer_text, formatted_dict

    @staticmethod
    def extension_answer3(driver):
        driver.switch_to.default_content()
        host = driver.find_element(By.TAG_NAME, 'plasmo-csui')
        # 找到Shadow DOM的宿主标签
        host = driver.find_element(By.TAG_NAME, 'plasmo-csui')
        result_3 = pyautogui.locateOnScreen(r'task\img\img_03.png', confidence=0.9)
        pyautogui.click(result_3)
        time.sleep(1)
        answer_text = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item > div:nth-child(2) > div:nth-child(3) > div > div");
            return elementInsideShadow.textContent;
            """, host
        )
        answer_choices = driver.execute_script(
            """
            var elementInsideShadow = arguments[0].shadowRoot.querySelector("#plasmo-overlay-0 > div > div.result-wrapper.show > div.skeleton-wrapper > div.result-item >div:nth-child(1) > div:nth-child(2) > div > div ");
            return elementInsideShadow.textContent;
            """, host
        )

        # 定制正则表达式应对紧密相连的情形
        pattern = r'([A-D])(?:\s*[:、.]*)\s*(.*?)(?=(\s*[A-D]|$))'
        matches = re.findall(pattern, answer_choices)

        # 将匹配项整理为字典，同时去除多余的空格
        choices_dict = {k: v.strip() for k, v, _ in matches}

        # 为字典键添加":"及后续空格
        formatted_dict = {v: f"{k}" for k, v in choices_dict.items()}

        try:
            answer = answer_text[answer_text.find("】") + 1:]
            # print(f'answer: {answer}')
            return answer, formatted_dict
        except:

            # print(f'answer: {answer_text}')
            return answer_text, formatted_dict


    def __requestAnswer(self, questionType,driver):
        """

        :return: 若找到答案则返答案的string，若没找到答案则返回空string
        """
        answerList = []
        answer_options_dicts_lst=[]
        # print('请搜题')
        # time.sleep()

        while True:
            try:

                answer0,answer_options_dict=GetAnswer.extension_answer1(driver)
                answer1=GetAnswer.__parseAnswer(answer0,questionType)
                answerList.append(answer1)
                answer_options_dicts_lst.append(answer_options_dict)
                break
            except:
                print(color.yellow('搜题失败1，请重新搜题，3秒后检测'),flush=True)
                time.sleep(3)
                continue

        while True:
            try:

                answer0 ,answer_options_dict= GetAnswer.extension_answer2(driver)
                answer2 = GetAnswer.__parseAnswer(answer0, questionType)
                answerList.append(answer2)
                answer_options_dicts_lst.append(answer_options_dict)

                break
            except:
                print(color.yellow('搜题失败2，请重新搜题，3秒后检测'),flush=True)
                time.sleep(3)
                continue

        while True:
            try:

                answer0 ,answer_options_dict= GetAnswer.extension_answer3(driver)
                answer3 = GetAnswer.__parseAnswer(answer0, questionType)
                answerList.append(answer3)
                answer_options_dicts_lst.append(answer_options_dict)

                break
            except:
                print(color.yellow('搜题失败3，请重新搜题，3秒后检测'),flush=True)
                time.sleep(3)
                continue
        return answerList,answer_options_dicts_lst


    @staticmethod
    def __parseAnswer(answer, questionType):
        if answer == "":
            return None
        separator = ("#", "\u0001", "\x01", "&nbsp;",',')
        for i in separator:
            if i in answer:
                answer = answer.split(i)

                break
        try:
            answer=answer.strip()
        except:
            pass
        # 验证获取的答案和题目类型是否相同
        if questionType == "":
            return answer

        elif questionType == "单选题":
            if isinstance(answer, list):
                return None
            return answer

        elif questionType == "多选题":
            # if not isinstance(answer, list):
            #     return None
            return answer
        elif questionType == "判断题":
            if isinstance(answer, list):
                return None
            data = {'√': True, '正确': True, 'T': True, 'ri': True, '是': True, '对': True,'A':True,
                    '×': False, 'X':False,'错误': False, '错': False, 'F': False, 'wr': False, '否': False,'B':False}
            for i in data.keys():
                if answer == i:
                    return data[i]
            return None


    def getAnswer(self, question,driver ,questionType=""):
        """
        :param driver:
        :param question: 待搜索的题目
        :param questionType: 题目的类型，若不提供题目类型则不检测查找答案正确性
        :return: 形如[[答案1], [答案2], [答案3]]的二维列表，其中列表的元素个数在[0, 5]范围内
        """
        print("正在搜索题目：{}\n".format(question),flush=True)
        answerList ,answer_options_dicts_lst= self.__requestAnswer( questionType,driver)
        # while None in answerList:
        #     answerList.remove(None)
        if not answerList:
            print(color.yellow('未找到答案'),flush=True)
            return
            # GetAnswer.callback(question, str(answerList[0]), questionType)
        else:
            print(color.green("找到 " + str(len(answerList)) + " 个答案"),flush=True)
            for i in range(len(answerList)):
                print(color.green("答案{}：{}".format(i + 1, answerList[i])),flush=True)
            return answerList,answer_options_dicts_lst



if __name__ == "__main__":
    getAnswer = GetAnswer(True)
    while True:
        q = input("输入题目（q退出）：")
        if q == "q":
            break
        answerList = getAnswer.getAnswer()
        print(color.green(answerList))
        print()

"""
资本-帝国主义列强不能灭亡和瓜分近代中国的最根本原因是(    )。
['物质是第一性的,意识是第二性的', '主观能动性的发挥,必须尊重客观规律']
['物质是第一性的,意识是第二性的', '主观能动性的发挥,必须尊重客观规律']
['物质是第一性的，意识是第二性的', '主观能动性的发挥，必须尊重客观规律']
"""
