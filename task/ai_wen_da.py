import re

import requests
import time
import hashlib
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pickle
import os
import asyncio
import ast
from task.DeepSeekAsk import DeepSeekAsk


@dataclass
class Question:
    """题目数据结构"""
    type: str  # 题目类型: 0-单选, 1-多选, 2-填空, 3-判断, 9-简答
    question: str
    options: List[str]
    html: str = ""
    work_type: str = ""
    page_type: str = ""
    API: str = ""


@dataclass
class AnswerResult:
    """答案结果"""
    form: str  # 答案来源
    answer: List[str]  # 答案列表
    duration: int = 0  # 耗时
    msg: str = ""  # 消息
    error: Optional[Exception] = None


class Cache:
    """缓存管理类"""


class Cache:
    """缓存管理类"""

    @staticmethod
    def set(key: str, value: Any, expire: int = 0) -> Any:
        """设置缓存"""
        cache_data = {
            'value': value,
            'expire': int(time.time()) + expire if expire > 0 else 0
        }
        try:
            with open(fr'task\record\cache_{key}.pkl', 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"缓存设置失败: {e}")
        return value

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """获取缓存"""
        try:
            with open(fr'task\record\cache_{key}.pkl', 'rb') as f:
                cache_data = pickle.load(f)
                if cache_data['expire'] > 0 and cache_data['expire'] < time.time():
                    os.remove(f'cache_{key}.pkl')
                    return default
                return cache_data['value']
        except FileNotFoundError:
            return default
        except Exception as e:
            print(f"缓存获取失败: {e}")
            return default


