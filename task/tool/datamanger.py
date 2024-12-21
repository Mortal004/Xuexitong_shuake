# -*- encoding = utf-8 -*-
# @Time : 2022-04-14 21:10
# @Author : Levitan
# @File : datamanger.py
# @Software : PyCharm

# 系统包
import time
import pickle
import base64
from . import file

# 用户数据文件管理器
class UserManger:
    def __init__(self, filename):
        self.__filename = filename
        self.__users = file.get_json_data(filename)

    def getUserData(self, username) -> dict:
        return self.__users[username]

    def getUsersName(self) -> list:
        return list(self.__users.keys())

    def modifyUserData(self, name, newData, mode="pwd"):
        """
        :param name: 需要修改信息的用户名
        :param newData: 需要修改的新信息
        :param mode:
            "pwd": 修改密码
            "acc": 修改账号
            "del": 删除用户
        :return: void
        """
        if mode == "pwd":
            self.__users[name]["password"] = newData
        elif mode == "acc":
            self.__users[name]["account"] = newData
        elif mode == "del":
            self.__users.pop(name)
        file.save_json_data(self.__filename, self.__users)

    def addNewUser(self, name, account, password):
        self.__users[name] = {"account": account, "password": password}
        file.save_json_data(self.__filename, self.__users)


# cookies 文件管理器
class CookiesManger:
    def __init__(self, filename):
        self.__filename = filename
        self.__cookies = self.__readData(filename)

    def __readData(self, filename):
        cookiesDict = file.get_json_data(filename)
        usernameList = cookiesDict.keys()
        expiredUsernameList = []
        for username in usernameList:
            cookies_b64 = cookiesDict[username]
            cookies_bytes = base64.b64decode(cookies_b64)
            cookies_list = pickle.loads(cookies_bytes)
            # 检查cookies是否过期
            # 如果过期则移出 cookies 字典
            for i in cookies_list:
                if "expiry" not in list(i.keys()):
                    continue
                expiry_timestamp = int(i['expiry'])
                if expiry_timestamp < int(time.time()):
                    expiredUsernameList.append(username)
                    break
        for expiredUsername in expiredUsernameList:
            cookiesDict.pop(expiredUsername)
        file.save_json_data(self.__filename, cookiesDict)
        return cookiesDict

    def getNameList(self):
        return list(self.__cookies.keys())

    def getCookies(self, username):
        # 用户不存在返回空
        if username not in self.getNameList():
            return []
        cookies_b64 = self.__cookies[username]
        cookies_bytes = base64.b64decode(cookies_b64)
        cookies_list = pickle.loads(cookies_bytes)
        return cookies_list

    def setCookies(self, username, cookies):
        cookies_bytes = pickle.dumps(cookies)
        cookies_b64 = base64.b64encode(cookies_bytes)
        self.__cookies[username] = str(cookies_b64, encoding="utf-8")
        file.save_json_data(self.__filename, self.__cookies)

    def isUserExist(self, username: str) -> bool:
        return username in self.getNameList()

    def removeCookie(self, username):
        self.__cookies.pop(username)
        file.save_json_data(self.__filename, self.__cookies)

    def removeAll(self):
        self.__cookies.clear()
        file.save_json_data(self.__filename, self.__cookies)


# 异常等级类
# 用于指定异常发生的等级
class ExceptionLevel:
    low = 1
    middle = 2
    high = 3
    severe = 0


# 日志文件管理器
class ExceptionLogManger:
    EXC_LEVEL = {0: "严重", 1: "低级", 2: "中级", 3: "高级"}

    def __init__(self, filePath):
        self.__filename = filePath

    def writeLog(self, version, info, excLevel=ExceptionLevel.low):
        # 异常等级
        level = self.EXC_LEVEL[excLevel]
        # 时间
        nowTime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # 异常信息
        data = "异常等级："+level + \
               "\n时间："+nowTime + \
               "\n版本："+version + \
               "\n异常信息：\n"+info + \
               "\n\n"
        file.append_text_file(self.__filename, data)


# 配置文件管理器
class ConfigManger:
    _configFilePath = r".\package\config.ini"
    _config = file.get_config_file(_configFilePath)

    @classmethod
    def getCfg(cls, section, option, default_value=None, config_file_path=None):
        try:
            return cls._config.get(section, option)
        except Exception as e:
            if default_value is not None:
                return default_value
            err_info = "配置文件路径：" + config_file_path + "\n" + \
                       '读取配置失败：section="' + section + '", option="' + option + '"\n错误信息：' + str(e)
            raise Exception(err_info)

    @classmethod
    def change_cfg(cls, section, option, value):
        cls._config.set(section, option, value)
        cls._config.write(open(cls._configFilePath, "w", encoding="utf-8"))
