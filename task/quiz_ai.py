# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.
import time
import re
import asyncio
from selenium.webdriver.common.by import By
from task.tool.no_secret import DecodeSecret
from task.tool import color
import sys
import io
from task.ai_wen_da import main,AnswerAPI,Question
from task.DeepSeekAsk import DeepSeekAsk
# 设置默认编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')



class Answer:
    def __init__(self, driver, test_frame, course_name, api,work_choice,times=0):
        self.driver=driver
        self.test_frame = test_frame
        self.decodeSecret = None
        self.questionList0 = []
        self.no_answer_dit = {}# 存储无答案的题目
        self.answer_list = []
        self.course_name = course_name
        self.driver=driver
        self.frame=test_frame
        self.API_KEY=api
        self.work_choice=work_choice
        self.ans_rate =None
        self.all_title_dit={}
        self.num_option_dit = {}
        self.questionType_list = []
        self.all_title = ''
        self.num_answer_dit = {}
        self.only_title_text = []
        self.reword_time = 0
        self.all_optionWebElementList = []
        self.times = times
        if self.work_choice is not None:
            self.main()

    def main(self):
        # 滚动到测试
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();",self.test_frame)

        except:
            return
        # 判断是否完成任务
        try:
            element = self.frame.find_element(By.XPATH, 'preceding-sibling::div[1]')
            txt = element.get_attribute('aria-label')
        except:
            self.driver.switch_to.frame(self.test_frame)
            self.driver.switch_to.frame('frame_content')
            element = self.driver.find_element(By.CLASS_NAME, 'testTit_status')
            txt = element.text
            time.sleep(3)
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame('iframe')
        if '已完成' in txt:
            print(color.green('测试已完成'), flush=True)
            return
        else:
            self.get_title_option()
            print(color.red('正在搜索中，请耐心等待...'))
            self.use_ai_wen_da()
            self.use_deepseek()
            print(color.green('开始答题'), flush=True)
            for title_num in self.num_answer_dit.keys():
                if self.finish_title(title_num):
                    self.reword_time += 1
                time.sleep(1)
            self.ans_rate = self.reword_time / len(self.questionList0)
            print(self.reword_time, '/', len(self.questionList0))
            message = self.submit()
            if not message and self.times<3:
                print(color.green('开始第{}次重新做题'.format(self.times+1)))
                self.driver.switch_to.frame('iframe')
                print(color.green('重新做题'), flush=True)
                Answer(self.driver, self.frame, self.course_name, self.API_KEY, self.work_choice,self.times+1)
            elif self.times>=3:
                print(color.red('测试答题失败，已重试3次'), flush=True)
    def get_title_option(self):
        self.driver.switch_to.frame(self.frame)
        self.driver.switch_to.frame('frame_content')
        # 实例化 DecodeSecret 类
        self.decodeSecret = DecodeSecret(1)
        print(color.yellow("启用字体解密"), flush=True)
        self.decodeSecret.getFontFace(self.driver)
        # 获取页面中的所有题目
        self.questionList0 = self.driver.find_elements(By.CSS_SELECTOR, '[class="singleQuesId"]')
        print(color.yellow("当前测试共有{}题".format(len(self.questionList0))), flush=True)

        for i in range(len(self.questionList0)):
            self.title_num = i + 1
            self.option_text_list = []
            self.title_and_option_element = self.questionList0[i]
            self.title_and_option_text = re.sub(r'\s+', '',
                                               self.decodeSecret.decode(self.title_and_option_element.text).strip())
            self.title_element = self.title_and_option_element.find_element(By.CSS_SELECTOR,
                                                                            '[class="clearfix font-cxsecret fontLabel"]')
            self.title = re.sub(r'\s+', '', self.decodeSecret.decode(self.title_element.text).strip())
            # 题目类型
            self.questionType = self.title[self.title.find("【") + 1: self.title.find("】")]
            # 题目文本
            self.title_text = self.title[self.title.find("】") + 1:]
            self.only_title_text.append(self.title_text)
            self.questionType_list.append(self.questionType)
            if self.questionType in ['单选题', '多选题','判断题']:
                self.all_optionWebElementList.append(
                    self.title_and_option_element.find_elements(By.TAG_NAME, 'li'))
                for option in self.title_and_option_element.find_elements(By.TAG_NAME, 'li'):
                    self.option_text_list.append(re.sub(r'\s+', '', self.decodeSecret.decode(option.text).strip()))
            elif self.questionType in ['简答题', '论述题', '填空题','名词解释','论述题']:
                self.all_optionWebElementList.append(None)
            else:
                print(color.red(f'第{i+1}题题型为{self.questionType},无法作答'))
                continue
            self.all_title_dit[i] = self.title_and_option_text
            self.num_option_dit[i] = self.option_text_list

    def use_ai_wen_da(self):
        for i in self.all_title_dit.keys():
            if self.times==0:
                print(color.green('\n<===================  分隔线  ===================>\n'), flush=True)
                self.answer_list = asyncio.run(
                    main(self.questionType_list[i], self.only_title_text[i], self.num_option_dit[i], self.API_KEY))
                if type(self.answer_list) is str:
                    self.answer_list = eval(self.answer_list)
                if not self.answer_list:
                    self.answer_list = asyncio.run(
                        main(self.questionType_list[i], self.only_title_text[i], self.num_option_dit[i], self.API_KEY))
                    if type(self.answer_list) is str:
                        self.answer_list = eval(self.answer_list)
            else:
                self.answer_list=[]
            if not self.answer_list:
                self.num_answer_dit[i] = []
                # print(color.red('无答案，跳过'), flush=True)
                continue
            else:
                self.num_answer_dit[i] = self.answer_list

    def use_deepseek(self):
        for i, answer in self.num_answer_dit.items():
            if not answer:
                self.no_answer_dit[i] = self.all_title_dit[i]
        if len(self.no_answer_dit) > 0:
            print(color.red('正在使用deepseek搜题，请耐心等待...'), flush=True)
            title = ''
            num = 0
            for no_answer_title in self.no_answer_dit.values():
                title += no_answer_title
            answers = DeepSeekAsk(self.API_KEY, title, 'all')
            # answers='C/B/ABCD/ABCD/实体经济/'
            parts = re.split(r'/', answers)
            for key, no_answer_title in self.no_answer_dit.items():
                self.num_answer_dit[key] = re.split(',', parts[num])
                # 缓存答案
                question = Question(
                    type=str(self.questionType_list[key]),  # 题目类型
                    question=self.only_title_text[key],
                    options=self.num_option_dit[key],
                    API=self.API_KEY)
                AnswerAPI().cache_answer(question, self.num_answer_dit[key])
                num += 1


    def finish_title(self, title_num):
        try:
            # 滚动到题目
            self.driver.execute_script("arguments[0].scrollIntoView();", self.questionList0[title_num])
            # pyautogui.scroll(50)
        except:
            pass
        print(color.green(f'正在回答第{title_num + 1}题...'), flush=True)
        answer=self.num_answer_dit[title_num]
        #去重
        print(color.green(f'该题为{self.questionType_list[title_num]}，答案：{answer}'), flush=True)
        option_num=0
        try:
            if self.questionType_list[title_num]=='单选题' or self.questionType_list[title_num]=='判断题':
                for option in self.num_option_dit[title_num]:
                    if answer[0] in option:
                       break
                    option_num+=1
                if self.all_optionWebElementList[title_num][option_num].get_attribute('aria-checked')== 'true':
                    print(color.red('已回答，无需重复回答'),flush=True)
                else:
                    self.all_optionWebElementList[title_num][option_num].click()
                return True
            elif self.questionType_list[title_num] == '多选题':
                self.answer_num=[]
                if len(answer)==1:
                    lst = answer[0]
                else:
                    lst = answer
                for option in self.num_option_dit[title_num]:
                    for ans in lst:
                        if ans in option:
                           self.answer_num .append(option_num)
                    option_num+=1
                self.answer_num=list(set(self.answer_num))
                # 点击正确答案
                for ans in self.answer_num:
                    time.sleep(1)
                    try:
                        if self.all_optionWebElementList[title_num][ans].get_attribute('aria-checked')== 'true':
                            print(color.red('已回答，无需重复回答'), flush=True)
                        else:
                            self.all_optionWebElementList[title_num][ans].click()
                    except:
                        self.all_optionWebElementList[title_num][ans].click()
                return True

            elif self.questionType_list[title_num]=='简答题' or self.questionType_list[title_num]=='论述题' or self.questionType_list[title_num]=='名词解释':
                text_frame=self.questionList0[title_num].find_element(By.TAG_NAME,'iframe')
                self.driver.switch_to.frame(text_frame)
                p_element=self.driver.find_element(By.TAG_NAME,'p')
                check_answer = p_element.text
                if check_answer != '':
                    print(color.red('已回答，无需重复回答'), flush=True)
                    self.driver.switch_to.parent_frame()
                    return True
                # self.driver.execute_script('arguments[0].innerText = arguments[1];', p_element, answer)
                p_element.click()
                p_element.send_keys(answer)
                self.driver.switch_to.parent_frame()
                return True
            elif self.questionType_list[title_num]=='填空题':
                if self.work_choice is not None:
                    elements = self.questionList0[title_num].find_elements(By.CLASS_NAME, 'InpDIV')
                else:
                    elements = self.questionList0[title_num].find_elements(By.CSS_SELECTOR,
                                                                           '[class="edui-editor-iframeholder edui-default"]')
                text_frames = self.questionList0[title_num].find_elements(By.TAG_NAME, 'iframe')
                if  len(answer)==1:
                    answer=re.split(r' ', answer[0])
                    print(color.red(f'修正答案：{answer}'), flush=True)
                if len(elements)!=len(answer):
                    print(color.red('填空题答案数量与题目数量不一致'), flush=True)
                    return False
                for number in range(len(elements)):
                    self.driver.execute_script("arguments[0].click();", elements[number])
                    self.driver.switch_to.frame(text_frames[number])
                    p_element = self.driver.find_element(By.TAG_NAME, 'p')
                    check_answer = p_element.text
                    if check_answer != '':
                        print(color.red('已回答，无需重复回答'), flush=True)
                        self.driver.switch_to.parent_frame()
                        continue
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
                return True
            else:
                print(color.red(f'该题为{self.questionType}，暂时无法作答'), flush=True)
                return False
        except Exception as e:
            print(color.red(f'答题时出错了{e}'), flush=True)
            return False

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
            if message:
                print(color.red(f'提交失败，原因：{message}'), flush=True)
                self.driver.find_element(By.ID, 'popok').click()
                return False
            self.save_score()
        else:
            print(color.yellow('3秒后保存'), flush=True)
            time.sleep(3)
            self.driver.find_element(By.CSS_SELECTOR, '[class="btnSave workBtnIndex"]').click()
        return True

    def save_score(self):
        element = self.driver.find_element(By.CLASS_NAME, 'prev_title')
        title = element.get_attribute('title')
        self.driver.switch_to.frame('iframe')
        self.driver.switch_to.frame(self.frame)
        self.driver.switch_to.frame('frame_content')
        try:
            f = open(fr'task\record\《{self.course_name}》的成绩记录.txt', 'a', encoding='utf-8')
            element = self.driver.find_element(By.CSS_SELECTOR, '.achievement i')
            score = element.text
            f.write(
                f'已完成:《{title}》章节中的测试题，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n测试得分：{score}分(本次使用{self.work_choice})\n\n')
        except:
            print(color.yellow('未查询到本次测试成绩'), flush=True)
            try:
                f.write(
                f'已完成:《{title}》章节的测试题，完成时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}\n测试得分：未查询到(本次使用{self.work_choice})\n\n')
            except:
                pass
        self.driver.switch_to.default_content()