class AnswerAPI:
    """答题API类"""

    def __init__(self):
        self.cache = Cache()
        self.api_scores = {}  # API评分记录


    def score(self, api_name: str, score: int):
        """记录API评分"""
        current_score = self.cache.get(f"api_{api_name}", {'score': 0})
        current_score['score'] += score
        self.cache.set(f"api_{api_name}", current_score, 600)

    def get_timestamp(self) -> int:
        """获取时间戳"""
        return int(time.time())

    def question_hash(self, question: Question) -> str:
        """生成题目哈希值"""
        content = f"{question.question}{''.join(question.options)}"
        # print(content,flush=True)
        # print('生成题目哈希值:',hashlib.md5(content.encode()).hexdigest(),flush=True)
        return hashlib.md5(content.encode()).hexdigest()

    async def get_free_answers(self, question: Question) -> List[AnswerResult]:
        """获取所有答案源"""
        tasks = [self.query_api(question)]
        return await asyncio.gather(*tasks)

    async def get_answers_free(self, question: Question) -> List[AnswerResult]:
        """免费答案获取"""
        tasks = [self.get_main_answer(question), self.get_answer1(question),self.get_answer2(question)]
        return await asyncio.gather(*tasks)

    async def get_answer1(self, question: Question) -> AnswerResult:
        """从一之题库获取答案"""
        headers = self._generate_random_headers()
        data = {"question": question.question}

        try:
            start_time = time.time()
            response = requests.post(
                "http://cx.icodef.com/wyn-nb?v=4",
                json=data,
                headers=headers,
                timeout=10
            )
            duration = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    answer_text = result.get('data', '')
                    # 过滤无效答案
                    invalid_keywords = ["傀儡", "公众号", "李恒雅", "一之"]
                    if not any(keyword in answer_text for keyword in invalid_keywords):
                        answers = answer_text.split('#')
                        print(answers,flush=True)
                        return AnswerResult(
                            form="一之题库",
                            answer=answers,
                            duration=duration
                        )

            return AnswerResult(
                form="一之题库",
                answer=[],
                duration=duration,
                msg="未找到答案"
            )

        except requests.exceptions.Timeout:
            self.score("icodef", -1)
            return AnswerResult(
                form="一之题库",
                answer=[],
                msg="timeout",
                duration=5000
            )
        except Exception as e:
            return AnswerResult(
                form="一之题库",
                answer=[],
                error=e,
                duration=10,
                msg="请求失败"
            )

    async def get_answer2(self, question: Question) -> AnswerResult:
        """从Muketool题库获取答案"""
        if question.type not in ['0', '1', '2']:
            return AnswerResult(
                form="muketool",
                answer=[],
                duration=0,
                msg="不支持的题型"
            )

        data = {
            "question": question.question,
            "type": int(question.type)
        }

        try:
            start_time = time.time()
            response = requests.post(
                "https://api.muketool.com/cx/v2/query",
                json=data,
                timeout=10
            )
            duration = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 1:
                    answers = result.get('data', '').split('#')
                    # print(2,answers,flush=True)
                    return AnswerResult(
                        form="muketool",
                        answer=answers,
                        duration=duration
                    )

            return AnswerResult(
                form="muketool",
                answer=[],
                duration=duration
            )

        except requests.exceptions.Timeout:
            self.score("muketool", -1)
            return AnswerResult(form="muketool", answer=[])
        except Exception as e:
            return AnswerResult(form="muketool", answer=[])

    async def get_main_answer(self, question: Question) -> AnswerResult:
        """从爱问答题库获取答案"""
        data = {
            "type": question.type,
            "question": question.question,
            "options": question.options.copy(),
            "html": question.html,
            "workType": question.work_type,
            "pageType": question.page_type
        }

        try:
            start_time = time.time()
            response = requests.post(
                "https://aiask.wk66.top/api/search",
                json=data,
                timeout=10
            )
            duration = int((time.time() - start_time) * 1000)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return AnswerResult(
                        form="爱问答题库",
                        answer=result.get('data', {}).get('answer', []),
                        duration=duration,
                        msg=result.get('msg', '')
                    )

            return AnswerResult(
                form="爱问答题库",
                answer=[],
                duration=duration,
                msg=result.get('msg', '') if response.status_code == 200 else '请求失败'
            )

        except Exception as e:
            return AnswerResult(
                form="爱问答题库",
                answer=[],
                error=e,
                duration=10,
                msg="请求失败"
            )

    async def query_api(self,question: Question)-> AnswerResult:
        """
        请求 wkexam API 获取答案
        :param question: 你要查询的问题字符串
        :param your_token: 你的 API Token
        :return: 解析后的 JSON 数据或错误信息
        """
        # API 的基础地址
        base_url = "https://webapi.zaizhexue.top/search"

        # 准备请求参数
        params = {
            "query": question.question,
            "type": "题目",
            "page": 1,
            "pageSize": 8,
            "sort": "newest"
        }

        try:
            start_time = time.time()

            # 发送 GET 请求
            response = requests.get(base_url, params=params, timeout=10)

            # 检查 HTTP 状态码
            response.raise_for_status()

            # 解析返回的 JSON 数据
            data = response.json()
            duration = int((time.time() - start_time) * 1000)

            # 根据返回的 code 判断请求是否成功
            if response.status_code == 200:
                answer = data["data"]["answer"]
                # 去掉首尾的空白字符（比如 \n 和空格）
                answer = re.split(r'#', answer.strip())
                print("请求成功！")
                if not answer:
                    return AnswerResult(
                form="免费题库",
                answer=[],
                duration=10,
                msg="无答案"
            )
                if type(answer)!=list:
                    answer=[str(answer)]
                return AnswerResult(
                    form="免费题库",
                    answer=answer,
                    duration=duration,
                    msg=data.get('msg', '')
                )
            else:
                return AnswerResult(
                    form="免费题库",
                    answer=[],
                    duration=10,
                    msg="请求失败"
                )

        except requests.exceptions.Timeout:
            print("请求超时，请检查网络或稍后重试。")
            return AnswerResult(
                form="免费题库",
                answer=[],
                duration=10,
                msg="请求失败"
            )
        except requests.exceptions.RequestException as e:
            print(f"请求过程中发生错误：{e}")
            return AnswerResult(
                form="免费题库",
                answer=[],
                error=e,
                duration=10,
                msg="请求失败"
            )
        except ValueError as e:
            print(f"解析返回数据失败，返回内容可能不是有效的 JSON。错误：{e}")
            return AnswerResult(
                form="免费题库",
                answer=[],
                error=e,
                duration=10,
                msg="请求失败"
            )

    def cache_answer(self, question: Question, answer: List[str]):
        """缓存答案"""
        cache_data = {
            'type': question.type,
            'question': question.question,
            'options': question.options,
            'answer': answer,
            'createTime': self.get_timestamp()
        }
        cache_key = f"ques1_{self.question_hash(question)}"
        self.cache.set(cache_key, cache_data)

    async def get_cache_answer(self, question: Question) -> AnswerResult:
        """从缓存获取答案"""
        cache_key = f"ques1_{self.question_hash(question)}"
        cached_data = self.cache.get(cache_key)

        if cached_data:
            return AnswerResult(
                form="本地缓存",
                answer=cached_data.get('answer', []),
                duration=10
            )
        else:
            return AnswerResult(
                form="本地缓存",
                answer=[],
                duration=10,
                msg="未找到缓存"
            )

    def _generate_random_headers(self) -> Dict[str, str]:
        """生成随机请求头"""
        ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
        return {
            "X-Forwarded-For": ip,
            "X-Real-IP": ip,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }


