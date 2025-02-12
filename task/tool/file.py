# Copyright (c) 2025 Mortal004
# All rights reserved.
# This software is provided for non-commercial use only.
# For more information, see the LICENSE file in the root directory of this project.

import os
import configparser
import json

# 读取配置文件
def get_config_file(filename) -> configparser.ConfigParser:
    conf_obj = configparser.ConfigParser()
    try:
        conf_obj.read(filename, encoding="utf-8")
    except Exception as e:
        raise Exception(filename+"解析错误："+str(e)+"\n"+"请检查"+filename+"中的信息")
    return conf_obj

# 读取json文件
def get_json_data(filename) -> dict:
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            try:
                json_data = json.load(f)
            except Exception as e:
                raise Exception("文件 "+filename + " 解析错误：" + str(e) + "\n"
                                + "请检查 " + filename + " 中的信息")
        return json_data
    except FileNotFoundError:
        raise Exception("文件 "+filename+" 未找到")


# 保存json数据
def save_json_data(filename, dictData):
    with open(filename, "w", encoding="utf-8") as f:
        data = json.dumps(dictData, indent=4, ensure_ascii=False)
        f.write(data)


# 保存文本文件
def save_text_file(filename, text):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

# 向文本文件中添加数据
def append_text_file(filename, text):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(text)

# 判断文件是否存在
def is_file_exists(filename):
    return filename if os.path.exists(filename) else ""
