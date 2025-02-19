# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import time
import re
import pyautogui
from openai import OpenAI
from selenium.webdriver.common.by import By
from task.tool.no_secret import DecodeSecret
from task.tool import color

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
                else:
                    self.optionWebElementList.append(None)
                self.all_title += self.title_and_option_text + '\n'
                self.all_title_list.append(self.title_and_option_text)
                self.questionType_list.append(self.questionType)
            self.prompt = '''请根据以下题目要求回答问题：
                                   1.不要其他话语，我仅仅需要这些题目的选择答案哟

             2.所有题目的答案必须从选项 A、B、C、D 中选择。多选题必须选多个答案，其答案紧挨着即可不用用'/'隔开

             3.对于判断题，答案只能是 A 或 B，分别对应题目中的 A（对） 和 B（错）。
            
             4.简答题只需给出答案即可,不要有多余的内容,论述题同样，论述题的答案字数在五十字左右,不要出现字母
            
             5.填空题的每个答案用“,”隔开
            
             6.如果题目重复出现，只需回答一次，不要重复回答

             7.请严格按照题目编号顺序给出答案,1,2,3,4这样的题目序号顺序给出选择的答案。
             每个题目的答案用“/”隔开,答案中不要题号，只需要答案，不用重复问题
             
             8.最终你给出的答案格式应当类似于下面这样：A/BCD/C/'论述题答案'/D/'填空题答案1','填空题答案2',...

             9.注意：请你忽略我的答案，这可能是错误答案哟；同时请你注意每道题目开头的【】
             里面内容判断这道题目是什么类型的题目
                                     \n'''
            self.prompt += self.all_title
            print(color.blue('正在使用deepseek搜索该测试所有题目答案...'), flush=True)
            try:
                # all_answer = 'A/A/你,好/啊啊啊,n'
                all_answer = self.DeepSeekAsk(self.prompt, 1.3)
            except:
                print(color.red('系统繁忙，请稍后再试'), flush=True)
                return
            print(color.green('已成功获取答案'), flush=True)
            # 使用正则表达式按 '/' 分隔字符串
            parts = re.split(r'/', all_answer)
            # 转换为字典
            self.answer_dict = {i : part for i, part in enumerate(parts)}
            self.finish_title()
            self.submit()

    def DeepSeekAsk(self,prompt, temperature):
        api_key = self.API_KEY
        message = {"role": "user", "content": prompt}
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[message],
            temperature=temperature,
            stream=False
        )
        return response.choices[0].message.content

    def finish_title(self):
        dit = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        print(color.green('开始答题'),flush=True)
        i=0
        j=0
        ans_num=0
        for num,answer in self.answer_dict.items():
            # 滚动到题目
            self.driver.execute_script("arguments[0].scrollIntoView();", self.titleWebElementList[num])
            pyautogui.scroll(50)
            print(color.green('\n<===================  分隔线  ===================>\n'),flush=True)
            print(color.green(f'正在回答第{num+1}题...\n{self.all_title_list[num]}'), flush=True)
            time.sleep(1)
            if self.questionType_list[num]=='单选题' or self.questionType_list[num]=='判断题':
                self.optionWebElementList[num][dit.get(answer)].click()
                ans_num+=1
            elif self.questionType_list[num]=='多选题':
                for ans in answer:
                    time.sleep(1)
                    self.optionWebElementList[num][dit.get(ans)].click()
                ans_num+=1
            elif self.questionType_list[num]=='简答题' or self.questionType_list[num]=='论述题' or self.questionType_list[num]=='名词解释':
                text_frame=self.driver.find_element(By.ID,f'ueditor_{i}')
                self.driver.switch_to.frame(text_frame)
                p_element=self.driver.find_element(By.TAG_NAME,'p')
                # self.driver.execute_script('arguments[0].innerText = arguments[1];', p_element, answer)
                p_element.click()
                p_element.send_keys(answer)
                self.driver.switch_to.parent_frame()
                i+=1
                ans_num+=1
            elif self.questionType_list[num]=='填空题':
                answer=answer.split(',')
                elements = self.driver.find_elements(By.CLASS_NAME, 'InpDIV')
                for ans in answer:
                    elements[j].click()
                    text_frame = self.driver.find_element(By.ID, f'ueditor_{i}')
                    self.driver.switch_to.frame(text_frame)
                    p_element = self.driver.find_element(By.TAG_NAME, 'p')
                    p_element.click()
                    p_element.send_keys(ans)
                    self.driver.switch_to.parent_frame()
                    time.sleep(1)
                    i+=1
                    j+=1
                ans_num+=1
            else:
                print(color.red(f'该题为{self.questionType_list[num]}，暂时无法作答'))
            print(color.green(f'该题为{self.questionType_list[num]}，答案：{answer}'), flush=True)
        self.ans_rate=ans_num/len(self.answer_dict)

    def submit(self):
        formatted_result = "{:.2%}".format(self.ans_rate)
        print(color.red(f'本次答题率为{formatted_result}'), flush=True)
        if self.ans_rate >= 0.9:
            # 点击提交
            print(color.yellow('5秒后提交'), flush=True)
            time.sleep(5)
            self.driver.find_element(By.XPATH, '//*[@id="RightCon"]/div[2]/div/div[3]/a[2]').click()
            time.sleep(1)
            # 点击确认
            self.driver.switch_to.default_content()
            self.driver.find_element(By.XPATH, '//*[@id="popok"]').click()
            time.sleep(1)
            self.save_score()

        else:
            print(color.yellow('3秒后保存'), flush=True)
            time.sleep(3)
            self.driver.find_element(By.XPATH, '//*[@id="RightCon"]/div[2]/div/div[3]/a[1]').click()
        return

    def save_score(self):
        element = self.driver.find_element(By.CLASS_NAME, 'prev_title')
        title = element.get_attribute('title')
        self.driver.switch_to.frame('iframe')
        self.driver.switch_to.frame(self.frame)
        self.driver.switch_to.frame('frame_content')
        f = open(fr'task\record\《{self.course_name}》的成绩记录.txt', 'a', encoding='utf-8')
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
