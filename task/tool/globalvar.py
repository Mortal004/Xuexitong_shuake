from task.tool.printer import color
from task.tool.factory import getPrinterBySetter
from task.tool.datamanger import *
from task.tool.exception import InitializationException
from task.tool import file
from task.tool.setter import *

# 全局变量是否初始化
is_init = False

# 学校配置
school_type: str

# 文件管理器
exception_log_manger: ExceptionLogManger    # 日志文件管理器

# 文件地址
user_file_path: str
cookie_file_path: str

# 浏览器配置
no_head = False
mute = False
no_img = False
browser_path = ""
driver_path = ""

# 任务点配置
judgment_TP_tate = True
quiz_get_answer_speed_max: int
quiz_get_answer_speed_min: int
quiz_click_speed_max: int
quiz_click_speed_min: int
decode_secret_status: int

# 其他配置
version = ""        # 程序当前版本

"""
    初始化异常信息打印器和分隔线打印器
"""
# 初始化异常打印器
errorPrinterSetter = MsgSetter("errorCfg")
errorPrinterSetter.color = "read"
errorPrinterSetter.horizontalSymbol = "*"
errorPrinter = getPrinterBySetter(errorPrinterSetter)

# 初始化分隔线打印器
splitSetter = SplitSetter("myDividerCfg")
splitSetter.symbol = "="
splitSetter.color = "green"
splitSetter.length = 20
splitSetter.message = ":I am the dividing line:"
splitSetter.leftmostSymbol = "<"
splitSetter.rightmostSymbol = ">"
spliter = getPrinterBySetter(splitSetter)


def init_global():
    """
    在配置文件中加载配置
    """
    global is_init, school_type, no_head, mute, no_img, browser_path, driver_path, user_file_path, cookie_file_path, \
        quiz_get_answer_speed_max, quiz_get_answer_speed_min, quiz_click_speed_max, quiz_click_speed_min, \
        exception_log_manger, version, decode_secret_status, judgment_TP_tate, version

    myCig = ConfigManger()
    try:
        # <--------------------加载浏览器配置------------------------->

        if myCig.getCfg("browser_config", "no_head") == "True":
            no_head = True
        if myCig.getCfg("browser_config", "mute_audion") == "True":
            mute = True
        if myCig.getCfg("browser_config", "no_img") == "True":
            no_img = True
        browser_path = file.is_file_exists(myCig.getCfg("browser_config", "browser_path"))
        if browser_path == "":
            raise Exception("浏览器路径错误，请检查路径 " + color.read(myCig.getCfg("browser_config", "browser_path")) + " 的正确性")
        driver_path = file.is_file_exists(myCig.getCfg("browser_config", "driver_path"))
        if driver_path == "":
            raise Exception("驱动路径错误，请检查路径 " + colour.read(myCig.getCfg("browser_config", "driver_path")) + " 的正确性")

        # <------------------------加载数据管理器----------------------->
        user_file_path = myCig.getCfg("user_config", "user_path")
        cookie_file_path = myCig.getCfg("user_config", "cookie_path")
        exception_log_manger = ExceptionLogManger(myCig.getCfg("other", "exception_log_file_path"))

        # <------------------------加载任务点配置----------------------->
        # ppt_speed_max = int(cfg_get("task_config", "ppt_speed_max"))
        # ppt_speed_min = int(cfg_get("task_config", "ppt_speed_min"))
        school_type = myCig.getCfg("school", "school_type")
        quiz_get_answer_speed_max = int(myCig.getCfg("task_config", "quiz_get_answer_speed_max"))
        quiz_get_answer_speed_min = int(myCig.getCfg("task_config", "quiz_get_answer_speed_min"))
        quiz_click_speed_max = int(myCig.getCfg("task_config", "quiz_click_speed_max"))
        quiz_click_speed_min = int(myCig.getCfg("task_config", "quiz_click_speed_min"))
        decode_secret_status = int(myCig.getCfg("task_config", "decode_secret_status"))
        judgment_TP_tate = eval(myCig.getCfg("task_config", "automatic_judgment_task_point_state"))

        # <------------------------加载其他点配置----------------------->
        version = file.get_json_data(myCig.getCfg("other", "version_file_path")).get("current_version")
        # default_wait_time = int(myCig.getCfg("other", "default_wait_time"))
        # default_wait_times = int(myCig.getCfg("other", "default_wait_times"))

        # 所有配置加载成功
        is_init = True
    except Exception as e:
        raise InitializationException(str(e))
