# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
import random
import time
import re
import pyautogui
from openai import OpenAI
from selenium.webdriver.common.by import By
from task.tool.no_secret import DecodeSecret
from task.tool import color
import requests
import sys
import io
# 设置默认编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class Answer:
    def __init__(self, driver, test_frame, course_name,API_KEY):
        self.course_name = course_name
        self.driver=driver
        self.frame=test_frame
        self.API_KEY=API_KEY
        self.ans_rate =None
        self.all_title_list=[]
        #滚动到测试
        driver.execute_script("arguments[0].scrollIntoView();", test_frame)
        # 判断是否完成任务
        try:
            element = self.frame.find_element(By.XPATH, 'preceding-sibling::div[1]')
            txt = element.get_attribute('aria-label')
        except:
            self.driver.switch_to.frame(test_frame)
            self. driver.switch_to.frame('frame_content')
            element =self. driver.find_element(By.CLASS_NAME, 'testTit_status')
            txt = element.text
            time.sleep(3)
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('iframe')
        if '已完成' in txt:
            print(color.green('测试已完成'), flush=True)
            return
        else:
            self.driver.switch_to.frame(test_frame)
            self.driver.switch_to.frame('frame_content')
            # 实例化 DecodeSecret 类
            decodeSecret = DecodeSecret(1)
            print(color.yellow("启用字体解密"), flush=True)
            decodeSecret.getFontFace(self.driver)
            # 获取页面中的所有题目
            self.questionList0 =self. driver.find_elements(By.CSS_SELECTOR, '[class="singleQuesId"]')
            print(color.yellow("当前测试共有{}题".format(len(self.questionList0))), flush=True)
            self.titleWebElementList=[]
            self.optionWebElementList = []
            self.questionType_list=[]
            self.all_title = ''
            for i in range(len(self.questionList0)):
                self.title_and_option_element =self. questionList0[i]
                self.title_and_option_text = decodeSecret.decode(self.title_and_option_element.text)
                self.title_element =self. title_and_option_element.find_element(By.CSS_SELECTOR, '[class="clearfix font-cxsecret fontLabel"]')
                self.titleWebElementList.append(self.title_element)
                self.title = decodeSecret.decode(self.title_element.text)
                # 题目类型
                self.questionType =self. title[self.title.find("【") + 1: self.title.find("】")]
                if self.questionType=='单选题' or self.questionType=='多选题' or self.questionType=='判断题':
                    self.optionWebElementList.append( self.title_and_option_element.find_elements(By.TAG_NAME, 'li'))
                    self.all_title_list.append(self.title_and_option_text)
                else:
                    self.all_title_list.append(self.title)
                    self.optionWebElementList.append(None)
                self.all_title += self.title_and_option_text + '\n'
                self.questionType_list.append(self.questionType)
            self.prompt = '''请根据以下题目要求回答问题：
                                   1.不要其他话语，我仅仅需要这些题目的选择答案哟

             2.所有题目的答案必须从选项 A、B、C、D 中选择。多选题必须选多个答案，其答案紧挨着即可不用用'/'隔开

             3.对于判断题，答案只能是 A 或 B，分别对应题目中的 A（对） 和 B（错）。
            
             4.简答题只需给出文字答案即可,不要有多余的内容,论述题同样，论述题的答案字数在五十字左右,不要出现字母或题号数字
            
             5.填空题的每个答案用“,”隔开
            
             6.如果题目重复出现，只需回答一次，不要重复回答。

             7.请严格按照题目编号顺序给出答案,1,2,3,4这样的题目序号顺序给出选择的答案。
             每个题目的答案用“/”隔开,答案中不要题号，只需要答案，不用重复问题,不要给多了答案，有多少道题就给多少答案，
             /的数量是能保持比题目数量少一个，不能多也不能少,不要有换行符
             
             8.最终你给出的答案格式应当类似于下面这样：A/BCD/C/'论述题答案'/D/'填空题答案1','填空题答案2',...

             9.注意：请你忽略我的答案，这可能是错误答案哟；同时请你注意每道题目开头的【】
             里面内容判断这道题目是什么类型的题目
                                     \n'''
            self.prompt += self.all_title
            print(color.blue('正在使用deepseek搜索该测试所有题目答案...'), flush=True)
            try:
                all_answer = self.DeepSeekAsk(self.prompt)
            except Exception as e:
                print(color.red('系统繁忙，请稍后再试\n{}'.format(e)), flush=True)
                return
            print(color.green('已成功获取答案'), flush=True)
            # 使用正则表达式按 '/' 分隔字符串
            parts = re.split(r'/', all_answer)
            # 转换为字典
            self.answer_dict = {i : part for i, part in enumerate(parts)}
            self.finish_title()
            message=self.submit()
            if message=='False':
                driver.switch_to.frame('iframe')
                print(color.green('重新做题'), flush=True)
                Answer(self.driver, self.frame, self.course_name,self.API_KEY)


    def DeepSeekAsk(self,prompt):
        message = {"role": "user", "content": prompt}
        client = OpenAI(api_key=self.API_KEY, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[message],
            temperature=1.3,
            stream=False
        )
        answer=response.choices[0].message.content
        return answer

    def finish_title(self):
        print(color.green('开始答题'), flush=True)
        k = 0
        ans_num = 0
        for num, answer in self.answer_dict.items():
            dit = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
            num = num - k
            try:
                # 滚动到题目
                self.driver.execute_script("arguments[0].scrollIntoView();", self.titleWebElementList[num])
                pyautogui.scroll(50)
            except:
                break
            print(color.green('\n<===================  分隔线  ===================>\n'),flush=True)
            print(color.green(f'正在回答第{num+1}题...\n{self.all_title_list[num]}'), flush=True)
            time.sleep(1)
            print(color.green(f'该题为{self.questionType_list[num]}，答案：{answer}'), flush=True)
            if self.questionType_list[num]=='单选题' or self.questionType_list[num]=='判断题':
                if answer not in ['A', 'B', 'C', 'D', 'E', 'F', 'G','H']:
                    k += 1
                    continue
                if answer not in ['A','B'] and self.questionType_list[num]=='判断题':
                    k += 1
                    continue
                if self.optionWebElementList[num][dit.get(answer)].get_attribute('aria-checked')=='true':
                    print(color.red('已回答，无需重复回答'),flush=True)
                    ans_num += 1
                    continue
                self.optionWebElementList[num][dit.get(answer)].click()
                ans_num+=1
            elif self.questionType_list[num]=='多选题':
                #点击正确答案
                for ans in answer:
                    time.sleep(1)
                    try:
                        # print(self.optionWebElementList[num][dit.get(ans)].get_attribute('aria-checked'))
                        if self.optionWebElementList[num][dit.get(ans)].get_attribute('aria-checked')=='true':
                            print(color.red('已回答，无需重复回答'), flush=True)
                        else:
                            self.optionWebElementList[num][dit.get(ans)].click()
                    except:
                        self.optionWebElementList[num][dit.get(ans)].click()
                    del dit[ans]
                #去除错误答案
                for value in dit.values():
                    try:
                        if self.optionWebElementList[num][value].get_attribute('aria-checked')=='true':
                            self.optionWebElementList[num][value].click()
                    except:
                        continue
                ans_num+=1
            elif self.questionType_list[num]=='简答题' or self.questionType_list[num]=='论述题' or self.questionType_list[num]=='名词解释':
                i = 0
                if answer in ['A','B','C','D','E','F','G']:
                    k+=1
                    continue
                text_frame=self.questionList0[num].find_element(By.TAG_NAME,'iframe')
                self.driver.switch_to.frame(text_frame)
                p_element=self.driver.find_element(By.TAG_NAME,'p')
                # self.driver.execute_script('arguments[0].innerText = arguments[1];', p_element, answer)
                p_element.click()
                p_element.send_keys(answer)
                self.driver.switch_to.parent_frame()
                i+=1
                ans_num+=1
            elif self.questionType_list[num]=='填空题':
                if answer in ['A','B','C','D','E','F','G']:
                    k+=1
                    continue
                answer=answer.split(',')
                elements = self.questionList0[num].find_elements(By.CLASS_NAME, 'InpDIV')
                text_frames = self.questionList0[num].find_elements(By.TAG_NAME, 'iframe')
                for number in range(len(elements)):
                    self.driver.execute_script("arguments[0].click();", elements[number])
                    self.driver.switch_to.frame(text_frames[number])
                    p_element = self.driver.find_element(By.TAG_NAME, 'p')
                    try:
                        p_element.click()
                    except:
                        self.driver.execute_script("arguments[0].click();", p_element)
                    try:
                        p_element.send_keys(answer[number])
                    except:
                        pass
                    self.driver.switch_to.parent_frame()
                    time.sleep(1)
                ans_num+=1
            else:
                print(color.red(f'该题为{self.questionType_list[num]}，暂时无法作答'), flush=True)
        self.ans_rate=ans_num/len(self.answer_dict)
        print(ans_num,'/',len(self.answer_dict))

    def submit(self):
        formatted_result = "{:.2%}".format(self.ans_rate)
        print(color.red(f'本次答题率为{formatted_result}'), flush=True)
        if self.ans_rate >= 0.9:
            # 点击提交
            print(color.yellow('5秒后提交'), flush=True)
            time.sleep(5)
            self.driver.find_element(By.CSS_SELECTOR, '[class="btnSubmit workBtnIndex"]').click()
            time.sleep(1)
            # 点击确认
            self.driver.switch_to.default_content()
            self.driver.find_element(By.XPATH, '//*[@id="popok"]').click()
            time.sleep(2)
            message =self.driver.find_element(By.ID, 'popcontent').text
            if '未达及格线' in message:
                print(color.red(f'提交失败，原因：{message}'), flush=True)
                self.driver.find_element(By.ID, 'popok').click()
                return 'False'
            self.save_score()
        else:
            print(color.yellow('3秒后保存'), flush=True)
            time.sleep(3)
            self.driver.find_element(By.CSS_SELECTOR, '[class="btnSave workBtnIndex"]').click()
        return

    def save_score(self):
        element = self.driver.find_element(By.CLASS_NAME, 'prev_title')
        title = element.get_attribute('title')
        self.driver.switch_to.frame('iframe')
        self.driver.switch_to.frame(self.frame)
        self.driver.switch_to.frame('frame_content')
        try:
            f = open(fr'task\record\《{self.course_name}》的成绩记录.txt', 'a', encoding='utf-8')
        except:
            pass
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, '.achievement i')
            score = element.text
            f.write(
                f'已完成:《{title}》章节中的测试题，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n测试得分：{score}分(本次使用DeepSeek AI答题)\n\n')
        except:
            print(color.yellow('未查询到本次测试成绩'), flush=True)
            f.write(
                f'已完成:《{title}》章节的测试题，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n测试得分：未查询到(本次使用DeepSeek AI答题)\n\n')
        self.driver.switch_to.default_content()
