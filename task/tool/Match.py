import re
from collections import Counter


def most_common_element(lst):
    counter = Counter(lst)
    max_count = max(counter.values())
    return [item for item, count in counter.items() if count == max_count]

def match(answer_options_dicts_lst, qType, question, answersList,  optionsWebElements):

    dit={'A':1,'B':2,'C':3,'D':4}
    num_lst=[]
    if qType == '单选题':
        for answer in answersList:
            if answer in ['A', 'B', 'C', 'D']:
                num=dit.get(answer)
                num_lst.append(num)
            else:
                match1 = re.search(r'[A-D]', str(answer))
                if match1:
                    answer = match1.group()
                    num = dit.get(answer)
                    num_lst.append(num)
                else:
                    for answer_options_dict in answer_options_dicts_lst:
                        num=dit.get(answer_options_dict.get(answer))
                        if num is None:
                            continue
                        else:
                            num_lst.append(num)
                            break
        i=int(most_common_element(num_lst)[0])
        return optionsWebElements[i-1]

    elif qType=='多选题':
        # answer_options_dict = answer_options_dicts_lst[0] # 取列表中的第一个元素
        for answer in answersList:
            if answer is None:
                answersList.remove(None)

        answerWebElementList = []
        answers_list=[]
        for answerList in answersList:
            for answer in answerList:
                if answer in ['A','B','C','D']:
                    answers_list.append(dit.get(answer))
                else:
                    answer_options_dict=answer_options_dicts_lst[0]
                    for content,option in answer_options_dict.items():
                        if content in answer:
                            num=dit.get(option)
                            if num is not None:
                                answers_list.append(num)
            if len(answers_list)!=0:
                break

        for i in answers_list:

            answerWebElementList.append(optionsWebElements[i-1])
        return answerWebElementList

        # return
    elif qType=='判断题' :
        answer=most_common_element(answersList)[0]
        if answer is None:
            for ans in answersList:
                if ans is not None:
                    answer=ans
        if answer:
            return optionsWebElements[0]
        else:
            return optionsWebElements[1]