class AnswerMatcher:
    """答案匹配器"""

    @staticmethod
    def is_true(text: str) -> bool:
        """判断是否为正确"""
        true_keywords = ["正确", "对", "是", "true", "yes", "A"]
        return any(keyword in text for keyword in true_keywords)

    @staticmethod
    def is_false(text: str) -> bool:
        """判断是否为错误"""
        false_keywords = ["错误", "错", "否", "false", "no", "B"]
        return any(keyword in text for keyword in false_keywords)

    @staticmethod
    def remove_html(html: str) -> str:
        """去除HTML标签"""
        import re
        return re.sub('<[^<]+?>', '', html)

    def match_answer(self, answers: List[str], question: Question) -> List[int]:
        """匹配答案和选项"""
        options=question.options
        finally_options = []
        if len(answers) == 1 and question.type == '1':
            answers = answers[0]
        for answer in answers:
            matched_indices=None
            option_scores = []
            num=len(options)
            if answer in ['A', 'B', 'C', 'D', 'E', 'F', 'G','H'][:num]:
                dit = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
                matched_indices = dit.get(answer, None)
            else:
                for i, option in enumerate(options):
                    similarity = self._calculate_similarity(answer, option)
                    # print(i, option, similarity,flush=True)
                    if similarity >= 0.4:
                        option_scores.append((i, similarity))
                    if answer.lower() in option or option in answer.lower():
                        matched_indices=i
                        break
                if matched_indices is None:
                    if not option_scores:
                      break
                    option_scores.sort(key=lambda x: x[1], reverse=True)
                    matched_indices = option_scores[0][0]
            finally_options.append(matched_indices)
        return finally_options


    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """计算字符串相似度"""
        if not str1 or not str2:
            return 0.0

        # 简单的相似度计算：共同字符比例
        set1 = set(str1)
        set2 = set(str2)
        intersection = set1.intersection(set2)
        union = set1.union(set2)

        if not union:

            return 0.0

        return len(intersection) / len(union)
    def api_answer_match(self, answer_results: List[AnswerResult], question: Question) -> Dict[str, Any]:
        """API答案匹配逻辑"""
        if not answer_results:
            return {'res': answer_results, 'haveAnswer': False}

        question_type = question.type
        answers_to_use = []

        # 过滤有效答案
        for result in answer_results:
            if result.answer:
                answers_to_use.append(result)

        if not answers_to_use:
            return {'res': answer_results, 'haveAnswer': False}

        # 根据题目类型进行匹配
        if question_type in ['0', '1']:  # 单选/多选
            return self._match_choice_questions(answers_to_use, question)
        elif question_type == '3':  # 判断
            return self._match_judgment_questions(answers_to_use, question)
        elif question_type in ['2', '9', '4', '5', '6', '7']:  # 填空/简答等
            return self._match_text_questions(answers_to_use, question)
        else:
            return {'res': answer_results, 'haveAnswer': False}

    def _match_choice_questions(self, answers: List[AnswerResult], question: Question) -> Dict[str, Any]:
        """匹配选择题"""
        best_answer = None

        answer_result = answers[0]
        matched_indices = self.match_answer(answer_result.answer, question)
        best_answer = answer_result

        if len(matched_indices) > 0:
            return {
                'res': answers,
                'form': best_answer,
                'haveAnswer': True,
                'matchedIndices': matched_indices,
                'answerType': 'choice'
            }

        return {'res': answers, 'haveAnswer': False}

    def _match_judgment_questions(self, answers: List[AnswerResult], question: Question) -> Dict[str, Any]:
        """匹配判断题"""
        for answer_result in answers:
            if answer_result.answer:
                answer_text = answer_result.answer[0] if isinstance(answer_result.answer,
                                                                    list) else answer_result.answer
                if self.is_true(answer_text):
                    for option in question.options:
                        for keyword in   ["正确", "对", "是", "true", "yes","A"]:
                            if keyword in option:
                                return {
                                    'res': answers,
                                    'form': answer_result,
                                    'haveAnswer': True,
                                    'answer': option,
                                    'answerType': 'judgment'
                                }
                elif self.is_false(answer_text):
                    for option in question.options:
                        for keyword in   ["错误", "错", "否", "false", "no","B"]:
                            if keyword in option:
                                return {
                                    'res': answers,
                                    'form': answer_result,
                                    'haveAnswer': True,
                                    'answer': option,
                                    'answerType': 'judgment'
                                }

        return {'res': answers, 'haveAnswer': False}

    def _match_text_questions(self, answers: List[AnswerResult], question: Question) -> Dict[str, Any]:
        """匹配文本题（填空/简答）"""

        def has_letters(text):
            """检测文本中是否含有字母"""
            return bool(re.search(r'[a-zA-Z]', text))
        for answer_result in answers:
            if answer_result.answer[0] in ["正确", "对", "是", "true", "yes","错误", "错", "否", "false", "no",'答案:',''] or has_letters(answer_result.answer[0]):
                continue
            if answer_result.answer:
                return {
                    'res': answers,
                    'form': answer_result,
                    'haveAnswer': True,
                    'answer': answer_result.answer,
                    'answerType': 'text'
                }

        return {'res': answers, 'haveAnswer': False}


class AutoAnswer:
    """自动答题器"""

    def __init__(self):
        self.api = AnswerAPI()
        self.matcher = AnswerMatcher()
    def use_deepseek(self, question: Question) :
        """使用DeepSeek API获取答案"""
        start_time = time.time()
        typ_dict = {'0': '单选题', '1': '多选题', '2': '填空题', '3': '判断题', '9': '简答题'}
        title = "【" + typ_dict[question.type] + "】" + question.question + str(question.options)
        answer = DeepSeekAsk(question.API, title,typ_dict[question.type])
        if type(answer) is str:
            answer = ast.literal_eval(answer)  # 转换为列表

        duration = int((time.time() - start_time) * 1000)
        return [AnswerResult(
            form="Deepseek",
            answer=answer,
            duration=duration
        )]
    async def auto_answer_question(self, question: Question) -> Dict[str, Any]:
        """自动回答单个题目"""
        global status
        print(f"\n🔍 正在搜索题目答案...",flush=True)
        print(f"题目类型: {question.type} | 题目:{question.question[:50]}...",flush=True)

        # 1. 尝试从缓存获取答案
        cache_result = await self.api.get_cache_answer(question)
        print(f"📦 缓存查询结果: {'找到' if cache_result.answer else '未找到'}",flush=True)

        # 2. 如果缓存没有，从API获取
        if not cache_result.answer :
            print("🌐 开始从网络API获取答案...",flush=True)
            time.sleep(1)
            api_results = await self.api.get_answers_free(question)

            # 显示每个API的结果
            for i, result in enumerate(api_results, 1):
                status = "✅ 找到答案" if result.answer else "❌ 未找到"
                # print(f"   {status} | 耗时: {result.duration}ms",flush=True)
                print(result.answer,flush=True)
                if result.answer:
                    break

        else:
            api_results = [cache_result]
            print(f"🎯 使用缓存答案",flush=True)
            print(cache_result.answer,flush=True)
            # 3. 匹配答案
        match_result = self.matcher.api_answer_match(api_results, question)
        if not match_result.get('haveAnswer'):
            api_results=self.use_deepseek(question)
            match_result = self.matcher.api_answer_match(api_results, question)

        # 添加详细的来源信息输出
        if match_result.get('haveAnswer'):
            # 缓存找到的答案
            for result in api_results:
                if result.answer:
                    self.api.cache_answer(question, result.answer)
                    break
            answer_source = match_result.get('form')
            if answer_source:
                # print(f"🎉 答案来源: {answer_source.form}",flush=True)
                print(f"📝 答案内容: {answer_source.answer}",flush=True)
                print(f"⏱️ 查询耗时: {answer_source.duration}ms",flush=True)
                if answer_source.msg:
                    print(f"💬 附加信息: {answer_source.msg}",flush=True)
            else:
                print("⚠️ 找到答案但无法确定具体来源",flush=True)
        else:
            print("😔 所有来源均未找到答案",flush=True)

        return match_result


# 使用示例
async def main(typ, question, options,api):
        """主函数 - 添加详细的来源信息输出"""
        typ_dict = {'单选题': 0, '多选题': 1, '填空题': 2, '判断题': 3, '简答题': 9}
    # 创建题目实例
        question_obj = Question(
        type=str(typ_dict[typ]),  # 题目类型
        question=question,
        options=options,
        API=api)

    # 创建自动答题器
        auto_answer = AutoAnswer()

    # 自动答题
        result = await auto_answer.auto_answer_question(question_obj)

        if result['haveAnswer']:
            answer_source = result.get('form')
            if answer_source:
                # 根据题目类型显示具体答案
                answer_type = result.get('answerType')
                if answer_type == 'choice' and 'matchedIndices' in result:
                    indices = result['matchedIndices']
                    selected_options = [question_obj.options[i] for i in indices]
                    # print(f"   选项: {selected_options}",flush=True)
                    return selected_options
                elif answer_type == 'judgment':
                    # print(f"   判断: {[result.get('answer')]}",flush=True)
                    return [result.get('answer')]
                elif answer_type == 'text':
                    # print(f"   文本答案: {answer_source.answer}",flush=True)
                    return answer_source.answer
            return result['form'].answer if result.get('form') else []
        else:
            print("❌ 未找到答案",flush=True)
            return []
